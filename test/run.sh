#!/bin/bash
echo "start monitor experiment"
sudo sysctl -w net.ipv4.tcp_congestion_control=reno
python Pullstat.py --exp exp1 \
		--iface eth1 \
		--nQ 2 \
		--out test.txt \
        --btnSpeed 5 \
		--sampleR 0.05 \
		--hs_bw 10 \
		--delay 10 \
		--maxq 100 \
		--intf eth1 \

echo "cleaning up..."
killall -9 iperf ping
mn -c > /dev/null 2>&1
echo "end"
