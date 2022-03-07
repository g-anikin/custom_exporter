from prometheus_client import make_wsgi_app
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from wsgiref.simple_server import make_server
from functions import get_status_jenkins, get_status_ghe, get_status_sast, get_status_nexus, get_status_artifactory
from ssl_checker_trust import check_cert
from get_sast_queue import sast_queue_len

class DsoCollector(object):
    def __init__(self):
        pass

    def collect(self):
        gauge_dso_service = GaugeMetricFamily('dso_service_status', 'dso_service_status', labels=['service_name', 'domain'])
        gauge_nexus_service = GaugeMetricFamily('nexus_service_status', 'nexus_service_status', labels=['service_name'])
        gauge_artifactory_service = GaugeMetricFamily('artifactory_service_status', 'artifactory_service_status', labels=['service_name'])
        gauge_artifactory_node = GaugeMetricFamily('artifactory_node_status', 'artifactory_node_status', labels=['node_name'])
        gauge_artifactory_check_page = GaugeMetricFamily('artifactory_check_page_status', 'artifactory_check_page_status', labels=['domain'])
        gauge_cert_duration_check = GaugeMetricFamily('dso_service_cert_duration_check', 'dso_service_cert_duration_check', labels=['domain'])
        gauge_sans_check = GaugeMetricFamily('dso_service_sans_check', 'dso_service_sans_check', labels=['domain'])
        gauge_sast_queue_len = GaugeMetricFamily('sast_queue_len', 'sast_queue_len', labels=['domain'])
        get_status_jenkins(gauge_dso_service)
        get_status_ghe(gauge_dso_service)
        get_status_sast(gauge_dso_service)
        get_status_nexus(gauge_dso_service,gauge_nexus_service)
        get_status_artifactory(gauge_dso_service, gauge_artifactory_service, gauge_artifactory_node, gauge_artifactory_check_page)
        check_cert(gauge_cert_duration_check, gauge_sans_check)
        sast_queue_len(gauge_sast_queue_len)
        yield gauge_dso_service
        yield gauge_nexus_service
        yield gauge_artifactory_service
        yield gauge_artifactory_node
        yield gauge_artifactory_check_page
        yield gauge_cert_duration_check
        yield gauge_sans_check
        yield gauge_sast_queue_len


if __name__ == '__main__':
    REGISTRY.register(DsoCollector())
    app = make_wsgi_app()
    httpd = make_server('0.0.0.0', 5000, app)
    httpd.serve_forever()
