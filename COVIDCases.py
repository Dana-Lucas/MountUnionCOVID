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
from datetime import datetime as dt
from datetime import timedelta
import matplotlib.patches as mpatches

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
This section creates and displays plots of the data
'''

FALL20_START_DATE = pd.to_datetime('2020-08-24',format='%Y/%m/%d')
FALL20_END_DATE = pd.to_datetime('2020-11-24',format='%Y/%m/%d')
SPRING21_START_DATE = pd.to_datetime('2021-01-11',format='%Y/%m/%d')
SPRING21_END_DATE = pd.to_datetime('2021-05-05',format='%Y/%m/%d')

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
ALL_TIME_DATE = pd.to_datetime('2020-09-01',format='%Y/%m/%d')
ALL_TIME_DATE_RANGE = [ALL_TIME_DATE]
while ALL_TIME_DATE < dateList[-1]:
    ALL_TIME_DATE += timedelta(weeks=5)
    ALL_TIME_DATE_RANGE.append(ALL_TIME_DATE) 
    
ALL_TIME_DATA_FILE = open('ALL_TIME_DATA.txt','wt')
for num, DATE in enumerate(dateList):
    if pd.to_datetime('1/1/2021',format='%m/%d/%Y') < DATE < pd.to_datetime('1/1/2022',format='%m/%d/%Y'):
        ACCUMULATED_TOTAL = totalList[num]+224
        ACCUMULATED_RECOVERED = recoveredList[num]+224
    else:
        ACCUMULATED_TOTAL = totalList[num]
        ACCUMULATED_RECOVERED = recoveredList[num]
    ALL_TIME_DATA_FILE.write(f'{DATE}\t{activeList[num]}\t{ACCUMULATED_RECOVERED}\t{ACCUMULATED_TOTAL}\t\n')
ALL_TIME_DATA_FILE.close()

# # This file is already written, Fall 20 semester over, just needs to be referenced from now on
# DATES_IN_FALL20 = []
# for DATE in dateList:
#     if FALL20_START_DATE < DATE < FALL20_END_DATE:
#         DATES_IN_FALL20.append(DATE)
# FALL20_DATA_FILE = open('FALL20_DATA.txt','wt')
# for f20num, DATE in enumerate(DATES_IN_FALL20):
#     FALL20_DATA_FILE.write(f'{DATE}\t{activeList[f20num]}\t{recoveredList[f20num]}\t{totalList[f20num]}\n')
# FALL20_DATA_FILE.close()

# DATES_IN_SPRING21 = []
# for DATE in dateList:
#     if SPRING21_START_DATE < DATE < SPRING21_END_DATE:
#         DATES_IN_SPRING21.append(DATE)
# SPRING21_DATA_FILE = open('SPRING21_DATA.txt','wt')
# for s21num, DATE in enumerate(DATES_IN_SPRING21):
#     SPRING21_DATA_FILE.write(f'{DATE}\t{activeList[s21num+61]}\t{recoveredList[s21num+61]}\t{totalList[s21num+61]}\t\n')
# SPRING21_DATA_FILE.close()

def ReadDataFile(file):
    DATE_LIST = []
    ACTIVE_LIST = []
    RECOVERED_LIST = []
    TOTAL_LIST = []
    NEW_LIST = []
    NEW_RECOVERED_LIST = []
    DATA_FILE = open(file,'r')
    for num, LINE in enumerate(DATA_FILE):
        SPLIT_LINE = LINE.split('\t')
        DATE_LIST.append(dt.strptime(SPLIT_LINE[0].split(' ')[0],"%Y-%m-%d"))
        ACTIVE_LIST.append(int(SPLIT_LINE[1]))
        RECOVERED_LIST.append(int(SPLIT_LINE[2]))
        TOTAL_LIST.append(int(SPLIT_LINE[3]))
            # Calculate new cases
        if len(DATE_LIST) > 1 and num > 1:
            NEW_LIST.append(TOTAL_LIST[-1]-TOTAL_LIST[-2])
            NEW_RECOVERED_LIST.append(RECOVERED_LIST[-1]-RECOVERED_LIST[-2])
        else: # To ensure the lists have the same length for plotting
            NEW_LIST.append(0)  
            NEW_RECOVERED_LIST.append(0)
    DATA_FILE.close()
    DATE_LIST = pd.to_datetime(DATE_LIST,format='%m/%d/%Y')
    return DATE_LIST,ACTIVE_LIST,RECOVERED_LIST,TOTAL_LIST,NEW_LIST,NEW_RECOVERED_LIST


# '''Graph 2: Fall 2020 Semester Only'''
# FALL2020_GRAPH = plt.figure(dpi=100)

# FALL20_DATE_LIST,FALL20_ACTIVE_LIST,FALL20_RECOVERED_LIST,FALL20_TOTAL_LIST,FALL20_NEW_LIST,FALL20_NEW_RECOVERED_LIST = ReadDataFile('FALL20_DATA.txt')
# FALL20_DATE_RANGE = pd.date_range(start=FALL20_DATE_LIST[0], end=FALL20_DATE_LIST[-1], periods=6)

# FALL20_DATE = FALL20_START_DATE
# FALL20_DATE_RANGE = [FALL20_DATE]
# while FALL20_DATE < FALL20_DATE_LIST[-1]:
#     FALL20_DATE += timedelta(days=7)
#     FALL20_DATE_RANGE.append(FALL20_DATE)  
    
# # # Plot the graph
# # plt.plot(FALL20_DATE_LIST,FALL20_ACTIVE_LIST,'r',label='Active Cases')
# # plt.plot(FALL20_DATE_LIST,FALL20_RECOVERED_LIST,'g',label='Recovered Cases')
# # plt.plot(FALL20_DATE_LIST,FALL20_TOTAL_LIST,'b',label='Total Cases')
# # plt.plot(FALL20_DATE_LIST,FALL20_NEW_LIST,'m',label='New Active Cases')
# # plt.plot(FALL20_DATE_LIST,FALL20_NEW_RECOVERED_LIST,'y',label='New Recovered Cases')
# # plt.plot(FALL20_DATE_LIST[-1],FALL20_ACTIVE_LIST[-1],'ms',mfc='none',markersize=7)
# # ## Add: line for when random testing started - Oct 26th, 2020

# # # Add legend, titles, labels
# # plt.legend(loc = 2) # add location
# # plt.title('Fall 2020 COVID Cases at Mount Union')
# # plt.xlabel('Date')
# # plt.ylabel('Number of Cases')

# # ## Add: Adjust x axis markers to show only last two digits of the year
# # ## Add: Adjust dates that show beginning of each month or whatever, something consistent, just to make it nicer
# # plt.xticks(FALL20_DATE_RANGE,rotation = 45)
# # plt.text(FALL20_DATE_LIST[-1],FALL20_ACTIVE_LIST[-1]+6,FALL20_ACTIVE_LIST[-1])
# # plt.subplots_adjust(left=None, bottom=0.225, right=None, top=0.92, wspace=None, hspace=None)








'''Create Graph 1: Accumulative Total of All Time'''
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
ALL_TIME_DATA_FILE.close()

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

'''Graph 2: Fall 2020 Semester Only'''
FALL2020_GRAPH = plt.figure(dpi=100)

# FALL20 = SemesterData('FALL20_DATA.txt')
FALL20_DATE_LIST,FALL20_ACTIVE_LIST,FALL20_RECOVERED_LIST,FALL20_TOTAL_LIST,FALL20_NEW_LIST,FALL20_NEW_RECOVERED_LIST = ReadDataFile('FALL20_DATA.txt')
FALL20_DATE_RANGE = pd.date_range(start=FALL20_DATE_LIST[0], end=FALL20_DATE_LIST[-1], periods=6)

FALL20_DATE = FALL20_START_DATE
FALL20_DATE_RANGE = [FALL20_DATE]
while FALL20_DATE < FALL20_DATE_LIST[-1]:
    FALL20_DATE += timedelta(days=7)
    FALL20_DATE_RANGE.append(FALL20_DATE)  
    
# Plot the graph
plt.plot(FALL20_DATE_LIST,FALL20_ACTIVE_LIST,'r',label='Active Cases')
plt.plot(FALL20_DATE_LIST,FALL20_RECOVERED_LIST,'g',label='Recovered Cases')
plt.plot(FALL20_DATE_LIST,FALL20_TOTAL_LIST,'b',label='Total Cases')
plt.plot(FALL20_DATE_LIST,FALL20_NEW_LIST,'m',label='New Active Cases')
plt.plot(FALL20_DATE_LIST,FALL20_NEW_RECOVERED_LIST,'y',label='New Recovered Cases')
plt.plot(FALL20_DATE_LIST[-1],FALL20_ACTIVE_LIST[-1],'ms',mfc='none',markersize=7)
## Add: line for when random testing started - Oct 26th, 2020

# Add legend, titles, labels
plt.legend(loc = 2) # add location
plt.title('Fall 2020 COVID Cases at Mount Union')
plt.xlabel('Date')
plt.ylabel('Number of Cases')

## Add: Adjust x axis markers to show only last two digits of the year
## Add: Adjust dates that show beginning of each month or whatever, something consistent, just to make it nicer
plt.xticks(FALL20_DATE_RANGE,rotation = 45)
plt.text(FALL20_DATE_LIST[-1],FALL20_ACTIVE_LIST[-1]+6,FALL20_ACTIVE_LIST[-1])
plt.subplots_adjust(left=None, bottom=0.225, right=None, top=0.92, wspace=None, hspace=None)

'''Graph 3: Spring 2021 Semester Only'''
SPRING2021_GRAPH = plt.figure(dpi=100)

SPRING21_DATE_LIST,SPRING21_ACTIVE_LIST,SPRING21_RECOVERED_LIST,SPRING21_TOTAL_LIST,SPRING21_NEW_LIST,SPRING21_NEW_RECOVERED_LIST = ReadDataFile('SPRING21_DATA.txt')

SPRING21_DATE_RANGE = pd.date_range(start=SPRING21_DATE_LIST[0], end=SPRING21_DATE_LIST[-1], periods=6) if len(SPRING21_DATE_LIST) > 6 else SPRING21_DATE_LIST

# # Use this once a substantial amount of data is collected; cleans up x-axis labels
# SPRING21_DATE = SPRING21_START_DATE
# SPRING21_DATE_RANGE = [SPRING21_DATE]
# while SPRING21_DATE < SPRING21_DATE_LIST[-1]:
#     SPRING21_DATE += timedelta(days=7)
#     SPRING21_DATE_RANGE.append(SPRING21_DATE) 

# Plot the graph
plt.plot(SPRING21_DATE_LIST,SPRING21_ACTIVE_LIST,'r',label='Active Cases')
plt.plot(SPRING21_DATE_LIST,SPRING21_RECOVERED_LIST,'g',label='Recovered Cases')
plt.plot(SPRING21_DATE_LIST,SPRING21_TOTAL_LIST,'b',label='Total Cases')
plt.plot(SPRING21_DATE_LIST,SPRING21_NEW_LIST,'m',label='New Active Cases')
plt.plot(SPRING21_DATE_LIST,SPRING21_NEW_RECOVERED_LIST,'y',label='New Recovered Cases')
plt.plot(SPRING21_DATE_LIST[-1],SPRING21_ACTIVE_LIST[-1],'ms',mfc='none',markersize=7)

# Add legend, titles, labels
plt.legend(loc = 2) # add location
plt.title('Spring 2020 COVID Cases at Mount Union')
plt.xlabel('Date')
plt.ylabel('Number of Cases')

## Add: Adjust x axis markers to show only last two digits of the year
## Add: Adjust dates that show beginning of each month or whatever, something consistent, just to make it nicer
plt.xticks(SPRING21_DATE_RANGE,rotation = 45)
plt.text(SPRING21_DATE_LIST[-1],SPRING21_ACTIVE_LIST[-1]+6,SPRING21_ACTIVE_LIST[-1])
plt.subplots_adjust(left=None, bottom=0.225, right=None, top=0.92, wspace=None, hspace=None)

'''Graph 4: Comparison Between Semesters''' '''Need to split up by week rather than exact date'''
# # All data already calculated, just need x-axis scaling (date range) and plots
# COMPARISON_GRAPH = plt.figure(dpi=100)

# FALL20_DATE_LIST,FALL20_ACTIVE_LIST,FALL20_RECOVERED_LIST,FALL20_TOTAL_LIST,FALL20_NEW_LIST,FALL20_NEW_RECOVERED_LIST = ReadDataFile('FALL20_DATA.txt')
# SPRING21_DATE_LIST,SPRING21_ACTIVE_LIST,SPRING21_RECOVERED_LIST,SPRING21_TOTAL_LIST,SPRING21_NEW_LIST,SPRING21_NEW_RECOVERED_LIST = ReadDataFile('SPRING21_DATA.txt')

# MAX_DATE_LIST = max([FALL20_DATE_LIST,SPRING21_DATE_LIST],key = len)
# DATE_OF_WEEK = FALL20_START_DATE if len(FALL20_DATE_LIST) > len(SPRING21_DATE_LIST) else SPRING21_START_DATE

# # Convert dates to number of days into the semester to overlay semester lines
# FALL20_DAY_LIST = []
# for FALL20_DATE_TO_CONVERT in FALL20_DATE_LIST:
#     FALL20_DATE_TO_CONVERT -= FALL20_START_DATE
#     FALL20_DAY_LIST.append(FALL20_DATE_TO_CONVERT)

# print(FALL20_DAY_LIST)
# DATE_TO_CONVERT = FALL20_START_DATE
# DAY_TO_CONVERT_TO = 1
# while DATE_TO_CONVERT != FALL20_END_DATE:
#     if DATE_TO_CONVERT in FALL20_DAY_LIST:
#         INDEX_TO_CONVERT = FALL20_DAY_LIST.index(DATE_TO_CONVERT)
#         FALL20_DAY_LIST[INDEX_TO_CONVERT] = DAY_TO_CONVERT_TO
#     DATE_TO_CONVERT += timedelta(days=1)
#     DAY_TO_CONVERT_TO += 1
# print(FALL20_DAY_LIST)


# # Create a new date range to graph to encompass all semesters, label x-axis by week number rather than actual date so they can be overlayed
# WEEK_RANGE = [DATE_OF_WEEK]
# WEEKS = ['1']
# while DATE_OF_WEEK < MAX_DATE_LIST[-1]:
#     DATE_OF_WEEK += timedelta(days=7)
#     WEEK_RANGE.append(DATE_OF_WEEK)
#     WEEKS.append(int(WEEKS[-1])+1)    

# # Plot the graph
# plt.plot(FALL20_DAY_LIST,FALL20_ACTIVE_LIST,'r',label='Fall20 - Active Cases')
# plt.plot(FALL20_DAY_LIST,FALL20_RECOVERED_LIST,'g',label='Fall20 - Recovered Cases')
# plt.plot(FALL20_DAY_LIST,FALL20_TOTAL_LIST,'b',label='Fall20 - Total Cases')
# plt.plot(FALL20_DAY_LIST,FALL20_ACTIVE_LIST,'r--',label='Spring21 - Active Cases')
# plt.plot(FALL20_DAY_LIST,FALL20_RECOVERED_LIST,'g--',label='Spring21 - Recovered Cases')
# plt.plot(FALL20_DAY_LIST,FALL20_TOTAL_LIST,'b--',label='Spring 21 - Total Cases')

# # Add legend, titles, labels
# plt.legend()
# # plt.legend(handles = [mpatches.Patch(color='red',label = 'Active Cases'),mpatches.Patch(color='green',label = 'Recovered Cases'),mpatches.Patch(color='blue',label = 'Total Cases')]) # add location
# plt.title('Fall 2020 COVID Cases at Mount Union')
# plt.xlabel('Week in Semester')
# plt.ylabel('Number of Cases')

# ## Add: Adjust x axis markers to show only last two digits of the year
# ## Add: Adjust dates that show beginning of each month or whatever, something consistent, just to make it nicer
# plt.xticks(WEEK_RANGE,WEEKS)
# # plt.text(MAX_DATE_LIST[-1],MAX_DATE_LIST[-1]+6,MAX_DATE_LIST[-1])
# # plt.subplots_adjust(left=None, bottom=0.225, right=None, top=0.92, wspace=None, hspace=None)


plt.show()

# This just prints the most recent data from the website into the console, formatted nicely
activeSuffix = 's' if caseList[1] != 1 else ''
recoveredSuffix = 's' if caseList[2] != 1 else ''
print(f'On {caseList[0]}, there were {caseList[1]} active case{activeSuffix}, {caseList[2]} recovered case{recoveredSuffix}, and {caseList[3]} total cases.') #date,active,recovered,total


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

Incorporate Object Oriented Programming
Make a class, with methods to calculate certain lists (for example, sometimes the 'new lists' aren't wanted'), maybe even to graph the data

'''








