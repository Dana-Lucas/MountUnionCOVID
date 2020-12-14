# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 20:52:29 2020

@author: Dana


A program that navigates to the Mount Union COVID page, extracts the 
latest COVID data, appends the data to a txt file, and creates a graph 
of all the data showing active, recovered, and total cases on campus.

"""

import bs4, requests
import pandas as pd
import matplotlib.pyplot as plt
import re

'''
This section extracts the current data from the webpage and correctly formats it
into a list called caseList in the form of [date,active,recovered,total]
'''

# Go to the webpage specified by URL
res = requests.get('https://www.mountunion.edu/covid-19-cases-reporting')
res.raise_for_status()
soup = bs4.BeautifulSoup(res.text, 'html.parser')

# Find the data values on the webpage that are needed
date = soup.select('#content > section.pad-4-b.pad-5-b-lg-up > div > div > div > section > div > ul > li:nth-child(1) > div > p > i')
cases = soup.find_all(style="font-size: 60px")

# Create a list and save the date and three case values to the list
caseList = []
# This last part just cleans up the string so the date is the only thing appended
# caseList.append(date[0].text.strip('As of ')) 

# use RegEx to strip the date from other text (As of/time, etc), first digit 
# is optional, so for example 07/25/20 and 7/25/20 will both work
stripDate = re.compile('\d?\d\/\d\d?\/\d\d')
strippedDate = stripDate.search(date[0].text)

# Add the data to the list of current data (which is currently empty)
caseList.append(strippedDate[0])

# Finish writing the list showing [date,active,recovered,total] altogether
for i in cases:
    c = int(i.text.strip())
    caseList.append(c)

'''This section checks to see if the data in caseList (the list of current data)
is already in the data text file. If it isn't, add it
'''

# Open the text file and paste the latest value of the list into there   
f_r = open('COVIDCases.txt','r') # To read the file
f_a = open('COVIDCases.txt','a') # To append new data to the file
writeData = 0

# Figure out if this line is already in the file; if so, writeData is turned to 'true' and loop is exited
for l in f_r:
    s = l.split()
    if s[0] == caseList[0]: # If data for this date is not already written in the txt file...
        writeData = 1
        break
    
# If not, write the data
if writeData == 0:
    f_a.write('\n'+str(caseList[0])+'\t'+str(caseList[1])+'\t'+str(caseList[2])+'\t'+str(caseList[3]))
    
# Close the files; we don't need them anymore    
f_r.close()
f_a.close()

'''
This section creates and displays a plot of all the data
'''

## Create lists to graph
dateList = []
activeList = []
recoveredList = []
totalList = []
g = open('COVIDCases.txt')
for line in g:
    s = line.split()
    if s[0] == "Date":
        continue
    ## Add: Make it so it still runs when there is a blank line in there
    else: 
        # Add all the file data to the lists that will be used to make the graph
        dateList.append(s[0])
        activeList.append(int(s[1]))
        recoveredList.append(int(s[2]))
        totalList.append(int(s[3]))
g.close()

## Create the graph
plt.figure(dpi=100)

# Convert dates from strings to dates
dateList = pd.to_datetime(dateList,format='%m/%d/%y')

# Make x-axis range label names
dateRange = pd.date_range(start=dateList[0], end=dateList[-1], periods=6)

# Plot the graph
plt.plot(dateList,activeList,'r',label='Active Cases')
plt.plot(dateList,recoveredList,'g',label='Recovered Cases')
plt.plot(dateList,totalList,'b',label='Total Cases')
plt.plot(dateList[-1],activeList[-1],'ms',mfc='none',markersize=7)
# plt.plot([dateList[0],dateList[-1]],[activeList[-1],activeList[-1]],'m--',markersize=1)
## Add line for when random testing started - Oct 26

# Add legend, titles, labels
plt.legend(loc = 2) # add location
plt.title('COVID Cases at Mount Union')
plt.xlabel('Date')
plt.ylabel('Number of Cases')

## Add: Adjust x axis markers to show only last two digits of the year
plt.xticks(dateRange,rotation = 45)
plt.text(dateList[-1],activeList[-1]+3,activeList[-1])
plt.subplots_adjust(left=None, bottom=0.225, right=None, top=0.92, wspace=None, hspace=None)

plt.show()

# This just prints the most recent data from the website into the console
print(caseList) #date,active,recovered,total


# Trying to update