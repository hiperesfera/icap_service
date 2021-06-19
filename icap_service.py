import random
import socketserver
import logging
import re
import configparser
import urllib.parse
import sys
from pyicap import *

# File containing list of AWS account/tenant IDs that users can access
configuration_file_path="/opt/proxy/icap_service.config"


config = configparser.ConfigParser(allow_no_value=True)
config.read(configuration_file_path)
aws_account_ids = config.items("AWS Account IDs")
aws_api_ids = config.items("AWS API IDs")


logging.basicConfig(
    #filename='/var/log/icap/icap_service.log',
    stream=sys.stdout,
    level=logging.NOTSET,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


class ThreadingSimpleServer(socketserver.ThreadingMixIn, ICAPServer):
    pass


class ICAPHandler(BaseICAPRequestHandler):

    def aws_OPTIONS(self):
        self.set_icap_response(200)
        self.set_icap_header(b'Methods', b'REQMOD')
        self.set_icap_header(b'Service', b'ICAP Server 1.0')

        # https://tools.ietf.org/html/rfc3507#section-4.5
        # Preview consisting of only encapsulated HTTP headers, the ICAP client would add the following header to the ICAP request
        # It will send a zero-length chunk and stop and wait for a "go ahead" to send more encapsulated body bytes to the ICAP server.
        self.set_icap_header(b'Preview', b'0')
        self.send_headers(False)

    def aws_REQMOD(self):

        self.set_icap_response(200)

        #self.set_enc_request(' '.join(self.enc_req))
        for header in self.enc_req_headers:
            for value in self.enc_req_headers[header]:
                # Set an encapsulated header to the given value
                self.set_enc_header(header, value)

                #logging.info("HTTP HEADER %s %s", header, value)


                # API ACCESS CHECK - START
                # checking API Authentication header
                if header.lower() == b'host' and b'.amazonaws.com' in value:
                    aws_api_auth_header_credential = re.findall('Credential=(.+?)/', urllib.parse.unquote((self.enc_req_headers[b'authorization'][0]).decode('utf-8')))
                    if aws_api_auth_header_credential and aws_api_auth_header_credential[0].lower() not in dict(aws_api_ids):
                        logging.warning('AWS Key ID %s access has been denied', aws_api_auth_header_credential[0])
                        msg = "AWS Key ID" + aws_api_auth_header_credential[0] + "is not allowed to access AWS"
                        self.send_enc_error(403, body=msg)
                        self.send_headers(False)
                        return
                # API ACCESS CHECK - END


                # WEB CONSOLE ACCESS CHECK - START
                # checking if Cookie headers are present
                if header.lower() == b'cookie':
                    aws_info_user_cookie = re.findall('aws-userInfo=.+username', urllib.parse.unquote(value.decode('utf-8')))
                    if aws_info_user_cookie:
                        #logging.info('AWS userInfo Cookie : %s :', aws_info_user_cookie[0])

                        # Extracting the AWS account ID from the aws-userInfo Cookie
                        aws_requested_account = (re.findall('iam::([0-9]+):',aws_info_user_cookie[0]))[0]
                        logging.info('AWS Account : %s', aws_requested_account)

                        # Check if the request is accessing an AWS account/tenant ID that is not allowlisted
                        # Allowed AWS accounts are inside the icap_service.config file
                        if aws_requested_account and aws_requested_account not in dict(aws_account_ids):
                            logging.warning('AWS Account %s access has been denied', aws_requested_account)

                            # OPTION - Set encapsulated status in response instead of encoding an error message
                            #self.set_enc_status(b'HTTP/1.1 403 Forbidden')

                            # HTTP Deny message response
                            msg = "<html><body style=\"background-color:Tomato\"><center>"
                            msg += "<br><img src=\"https://s3.amazonaws.com/grational.com/error.gif\"></br></br></br>"
                            msg += "You are not allowed to access AWS Account/Tenant ID <b>" + aws_requested_account + "</b>"
                            msg += "</center></body></html>"

                            self.send_enc_error(403, body=msg)
                            self.send_headers(False)
                            return
                # WEB CONSOLE ACCESS CHECK - END


        # Set encapsulated request
        self.set_enc_request(b' '.join(self.enc_req))

        # Getting the body of the request
        if not self.has_body:
            self.send_headers(False)
            return
        else:
            self.send_headers(True)
            buff=b''
            while True:
                chunk = self.read_chunk()
                self.send_chunk(chunk)
                if chunk == b'':
                    break
                buff += chunk
            #logging.info("HTTP BODY %s", buff)

server = ThreadingSimpleServer((b'127.0.0.1', 1344), ICAPHandler)

try:
    while True:
        server.handle_request()
except:
    print("Exception happened during processing of icap_service.py")
