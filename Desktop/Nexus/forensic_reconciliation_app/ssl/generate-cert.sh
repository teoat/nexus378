#!/bin/bash

# This script generates a self-signed SSL certificate.

# Set the output directory to the location of this script
OUTPUT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Certificate details
COUNTRY="US"
STATE="California"
LOCALITY="San Francisco"
ORG_NAME="Forensic Reconciliation Inc."
ORG_UNIT="Development"
COMMON_NAME="localhost"
EMAIL="dev@forensic-reconciliation.com"

# File names
KEY_FILE="$OUTPUT_DIR/key.pem"
CERT_FILE="$OUTPUT_DIR/cert.pem"

# Generate the private key and certificate
openssl req -x509 -newkey rsa:4096 -keyout "$KEY_FILE" -out "$CERT_FILE" \
  -sha256 -days 365 -nodes \
  -subj "/C=$COUNTRY/ST=$STATE/L=$LOCALITY/O=$ORG_NAME/OU=$ORG_UNIT/CN=$COMMON_NAME/emailAddress=$EMAIL"

echo "Certificate generated successfully:"
echo "Private Key: $KEY_FILE"
echo "Certificate: $CERT_FILE"
