# Custom prometheus exporter
Custom prometheus exporter based on python library prometheus_client.

## Exporter can get metrics of avaliability from servers:
* Jenkins
* Nexus
* GitHub Enterprise
* Checkmarx SAST
* JFrog Artifactory

## Other features
* Get metrics about certificate duration in days left
* Get metrics about certificate that hostname is in Subject Alternative Name
* Get metrics about SAST queue of started code-checks

## Avaliability is checking by HTTP-requests to:
* Jenkins login-page https://jenkins-server/login?from=%2F
* Nexus healthcheck-page https://nexus-server/service/rest/v1/status/check (exporter parces this page and get status of services)
* GitHub Enterprise status-page https://github-server/status
* Checkmarx SAST page https://sast-server/cxrestapi/auth/identity/connect/token (response 200 means that web-interface, database and other services are avaliable)
* JFrog Artifactory status pages: 
    * https://artifactory-server/artifactory/api/system/ping
    * https://artifactory-server/ui/api/v1/system/status/nodes (exporter parces this page and get status of nodes)
    * https://artifactory-server/artifactory/api/system/status (exporter parces this page and get status of services)
## Deploy using docker
1. Clone repository and go to its directory
```
$ git clone https://github.com/g-anikin/custom_exporter.git
$ cd custom_exporter/
```
2. Build docker image and run it(in run command you need to set all environment variables)
```
$ docker build -t custom_exporter -f ./Dockerfile .
$ docker run -it -d --name custom_exporter -p 5000:5000 custom_exporter
```
There is a kubernetes-template in okd-folder to deploy exporter in openshift/kubernetes.
