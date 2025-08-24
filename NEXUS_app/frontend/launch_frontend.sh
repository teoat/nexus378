#!/bin/bash
echo "Installing frontend dependencies..."
pip3 install -r requirements.txt
echo "Starting Nexus Platform Frontend..."
python3 app.py
