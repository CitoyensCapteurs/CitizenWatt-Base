#!/bin/bash

echo "Starting receive script…"
screen -dmS receive && screen -S receive -p 0 -X stuff "while true; do ./receive; done$(printf \\r)"
echo "Done !\n"
sleep 0.2
echo "Starting processing script…"
screen -dmS process && screen -S process -p 0 -X stuff "while true; do python3 process.py; done$(printf \\r)"
echo "Done !\n"

echo "Ready to start !"
