#!/usr/bin/python

# this source is part of my Hackster.io project:  https://www.hackster.io/mariocannistra/radio-astronomy-with-rtl-sdr-raspberrypi-and-amazon-aws-iot-45b617

# this program will determine the overall range of signal strengths received during the whole session.

# this program can be run standalone but is usually run at end of session by  doscanw.py

# Its output will be stored in 2 files:
# dbminmax.txt and session-overview.png . The first contains two rows of text with just the maximum
# and minimum of the whole session. The second contains a chart of all the min and max values for each of
# the scan files

from glob import glob
import numpy as np
import radioConfig
import subprocess
import os
import datetime
import sys

import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def outmsg(smsg):
    thisprogmsg = "..findsessionrangew.py: " + smsg
    print(thisprogmsg)

def strinsert(source_str, insert_str, pos):
    return source_str[:pos]+insert_str+source_str[pos:]

outmsg("Finding session range...")

globmax = -9000
globmin = 9000

sessmin = np.empty(shape=[0, 1])
sessmax = np.empty(shape=[0, 1])
scantimeline = np.empty(shape=[0, 1])

sessionfolder = sys.argv[1]
overviewname = sessionfolder + os.sep + 'session-overview.png'
minmaxname = sessionfolder + os.sep + 'dbminmax.txt'
binpattern = sessionfolder + os.sep + '*.bin'

files_in_dir = sorted(glob(binpattern))
for fname in files_in_dir:
    outmsg(fname)
    dbs = np.fromfile(fname, dtype='float32')
    thismin=dbs.min()
    thismax=dbs.max()
    scantime=str(fname)[20:26]
    scandate=str(fname)[12:20]

    if thismin < globmin:
        globmin = thismin
    if thismax > globmax:
        globmax = thismax
    sessmin = np.append(sessmin, thismin)
    sessmax = np.append(sessmax, thismax)
    scantime = strinsert(scantime, ":", 2)
    scantime = strinsert(scantime, ":", 5)
    scantime = scandate[-2:] + " " + scantime
    msg = "%s %s %f %f" % (scandate,scantime,thismin,thismax)
    outmsg(msg)
    scantimeline = np.append(scantimeline, scantime)

mytitle = 'This session signal range: min %.2f .. max %.2f' % (globmin,globmax)
outmsg(mytitle)

# this red plot will help us in finding the scan with highest power range
# (when using the gainloop.py program it will be useful to find the best gain values)
# adding globmin value just to offset the red plot to the middle of the chart
sessdiff = ( sessmax - sessmin ) + globmin

xs = range(len(scantimeline))
plt.figure(figsize=(12, 9), dpi=600)
plt.xlabel('Scan time (UTC)', fontsize=8)
plt.ylabel('Signal power', fontsize=8)
plt.tick_params(labelsize=8)
plt.plot(xs, sessmax, linestyle='--', marker='o' )
plt.plot(xs, sessmin, linestyle='--', marker='o' )
#plt.plot(xs,sessdiff )
plt.xticks(xs,scantimeline,rotation=70,fontsize=8)

for i,j in zip(xs,sessmin):
    tann = '%.1f' % j
    plt.annotate( tann, xy=(i,j), xytext=(0,15), textcoords='offset points', fontsize=8 )
for i,j in zip(xs,sessmax):
    tann = '%.1f' % j
    plt.annotate( tann, xy=(i,j), xytext=(0,-20), textcoords='offset points', fontsize=8 )
plt.grid()
#leg = plt.legend( ('maxima','minima','difference'), loc='upper right' )
leg = plt.legend( ('maxima','minima'), loc='upper right' )
leg.get_frame().set_alpha(0.5)
plt.title(mytitle)
#plt.show()
plt.tight_layout()
plt.savefig(overviewname)

sessfile = open(minmaxname, "w")
sessfile.write(str(globmax))
sessfile.write("\n")
sessfile.write(str(globmin))
sessfile.write("\n")
sessfile.close()

outmsg("Session signal range chart saved")
