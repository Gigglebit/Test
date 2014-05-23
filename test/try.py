#!/usr/bin/python
from time import *
from pylab import figure
import matplotlib.pyplot as plt

def col(n, obj = None, clean = lambda e: e):
    """A versatile column extractor.

    col(n, [1,2,3]) => returns the nth value in the list
    col(n, [ [...], [...], ... ] => returns the nth column in this matrix
    col('blah', { ... }) => returns the blah-th value in the dict
    col(n) => partial function, useful in maps
    """
    if obj == None:
        def f(item):
            return clean(item[n])
        return f
    if type(obj) == type([]):
        if len(obj) > 0 and (type(obj[0]) == type([]) or type(obj[0]) == type({})):
            return map(col(n, clean=clean), obj)
    if type(obj) == type([]) or type(obj) == type({}):
        try:
            return clean(obj[n])
        except:
            #print T.colored('col(...): column "%s" not found!' % (n), 'red')
            return None
    # We wouldn't know what to do here, so just return None
    #print T.colored('col(...): column "%s" not found!' % (n), 'red')
    return None


def read_list(fname, delim=','):
    start = time()
    print start
    lines = open(fname).xreadlines()
    ret = []
    for l in lines:
        ls = l.strip().split(delim)
        ls = map(lambda e: '0' if e.strip() == '' or e.strip() == 'ms' or e.strip() == 's' else e, ls)
        ret.append(ls)

    return ret
def plot_stats(fname,SPEED=5):
#fname = 'test_stats.txt'
#fname = 'Q1test2.txt'
#for i, f in enumerate():
#    print f
    data = read_list(fname)
    time = col(0,data)
    sent_B = col(1,data)
    sent_P = col(2,data)
    back_B = col(3,data)
    back_P = col(4,data)
    drop = col(5,data)
#SPEED = 5 #50Mbps

    reftime = []
    rate = []
    mrate = []
    mdelay = []
    delay = []
    utilink = []
    loss = []

    for i in range(len(time)):
        if i > 0:
           delta_t=float(time[i])-float(time[i-1])
           delta_sentB=int(sent_B[i])-int(sent_B[i-1])
           rate.append(delta_sentB/delta_t) # Throughput in B/s
           mrate.append(rate[i]*8/1000000)       # in MB/s
           desiredP = int(drop[i])-int(drop[0])+int(sent_P[i])-int(sent_P[0])
           if desiredP !=0:
              loss.append((int(drop[i])-int(drop[0]))/float(desiredP)*100) #Packet Loss
	   else:
              loss.append(0)
           reftime.append(float(time[i])-float(time[0])) #Reference Time
           utilink.append(delta_sentB*8*100/(delta_t*SPEED*1000000))#link utilisation
        else:
           reftime.append(0)
           rate.append(0)
           mrate.append(0)
           utilink.append(0)
           loss.append(0)
       
        if rate[i]!=0:
           delay.append(int(back_B[i])/rate[i]) # Foreseeable delay for any incoming data
           mdelay.append(delay[i] * 1000)       #in ms
        else: 
           delay.append(0)
           mdelay.append(0)

      

#      print "At time: %.3f s" % reftime[i]
#      print "Throughput: %.3f Mbps\nLoss in percentage: %.3f" % (mrate[i],loss[i])
#      print "Latency in the Q: %.3f ms delay" % mdelay[i]
#      print "Link Utilisation: %.0f percent" % utilink[i]
    plt.figure(1)
    plt.grid(True)

#ax=fig.add_subplot(111)
    plt.subplot(221)
#ax.plot(reftime,mrate)
    plt.title("Throughput vs Time",size=15)
    plt.plot(reftime,mrate)
    plt.ylabel("Mbps")
    plt.xlabel("Seconds")
    plt.ylim((0,5))

    plt.subplot(222)
    plt.plot(reftime,mdelay)
    plt.title("Queueing Delay vs Time",size=15)
    plt.ylabel("Milliseconds")
    plt.xlabel("Seconds")

    plt.subplot(223)
    plt.plot(reftime,loss)
    plt.title("Loss rate vs Time",size=15)
    plt.ylabel("Percentage")
    plt.xlabel("Seconds")
    plt.ylim((0,100))

    plt.subplot(224)
    plt.plot(reftime,utilink)
    plt.title("Link Utilisation on this Q vs Time",size=15)
    plt.ylabel("Percentage")
    plt.xlabel("Seconds")
    plt.ylim((0,100))
    plt.tight_layout(pad=0.5,w_pad=1.0,h_pad=1.0)
    plt.savefig("Throughput.png")

if __name__ == '__main__':
    plot_stats("Q1test2.txt",5)
