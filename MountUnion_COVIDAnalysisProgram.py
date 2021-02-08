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
# import matplotlib.patches as mpatches
import tkinter as tk
from tkinter import *
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk) 
import numpy as np
import myfunction
from matplotlib.figure import Figure
 
dateList,activeList,recoveredList,totalList,ACCUMULATED_TOTAL,ACCUMULATED_RECOVERED,ALL_TIME_DATE_RANGE = myfunction.CreateMasterLists()

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
        self.calculate_data()
        self.calculate_new_data()
        self.determine_range()
    
        ax.clear() # clear axes to redraw new plot lines
        
        ax.plot(self.DATE_LIST,self.ACTIVE_LIST,'r',label='Active Cases')
        ax.plot(self.DATE_LIST,self.RECOVERED_LIST,'g',label='Recovered Cases')
        ax.plot(self.DATE_LIST,self.TOTAL_LIST,'b',label='Total Cases')
        ax.plot(self.DATE_LIST[-1],self.ACTIVE_LIST[-1],'ms',mfc='none',markersize=7)
        try: # Only plots this if the calculate_new_data function was run
            ax.plot(self.DATE_LIST,self.NEW_LIST,'m',label='New Active Cases')
            ax.plot(self.DATE_LIST,self.NEW_RECOVERED_LIST,'y',label='New Recovered Cases')
        except:
            pass
    
        ax.legend(loc = 2) # add location
        ax.set_title(f'{self.name} COVID Cases at Mount Union')
        ax.set_xlabel('Date')
        ax.set_ylabel('Number of Cases')
        # # Add: Adjust x axis markers to show only last two digits of the year
        # # Add: Adjust dates that show beginning of each month or whatever, something consistent, just to make it nicer
        # ax.set_xticklabels(self.DATE_RANGE,rotation=45)
        ax.text(self.DATE_LIST[-1],self.ACTIVE_LIST[-1]+(max(self.ACTIVE_LIST)/5),self.ACTIVE_LIST[-1])
        # ax.subplots_adjust(left=None, bottom=0.225, right=None, top=0.92, wspace=None, hspace=None)
            
        plot_canvas.draw() # redraw canvas to put updates in affect
        
    def comparison_graph(self,other,new_data):
        self.calculate_data()
        # FALL20.calculate_new_data()
        self.new_data = new_data
        other.calculate_data()
        if self.new_data == True: # similar to try-except, prevents errors if new_data not in correct format
            other.calculate_new_data()
            
        ax.clear() # clear axes to redraw new plot lines
        
        ax.plot(self.DAY_LIST,self.ACTIVE_LIST,'r--',label='Fall 2020 Active Cases')
        ax.plot(self.DAY_LIST,self.RECOVERED_LIST,'g--',label='Fall 2020 Recovered Cases')
        ax.plot(self.DAY_LIST,self.TOTAL_LIST,'b--',label='Fall 2020 Total Cases')
        try:
            ax.plot(self.DAY_LIST,self.NEW_LIST,'m--',label='Fall 2020 New Active Cases')
            ax.plot(self.DAY_LIST,self.NEW_RECOVERED_LIST,'y--',label='Fall 2020 New Recovered Cases')
        except:
            pass
        ax.plot(other.DAY_LIST,other.ACTIVE_LIST,'r',label='Spring 2021 Active Cases')
        ax.plot(other.DAY_LIST,other.RECOVERED_LIST,'g',label='Spring 2021 Recovered Cases')
        ax.plot(other.DAY_LIST,other.TOTAL_LIST,'b',label='Spring 2021 Total Cases')
        try:
            ax.plot(other.DAY_LIST,other.NEW_LIST,'m',label='Spring 2021 New Active Cases')
            ax.plot(other.DAY_LIST,other.NEW_RECOVERED_LIST,'y',label='Spring 2021 New Recovered Cases')
        except:
            pass
        
        self.DAY_RANGE = range(1,(max(self.DAY_LIST[-1],other.DAY_LIST[-1])//7+1)*7,7)
        # Add legend, titles, labels
        ax.legend()
        # plt.legend(handles = [mpatches.Patch(color='red',label = 'Active Cases'),mpatches.Patch(color='green',label = 'Recovered Cases'),mpatches.Patch(color='blue',label = 'Total Cases')]) # add location
        ax.set_title('Fall 2020 vs Spring 2021 COVID Cases at Mount Union')
        ax.set_xlabel('Week in Semester')
        ax.set_ylabel('Number of Cases')
        # ax.set_xticklabels(self.DAY_RANGE,range(1,len(self.DAY_RANGE)+1))
        # plt.text(MAX_DATE_LIST[-1],MAX_DATE_LIST[-1]+6,MAX_DATE_LIST[-1])
        # plt.subplots_adjust(left=None, bottom=0.225, right=None, top=0.92, wspace=None, hspace=None)
        
        plot_canvas.draw() # redraw canvas to put updates in affect
        
'''Create Graph 1: Accumulative Total of All Time'''
def plot_all_data():
    ax.clear() # clear axes to redraw new plot lines
    
    # fig = plt.figure(dpi=100)
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
    ax.plot(dateList,activeList,'r',label='Active Cases')
    ax.plot(dateList,ACCUMULATIVE_RECOVERED_LIST,'g',label='Recovered Cases')
    ax.plot(dateList,ACCUMULATIVE_TOTAL_LIST,'b',label='Total Cases')
    ax.plot(dateList,newList,'m',label='New Active Cases')
    ax.plot(dateList,newRecoveredList,'y',label='New Recovered Cases')
    ax.plot(dateList[-1],activeList[-1],'ms',mfc='none',markersize=7)
    ## Add: line for when random testing started - Oct 26th, 2020
    # Add legend, titles, labels
    ax.legend(loc = 2) # add location
    ax.set_title('Accumulative COVID Cases at Mount Union')
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Cases')
    ## Add: Adjust x axis markers to show only last two digits of the year
    ## Add: Adjust dates that show beginning of each month or whatever, something consistent, just to make it nicer
    # ax.set_xticks(ALL_TIME_DATE_RANGE,rotation = 45)
    # ax.text(dateList[-1],activeList[-1]+(max(activeList)/5),activeList[-1])
    # ax.subplots_adjust(left=None, bottom=0.225, right=None, top=0.92, wspace=None, hspace=None)

HEIGHT = 750
WIDTH = 900
root = tk.Tk()
root.title('Analysis of COVID Data at the University of Mount Union')
canvas = tk.Canvas(root,height=HEIGHT,width=WIDTH)
canvas.pack()

title_label = tk.Label(root,text='Analysis of COVID Data at the University of Mount Union',font=('Bookman Old Style',15))
title_label.place(relx=0.1,rely=0.01,relheight=0.1,relwidth=0.8)

frame = tk.Frame(root,bg='#d88cf2',bd=5)
frame.place(relx=0.025,rely=0.1,relheight=0.125,relwidth=0.95)


# This is currently creating new labels on top of each other; not very efficient. Make it replace the label instead
# def create_label(label_text=''):
#     display_label = tk.Label(,text=label_text) #,command = lambda: write_label
#     
# create_label()

# create default figure, nothing plotted yet
fig = Figure()
ax = fig.add_subplot(111)

plot_canvas = FigureCanvasTkAgg(fig,master=root)
plot_canvas.get_tk_widget().place(relx=0.15,rely=0.35,relwidth=0.7,relheight=0.6)
# ax.subplots_adjust(left=None, bottom=0.225, right=None, top=0.92, wspace=None, hspace=None)

label_text=StringVar() # Defaults to empty string label
label = Label(root,relief='groove',bd=5,textvariable = label_text) 
label.place(relx=0.05,rely=0.25,relheight=0.06,relwidth=0.9)

def get_data_button_command():
    label_text.set(myfunction.check_for_data())

def graph1_button_command():
    plot_all_data()
    plot_canvas.draw()
    showtext = 'All Data Plotted'
    label_text.set(showtext) # update label text
    
def graph2_button_command():
    FALL20 = SemesterData('FALL20_DATA.txt','Fall 2020','2020-08-24','2020-11-24')
    FALL20.graph_data()
    showtext = 'Fall 2020 Data Plotted'
    label_text.set(showtext) # update label text
    
def graph3_button_command():
    SPRING21 = SemesterData('SPRING21_DATA.txt','Spring 2021','2021-01-11','2021-05-05')
    SPRING21.graph_data()
    showtext = 'Spring 2021 Data Plotted'
    label_text.set(showtext) # update label text

def graph4_button_command():
    FALL20 = SemesterData('FALL20_DATA.txt','Fall 2020','2020-08-24','2020-11-24')
    FALL20.comparison_graph(SemesterData('SPRING21_DATA.txt','Spring 2021','2021-01-11','2021-05-05'),False)
    showtext = 'Comparing Fall 2020 and Spring 2021 Data'
    label_text.set(showtext) # update label text
    
get_data_button = tk.Button(frame,text='Check for \nNew Data',bd=5,font=('Bookman Old Style',10),command=get_data_button_command)
get_data_button.place(relx=0.005,rely=0.05,relheight=0.9,relwidth=0.19)

graph1_button = tk.Button(frame,text='Plot All Data',bd=5,font=('Bookman Old Style',10),command=graph1_button_command)
graph1_button.place(relx=0.201,rely=0.05,relheight=0.9,relwidth=0.19)

graph2_button = tk.Button(frame,text='Plot Fall 2020 \nData',bd=5,font=('Bookman Old Style',10),command=graph2_button_command)
graph2_button.place(relx=0.4015,rely=0.05,relheight=0.9,relwidth=0.19)

graph3_button = tk.Button(frame,text='Plot Spring 2021 \nData',bd=5,font=('Bookman Old Style',10),command=graph3_button_command)
graph3_button.place(relx=0.602,rely=0.05,relheight=0.9,relwidth=0.19)

graph4_button = tk.Button(frame,text='Plot Semester \nComparison Data',bd=5,font=('Bookman Old Style',10),command=graph4_button_command)
graph4_button.place(relx=0.8025,rely=0.05,relheight=0.9,relwidth=0.19)

root.mainloop()


'''
Improvements

Doesn't update plots once "find new data" clicked

Might have to close/reopen covidcases.txt again to update with the new data
'''