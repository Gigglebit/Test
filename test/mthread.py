import threading
import thread
from time import time,sleep
import os
#exitFlag=0
class myThread (threading.Thread):
	def __init__(self,threadID, iface, delay):
		super(myThread, self).__init__()
		self.threadID = threadID
		self.delay = delay
		self.iface = iface
		self.keepRunning = 1
	def run(self):
		print "Starting setQ"
		try:
		   start = time()
                   counter = 0
#         	   q=[5,10,20,50,80,100,200,500,800,1000]
		   q=[1,2,5,8,10]
                   while self.keepRunning:
		      end = time()
		      if end-start > self.delay:
			   set_q(self.iface,counter,q)
		      	   start = end 
        	           if counter < len(q)-1:
			      counter+=1
#		      sleep(self.delay)
		except KeyboardInterrupt:
		   print "Force stop"
  		print "Exiting setQ"
	def stop(self):
		self.keepRunning = 0

def set_q(iface,counter,q):

        	      cmd = ("tc qdisc change dev %s parent 1:100 "
               	             "handle 100: netem limit %s" % (iface, q[counter]))
        	      os.system(cmd)
