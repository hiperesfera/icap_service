# HTTP headers and POST payload interception and inspection #

First of all, intercepting encrypted connections like HTTPS is bad (very bad) as it defeats the purpose of using encrypted connections. Having said that, there may be special circumstances, mostly within enterprise environments, where we need to monitor which websites users are connecting to and what information is being exchanged. This is mostly to detect and block employees browsing non related work content, unethical or illegal content and also preventing data exfiltration attempts.

In this deployment, Squid proxy uses a local ICAP service written in Python to print HTTP headers and POST payloads. Both services are managed by supervisord which is the best option when running multiple sevices in a single container. Ideally, we should be using one container per service but for testing purposes I placed them in a single container and limit the comunications to localhost only.



### Build container ###
`docker build -t squid:icap -f squid_docker_file .`

### Run container with an interactive session for troubleshooting purposes###
`docker run -it --rm --name icap  squid:icap /bin/bash`

then, inside the container run

`/etc/init.d/supervisor start`


# Why #

A lot of IaaS, PaaS, SaaS providers do not have dedicated endpoints per client. For example, AWS does not provide a unique URLs [....]
