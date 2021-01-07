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
stripDate = re.compile('\d?\d\/\d\d?\/\d\d\d\d')
strippedDate = stripDate.search(date[0].text)

# Add the data to the list of current data (which is currently empty)
caseList.append(strippedDate[0])

# Finish writing the list showing [date,active,recovered,total] altogether
for VALUE in cases:
    caseList.append(int(VALUE.text.strip()))

'''This section checks to see if the data in caseList (the list of current data)
is already in the data text file. If it isn't, add it
'''

# Open the text file and paste the latest value of the list into there   
READ_COVID_FILE = open('COVIDCases.txt','r') # To read the file
APPEND_COVID_FILE = open('COVIDCases.txt','a') # To append new data to the file
writeData = 0

# Figure out if this line is already in the file; if so, writeData is turned to 'true' and loop is exited
for CHECK_LINE in READ_COVID_FILE:
    CHECK_LINE = CHECK_LINE.split()
    if CHECK_LINE != []: # Allows it to run if there is an empty space in the file
        if CHECK_LINE[0] == caseList[0]: # If data for this date is already written in the txt file...
            writeData = 1
            break

# If not, write the data
if writeData == 0:
    APPEND_COVID_FILE.write('\n'+str(caseList[0])+'\t'+str(caseList[1])+'\t'+str(caseList[2])+'\t'+str(caseList[3])+'\t')
    
# Close the files; we don't need them anymore    
READ_COVID_FILE.close()
APPEND_COVID_FILE.close()

'''
This section creates and displays a plot of all the data
'''

## Create lists to graph
dateList = []
activeList = []
recoveredList = []
totalList = []

COVID_FILE = open('COVIDCases.txt')
for COVID_FILE_LINE in COVID_FILE:
    SPLIT_COVID_FILE_LINE = COVID_FILE_LINE.split()
    if SPLIT_COVID_FILE_LINE == []: # Allows it to run if there is an empty space in the file
        continue
    elif SPLIT_COVID_FILE_LINE[0] == "Date": # Skips first line showing labels
        continue
    else: 
        # Add all the file data to the lists that will be used to make the graph
        dateList.append(SPLIT_COVID_FILE_LINE[0])
        activeList.append(int(SPLIT_COVID_FILE_LINE[1]))
        recoveredList.append(int(SPLIT_COVID_FILE_LINE[2]))
        totalList.append(int(SPLIT_COVID_FILE_LINE[3]))

COVID_FILE.close()

# Convert dates from strings to dates
dateList = pd.to_datetime(dateList,format='%m/%d/%Y')

# Make x-axis range label names
ALL_TIME_DATE_RANGE = pd.date_range(start=dateList[0], end=dateList[-1], periods=6)

ALL_TIME_DATA_FILE = open('ALL_TIME_DATA.txt','wt')
for num, DATE in enumerate(dateList):
    if pd.to_datetime('1/1/2021',format='%m/%d/%Y') < DATE < pd.to_datetime('05/31/2021',format='%m/%d/%Y'):
        ACCUMULATED_TOTAL = totalList[num]+224
        ACCUMULATED_RECOVERED = recoveredList[num]+224
    else:
        ACCUMULATED_TOTAL = totalList[num]
        ACCUMULATED_RECOVERED = recoveredList[num]
    ALL_TIME_DATA_FILE.write(f'{DATE}\t{activeList[num]}\t{ACCUMULATED_RECOVERED}\t{ACCUMULATED_TOTAL}\t\n')
ALL_TIME_DATA_FILE.close()

# # This file is already written, Fall 20 semester over, just needs to be referenced from now on
# FALL20_DATE_RANGE = []
# for DATE in dateList:
#     if DATE < pd.to_datetime('12/31/2020',format='%m/%d/%Y'):
#         FALL20_DATE_RANGE.append(DATE)  
# FALL20_DATA_FILE = open('FALL20_DATA.txt','wt')
# for f20num, DATE in enumerate(FALL20_DATE_RANGE):
#     FALL20_DATA_FILE.write(f'{DATE}\t{activeList[f20num]}\t{recoveredList[f20num]}\t{totalList[f20num]}\n')
# FALL20_DATA_FILE.close()

SPRING21_DATE_RANGE = []
for DATE in dateList:
    if pd.to_datetime('1/1/2021',format='%m/%d/%Y') < DATE < pd.to_datetime('05/31/2021',format='%m/%d/%Y'):
        SPRING21_DATE_RANGE.append("%s"% (DATE)) 
SPRING21_DATA_FILE = open('SPRING21_DATA.txt','wt')
for s21num, DATE in enumerate(SPRING21_DATE_RANGE):
    SPRING21_DATA_FILE.write(f'{DATE}\t{activeList[s21num+61]}\t{recoveredList[s21num+61]}\t{totalList[s21num+61]}\t\n')
SPRING21_DATA_FILE.close()

'''Create Graph 1: Accumulative total of all time'''
ACCUMULATIVE_GRAPH = plt.figure(dpi=100)

# Read the 'All Time Data' file, dateList, activeList shouldn't change
ACCUMULATIVE_RECOVERED_LIST = []
ACCUMULATIVE_TOTAL_LIST = []
newList = []
newRecoveredList = []

ALL_TIME_DATA_FILE = open('ALL_TIME_DATA.txt','r')
for alltimenum, ALL_TIME_LINE in enumerate(ALL_TIME_DATA_FILE):
    SPLIT_ALL_TIME_LINE = ALL_TIME_LINE.split('\t')
    ACCUMULATIVE_RECOVERED_LIST.append(int(SPLIT_ALL_TIME_LINE[2]))
    ACCUMULATIVE_TOTAL_LIST.append(int(SPLIT_ALL_TIME_LINE[3]))
    
    # Calculate new cases
    if len(dateList) > 1 and alltimenum > 1:
        newList.append(ACCUMULATIVE_TOTAL_LIST[-1]-ACCUMULATIVE_TOTAL_LIST[-2])
        newRecoveredList.append(ACCUMULATIVE_RECOVERED_LIST[-1]-ACCUMULATIVE_RECOVERED_LIST[-2])
    else: # To ensure the lists have the same length for plotting
        newList.append(0)  
        newRecoveredList.append(0)

# Plot the graph
plt.plot(dateList,activeList,'r',label='Active Cases')
plt.plot(dateList,ACCUMULATIVE_RECOVERED_LIST,'g',label='Recovered Cases')
plt.plot(dateList,ACCUMULATIVE_TOTAL_LIST,'b',label='Total Cases')
plt.plot(dateList,newList,'m',label='New Active Cases')
plt.plot(dateList,newRecoveredList,'y',label='New Recovered Cases')
plt.plot(dateList[-1],activeList[-1],'ms',mfc='none',markersize=7)
## Add: line for when random testing started - Oct 26th, 2020

# Add legend, titles, labels
plt.legend(loc = 2) # add location
plt.title('Accumulative COVID Cases at Mount Union')
plt.xlabel('Date')
plt.ylabel('Number of Cases')

## Add: Adjust x axis markers to show only last two digits of the year
## Add: Adjust dates that show beginning of each month or whatever, something consistent, just to make it nicer
plt.xticks(ALL_TIME_DATE_RANGE,rotation = 45)
plt.text(dateList[-1],activeList[-1]+6,activeList[-1])
plt.subplots_adjust(left=None, bottom=0.225, right=None, top=0.92, wspace=None, hspace=None)



plt.show()

# This just prints the most recent data from the website into the console, formatted nicely
print(f'On {caseList[0]}, there were {caseList[1]} active case(s), {caseList[2]} recovered case(s), and {caseList[3]} total cases.') #date,active,recovered,total



'''
GUI Application

Click buttons to: 
    collect potential new data
    produce ACCUMULATIVE_GRAPH showing accumualtive total of all time
    produce FALL20_GRAPH showing Fall 2020 data only
    produce SPRING21_Graph showing Spring 2021 data only
    produce COMPARE_SEMESTERS_GRAPH showing data for all semesters overlapped
    turn on/off features on graph (for example, the active case text on graph or line showing when random testing started)
show one graph at a time (maybe 2?), embedded in the application
'''











