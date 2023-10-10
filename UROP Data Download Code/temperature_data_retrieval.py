#!/usr/bin/env python
# coding: utf-8

# Code download temperature data on an orbit-by-orbit basis
# based on orbit.info.txt file
# Will write a set of orbit temperature files to the subfolder 'temperatures'
# Existing files will not be overwritten, so to force a reload, delete an existing file
# Note that the RDM processing returns many zero values (RTU off?) which are not always easy
# to distinguish from true zero values - some of the .CSV files have been edited to remove
# obvious bad values. 

# Inputs:
# Loads orbit info from data previously saved by running 'orbit_info_processing.py'
# Outputs:
# A set of orbit CSV files in temperatures subfolder

# In[1]:

from pandas import read_csv,to_datetime
from os import system
from os.path import exists
from numpy import load,mean
# from numpy import polyfit,poly1d,sqrt
# from datetime import datetime,timedelta
from matplotlib.pyplot import subplots,plot,xlabel,ylabel,title,grid
from matplotlib import pyplot
pyplot.rcParams['figure.figsize'] = [10, 4] # default 6,4
pyplot.rcParams['figure.dpi'] = 72 # default 72

#%% Global Variables
# orbit information from the orbit.info.txt file
global orbit_numbers, orbit_start_times, orbit_end_times
# for the case that there is a gap
# default_orbit_duration = timedelta(hours=57)

#%% Load Orbit Info
orbit_numbers = list(load("./orbit_numbers.npy",allow_pickle=True))
orbit_start_times = list(load("./orbit_start_times.npy",allow_pickle=True))
orbit_end_times = list(load("./orbit_end_times.npy",allow_pickle=True))

# In[3]: Function definitions for retrieving the spacecraft housekeeping

# generate a parameter string file params.txt according to the CAA CLI specification
# assumes that the file params.txt exists in the directory
# but will erase any current contents
# start and end times are as-read from the orbit.info.txt file
# spacecraft is a character e.g. '1'

def write_params_file(start_time,end_time,spacecraft):
    pstring = '{"date_from": "'
    pstring += start_time.replace(tzinfo=None).isoformat(timespec='minutes')+"Z"
    pstring += '","date_to": "' 
    pstring += end_time.replace(tzinfo=None).isoformat(timespec='minutes')+"Z"
    pstring += '","sc": '
    pstring += spacecraft
    pstring += ',"parameters": ["F_074"]}'
    # write the string into the file params.txt
    file = open("params.txt","w")
    file.truncate() # erase content
    file.write(pstring)
    file.close()
    return

# generate a filename for a csv destination file 
def temperature_filename(spacecraft,orbit_number):
    filename = "C" + spacecraft + "_orbit_" + str(orbit_number) + ".csv"
    return filename

# will retrieve data according to the contents of an (assumed to exist) params.txt file
# save according to string 'filename', which is to be supplied with a .csv extension
# in the folder 'temperatures'
# will abort if file exists
def get_rdm(filename):
    relativepath = "./temperatures/" + filename
    # check for existing csv file
    if exists(relativepath):
        print("Aborting: %s exists" % relativepath)
    else:
        relativepath += ".gz"
        parameter_string = 'curl -X GET https://caa.esac.esa.int/rdm-hk/api/data/ -H "Content-Type: application/json" -d @params.txt -o ' + relativepath
        system(parameter_string)
        parameter_string = 'gunzip ' + relativepath
        system(parameter_string) 
    return

# download all temperature data files according to the orbit.info file
def get_temperature_files(spacecraft):
    for i in range(0,len(orbit_numbers)):
        orbit_number = orbit_numbers[i]
        start_time = orbit_start_times[i]
        end_time = orbit_end_times[i]
        write_params_file(start_time,end_time,spacecraft)
        filename = temperature_filename(spacecraft,orbit_number)
        print("Getting orbit "+str(orbit_number)+" for spacecraft "+spacecraft+" from "+start_time.isoformat()+" to "+end_time.isoformat())
        get_rdm(filename)      
    return
    
# open a temperature file for a given spacecraft aorbit number
def open_temperature_file(spacecraft,orbit_number):
    filename = temperature_filename(spacecraft,orbit_number)
    pathstring = "./temperatures/"+filename
    if exists(pathstring):        
        data = read_csv(pathstring)
        times = to_datetime(data['time'][:],format="ISO8601")
        temperatures = data['1F_074'][:]
    else:
        print("WARNING: Filename %s does not exist" % filename)
    return times,temperatures

# function to open, read and plot the contents of an individual file
def orbit_plot(spacecraft,orbit_number):
    # open and read an individual temperature file
    times,temperatures = open_temperature_file(spacecraft,orbit_number)
    # plot the contents
    subplots(figsize=(12,4))
    plot(times,temperatures,'o')
    grid()
    xlabel('date time')
    ylabel('temperature (deg.C)')
    title("Filename "+temperature_filename(spacecraft, orbit_number)+" Start "+str(orbit_start_times[orbit_numbers.index(orbit_number)]))

# open a temperature file and produce averaged and resampled values
def resampled_plot(spacecraft,orbit_number,halfwidth):
    times,temperatures = open_temperature_file(spacecraft,orbit_number)
    resampled_times = []
    resampled_temperatures = []
    for i in range(halfwidth,len(temperatures)-halfwidth,2*halfwidth):
        resampled_times.append(times[i])
        resampled_temperatures.append(mean(temperatures[i-halfwidth:i+halfwidth]))
    subplots(figsize=(12,4))
    plot(resampled_times,resampled_temperatures,'o')
    grid()
    xlabel('date time')
    ylabel('temperature (deg.C)')
    title("Resampled - halfwidth " +str(halfwidth)+ " - Filename "+temperature_filename(spacecraft, orbit_number)+" Start "+str(orbit_start_times[orbit_numbers.index(orbit_number)]))


#%% Download temperature files
# get temperature files according to orbits listed in orbit.info.txt
# existing files will not be overwritten
# so in case an update is required, existing file to be deleted
get_temperature_files(spacecraft='1')

#%% Inspection Plot
# Having downloaded datafiles, use the cell below to open and inspect a specified file\
# Note that, typically, 'no data' will be epresented by zero values
orbit_plot(spacecraft='1',orbit_number=2334)

#%% Sub-orbital averaging
resampled_plot(spacecraft='1',orbit_number=2370,halfwidth=128)



