#!/bin/bash
bin_path="/home/di/Data/01/mongodb/bin/mongod"
port="27017"
db_path="/home/di/Data/01/Workplace/MongoDB/tornadobb"
log_path="/home/di/Data/01/Workplace/MongoDB/tornadobb.log"
bind_ip="127.0.0.1"
echo "Starting mongodb....."
echo "Listening at " $port
echo "DB Path: " $db_path
echo "Log Path: " $log_path
echo "Bind IP: " $bind_ip
$bin_path --port $port --dbpath $db_path  --logpath $log_path --bind_ip $bind_ip
echo "Mongodb started....."
