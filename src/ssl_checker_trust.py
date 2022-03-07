import json
import ssl
import socket
import datetime
import os

#  Define some 'consts'
SERVICE_URL = 'service url'
EXPIRATION_DATE = 'certificate expiration date in days'
CN = 'certificate cn'
SANS = 'certificate san(s)'
RFC2818 = 'rfc2818 compliant'


# Get certificate info
def get_ssl_expiry_date(host_port):
    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'

    # Remove https from host (if exists)
    host_port = host_port.replace("https://", "")
    host = host_port.split(":")[0]

    try:
        port = host_port.split(":")[1]
    except IndexError:
        port = 443  # Default https port

    context = ssl.create_default_context()
    conn = context.wrap_socket(
        socket.socket(socket.AF_INET),
        # server_hostname=host.split(":")[0],
        server_hostname=host,
    )
    # 3 second timeout because Lambda has runtime limitations
    conn.settimeout(3.0)
    try:
        # conn.connect((host.split(":")[0], int(host.split(":")[1])))
        conn.connect((host, int(port)))
    except socket.timeout:
        print(f'Error: could not establish ssl handshake with server {host}')
        return ""
    except socket.gaierror:
        print(f'Error: dns name not known for server {host}')
        return
    except ssl.SSLCertVerificationError:
        print(f'Error: certificate has expired for server {host}')
        return ""

    ssl_info = conn.getpeercert()
    
    # Marshal cert data to json
    data = json.loads(json.dumps(ssl_info))
    
    # Get cert expires time
    try:
        expires_in = datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)
    except KeyError:
        print(f'Error: unable to get cert expiration info with "notAfter" for server {host}')
        return ""

    # Get CN cert name
    cn = ""
    try:
        for val in data['subject']:
            for v in val:
                if v[0] == 'commonName':
                    cn = v[1]
    except KeyError:
        cn = f'Error: unable to get cert info with "commonName" for server {host}'

    # Get SANs names
    sans = []
    try:
        for val in data['subjectAltName']:
            sans.append(val[1])
    except KeyError:
        sans.append(f'Error: unable to get cert info with "subjectAltName" for server {host}')


    returned_dict = {
        SERVICE_URL: f'https://{host}:{str(port)}',
        EXPIRATION_DATE: str((expires_in - datetime.datetime.utcnow()).days),
        CN: cn,
        SANS: ', '.join(sans),
        RFC2818: str(if_rfc_2818_compliant(cn, sans)),
    }

    return returned_dict


# check if cn in sans list
def if_rfc_2818_compliant(cn, sans):
    if cn in sans:
       return 1
    else:
        return 0


# Main func
def check_cert(gauge_cert_duration_check, gauge_sans_check):

    # Define list of hosts to check ssl certs
    hosts = os.environ.get('CHECK_CERT_HOSTS').split(',')

    for host in hosts:
        data = get_ssl_expiry_date(host)
        gauge_cert_duration_check.add_metric([data['service url']], data['certificate expiration date in days'])
        gauge_sans_check.add_metric([data['service url']], data['rfc2818 compliant'])
