## Runtime image 
FROM registry.access.redhat.com/ubi8/python-38
## Working directory
WORKDIR /app
## Copy sources
COPY --chown=1001:0 ./src ./src
## Working directory
WORKDIR /app/src
## Install Python requirements
RUN pip install -r ./requirements.txt
# Network properties
EXPOSE 5000
# Setting entrypoint for container
CMD python main.py