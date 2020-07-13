import argparse
import copy
import json
import os
import pathlib

from kmip.services.server import KmipServer


BASE_DIR = os.path.join(pathlib.Path(__file__).parent.parent.absolute())
CERT_BASE_PATH = os.path.join(BASE_DIR, 'certificates')
DEFAULT_CONF = {
    'hostname': '0.0.0.0',
    'port': 5696,
    'certificate_path': os.path.join(CERT_BASE_PATH, 'server_certificate.pem'),
    'key_path': os.path.join(CERT_BASE_PATH, 'server_key.pem'),
    'ca_path': os.path.join(CERT_BASE_PATH, 'root_certificate.pem'),
    'auth_suite': 'Basic',
    'database_path': os.path.join(BASE_DIR, 'kmip.db'),
    'enable_tls_client_auth': 'True',
    'tls_cipher_suites': [
        'TLS_RSA_WITH_AES_128_CBC_SHA256',
        'TLS_RSA_WITH_AES_256_CBC_SHA256',
        'TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384',
    ],
    'logging_level': 'DEBUG',
}


def write_config_file():
    override_path = os.path.join(BASE_DIR, 'server_config/override.json')
    if os.path.exists(override_path):
        with open(override_path, 'r') as f:
            user_overrides = json.loads(f.read())
    else:
        user_overrides = {}

    conf = copy.deepcopy(DEFAULT_CONF)
    conf.update(user_overrides)

    with open(os.path.join(BASE_DIR, 'server_config/server.conf'), 'w') as f:
        f.write('[server]\n')
        for k, v in conf.items():
            if isinstance(v, list):
                f.write(f'{k}=\n')
                if v:
                    for i in v:
                        f.write(f'\t{i}\n')
            else:
                f.write(f'{k}={v}\n')


def run_server():
    write_config_file()
    server = KmipServer(
        log_path=os.path.join(BASE_DIR, 'logs/log.log'),
        config_path=os.path.join(BASE_DIR, 'server_config/server.conf')
    )
    with server:
        server.serve()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help', dest='action')

    parser_run = subparsers.add_parser('run', help='Run KMIP Server')

    args = parser.parse_args()
    if args.action == 'run':
        run_server()
    else:
        parser.print_help()
