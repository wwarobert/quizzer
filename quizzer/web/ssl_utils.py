"""
SSL certificate utilities for HTTPS support.

Copyright 2026 Quizzer Project
Licensed under the Apache License, Version 2.0
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple

from quizzer.constants import CERT_FILENAME, CERT_VALIDITY_DAYS, KEY_FILENAME


def generate_self_signed_cert(
    cert_dir: str = "certs",
) -> Tuple[Optional[str], Optional[str]]:
    """
    Generate self-signed SSL certificates for HTTPS.

    Why we use HTTPS even in development:
    Modern browsers require HTTPS for certain features (geolocation, PWA, etc.)
    and encrypting traffic is good practice even locally.

    Args:
        cert_dir: Directory to store certificates (default: 'certs')

    Returns:
        tuple: (cert_path, key_path) or (None, None) if generation fails
    """
    try:
        from cryptography import x509
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.x509.oid import NameOID

        cert_path = Path(cert_dir) / CERT_FILENAME
        key_path = Path(cert_dir) / KEY_FILENAME

        # Check if certificates already exist
        if cert_path.exists() and key_path.exists():
            return str(cert_path), str(key_path)

        # Create certs directory if it doesn't exist
        Path(cert_dir).mkdir(exist_ok=True)

        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        # Generate certificate
        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Local"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Localhost"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Quizzer Development"),
                x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            ]
        )

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(
                # Certificate valid for configured days - balance security with convenience
                datetime.utcnow()
                + timedelta(days=CERT_VALIDITY_DAYS)
            )
            .add_extension(
                x509.SubjectAlternativeName(
                    [
                        x509.DNSName("localhost"),
                        x509.DNSName("127.0.0.1"),
                    ]
                ),
                critical=False,
            )
            .sign(private_key, hashes.SHA256())
        )

        # Write certificate to file
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        # Write private key to file
        with open(key_path, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

        print(f"✅ Generated self-signed certificates in '{cert_dir}/' directory")
        return str(cert_path), str(key_path)

    except ImportError:
        print(
            "⚠️  cryptography package not installed. Install with: pip install cryptography"
        )
        print("   Running without HTTPS support.")
        return None, None
    except Exception as e:
        print(f"⚠️  Failed to generate SSL certificates: {e}")
        print("   Running without HTTPS support.")
        return None, None
