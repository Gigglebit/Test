#!/usr/bin/python

"""
"""
import re
import sys
import os

from mininet.log import setLogLevel, debug, info, error,lg
from mininet.net import Mininet
from mininet.link import Intf,TCIntf
from mininet.util import custom,quietRun,irange,dumpNodeConnections
from mininet.cli import CLI
from mininet.node import Node,Controller,RemoteController,OVSKernelSwitch
from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from monitor import monitor_qlen
from mthread import *
from subprocess import *
from plot_stats import plot_st
from time import sleep, time
from multiprocessing import Process
from argparse import ArgumentParser
from nathw import *

parser = ArgumentParser(description = "Pulling Stats Tests")

parser.add_argument('--exp', '-e',
                    dest="exp",
                    action="store",
                    help="Name of the Experiment",
                    required=True)

parser.add_argument('--iface', '-i',
                    dest="iface",
                    action="store",
                    help="Name of the Interface",
                    required=True)

parser.add_argument('--nQ', '-nQ',
                    dest="nQ",
                    action="store",
                    help="Tell me Number of Queues of this iface",
                    required=True)

parser.add_argument('--out', '-o',
                    dest="out",
                    action="store",
                    help="Name of the Output suffix",
                    required=True)

parser.add_argument('--btnSpeed', '-b',
                    dest="btn",
                    action="store",
                    help="Bottleneck link speed",
                    required=True)

parser.add_argument('--sampleR', '-s',
                    dest="sampleR",
                    action="store",
                    help="Sampling rate; Default is 1",
                    required=True)

parser.add_argument('--hs_bw', '-HS',
                    dest="hs_bw",
                    type=float,
                    action="store",
                    help="Bandwidth between hosts and switchs",
                    required=True)

parser.add_argument('--delay',
                    dest="delay",
                    type=float,
                    help="Delay in milliseconds of host links",
                    default=10)

parser.add_argument('--maxq',
                    dest="maxq",
                    action="store",
                    help="Max buffer size of network interface in packets",
                    default=100)

parser.add_argument('--intf',
                    dest="intf",
                    type=str,
                    action="store",
                    help="Real Interface",
                    required=True)

args = parser.parse_args()

class SimpleTopo(Topo):

   def __init__(self, k=2, ss_bw=50, dhs_bw=50, hs_bw=50, 
                maxq=None, diff=False):
       super(SimpleTopo, self).__init__()
       self.k = k
       dhcp = self.addHost('dhcp')
       switch = self.addSwitch('s1')
       self.addLink(dhcp,switch,bw=args.hs_bw, max_queue_size=int(args.maxq), use_htb=True)
       host = self.addHost('h1')
       self.addLink(host,switch,bw=args.hs_bw, max_queue_size=int(args.maxq), use_htb=True)
       
       


topos = { 'mytopo': ( lambda: SimpleTopo() ) }




def Test():
   "Create network and run simple performance test"
   topo = SimpleTopo(k=2)
   net = Mininet(topo=topo,
                 host=CPULimitedHost, link=TCLink)
   addrealintf(net,args.intf,args.btn,args.maxq)
   rootnode = connectToInternet(net)
   print "Dumping host connections"
   dumpNodeConnections(net.hosts)
   print "Testing network connectivity"
   net.pingAll()
   h1 = net.getNodeByName('h1')
   h2 = net.getNodeByName('dhcp')
   #h1.cmd("tc -s qdisc show dev h1-eth0")
   print "Allocate two Qs to s1"
   #os.system("tc -s qdisc show dev %s" % args.iface)
#   os.system("bash tc_cmd_diff.sh %s" % args.iface)
   os.system("bash tc_diablo.sh %s" % args.iface)
   #h1.cmd("bash tc_cmd_diff.sh h1-eth0")
   #h1.cmd("tc -s show dev h1-eth0")
  # h2.cmd('iperf -s -w 16m -p 5001 -i 1 > iperf-recv.txt &')
   #h2.cmd('iperf -s -p %s -i 1 > iperf_server_TCP.txt &' % 5001)
#               (CUSTOM_IPERF_PATH, 5001, args.dir))
   #monitoring the network
   monitor = Process(target=monitor_qlen,
                     args=("%s"%args.iface,float(args.sampleR),int(args.nQ), "%s_%s"% (args.exp,args.out)))   
       
   threadq = myThread(1,args.iface,120) 
   monitor.start() 
   threadq.start()                  
   #start mininet CLI
   CLI(net)
   #terminate
   monitor.terminate()
   threadq.stop()
   os.system('killall -9 iperf' )
   net.hosts[0].cmd('killall -9 dhcpd')
   stopNAT( rootnode )
   net.stop()
   #plot
   for i in xrange(int(args.nQ)):
       print "Saving and ploting output files..."
       plot_st("Q%d%s_%s" % (i+1,args.exp,args.out),int(args.btn),i+1)

   Popen("killall -9 cat", shell=True).wait()

if __name__ == '__main__':
   setLogLevel('info')
   Test()
