#!/bin/sh

echo "Starting the webserver…"
screen -dmS visu && screen -S visu -p 0 -X stuff "while true; do python3 visu.py; done$(printf \\r)"

echo "Starting receive script…"
screen -dmS receive && screen -S receive -p 0 -X stuff "while true; do ./receive; done$(printf \\r)"
echo "Done !\n"
sleep 0.2
echo "Starting processing script…"
screen -dmS process && screen -S process -p 0 -X stuff "while true; do python3 process.py; done$(printf \\r)"
echo "Done !\n"

while ! curl -s --head http://localhost:8080 2>&1 > /dev/null; do
    echo "Webserver is starting…"
    sleep 1
done
echo "Webserver started !\n"

echo "Ready to start !"
