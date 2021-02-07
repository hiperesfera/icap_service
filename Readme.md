# HTTP headers and POST payload inteception #

In this deployment, Squid proxy uses a local ICAP service written in Python to print HTTP headers and POST payloads. 


Build container 
`docker build -t squid:icap -f squid_docker_file .`

Run container with an interactive session. 
`docker run -it --rm --name icap  squid:icap /bin/bash`

