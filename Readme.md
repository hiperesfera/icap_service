
# How to limit what AWS Acccounts users can access from your corporate environment #

## Intercepting HTTP Cookies with Squid and an ICAP service could be the solution ##

While some Cloud Service Providers such as Azure or GCP support the injection of special HTTP headers containing a list of cloud accounts users can access to, AWS and other cloud providers do not offer such an option. In general, there is no easy way to prevent users from accessing external cloud resources that do not belong to your organization. 

This is one of the biggest security challenges when using cloud services providers in an enterprise environment, how to restrict employees to only access those cloud resources managed by the company. Cloud services providers could be become one of the biggest exfiltration channels if companies are not able to control how their internal employees interact with them. This has lead to different approach like completly blocking AWS 

How can you block users from uploading corporate data to a personal S3 bucket or pasting source-code into an external AWS Codecommit without blocking access to the AWS Management Console entirely ?


<p align="center"><img src="https://github.com/hiperesfera/icap_service/blob/main/data/picture1.png?raw=true"/></p>



This has led to multiple approaches, from reducing access to the Cloud management console only to a handful of employees, to completely disable the management console and enforcing programmatic access only via SDLC channels. These approaches are great but they do not entirely remove the fact that access to an external Cloud account is still possible.


Leveraging cookie interception at the perimeter proxy could be a way to tackle this problem. You will be surprised how much information is included in these Cookies, and how we could easily leverage this information to create rules based on certain criteria or conditions.

In this example, intercepting a simple AWS Cookie gives us the hability to allow or deny a connection to a certain AWS Account ID.

![alt text](https://github.com/hiperesfera/icap_service/blob/main/data/picture2.png?raw=true)

aws-infoUser Cookie contains the ARN of the IAM account connecting to the AWS environment. ARN is one of the main attributes when building IAM policies. They are unique identifiers for your AWS resources therefore, if we are able to inspect them at the proxy when users connect to AWS, it will be trivial using them to create rules containting the account IDSs your users can connect to. Or even go further, and restrict resources your users can use within a particular AWS account ID, but this would be reinventing the wheel as the IAM policies attached to your IAM account does that job for you.



In this example, I am using Squid and a ICAP service written in Python to PoC this idea. The main reason for using an ICAP service is that I did not manage to find an easy way for intercepting Cookies in Squid despite them being a HTTP header. If anyone found a way to do that, please do let me know as reducing the number of services in this deployment would significantly decrease the complexity and improve security :)













## HTTP headers and POST payload interception and inspection ##

First of all, intercepting encrypted connections like HTTPS is bad (very bad) as it defeats the purpose of using encrypted connections. Having said that, there may be special circumstances, mostly within enterprise environments, where we need to monitor which websites users are connecting to and what information is being exchanged. This is mostly to detect and block employees browsing non related work content, unethical or illegal content and also preventing data exfiltration attempts.

In this deployment, Squid proxy uses a local ICAP service written in Python to print HTTP/S headers and POST payloads. Both services are managed by supervisord which is the best option when running multiple sevices in a single container. Ideally, we should be using one container per service but for testing purposes I placed them in a single container and limit the comunications to localhost only. 

Inspecting this content gives us full visibility inside the HTTP/S connections which we can use to create granular rules depending on the value of certain parameters like HTTP Cookies or POST payloads. 


### Build container ###
`docker build -t squid:icap -f squid_docker_file .`

### Run container ###
`docker run -d --rm --name icap  squid:icap`

### Show the container logs ###
Squid and the ICAP service are both managed by the Supervisord service. Supervisord is configured to run the foreground (nodaemon) which makes logging available via /dev/stdout. You can see the logs using:

`docker logs -f icap`


### Run container with an interactive session for troubleshooting purposes ###
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


