
In this deployment, a Squid proxy uses a local ICAP service written in Python to print HTTP hearders and POST payloads. 

docker build -t squid:icap -f squid_docker_file .

docker run -it --rm --name icap  squid:icap /bin/bash
