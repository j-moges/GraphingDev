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
	#using GPS coordinates in DDM format from file
	x = []
	y = []
	xGraph = []
	yGraph = []
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
			latDeg = int(latDeg) #make sure it's an int
		if "-" in temp[0]:
			latDeg = temp[0][1:]
			latDeg = (-(int(latDeg))) #make sure it's an int
		latMin = float(temp[1][:-1]) #get rid of N/S

		#longitude
		if "+" in temp[2]:
			lonDeg = temp[2][1:]
			lonDeg = int(lonDeg)
		if "-" in temp[2]:
			lonDeg = temp[2][1:]
			lonDeg = (-(int(lonDeg)))
		lonMin = float(temp[3][:-1]) #get rid of E/W

		#below is formatting to get the correct Latitude and Longitude for Google Earth
		#If the coordinate is negative, subtract to get the correct final coordinate
		if latDeg < 0:
			lat = float(latDeg) - (latMin / 60)
		else:
			lat = float(latDeg) + (latMin / 60)

		if lonDeg < 0:
			lon = float(lonDeg) - (lonMin / 60)
		else:
			lon = float(lonDeg) + (lonMin / 60)

		#have to do this to get all of the route gps coordinates to display properly...
		latDeg = latDeg + (-1*(latDeg*2))
		lonDeg = lonDeg + (-1*(lonDeg*2))

		#formatted to display the graph properly
		latGraph = float(latDeg) + (latMin / 60)
		lonGraph = float(lonDeg) + (lonMin / 60)


		#Error checking
		if (lat > 90.0) or (lat < -90.0):
			raise ValueError("Latitude value out of range " + str(lat))

		if (lon > 180.0) or (lon < -180.0):
			raise ValueError("Longitude value out of range " + str(lon))

		#xGraph and yGraph are for plotting
		xGraph.append(latGraph)
		yGraph.append(lonGraph)
		#x and y are for GPX file
		x.append(lat)
		y.append(lon)
		xStr = x[-1]
		yStr = y[-1]
		point = str(xStr) + ", " + str(yStr)
		points.append(point)
	return x, y, xGraph, yGraph


#formats the coordinates given in the bottom right corner of the figure when
#you mouse over the bottom plot
def format_coord(x, y):
	xLocation = int(x)
	fc_time = xLocation  #x
	fc_rpm = rpm[xLocation]
	fc_throttle = throttlePos[xLocation]
	fc_leanAngle = leanAngle[xLocation]
	fc_speed = speed[xLocation]
	return ("Time: %d RPM: %d Speed: %d Throttle: %d Lean: %d" % 
		(fc_time, fc_rpm, fc_speed, fc_throttle, fc_leanAngle))




#-------------------------------------------------------------------
#			END of Function Definitions - Start of main program
#-------------------------------------------------------------------
rpm = []
throttlePos = []
leanAngle = []
speed = []

def main():
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


	plotLink = {} #dictionary to link the mouse position in the lower plot to a dot on the GPS plot

	#this while loop only parses out and converts RPM.  Reuse this to do it for everything else
	while i < len(loggedData):
		dataPoint = loggedData[i][0] #String of the data point
		dataPoint = dataPoint.split(',') #creates a list separating different types of data

		gpsPoint = dataPoint[0] #get the GPS coordinate from the data point

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

	#gpxLat and gpxLong are used for output to the GPX file - xList and yList are used for plotting the route
	gpxLat, gpxLong, xList, yList = toCartesian(plotLink)

	#make a dictionary of points to use for the dot on the GPS plot
	gpsDots = {}
	i = 0
	while i < len(gpxLat):
		gpsDots[i] = gpxLat[i], gpxLong[i]
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
	ax4.axis['right'].toggle(all=True)


	host.set_xlabel('Time')
	host.set_ylabel('RPM', color='blue')
	ax2.set_ylabel('Throttle', color='green')
	ax3.set_ylabel('Lean Angle', color = 'orange')
	ax4.set_ylabel('Speed (MPH)', color = 'red')


	#not using these tuples right now, just plot the stuff
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

	plt.xlim(0, 500) #limit the x axis to 500 data points at a time

	fig.suptitle("Use the 'Pan Axes' button to move the data plot left and right", 
		fontweight='bold')






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
	        	self.lx.set_ydata(y)
	        	self.ly.set_xdata(x)
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
			TRACKSEG = ET.SubElement(TRACK, 'trkseg')

			for item in gpsDots:
				TRACKPOINT = ET.SubElement(TRACKSEG, 'trkpt')
				TRACKPOINT.set('lat', str(gpsDots[item][0]))
				TRACKPOINT.set('lon', str(gpsDots[item][1]))

			tree = ET.ElementTree(ROOT)
			tree.write("UNIQUEname.gpx")


	btn = plt.axes([0.5, 0.5, 0.1, 0.075]) #place the button roughly in the middle of the screen

	callback = Kml()
	toKMLButton = Button(btn, "GPS to GPX File")
	toKMLButton.on_clicked(callback.toKML)

	ax.format_coord = format_coord

	fig.canvas.set_window_title("Vehicle Data Viewer") #title of window

	#maximize the window on startup
	figMgr = plt.get_current_fig_manager()
	figMgr.window.state('zoomed') 

	plt.show()

main()	