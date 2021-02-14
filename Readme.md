# HTTP headers and POST payload interception and inspection #

First of all, intercepting encrypted connections like HTTPS is bad (very bad) as it defeats the purpose of using encrypted connections. Having said that, there may be special circumstances, mostly within enterprise environments, where we need to monitor which websites users are connecting to and what information is being exchanged. This is mostly to detect and block employees browsing non related work content, unethical or illegal content and also preventing data exfiltration attempts.

In this deployment, Squid proxy uses a local ICAP service written in Python to print HTTP/S headers and POST payloads. Both services are managed by supervisord which is the best option when running multiple sevices in a single container. Ideally, we should be using one container per service but for testing purposes I placed them in a single container and limit the comunications to localhost only. 

Inspecting this content gives us full visibility inside the HTTP/S connections which we can use to create granular rules depending on the value of certain parameters like HTTP Cookies or POST payloads. 


### Build container ###
`docker build -t squid:icap -f squid_docker_file .`

### Run container with an interactive session for troubleshooting purposes###
`docker run -it --rm --name icap  squid:icap /bin/bash`

then, once inside the container run:

`/etc/init.d/supervisor start`

you can also 'tail' the icap_service log file to see what is happening in real-time while testing your HTTP/S connections

` tail -f /var/log/icap/icap_service.log`


# Why we want to do this #

A lot of IaaS, PaaS, SaaS providers do not have dedicated endpoints per client. For example, AWS does not provide a unique domain/URL per customer like customer-A.aws.amazon.com instead, all customers share and use the same domain/URL to access the different AWS services i.e. .aws.amazon.com. 

This presents some challenges when companies want to restrict employees to only have access to their corporate managed cloud environments from their workplace. Some cloud providers like Google and Azure have addressed this issue by injecting HTTP headers that contain the customer's IDs (or tenant ID) with the purpose of identifying and blocking any authentication attempts that does not belong to the given ID. This is done by deploying an on-premise inline proxy that intercepts and injects a HTTP header before the request is sent to the cloud provider. 

[DIAGRAM]


AWS, among other cloud providers, does not offer this option therefore employees would have the ability to connect to their personal AWS environment from the corporate network. Consequently, this opens an exfiltration channel that a malicious insider can leverage to leak classified information like intellectual property or personal information.


[DIAGRAM]


