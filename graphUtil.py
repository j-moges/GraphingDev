from tkinter import *
from tkinter import filedialog
from matplotlib.widgets import Cursor
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
from matplotlib.widgets import Button
from xml.etree.ElementTree import Element

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
		lonMin = float(temp[3][:-1]) #get rid of E/W

		lat = float(latDeg) + (latMin / 60)
		lon = float(lonDeg) + (lonMin / 60)
		x.append(lat)
		y.append(lon)
		xStr = x[-1]
		yStr = y[-1]
		point = str(xStr) + ", " + str(yStr)
		points.append(point)
	return x, y




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


i = 1

latitude = []
longitude = []
rpm = []
throttlePos = []
leanAngle = []
speed = []

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

	#RPM separation
	if rpmDataItem == "":
		rawRPMData = 0
	else:
	 	rawRPMData = int(rpmDataItem)
	rpm.append(rawRPMData)

	#Throttle Position
	throttleDataItem = (dataPoint[-1])
	throttleDataItem = throttleDataItem.replace(" ", "") #eliminate whitespace, just in case

	if throttleDataItem == "":
		rawThrottleData = 0
	else:
		rawThrottleData = int(throttleDataItem)
	throttlePos.append(rawThrottleData)
	#End Throttle position

	#Lean Angle
	leanAngleItem = (dataPoint[-3])
	leanAngleItem = leanAngleItem.replace(" ", "")

	if leanAngleItem == "":
		rawLeanAngle = 0
	else:
		rawLeanAngle = float(leanAngleItem)
	leanAngle.append(rawLeanAngle)
	#END lean angle

	#Speed
	speedItem = (dataPoint[-4])
	speedItem = speedItem.replace(" ", "")

	if speedItem == "":
		rawSpeed = 0
	else:
		rawSpeed = float(speedItem)
	speed.append(rawSpeed)
	#END Speed

	i = i+1

	#cartesian x/y = (degrees + minutes/60)

#gpsCart = toCartesian(plotLink) #returns ordered pairs for graphing GPS route
xList, yList = toCartesian(plotLink)

#make a dictionary of points to use for the dot on the GPS plot
gpsDots = {}
i = 0
while i < len(xList):
	gpsDots[i] = xList[i], yList[i]
	i = i + 1


#-----------------------------------------
#                                        -
#		   START PLOTTING                -
#                                        -  
#-----------------------------------------


#Small function to make it easier to clear the GPS plot of red dots
#This function simply creates the GPS plot 
def gpsPlot():
	plt.subplot(211) #create a 2 row by 1 column set of subplots (this is the first subplot)
	originalGPSPlot = plt.plot(xList, yList)
	plt.xlabel('GPS X')
	plt.ylabel('GPS Y')
	plt.axis('off') #turn off axes for the GPS plot	


fig = plt.figure()


plt.figure(1)
#plot the GPS 
gpsPlot()


#Set up axes variables
host = host_subplot(212, axes_class=AA.Axes) #RPM
ax2 = host.twinx() #Throttle Position
ax3 = host.twinx() #Lean Angle
ax4 = host.twinx() #Speed (MPH)

offset = 60 #offset beween axes

new_fixed_axis = host.get_grid_helper().new_fixed_axis
host.axis['left'] = new_fixed_axis(loc='left', axes=host, offset=(0, 0))
ax2.axis['right'] = new_fixed_axis(loc='right', axes=ax2, offset=(0, 0))
ax3.axis['left'] = new_fixed_axis(loc='left', axes=ax3, offset=(-offset, 0))
ax4.axis['right'] = new_fixed_axis(loc='right', axes=ax4, offset=(offset, 0))

#not sure this block does anything at all
host.axis['left'].toggle(all=True)
ax2.axis['right'].toggle(all=True)
ax3.axis['left'].toggle(all=True)
#ax3.axis['right'].toggle(ticklabels=False)
ax4.axis['right'].toggle(all=True)


host.set_xlabel('Time')
host.set_ylabel('RPM', color='blue')
ax2.set_ylabel('Throttle', color='green')
ax3.set_ylabel('Lean Angle', color = 'orange')
ax4.set_ylabel('Speed (MPH)', color = 'red')


#get tuple of the ticks for each plot???
hostTicks, = host.plot(rpm, color='blue', label = 'RPM')
ax2Ticks, = ax2.plot(throttlePos, color = 'green', label = 'Throttle Position')
ax3Ticks, = ax3.plot(leanAngle, color = 'orange', label = 'Lean Angle')
ax4Ticks, = ax4.plot(speed, color = 'red', label = 'Speed (MPH)')

#Turn off all axis stuff for the lean angle on the right
#without this the lean angle y axis would be duplicated and overlap the 
#throttle on the right side
ax3.axis['right'].toggle(all=False)

fig.subplots_adjust(hspace=.5) #spacing between the plots
ax = plt.gca() #get the current axes
#create a crosshair cursor on the lower plot (not GPS)
#OLD CROSSHAIR
cursor = Cursor(ax, useblit=True, color='red', linewidth=1 )








#-------------------------------------------------

#	EVENT HANDLING STUFF - For mouse movement

#-------------------------------------------------

def on_move(event):
	#get the X coordinate which corresponds to the index in the GPS coordinates
	#handle mouse event problems...Work-around because I couldn't get the event
	#to only trigger on the lower plot
	plt.subplot(211).clear()
	gpsPlot()
	if event.xdata != None and (event.xdata >= 0 and event.xdata <= len(xList)):
		mouseX = int(event.xdata)
		plt.subplot(211)
		plt.plot(xList[mouseX], yList[mouseX], 'ro', linewidth=1)
		plt.draw()


#Supposed to enter the bottom axes and trigger the on_move event to
#track the GPS dot.  That's not what ends up happening, but it works...
def enter_axes(event):
	fig.canvas.mpl_connect('motion_notify_event', on_move)
	event.canvas.draw()

def leave_axes(event):
    event.canvas.draw()


#event handlers that end up not really doing anything
fig.canvas.mpl_connect('axes_enter_event', enter_axes)
fig.canvas.mpl_connect('axes_leave_event', leave_axes)



#Building KML File
class Kml:
	def toKML(self, event):
		print("TO KML")
		"""E = Element()
		ROOT = E.kml
		PLACEMARK = E.placemark
		NAME = E.name
		POINT = E.point
		COORDS = E.coordinates
		kmlFile = ROOT(
					PLACEMARK(
						NAME('Test Name'),
						POINT(
							COORDS()
						)
					)
				)
		print(lxml.etree.tostring(kmlFile, pretty_print=True))"""

btn = plt.axes([0.8, 0.05, 0.1, 0.075])
callback = Kml()
toKMLButton = Button(btn, "GPS to KML")
toKMLButton.on_clicked(callback.toKML)

plt.show()