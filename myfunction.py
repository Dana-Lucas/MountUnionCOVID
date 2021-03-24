# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 13:57:51 2021

@author: dana
"""

import bs4, requests
import pandas as pd
import re
from datetime import timedelta
from pandas._libs.tslibs.timestamps import Timestamp

def CreateMasterLists():
    '''
    This section creates and displays plots of the data
    '''
    # Create lists to graph
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
    ALL_TIME_DATE_RANGE = [str(Timestamp(ALL_TIME_DATE).to_pydatetime()).split()[0]]
    while ALL_TIME_DATE < dateList[-1]:
        ALL_TIME_DATE += timedelta(weeks=5)
        ts = Timestamp(ALL_TIME_DATE).to_pydatetime() # convert from 'pandas._libs.tslibs.timestamps.Timestamp' to 'datetime'
        ts = str(ALL_TIME_DATE).split()[0]
        ALL_TIME_DATE_RANGE.append(ts)
        
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
    
    FALL20_START_DATE = pd.to_datetime('2020-08-24',format='%Y/%m/%d')
    FALL20_END_DATE = pd.to_datetime('2020-11-24',format='%Y/%m/%d')
    SPRING21_START_DATE = pd.to_datetime('2021-01-11',format='%Y/%m/%d')
    SPRING21_END_DATE = pd.to_datetime('2021-05-05',format='%Y/%m/%d')

    # This file is already written, Fall 20 semester over, just needs to be referenced from now on
    DATES_IN_FALL20 = []
    for DATE in dateList:
        if FALL20_START_DATE <= DATE <= FALL20_END_DATE:
            DATES_IN_FALL20.append(DATE)
    FALL20_DATA_FILE = open('FALL20_DATA.txt','wt')
    for f20num, DATE in enumerate(DATES_IN_FALL20):
        FALL20_DATA_FILE.write(f'{DATE}\t{activeList[f20num]}\t{recoveredList[f20num]}\t{totalList[f20num]}\t{DATE-FALL20_START_DATE}\n')
    FALL20_DATA_FILE.close()
    
    DATES_IN_SPRING21 = []
    for DATE in dateList:
        if SPRING21_START_DATE <= DATE <= SPRING21_END_DATE:
            DATES_IN_SPRING21.append(DATE)
    SPRING21_DATA_FILE = open('SPRING21_DATA.txt','wt')
    for s21num, DATE in enumerate(DATES_IN_SPRING21):
        SPRING21_DATA_FILE.write(f'{DATE}\t{activeList[s21num+63]}\t{recoveredList[s21num+63]}\t{totalList[s21num+63]}\t{DATE-SPRING21_START_DATE}\n')
    SPRING21_DATA_FILE.close()

    return dateList,activeList,recoveredList,totalList,ACCUMULATED_TOTAL,ACCUMULATED_RECOVERED,ALL_TIME_DATE_RANGE


'''Check For New Data'''
def check_for_data():
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
    
    # This just prints the most recent data from the website into the console, formatted nicely
    activeSuffix = 's' if caseList[1] != 1 else ''
    recoveredSuffix = 's' if caseList[2] != 1 else ''
    werewas = 'was' if caseList[2] != 1 else 'were'
    
    # print(f'On {caseList[0]}, there were {caseList[1]} active case{activeSuffix}, {caseList[2]} recovered case{recoveredSuffix}, and {caseList[3]} total cases.') #date,active,recovered,total
    label_text = f'On {caseList[0]}, there {werewas} {caseList[1]} active case{activeSuffix}, {caseList[2]} recovered case{recoveredSuffix}, and {caseList[3]} total cases.'
    
    dateList,activeList,recoveredList,totalList,ACCUMULATED_TOTAL,ACCUMULATED_RECOVERED,ALL_TIME_DATE_RANGE = CreateMasterLists()
    
    return label_text,dateList,activeList,recoveredList,totalList,ACCUMULATED_TOTAL,ACCUMULATED_RECOVERED,ALL_TIME_DATE_RANGE


