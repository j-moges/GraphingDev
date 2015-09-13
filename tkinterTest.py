from tkinter import *
from tkinter import filedialog
import sys
import numpy
import matplotlib.pyplot as plt

root = Tk()
root.fileName = filedialog.askopenfilename( filetypes = 
	( ("Text File", "*.txt"), ("Comma Separated", "*.csv"), ("All Files", "*.*") ) )

logFile = root.fileName

with open(logFile) as f:
	loggedData = f.readlines()

lineData = []
#print(loggedData)
#print('-------------------')
#get rid of \n and create a list for each set of values
loggedData = [i.split('\n') for i in loggedData]
#print(loggedData)

#print(loggedData[0:3])
print('-------------------')
print(loggedData[-1][0])


print('-----------------')
#print(loggedData[0:3])
i = 1

rpm = []

#this while loop only parses out and converts RPM.  Reuse this to do it for everything else
while i < len(loggedData):
	dataPoint = loggedData[i][0] #String of the data point
	dataPoint = dataPoint.split(',') #creates a list separating different types of data

	dataItem = (dataPoint[-2])
	dataItem = dataItem.replace(" ", "") #eliminate whitespace from the string

	if dataItem == "":
		rawData = 0
	else:
	 	rawData = int(dataItem)
	rpm.append(rawData)
	i = i+1



print(rpm)
cell_text = []
for i in rpm:
	cell_text.append([i])
print('-------------------------')
print(cell_text)

columns = ('RPM')
plt.table(cellText = cell_text
	, colLabels=columns
	, loc='bottom')

plt.plot(rpm)
plt.ylabel('RPM')
plt.xlabel('Time?')
plt.show()