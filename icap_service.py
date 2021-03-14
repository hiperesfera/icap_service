import random
import SocketServer
import logging
import re
import ConfigParser
import urllib
import sys
from pyicap import *

# File containing list of AWS account/tenant IDs that users can access
configuration_file_path="/opt/proxy/icap_service.config"


config = ConfigParser.ConfigParser(allow_no_value=True)
config.read(configuration_file_path)
aws_accounts = config.items("AWS Account IDs")

logging.basicConfig(
    #filename='/var/log/icap/icap_service.log',
    stream=sys.stdout,
    level=logging.NOTSET,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


class ThreadingSimpleServer(SocketServer.ThreadingMixIn, ICAPServer):
    pass


class ICAPHandler(BaseICAPRequestHandler):

    def aws_OPTIONS(self):
        self.set_icap_response(200)
        self.set_icap_header('Methods', 'REQMOD')
        self.set_icap_header('Service', 'ICAP Server' + ' ' + self._server_version)
        self.set_icap_header('Preview', '0')
        self.send_headers(False)

    def aws_REQMOD(self):

        self.set_icap_response(200)

        #self.set_enc_request(' '.join(self.enc_req))
        for header in self.enc_req_headers:
            for value in self.enc_req_headers[header]:
                # Set an encapsulated header to the given value
                self.set_enc_header(header, value)

                # checking if Cookie headers are present
                if header.lower() == 'cookie':
                    aws_info_user_cookie = re.findall('aws-userInfo=.+username', urllib.unquote(value))
                    if aws_info_user_cookie:
                        #logging.info('AWS userInfo Cookie : %s :', aws_info_user_cookie[0])

                        # Extracting the AWS account ID from the aws-userInfo Cookie
                        aws_requested_account = (re.findall('iam::([0-9]+):',aws_info_user_cookie[0]))[0]
                        logging.info('AWS Account : %s', aws_requested_account)

                        # Check if the request is accessing an AWS account/tenant ID that is not allowlisted
                        # Allowed AWS accounts are inside the icap_service.config file
                        if aws_requested_account and aws_requested_account not in dict(aws_accounts):
                            logging.warning('AWS Account %s access has been denied', aws_requested_account)

                            # OPTION - Set encapsulated status in response instead of encoding an error message
                            #self.set_enc_status('HTTP/1.1 403 Forbidden')

                            # HTTP Deny message response
                            msg = "<html><body style=\"background-color:Tomato\"><center>"
                            msg += "<br><img src=\"https://s3.amazonaws.com/grational.com/error.gif\"></br></br></br>"
                            msg += "You are not allowed to access AWS Account/Tenant ID <b>" + aws_requested_account + "</b>"
                            msg += "</center></body></html>"

                            self.send_enc_error(403, body=msg)
                            self.send_headers(False)
                            return

        # Set encapsulated request
        self.set_enc_request(' '.join(self.enc_req))

        # Getting the body of the request
        if not self.has_body:
            self.send_headers(False)
            return
        else:
            self.send_headers(True)
            buff=''
            while True:
                chunk = self.read_chunk()
                self.send_chunk(chunk)
                if chunk == '':
                    break
                buff += chunk
            #logging.info("HTTP POST BODY %s", buff)

server = ThreadingSimpleServer(('127.0.0.1', 1344), ICAPHandler)

try:
    while 1:
        server.handle_request()
except KeyboardInterrupt:
    print "Finished"
