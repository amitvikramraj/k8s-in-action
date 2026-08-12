#!/bin/sh

steps=${1:-5}

echo "Initialization started..."
echo

for i in $(seq 1 $steps); do
    echo "    Performing init procedure $i/$steps"
    sleep 1
done

echo
echo "\nInitialization complete!"
