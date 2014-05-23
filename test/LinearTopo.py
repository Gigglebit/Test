#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import irange,dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
from monitor import monitor_qlen
from subprocess import *
from multiprocessing import Process
from time import sleep, time
from plot_stats import plot_st
import os
import sys
from argparse import ArgumentParser

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

parser.add_argument('--buffSize', '-bS',
                    dest="buff",
                    action="store",
                    help="Buffersize",
                    required=False)

args = parser.parse_args()


class LinearTopo(Topo):
   "Linear topology of k switches, with one host per switch."

   def __init__(self, k=2, **opts):
       """Init.
           k: number of switches (and hosts)
           hconf: host configuration options
           lconf: link configuration options"""

       super(LinearTopo, self).__init__(**opts)

       self.k = k

       lastSwitch = None
       for i in irange(1, k):
           host = self.addHost('h%s' % i, cpu=.5/k)
           switch = self.addSwitch('s%s' % i)
           # 10 Mbps, 5ms delay, 1% loss, 1000 packet queue
           self.addLink( host, switch, bw=10, max_queue_size=1000, use_htb=True)
           if lastSwitch:
               self.addLink(switch, lastSwitch, bw=10, max_queue_size=1000, use_htb=True)
           lastSwitch = switch
       host = self.addHost('h3' , cpu=.5/k)
       self.addLink(host, lastSwitch, bw=10, max_queue_size=1000, use_htb=True)

def ping_latency(net):
    "(Incomplete) verify link latency"
    h1 = net.getNodeByName('h1')
    h1.sendCmd('ping -c 2 10.0.0.2')
    result = h1.waitOutput()
    print "Ping result:"
    print result.strip()

def set_q(iface, q):
    "Change queue size limit of interface"
    cmd = ("tc qdisc change dev %s parent 1:1 "
           "handle 10: netem limit %s" % (iface, q))
    os.system(cmd)

def set_speed(iface, spd):
    "Change htb maximum rate for interface"
    cmd = ("tc class change dev %s parent 1:0 classid 1:1 "
           "htb rate %s burst 15k" % (iface, spd))
    os.system(cmd)

def perfTest():
   "Create network and run simple performance test"
   topo = LinearTopo(k=2)
   net = Mininet(topo=topo,
                 host=CPULimitedHost, link=TCLink)
   net.start()
   print "Dumping host connections"
   dumpNodeConnections(net.hosts)
   print "Testing network connectivity"
   net.pingAll()
   ping_latency(net)
   h1 = net.getNodeByName('h1')
   h2 = net.getNodeByName('h2')
   h3 = net.getNodeByName('h3')
   #h1.cmd("tc -s qdisc show dev h1-eth0")
   print "Allocate two Qs to s1"
   #os.system("tc -s qdisc show dev %s" % args.iface)

   os.system("bash tc_cmd_diff.sh %s" % args.iface)
   #h1.cmd("bash tc_cmd_diff.sh h1-eth0")
   #h1.cmd("tc -s show dev h1-eth0")

  # h2.cmd('iperf -s -w 16m -p 5001 -i 1 > iperf-recv.txt &')
   h2.cmd('iperf -s -p %s -i 1 > iperf_server_TCP.txt &' % 5001)
#               (CUSTOM_IPERF_PATH, 5001, args.dir))
   h3.cmd('iperf -s -p %s -u -i 1 > iperf_server_UDP.txt &' % 5003)
   
   monitor = Process(target=monitor_qlen,
                     args=("%s"%args.iface,float(args.sampleR),int(args.nQ), "%s_%s"% (args.exp,args.out)))
   
   monitor.start()                        

   
   #h1.cmd("./monitor.sh test1 h1-eth0")
   CLI(net)

   monitor.terminate()
   
   os.system('killall -9 iperf' )

   net.stop()
   for i in xrange(int(args.nQ)):
       print "Saving and ploting output files..."
       plot_st("Q%d%s_%s" % (i+1,args.exp,args.out),int(args.btn),i+1)

   Popen("killall -9 cat", shell=True).wait()

if __name__ == '__main__':
   setLogLevel('info')
   perfTest()
