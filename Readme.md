# HTTP headers and POST payload interception #

In this deployment, Squid proxy uses a local ICAP service written in Python to print HTTP headers and POST payloads. Both services are managed by supervisord which is the best option when running multiple sevices in a single container. Ideally, we should be using one container per service but for testing purposes I placed them in a single container and limit the comunications to localhost only 


### Build container ###
`docker build -t squid:icap -f squid_docker_file .`

### Run container with an interactive session ### 
`docker run -it --rm --name icap  squid:icap /bin/bash`

