import random
import SocketServer
import logging

from pyicap import *

logging.basicConfig(
    filename='/var/log/icap_service.log',
    level=logging.NOTSET,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


class ThreadingSimpleServer(SocketServer.ThreadingMixIn, ICAPServer):
    pass

class ICAPHandler(BaseICAPRequestHandler):

    def echo_OPTIONS(self):
        self.set_icap_response(200)
        self.set_icap_header('Methods', 'REQMOD')
        #self.set_icap_header('Preview', '0')
        self.send_headers(False)

    def echo_REQMOD(self):
        # HTTP GET Headers
        if self.enc_req[0] != "POST":
            self.set_icap_response(200)
            self.set_enc_request(' '.join(self.enc_req))
            for h in self.enc_req_headers:
                for v in self.enc_req_headers[h]:
                    logging.info('HTTP Headers %s : %s', h, v)
                    self.set_enc_header(h, v)
            self.send_headers(False)
            self.no_adaptation_required()

        else:
            # HTTP POST Headers
            self.set_icap_response(200)
            if not self.has_body:
                self.set_enc_request(' '.join(self.enc_req))
                for h in self.enc_req_headers:
                    for v in self.enc_req_headers[h]:
                        logging.info('HTTP Headers %s : %s', h, v)
                        self.set_enc_header(h, v)
                self.send_headers(False)
                self.no_adaptation_required()
                return

            # HTTP POST Body
            buff = ''
            while True:
                chunk = self.read_chunk()
                if chunk == '':
                    break
                buff += chunk

            logging.info("HTTP POST %s", buff)

            self.send_headers(False)
            self.no_adaptation_required()

server = ThreadingSimpleServer(('127.0.0.1', 1344), ICAPHandler)
try:
    while 1:
        server.handle_request()
except KeyboardInterrupt:
    print "Finished"
