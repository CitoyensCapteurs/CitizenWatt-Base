#!/bin/bash

echo "Starting receive script…"
screen -dmS receive && screen -S receive -p 0 -X stuff "./receive$(printf \\r)"
echo "Done !\n"
sleep 0.2
echo "Starting processing script…"
screen -dmS process && screen -S process -p 0 -X stuff "python3 process.py$(printf \\r)"
echo "Done !\n"

echo "Ready to start !"
