#!/bin/bash
# GCP Firewall Configuration Script

echo "Configuring GCP firewall for JTS API..."

# Create firewall rule for port 5000
gcloud compute firewall-rules create allow-jts-api \
  --allow tcp:5000 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow JTS API access" \
  --direction INGRESS

echo "Firewall rule created successfully!"
echo "Testing connectivity..."

# Test the connection
curl -s http://localhost:5000/health

echo "Firewall configuration complete!" 