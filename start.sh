#!/bin/bash
apt-get update && apt-get install -y chromium-chromedriver
gunicorn -w 4 -b 0.0.0.0:10000 app:app