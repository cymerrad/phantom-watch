#!/bin/bash
sudo docker ps | awk '$2 ~ /mysql.*/ { print $1 }' | cut -d' ' -f1 | while read line; do ./force_kill_container.sh $line; sleep 1; sudo docker rm $line; done