#!/bin/bash

rate=5Mbit
rate2=1kbit

function add_qdisc {
    dev=$1
    tc qdisc del dev $dev root
    echo qdisc removed

    tc qdisc add dev $dev root handle 1: htb default 1
    echo qdisc added

    tc class add dev $dev classid 1:1 parent 1: htb rate $rate ceil $rate
    tc class add dev $dev classid 1:10 parent 1:1 htb rate 0.1Mbit ceil 1Mbit
    tc class add dev $dev classid 1:11 parent 1:1 htb rate 4.9Mbit ceil $rate
    tc class add dev $dev classid 1:100 parent 1:10 htb rate 1kbit ceil 30kbit
    #tc class add dev $dev classid 11:1 parent 1:11 htb rate $rate2 ceil 200kbit
    echo classes created

    tc qdisc add dev $dev parent 1:100 handle 100: netem limit 5
    tc qdisc add dev $dev parent 1:11 handle 11: netem limit 1000
#    tc qdisc add dev $dev parent 1:1 handle 100: netem limit 1000
    echo netem added
    # Direct iperf traffic to classid 10:1
#    tc filter add dev $dev protocol ip parent 1: u32 match ip dport 5001 0xffff flowid 1:11
#    tc filter add dev $dev protocol ip parent 1: u32 match ip sport 5001 0xffff flowid 1:11
#    tc filter add dev $dev protocol ip parent 1: u32 match ip protocol 17 0xff flowid 1:11
#    tc filter add dev $dev protocol ip parent 1: u32 match ip protocol 6 0xff flowid 1:11

    tc filter add dev $dev protocol ip parent 1: u32 match ip sport 1 0xfc00 flowid 1:11 #0-1023
    tc filter add dev $dev protocol ip parent 1: u32 match ip sport 1024 0xffc0 flowid 1:11 #1024-1087
    tc filter add dev $dev protocol ip parent 1: u32 match ip sport 1088 0xfff0 flowid 1:11 #1088-1103
    tc filter add dev $dev protocol ip parent 1: u32 match ip sport 1104 0xfff8 flowid 1:11 #1104-1111
    tc filter add dev $dev protocol ip parent 1: u32 match ip sport 1112 0xfffc flowid 1:11 #1112-1115
    tc filter add dev $dev protocol ip parent 1: u32 match ip sport 1116 0xfffe flowid 1:11 #1116-1117
    tc filter add dev $dev protocol ip parent 1: u32 match ip sport 1118 0xffff flowid 1:11 #1118

    tc filter add dev $dev protocol ip parent 1: u32 match ip sport 1120 0xffe0 flowid 1:11 #1120-1151
    tc filter add dev $dev protocol ip parent 1: u32 match ip sport 1152 0xff80 flowid 1:11 #1152-1279
    tc filter add dev $dev protocol ip parent 1: u32 match ip sport 1280 0xff00 flowid 1:11 #1280-1535
    tc filter add dev $dev protocol ip parent 1: u32 match ip sport 1536 0xfe00 flowid 1:11 #1536-2048
    tc filter add dev $dev protocol ip parent 1: u32 match ip sport 2048 0xf800 flowid 1:11 #2048-4095
    tc filter add dev $dev protocol ip parent 1: u32 match ip sport 4096 0xf000 flowid 1:11 #4096-8191
    tc filter add dev $dev protocol ip parent 1: u32 match ip sport 8192 0xe000 flowid 1:11 #8192-16383
    tc filter add dev $dev protocol ip parent 1: u32 match ip sport 16384 0xc000 flowid 1:11 #16384-32767
    tc filter add dev $dev protocol ip parent 1: u32 match ip sport 32768 0x8000 flowid 1:11 #32768-65535




    #tc filter add dev $dev protocol ip parent 1: u32 match ip dport 1119 0xffff flowid 1:10
    tc filter add dev $dev protocol ip parent 1: prio 1 u32 match ip sport 1119 0xffff flowid 1:100
  #  tc filter add dev $dev protocol ip parent 1: prio 1 u32 match ip sport 1119 0xffff flowid 1:100

    #tc filter add dev $dev protocol ip parent 1: prio 1 u32 match ip dport 80 0xffff flowid 1:11
    #tc filter add dev $dev protocol ip parent 1: prio 1 u32 match ip sport 80 0xffff flowid 1:11
    echo filters added
}

add_qdisc $1
#add_qdisc s0-eth2
