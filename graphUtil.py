from tkinter import *
from tkinter import filedialog
from matplotlib.widgets import Cursor
import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
from matplotlib.widgets import Button
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement

#----------------------------------------------
#	Function definitions - Main code below...
#----------------------------------------------


def toCartesian(dictOfPoints):
	kmlCoords(dictOfPoints) #call the other function to format for KML
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

kmlCoordinates = []

#works with the coordinates to use in Google Earth
def kmlCoords(dictOfPoints):
	latLon = []
	kmlLat = []
	kmlLon = []
	latDeg = 0
	lonDeg = 0
	latMin = 0
	lonMin = 0
	lat = 0.0
	lon = 0.0
	for val in dictOfPoints:
		latLon.append(dictOfPoints[val].split(",")[0])
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
			lonDeg = ("-" + lonDeg)
		lonMin = float(temp[3][:-1]) #get rid of E/W
		kmlLat.append(str(latDeg) + " " + str(latMin))
		kmlLon.append(str(lonDeg) + " " + str(lonMin))
	i = 0
	while i < len(kmlLon):
		kmlCoordinates.append(kmlLat[i] + ", " + kmlLon[i])
		i = i+1
	#print(kmlCoordinates)















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
#cursor = Cursor(ax, useblit=True, color='red', linewidth=1 )





plt.xlim(0, 500) #limit the x axis to 500 data points at a time

fig.suptitle("Use the 'Pan Axes' button to move the dataplot left and right")






#-------------------------------------------------

#	EVENT HANDLING STUFF - For mouse movement

#-------------------------------------------------

class Cursor:
    def __init__(self, ax):
        self.ax = ax
        self.lx = ax.axhline(color='k')  # the horiz line
        self.ly = ax.axvline(color='k')  # the vert line

        # text location in axes coords
        self.txt = ax.text( 0.7, 0.9, '', transform=ax.transAxes)

    def mouse_move(self, event):
        if not event.inaxes: return
        #establish use of the GPS plot again or dots will draw on the 'GPS to file' button
        plt.subplot(211).clear()
        gpsPlot()
        if event.xdata != None and (event.xdata >= 0 and event.xdata <= len(xList)):
        	x, y = event.xdata, event.ydata
        	mouseX = int(event.xdata)
        	# update the line positions
        	self.lx.set_ydata(y )
        	self.ly.set_xdata(x )
        	plt.plot(xList[mouseX], yList[mouseX], 'ro', linewidth=1) #GPS Dot
        	plt.draw()

#NEW CURSOR EVENTS
cursor = Cursor(ax)
fig.canvas.mpl_connect('motion_notify_event', cursor.mouse_move)



#Building KML File
class Kml:
	def toKML(self, event):
		#print("TO KML")
		XMLVER = ET.Element('?xml version="1.0" encoding="UTF-8"?')
		ROOT = ET.Element('gpx')
		ROOT.set('version', '1.0')
		
		TRACK = ET.SubElement(ROOT, 'trk')
		NAME = ET.SubElement(TRACK, 'name')
		NAME.text = 'GPX Track'
		#for point in plotLink:
		TRACKSEG = ET.SubElement(TRACK, 'trkseg')
			#NAME = PLACEMARK.SubElement(PLACEMARK, 'name')
		#LINESTRING = ET.SubElement(PLACEMARK, 'LineString')
		
		
		for index, point in enumerate(kmlCoordinates):
			print(point)
			TRACKPOINT = ET.SubElement(TRACKSEG, 'trkpt')
			TRACKPOINT.text = point
		#ET.dump(XMLVER)
		#rootString = ET.dump(ROOT)
		#kmlOutput = open('kmlOutput.kml', 'w')
		#kmlOutput.write('<?xml version="1.0" encoding="UTF-8"?>')
		#kmlOutput.write(ET.tostring(ROOT))
		#kmlOutput.close()
		tree = ET.ElementTree(ROOT)
		tree.write("UNIQUEname.gpx")


btn = plt.axes([0.5, 0.5, 0.1, 0.075]) #place the button roughly in the middle of the screen
#btn = host.axes()

callback = Kml()
toKMLButton = Button(btn, "GPS to KML")
toKMLButton.on_clicked(callback.toKML)

plt.show()