from tkinter import *
from tkinter import filedialog
from matplotlib.widgets import Cursor
import sys
import numpy as np
import matplotlib.pyplot as plt

root = Tk()
root.fileName = filedialog.askopenfilename( filetypes = 
	( ("Text File", "*.txt"), ("Comma Separated", "*.csv"), ("All Files", "*.*") ) )

logFile = root.fileName

root.quit() 
root.destroy() #close out the Tk interface for the file opening prompt

with open(logFile) as f:
	loggedData = f.readlines()

lineData = []
#get rid of \n and create a list for each set of values
loggedData = [i.split('\n') for i in loggedData]

print('-------------------')
print(loggedData[-1][0])


print('-----------------')

i = 1

latitude = []
rpm = []

#this while loop only parses out and converts RPM.  Reuse this to do it for everything else
while i < len(loggedData):
	dataPoint = loggedData[i][0] #String of the data point
	dataPoint = dataPoint.split(',') #creates a list separating different types of data

	rpmDataItem = (dataPoint[-2])
	rpmDataItem = rpmDataItem.replace(" ", "") #eliminate whitespace from the string

	if rpmDataItem == "":
		rawData = 0
	else:
	 	rawData = int(rpmDataItem)
	rpm.append(rawData)
	i = i+1



print(rpm)
#cell_text = []
#for i in rpm:
#	cell_text.append([i])
#print('-------------------------')
#print(cell_text)

fig = plt.figure()

columns = ('RPM')
"""plt.table(cellText = cell_text
	, colLabels=columns
	, loc='bottom')
"""
ax = plt.gca() #get the current axes
cursor = Cursor(ax, useblit=True, color='red', linewidth=2 )


plt.figure(1)
plt.subplot(211) #create a 2 row by 1 column set of subplots (this is the first subplot)
plt.plot(np.sin(1))

plt.subplot(212) #second subplot
plt.plot(rpm)
plt.ylabel('RPM')
plt.xlabel('Time?')
plt.show()