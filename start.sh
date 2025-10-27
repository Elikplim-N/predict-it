#!/bin/bash

echo "========================================="
echo "ML Competition Platform"
echo "========================================="
echo ""

# Get IP address
echo "Your IP address(es):"
hostname -I
echo ""

echo "Students should access the platform at:"
echo "http://YOUR_IP_ADDRESS:5000"
echo ""

echo "Starting the application..."
echo "Press Ctrl+C to stop the server"
echo ""
echo "========================================="
echo ""

python3 app.py
