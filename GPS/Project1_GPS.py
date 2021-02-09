#!/bin/python
# MATH 465/665 Fall 2020 Project 1
#
# Copyright (c) 2016 by Michael Robinson <michaelr@american.edu>
# Adjusted 2020 by Donna Dietz <dietz@american.edu>
# Permission is granted to copy and modify for educational use, provided that this notice is retained
# Permission is NOT granted for all other uses -- please contact the author for details

# Load the necessary modules
from math import *
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re

def readGPX(filename):
    """Read a GPS track in GPX format

    lats,lons,els,ts=readGPX(filename)

    Input: filename = GPX file to read
    Output: lats = list of latitudes in track (degrees)
            lons = list of longitudes in track (degrees)
            els  = list of elevations in track (meters)
            ts   = list of times in track (seconds)"""

    # Format of the file we're interested amounts to three lines per sample
    # first with lat, lon, then elevation, followed by timestamp

    lats=[]
    lons=[]
    els=[]
    ts=[]

    # Open the file
    fy = open(filename,'r')
    data=""
    for line in fy:
        data=data+line
    fy.close()

    data2 = re.sub("\n","",data)
    data3 = re.sub("<trkpt","\n<trkpt", data2)
    data3 = re.sub("<ele","\n<ele", data3)
    data3 = re.sub("<time", "\n<time", data3)
    data3 = re.sub("Z</time", "</time", data3)
    datalines = re.split("\n", data3)

    for line in datalines:
        idx=0
        if line.startswith('<trkp',idx):
                    lats.append(float(line[line.find('lat='):].replace('=',' ').replace('\"',' ').split()[1]))
                    lons.append(float(line[line.find('lon='):].replace('=',' ').replace('\"',' ').split()[1]))
        elif line.startswith('<ele>',idx):
                    els.append(float(line[idx+5:].replace('<',' ').split()[0]))
        elif line.startswith('<time',idx):
                    a=line[line.find('T')+1:].replace(':',' ').replace('<',' ').split()
                    ts.append(float(a[0])*3600+float(a[1])*60+float(a[2]))
    return (np.array(lats),np.array(lons),np.array(els),np.array(ts))


# 3D plot of lat vs lon vs time
df = readGPX('gpstrack.gpx')

fig = plt.figure()
ax = fig.gca(projection='3d')
ax.set_xlabel('Latitude')
ax.set_ylabel('Longitude')
ax.set_zlabel('Time')
lats = df[0]
lons = df[1]
el = df[2]
ts = df[3]
ax.plot(lats, lons, ts)
ax.legend()

# 3d plot of lat vs lon vs elevation
plt.show()

fig = plt.figure()
ax = fig.gca(projection='3d')
ax.set_xlabel('Latitude')
ax.set_ylabel('Longitude')
ax.set_zlabel('Elevation')
ax.plot(lats, lons, el)
ax.legend()

plt.show()



def stepsize(lat1, long1, lat2, long2):
    """Compute distance between two lat/lon pairs in miles.
    Use the haversine formula explained at
    https://www.movable-type.co.uk/scripts/latlong.html
    """
    lat1 = lat1 * pi/180
    lat2 = lat2 * pi/180
    dlat = (lat2 - lat1)
    dlon = (long2 - long1) * pi/180
    a = (sin(dlat/2))**2 + cos(lat1)*cos(lat2) * (sin(dlon/2))**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    R = 6371000 # Earth's radius in meters
    d = R * c

    return d / 1609 # Meters to miles conversion

def stepsize_feet(lat1, long1, lat2, long2):
    """Compute distance between two lat/lon pairs in feet.
    """
    ss = stepsize(lat1, long1, lat2, long2)

    return ss * 5280 # Miles to feet conversion


def speedoverstep(lat1, long1, lat2, long2, ts1, ts2):
    """Compute speed in miles per hour between two lat/long pairs
    and two (epoch) timestamps in seconds.
    """

    ss = stepsize(lat1, long1, lat2, long2)

    dt = (ts2/60 - ts1/60) / 60 # Seconds to hours conversion

    return ss / dt


lats, lons, els, ts = readGPX("gpstrack.gpx")


# Takes GPX file as input and writes .csv as output
cum_dist = 0

f = open("output.csv", "w")
f.write("0, "+str(lats[0])+", "+str(lons[0])+", "+str(3.28084*els[0])+", "+"0, "+"0, "+"0, "+"\n")

for i in range(1, len(lons)):
    cum_dist += stepsize(lats[i-1], lons[i-1], lats[i], lons[i])
    f.write(str(i)+", "+str(lats[i])+", "+str(lons[i])+", "+str(3.28084 * els[i])+", "+\
    str(speedoverstep(lats[i-1], lons[i-1], lats[i], lons[i], ts[i-1], ts[i]))+", "+\
    str(cum_dist)+", "+\
    str(stepsize_feet(lats[i-1], lons[i-1], lats[i], lons[i]))+"\n")


f.close()
