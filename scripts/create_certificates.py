import argparse
import datetime
import os

from cryptography import x509
from cryptography.hazmat import backends
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def create_rsa_private_key(key_size=2048, public_exponent=65537):
    private_key = rsa.generate_private_key(
        public_exponent=public_exponent,
        key_size=key_size,
        backend=backends.default_backend()
    )
    return private_key


def create_self_signed_certificate(subject_name, private_key, days_valid=365):
    subject = x509.Name([
        x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, u"Test, Inc."),
        x509.NameAttribute(x509.NameOID.COMMON_NAME, subject_name)
    ])
    certificate = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        subject
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=days_valid)
    ).sign(private_key, hashes.SHA256(), backends.default_backend())

    return certificate


def create_certificate(
    subject_name, private_key, signing_certificate, signing_key, days_valid=365, client_auth=False
):
    subject = x509.Name([
        x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, u"Test, Inc."),
        x509.NameAttribute(x509.NameOID.COMMON_NAME, subject_name)
    ])
    builder = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        signing_certificate.subject
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=days_valid)
    )

    if client_auth:
        builder = builder.add_extension(
            x509.ExtendedKeyUsage([x509.ExtendedKeyUsageOID.CLIENT_AUTH]),
            critical=True
        )

    certificate = builder.sign(
        signing_key,
        hashes.SHA256(),
        backends.default_backend()
    )
    return certificate


def create_root_certificate(root_ca_cn):
    root_key = create_rsa_private_key()
    return root_key, create_self_signed_certificate(root_ca_cn, root_key)


def create_server_certificate(server_cert_cn, root_cert, root_key):
    server_key = create_rsa_private_key()
    return server_key, create_certificate(server_cert_cn, server_key, root_cert, root_key)


def create_client_certificate(client_cn, root_cert, root_key):
    client_key = create_rsa_private_key()
    return client_key, create_certificate(client_cn, client_key, root_cert, root_key, client_auth=True)


def write_key_to_file(key, path):
    with open(path, 'wb') as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))


def write_cert_to_file(cert, path):
    with open(path, 'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))


def setup_certs(root_ca_cn, server_cert_cn, clients, destination):
    if not destination:
        destination = os.path.join(os.path.dirname(__file__), '..', 'certificates')

    root_key, root_certificate = create_root_certificate(root_ca_cn)

    server_key, server_certificate = create_server_certificate(server_cert_cn, root_certificate, root_key)

    client_certs = []
    for client in (clients or []):
        client_certs.append(create_client_certificate(client, root_certificate, root_key))

    write_cert_to_file(root_certificate, os.path.join(destination, 'root_certificate.pem'))
    write_key_to_file(root_key, os.path.join(destination, 'root_key.pem'))

    write_cert_to_file(server_certificate, os.path.join(destination, 'server_certificate.pem'))
    write_key_to_file(server_key, os.path.join(destination, 'server_key.pem'))

    for client_cn, client in zip(clients, client_certs):
        write_cert_to_file(client[1], os.path.join(destination, f'client_certificate_{client_cn}.pem'))
        write_key_to_file(client[0], os.path.join(destination, f'client_key_{client_cn}.pem'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help', dest='action')

    parser_setup = subparsers.add_parser('setup', help='Setup certificates')
    parser_setup.add_argument('--root_cn', help='Common name of ROOT CA', required=True)
    parser_setup.add_argument('--server_cn', help='Common name of Server Certificate', required=True)
    parser_setup.add_argument('-cl', '--client_list', nargs='+', help='Client certificates CN', required=True)
    parser_setup.add_argument(
        '--destination', help='Destination directory for writing certificates, defaults to certificates directory'
    )

    args = parser.parse_args()
    if args.action == 'setup':
        setup_certs(args.root_cn, args.server_cn, args.client_list, args.destination)
    else:
        parser.print_help()
