

docker build -t squid:icap -f squid_docker_file .

docker run -it --rm --name icap  squid:icap /bin/bash
