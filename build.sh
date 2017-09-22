#!/bin/bash

echo "Creating dist folder"
mkdir -p dist
echo "Copying lambda code into dist folder"
cp -f lambda/eb-platform-update-notify-slack.py ./dist/eb-platform-update-notify-slack.py
cd dist
echo "Creating lambda zip"
zip -r eb-platform-update-notify-slack .
cd ..
echo "DONE"
