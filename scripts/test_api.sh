#!/bin/bash

# Judicial Process Verification - Testing Script

echo "Testing Judicial Process Verification API"
echo "=========================================="
echo ""

# Configuration
API_URL="http://localhost:8000"
EXAMPLES_DIR="./examples"

# Test Health Endpoint
echo "Testing Health Endpoint..."
curl -s "${API_URL}/health" | json_pp
echo ""
echo ""

# Test Approved Process
echo "Testing Approved Process (0001234-56.2023.4.05.8100)..."
curl -s -X POST "${API_URL}/v1/verify" \
  -H "Content-Type: application/json" \
  -d @"${EXAMPLES_DIR}/test_process_approved.json" | json_pp
echo ""
echo ""

# Test Rejected Process (Labor)
echo "Testing Rejected Process - Labor Sphere (0100001-11.2023.5.02.0001)..."
curl -s -X POST "${API_URL}/v1/verify" \
  -H "Content-Type: application/json" \
  -d @"${EXAMPLES_DIR}/test_process_rejected_labor.json" | json_pp
echo ""
echo ""

# Test Incomplete Process
echo "Testing Incomplete Process (0023456-78.2022.4.05.0000)..."
curl -s -X POST "${API_URL}/v1/verify" \
  -H "Content-Type: application/json" \
  -d @"${EXAMPLES_DIR}/test_process_incomplete.json" | json_pp
echo ""
echo ""

echo "Testing complete!"
echo "View API documentation at: ${API_URL}/api/docs"

