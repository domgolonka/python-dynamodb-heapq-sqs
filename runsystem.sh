#!/bin/bash
INPUT_Q=$1
OUTPUT_Q=$2

echo $INPUT_Q


gnome-terminal -e ./frontend/frontend.py $INPUT_Q er
gnome-terminal -e ./database/DB1.py
