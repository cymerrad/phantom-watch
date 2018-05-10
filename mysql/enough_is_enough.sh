#!/bin/bash
./docker_force_kill.sh $(sudo docker ps | grep mysql1 | cut -d' ' -f1)