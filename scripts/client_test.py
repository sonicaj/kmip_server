import os
import pathlib

from kmip.pie.client import ProxyKmipClient
from kmip import enums


BASE_DIR = pathlib.Path(__file__).parent.parent.absolute()
CERT_BASE_PATH = os.path.join(BASE_DIR, 'certificates')


client = ProxyKmipClient(
    hostname='127.0.0.1',
    port=5696,
    cert=os.path.join(CERT_BASE_PATH, 'client_certificate_jane_doe.pem'),
    key=os.path.join(CERT_BASE_PATH, 'client_key_jane_doe.pem'),
    ca=os.path.join(CERT_BASE_PATH, 'root_certificate.pem'),
    ssl_version='PROTOCOL_SSLv23',
    config='client',
    config_file=os.path.join(BASE_DIR, 'client_conf/pykmip.conf')
)

client.open()

key_id = client.create(
    enums.CryptographicAlgorithm.AES,
    256,
    operation_policy_name='default',
    name='Test_256_AES_Symmetric_Key',
    cryptographic_usage_mask=[
        enums.CryptographicUsageMask.ENCRYPT,
        enums.CryptographicUsageMask.DECRYPT
    ]
)
print(f'Key [{key_id}] created')

key = client.get(key_id)
print(f'Key: {key}')
