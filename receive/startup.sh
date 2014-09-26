#!/bin/bash

screen -dmS receive && screen -S receive -p 0 -X stuff "./receive$(printf \\r)"
screen -dmS process && screen -S process -p 0 -X stuff "python3 process.py$(printf \\r)"
