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
import tkinter as tk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk) 

def CheckForNewData():
    
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
    
    return caseList

caseList = CheckForNewData()

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
        SPRING21_DATA_FILE.write(f'{DATE}\t{activeList[s21num+61]}\t{recoveredList[s21num+61]}\t{totalList[s21num+61]}\t{DATE-SPRING21_START_DATE}\n')
    SPRING21_DATA_FILE.close()

    return dateList,activeList,recoveredList,totalList,ACCUMULATED_TOTAL,ACCUMULATED_RECOVERED,ALL_TIME_DATE_RANGE

dateList,activeList,recoveredList,totalList,ACCUMULATED_TOTAL,ACCUMULATED_RECOVERED,ALL_TIME_DATE_RANGE = CreateMasterLists()

class SemesterData: 
    def __init__(self,file,name,start,end):
        self.name = name
        self.file = file   
        self.start = start
        self.end = end
        self.START_DATE = pd.to_datetime(self.start,format='%Y/%m/%d')
        self.END_DATE = pd.to_datetime(self.end,format='%Y/%m/%d')
    def calculate_data(self):
        self.DATE_LIST = []
        self.ACTIVE_LIST = []
        self.RECOVERED_LIST = []
        self.TOTAL_LIST = []
        self.DAY_LIST = []
        self.DATA_FILE = open(self.file,'r')
        for num, LINE in enumerate(self.DATA_FILE):
            SPLIT_LINE = LINE.split('\t')
            self.DATE_LIST.append(dt.strptime(SPLIT_LINE[0].split(' ')[0],"%Y-%m-%d"))
            self.ACTIVE_LIST.append(int(SPLIT_LINE[1]))
            self.RECOVERED_LIST.append(int(SPLIT_LINE[2]))
            self.TOTAL_LIST.append(int(SPLIT_LINE[3]))
            self.DAY_LIST.append(int(SPLIT_LINE[4].split(' ')[0])+1)
        self.DATE_LIST = pd.to_datetime(self.DATE_LIST,format="%Y-%m-%d")
        self.DATA_FILE.close()
        return self.DATE_LIST,self.ACTIVE_LIST,self.RECOVERED_LIST,self.TOTAL_LIST,self.DAY_LIST
    def calculate_new_data(self):
        self.NEW_LIST = []
        self.NEW_RECOVERED_LIST = []
        self.DATA_FILE = open(self.file,'r')
        for num, LINE in enumerate(self.DATA_FILE):
            if len(self.DATE_LIST) > 1 and num > 1:
                self.NEW_LIST.append(self.TOTAL_LIST[num]-self.TOTAL_LIST[num-1])
                self.NEW_RECOVERED_LIST.append(self.RECOVERED_LIST[num]-self.RECOVERED_LIST[num-1])
            else: # To ensure the lists have the same length for plotting
                self.NEW_LIST.append(0)  
                self.NEW_RECOVERED_LIST.append(0)
        self.DATA_FILE.close()
        return self.NEW_LIST,self.NEW_RECOVERED_LIST
    def determine_range(self):
        if len(self.DATE_LIST) > 6:
            DATE_TO_DISPLAY = self.START_DATE
            self.DATE_RANGE = [DATE_TO_DISPLAY]
            while DATE_TO_DISPLAY < self.DATE_LIST[-1]:
                DATE_TO_DISPLAY += timedelta(days=7)
                self.DATE_RANGE.append(DATE_TO_DISPLAY)  
        else:
            # self.DATE_RANGE = self.DATE_LIST
            self.DATE_RANGE = pd.date_range(start=self.DATE_LIST[0], end=self.DATE_LIST[-1], periods=len(self.DATE_LIST))
        return self.DATE_RANGE
    def graph_data(self):
        plt.figure(dpi=100)
        plt.plot(self.DATE_LIST,self.ACTIVE_LIST,'r',label='Active Cases')
        plt.plot(self.DATE_LIST,self.RECOVERED_LIST,'g',label='Recovered Cases')
        plt.plot(self.DATE_LIST,self.TOTAL_LIST,'b',label='Total Cases')
        plt.plot(self.DATE_LIST[-1],self.ACTIVE_LIST[-1],'ms',mfc='none',markersize=7)
        try: # So it only plots this if the calculate_new_data function was run
            plt.plot(self.DATE_LIST,self.NEW_LIST,'m',label='New Active Cases')
            plt.plot(self.DATE_LIST,self.NEW_RECOVERED_LIST,'y',label='New Recovered Cases')
        except:
            pass
        # Add legend, titles, labels
        plt.legend(loc = 2) # add location
        plt.title(f'{self.name} COVID Cases at Mount Union')
        plt.xlabel('Date')
        plt.ylabel('Number of Cases')
        ## Add: Adjust x axis markers to show only last two digits of the year
        ## Add: Adjust dates that show beginning of each month or whatever, something consistent, just to make it nicer
        plt.xticks(self.DATE_RANGE,rotation = 45)
        plt.text(self.DATE_LIST[-1],self.ACTIVE_LIST[-1]+6,self.ACTIVE_LIST[-1])
        plt.subplots_adjust(left=None, bottom=0.225, right=None, top=0.92, wspace=None, hspace=None)
    def comparison_graph(self,other,new_data):
        # other = SemesterData(other)
        self.new_data = new_data
        other.calculate_data()
        if self.new_data == True:
            other.calculate_new_data()
        plt.plot(self.DAY_LIST,self.ACTIVE_LIST,'r',label='Fall 2020 Active Cases')
        plt.plot(self.DAY_LIST,self.RECOVERED_LIST,'g',label='Fall 2020 Recovered Cases')
        plt.plot(self.DAY_LIST,self.TOTAL_LIST,'b',label='Fall 2020 Total Cases')
        try: # So it only plots this if the calculate_new_data function was run
            plt.plot(self.DAY_LIST,self.NEW_LIST,'m',label='Fall 2020 New Active Cases')
            plt.plot(self.DAY_LIST,self.NEW_RECOVERED_LIST,'y',label='Fall 2020 New Recovered Cases')
        except:
            pass
        plt.plot(other.DAY_LIST,other.ACTIVE_LIST,'r--',label='Spring 2021 Active Cases')
        plt.plot(other.DAY_LIST,other.RECOVERED_LIST,'g--',label='Spring 2021 Recovered Cases')
        plt.plot(other.DAY_LIST,other.TOTAL_LIST,'b--',label='Spring 2021 Total Cases')
        try: # So it only plots this if the calculate_new_data function was run
            plt.plot(other.DAY_LIST,other.NEW_LIST,'m--',label='Spring 2021 New Active Cases')
            plt.plot(other.DAY_LIST,other.NEW_RECOVERED_LIST,'y--',label='Spring 2021 New Recovered Cases')
        except:
            pass
        self.DAY_RANGE = range(1,(max(self.DAY_LIST[-1],other.DAY_LIST[-1])//7+1)*7,7)
        # Add legend, titles, labels
        plt.legend()
        # plt.legend(handles = [mpatches.Patch(color='red',label = 'Active Cases'),mpatches.Patch(color='green',label = 'Recovered Cases'),mpatches.Patch(color='blue',label = 'Total Cases')]) # add location
        plt.title('Fall 2020 vs Spring 2021 COVID Cases at Mount Union')
        plt.xlabel('Week in Semester')
        plt.ylabel('Number of Cases')
        plt.xticks(self.DAY_RANGE,range(1,len(self.DAY_RANGE)+1))
        # plt.text(MAX_DATE_LIST[-1],MAX_DATE_LIST[-1]+6,MAX_DATE_LIST[-1])
        # plt.subplots_adjust(left=None, bottom=0.225, right=None, top=0.92, wspace=None, hspace=None)
        

'''Create Graph 1: Accumulative Total of All Time'''
def plot_all_data():
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

label_text = ''

'''Graph 2: Fall 2020 Semester Only'''
def plot_Fall20_data():
    FALL20 = SemesterData('FALL20_DATA.txt','Fall 2020','2020-08-24','2020-11-24')
    FALL20.calculate_data()
    FALL20.calculate_new_data()
    FALL20.determine_range()
    FALL20.graph_data()
    label_text = 'Fall 2020 Data Plotted'

'''Graph 3: Spring 2021 Semester Only'''
def plot_Spring21_data(): 
    SPRING21 = SemesterData('SPRING21_DATA.txt','Spring 2021','2021-01-11','2021-05-05')
    SPRING21.calculate_data()
    SPRING21.calculate_new_data()
    SPRING21.determine_range()
    SPRING21.graph_data()
    label_text = 'Spring 2021 Data Plotted'

'''Graph 4: Comparison Between Semesters''' '''Need to split up by week rather than exact date'''
def plot_comparison_data(): 
    COMPARISON_GRAPH = plt.figure(dpi=100)
    FALL20 = SemesterData('FALL20_DATA.txt','Fall 2020','2020-08-24','2020-11-24')
    FALL20.calculate_data()
    # FALL20.calculate_new_data()
    FALL20.comparison_graph(SemesterData('SPRING21_DATA.txt','Spring 2021','2021-01-11','2021-05-05'),False)
    label_text = 'All Data Plotted'

plt.show()

# This just prints the most recent data from the website into the console, formatted nicely
activeSuffix = 's' if caseList[1] != 1 else ''
recoveredSuffix = 's' if caseList[2] != 1 else ''
print(f'On {caseList[0]}, there were {caseList[1]} active case{activeSuffix}, {caseList[2]} recovered case{recoveredSuffix}, and {caseList[3]} total cases.') #date,active,recovered,total

HEIGHT = 600
WIDTH = 800
root = tk.Tk()
root.title('Analysis of COVID Data at the University of Mount Union')
canvas = tk.Canvas(root,height=HEIGHT,width=WIDTH)
canvas.pack()

title_label = tk.Label(root,text='Analysis of COVID Data at the University of Mount Union',font=('Bookman Old Style',15))
title_label.place(relx=0.1,rely=0.01,relheight=0.1,relwidth=0.8)

frame = tk.Frame(root,bg='#d88cf2',bd=5)
frame.place(relx=0.025,rely=0.1,relheight=0.125,relwidth=0.95)

get_data_button = tk.Button(frame,text='Check for \nNew Data',bd=5,font=('Bookman Old Style',10))
get_data_button.place(relx=0.005,rely=0.05,relheight=0.9,relwidth=0.19)

graph1_button = tk.Button(frame,text='Plot All Data',bd=5,font=('Bookman Old Style',10),command=plot_all_data)
graph1_button.place(relx=0.201,rely=0.05,relheight=0.9,relwidth=0.19)

graph2_button = tk.Button(frame,text='Plot Fall 2020 \nData',bd=5,font=('Bookman Old Style',10),command=plot_Fall20_data)
graph2_button.place(relx=0.4015,rely=0.05,relheight=0.9,relwidth=0.19)

graph3_button = tk.Button(frame,text='Plot Spring 2021 \nData',bd=5,font=('Bookman Old Style',10),command=plot_Spring21_data)
graph3_button.place(relx=0.602,rely=0.05,relheight=0.9,relwidth=0.19)

graph4_button = tk.Button(frame,text='Plot Semester \nComparison Data',bd=5,font=('Bookman Old Style',10),command=plot_comparison_data)
graph4_button.place(relx=0.8025,rely=0.05,relheight=0.9,relwidth=0.19)

display_label = tk.Label(root,relief='groove',bd=5,text="I'm going to put things like \'Fall 2020 data plotted\' or \'Latest data is: ____\' here") #,command = lambda: write_label
display_label.place(relx=0.05,rely=0.25,relheight=0.06,relwidth=0.9)

# figure_window = FigureCanvasTkAgg()   
# figure_window.draw() 
# figure_window.get_tk_widget().pack() 

root.mainloop()




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

check for new data - put in try except 'unable to locate any data' so when the site goes down, code still runs
'''








