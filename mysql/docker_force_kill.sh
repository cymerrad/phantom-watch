#!/bin/bash
# $1 == container hash
_pid=$(ps -aux | grep $1 | grep -v grep | cut -d' ' -f6)
sudo kill -9 $_pid
return 0