#!/bin/bash

if [ $# -ne 2 ]
then
    echo "Usage: `basename $0` {experiment_name} {interface}"
exit
fi

exp=$1
iface=$2
sudo python exp_monitor.py -e ${exp} -i ${iface}
