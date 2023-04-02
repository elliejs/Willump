import asyncio
import aiohttp
from aiohttp import web
import datetime
import logging
import os
import socket
import ssl

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
        return IP

class Nunu:
    def __init__(self, wllp, Allow_Origin, sslCert, sslKey, forceNew, port, host):
        logging.info(f"Allow_Origin {Allow_Origin}")
        self._headers = {
            'Access-Control-Allow-Origin': Allow_Origin,
            'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }

        self.host=host or get_local_ip()

        self.wllp = wllp
        self.web_app = web.Application()
        self.web_app.add_routes([web.get('/ws', self.websocket_handler), web.route('*', '/{tail:.*}', self.router)])

        ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
        
        if not sslCert or not sslKey:
            sslCert, sslKey = self.createDefaultCert(forceNew)

        ssl_context.load_cert_chain(sslCert, sslKey)

        self.app_task = asyncio.create_task(web._run_app(self.web_app, host=self.host, port=port, ssl_context=ssl_context))
        logging.info(f"nunu started and running at {self.host}")

    # TODO: Make server return refused when Nunu is up but LCU isn't.
    async def router(self, req):
        logging.info(str(req.method) + str(req.rel_url))

        if req.method == 'OPTIONS':
            return web.Response(headers = self._headers)
        #if not self.wllp.willump_alive:
        #   return 500 yeet
        data = await req.json() if req.can_read_body else None
        resp = await self.wllp.request(req.method, req.rel_url, data=data)
        return web.json_response(await resp.json(), headers = self._headers)

    async def websocket_handler(self, request):

        ws = web.WebSocketResponse()
        await ws.prepare(request)

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    await ws.send_str(msg.data + '/answer')
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('ws connection closed with exception %s' %
                      ws.exception())

        print('websocket connection closed')

        return ws

    async def close(self):
        await self.web_app.shutdown()
        await self.web_app.cleanup()
        await self.app_task

    def createDefaultCert(self, forceNew):
        out_file_name: str = "domain_srv"
        #if the files exist just return them. don't regen unnessarily
        if not forceNew and os.path.isfile(out_file_name + ".crt") and os.path.isfile(out_file_name + ".key"):
            logging.debug("found existing ssl files, nunu will use those")
            return out_file_name + ".crt", out_file_name + ".key"
    
        # GENERATE KEY
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        with open(f"{out_file_name}.key", "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            ))

        subject = issuer = x509.Name([
            x509.NameAttribute(x509.NameOID.COUNTRY_NAME, u"RE"), #RUNETERRA, also Réunion, which is an island in the Indian Ocean that is an overseas department and region of France.
            x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, u"FRELJORD"),
            x509.NameAttribute(x509.NameOID.LOCALITY_NAME, u"NOTAI TRIBE"),
            x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, u"Friendly Yeti Incorporated"),
            x509.NameAttribute(x509.NameOID.COMMON_NAME, self.host),
        ])

        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            # Our certificate will be valid for 5 years
            datetime.datetime.utcnow() + datetime.timedelta(days=365*5)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(u"localhost"),
                x509.DNSName(self.host),
                x509.DNSName(u"127.0.0.1")]),
            critical=False,
        # Sign our certificate with our private key
        ).sign(key, hashes.SHA256())
        with open(f"{out_file_name}.crt", "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        return out_file_name