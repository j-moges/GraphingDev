from tkinter import *
from tkinter import filedialog
from matplotlib.widgets import Cursor
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA

#----------------------------------------------
#	Function definitions - Main code below...
#----------------------------------------------

def toCartesian(dictOfPoints):
	#using GPS coordinates in DDM format from file
	x = []
	y = []
	points = []
	latLon = []
	latDeg = 0
	lonDeg = 0
	latMin = 0
	lonMin = 0
	lat = 0.0
	lon = 0.0
	#just get the coordinates
	for val in dictOfPoints:
		latLon.append(dictOfPoints[val].split(",")[0])
	#now separate the latitude and longitude, do the math, and store in x and y
	for val in latLon:
		temp = val.split(" ")
		#print(temp)
		#latitude manipulation
		if "+" in temp[0]:
			latDeg = temp[0][1:]
			int(latDeg) #make sure it's an int
		if "-" in temp[0]:
			latDeg = temp[0][1:]
			int(latDeg) #make sure it's an int
			latDeg = (-latDeg)
		latMin = float(temp[1][:-1]) #get rid of N/S

		#longitude
		if "+" in temp[2]:
			lonDeg = temp[2][1:]
			int(lonDeg)
		if "-" in temp[2]:
			lonDeg = temp[2][1:]
			int(lonDeg)
			#print(lonDeg)
			#lonDeg = (-lonDeg)
		lonMin = float(temp[3][:-1]) #get rid of E/W

		lat = float(latDeg) + (latMin / 60)
		lon = float(lonDeg) + (lonMin / 60)
		x.append(lat)
		y.append(lon)
		xStr = x[-1]
		yStr = y[-1]
		point = str(xStr) + ", " + str(yStr)
		points.append(point)
	#print(points)
	return x, y


	#print(latLon)


#-------------------------------------------------------------------
#			END of Function Definitions - Start of main program
#-------------------------------------------------------------------

root = Tk()
root.fileName = filedialog.askopenfilename( filetypes = 
	( ("Text File", "*.txt"), ("Comma Separated", "*.csv"), ("All Files", "*.*") ) )

logFile = root.fileName

root.quit() 
root.destroy() #close out the Tk interface from the file opening prompt

with open(logFile) as f:
	loggedData = f.readlines()

lineData = []
#get rid of \n and create a list for each set of values
loggedData = [i.split('\n') for i in loggedData]

#print('-------------------')
#print(loggedData[-1][0])
#print('-----------------')

i = 1

latitude = []
longitude = []
rpm = []
throttlePos = []

plotLink = {} #dictionary to link the mouse position in the lower plot to a dot on the GPS plot

#this while loop only parses out and converts RPM.  Reuse this to do it for everything else
while i < len(loggedData):
	dataPoint = loggedData[i][0] #String of the data point
	dataPoint = dataPoint.split(',') #creates a list separating different types of data

	gpsPoint = dataPoint[0] #get the GPS coordinate from the data point
	#print(gpsPoint)

	rpmDataItem = (dataPoint[-2])
	rpmDataItem = rpmDataItem.replace(" ", "") #eliminate whitespace from the string

	plotLink[i] = (gpsPoint + ", " + rpmDataItem) #add the GPS and RPM to the dictionary

	if rpmDataItem == "":
		rawRPMData = 0
	else:
	 	rawRPMData = int(rpmDataItem)
	rpm.append(rawRPMData)

	throttleDataItem = (dataPoint[-1])
	throttleDataItem = throttleDataItem.replace(" ", "") #eliminate whitespace, just in case

	if throttleDataItem == "":
		rawThrottleData = 0
	else:
		rawThrottleData = int(throttleDataItem)
	throttlePos.append(rawThrottleData)
	i = i+1

	#cartesian x/y = (degrees + minutes/60)

#gpsCart = toCartesian(plotLink) #returns ordered pairs for graphing GPS route
xList, yList = toCartesian(plotLink)

#print(throttlePos)

#temp = 0 #this was just to check the ordered pairs
#for i in xList:
	#print("(" + str(xList[temp]) + ", " + str(yList[temp]) + ")")
	#temp += 1


#print(rpm)
#cell_text = []
#for i in rpm:
#	cell_text.append([i])
#print('-------------------------')
#print(cell_text)

fig = plt.figure()

"""columns = ('RPM')
plt.table(cellText = cell_text
	, colLabels=columns
	, loc='bottom')
"""



plt.figure(1)
plt.subplot(211) #create a 2 row by 1 column set of subplots (this is the first subplot)
plt.plot(xList, yList)
plt.xlabel('GPS X')
plt.ylabel('GPS Y')



plt.subplot(212) #second subplot

host = host_subplot(212, axes_class=AA.Axes)
#axisRPM = host.twinx()
#axisThrottle = host.twinx()
#axes = [axisRPM, axisThrottle]

#multiple y axes
#axisRPM.set_ylabel('RPM')
#axisThrottle.set_ylabel('Throttle Position') #or axes[1].set_ylabel('Throttle Position')



plt.plot(rpm, color='blue')
host.set_ylabel('RPM', color='blue')
ax2 = host.twinx()

ax2.plot(throttlePos, color = 'green')
#plt.plot(throttlePos, color = 'green', label = 'Throttle Position')
#plt.ylabel('RPM')
#plt.xlabel('Time')


ax2.set_ylabel('Throttle', color='green')
#host.set_ylabel('RPM', color='blue')
#for tl in host.get_yticklabels():
#    tl.set_color('blue')

#host.tick_params(axis='y')

fig.subplots_adjust(hspace=.5) #spacing between the plots
ax = plt.gca() #get the current axes
#create a crosshair cursor on the lower plot (not GPS)
cursor = Cursor(ax, useblit=True, color='red', linewidth=1 )

plt.show()