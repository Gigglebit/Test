#!/bin/bash

rate=5Mbit
rate2=0.1kbit

function add_qdisc {
    dev=$1
    tc qdisc del dev $dev root
    echo qdisc removed

    tc qdisc add dev $dev root handle 1: htb default 1
    echo qdisc added

    tc class add dev $dev classid 1:1 parent 1: htb rate $rate
    tc class add dev $dev classid 1:10 parent 1:1 htb rate $rate2 ceil $rate
    tc class add dev $dev classid 1:11 parent 1:1 htb rate $rate2 ceil $rate
    echo classes created

    tc qdisc add dev $dev parent 1:10 handle 10: netem limit 5
    tc qdisc add dev $dev parent 1:11 handle 11: netem limit 1000

    # Direct iperf traffic to classid 10:1
    #tc filter add dev $dev protocol ip parent 1: prio 1 u32 match ip dport 5001 0xffff flowid 1:10
    #tc filter add dev $dev protocol ip parent 1: prio 1 u32 match ip sport 5001 0xffff flowid 1:10
    tc filter add dev $dev protocol ip parent 1: prio 1 u32 match ip protocol 17 0xff flowid 1:10
    tc filter add dev $dev protocol ip parent 1: prio 1 u32 match ip protocol 6 0xff flowid 1:11
    #tc filter add dev $dev protocol ip parent 1: prio 1 u32 match ip dport 80 0xffff flowid 1:11
    #tc filter add dev $dev protocol ip parent 1: prio 1 u32 match ip sport 80 0xffff flowid 1:11
    echo filters added
}

add_qdisc $1
#add_qdisc s0-eth2
