#!/usr/bin/env python
# coding: utf-8

# Code open and decode the orbite temperature files and produce orbit averages etc

# Inputs:
# Orbit temperature files in the 'temperatures' folder
# Orbit info to be loaded from previously decoded .npy files

# Outputs:
# Will write output to .npy files
# format is a numpy array containing a list of lists

# In[1]:

from pandas import read_csv
# from os import system
from os.path import exists
from numpy import array,load,mean,std,save#,where
# from numpy import polyfit,poly1d,sqrt
from datetime import timedelta
from matplotlib.pyplot import subplots,plot,xlabel,ylabel,grid
from matplotlib import pyplot

pyplot.rcParams['figure.figsize'] = [10, 4] # default 6,4
pyplot.rcParams['figure.dpi'] = 72 # default 72

#%% Global Variables
# orbit information from the orbit.info.txt file
global orbit_numbers, orbit_start_times, orbit_end_times
#%Load Orbit Info
orbit_numbers = list(load("./orbit_numbers.npy",allow_pickle=True))
orbit_start_times = list(load("./orbit_start_times.npy",allow_pickle=True))
orbit_end_times = list(load("./orbit_end_times.npy",allow_pickle=True))

# Global variables for temperature data
# these are lists of values for which temperature data exists, ie. subset of the above
# global orbits, start_times
global averages, sigmas, maxima, minima, counts
global nonzeroaverages

#%% function definitions for temperature statistics

# generate a filename for a csv file to be opened 
def temperature_filename(spacecraft,orbit_number):
    filename = "C" + spacecraft + "_orbit_" + str(orbit_number) + ".csv"
    return filename

# create averages and stdev
# improved version which doesn't decode times (not needed for orbit stats)

def orbit_averages(spacecraft):
    global averages, maxima, minima, counts, sigmas
    global nonzeroaverages
    
    nonzeroaverages = []    
    averages = []
    sigmas = []
    maxima = []
    minima = []
    counts = []

    for orbit_number in orbit_numbers:
        filename = temperature_filename(spacecraft,orbit_number)
        pathstring = "./temperatures/"+filename
        if exists(pathstring):        
            data = read_csv(pathstring)
            temperatures = data['1F_074'][:]
        else:
            print("WARNING: Filename %s does not exist" % filename)
       
        # check for file integrity
        validtemperatures = [x for x in temperatures if x<20 and x>-80]
        nonzerotemperatures = [x for x in validtemperatures if x != 0]
        if len(temperatures) == 0:
            print("WARNING: Orbit %i file is empty" % orbit_number)
        elif len(validtemperatures) ==0:
            print("WARNING: Orbit %i contains no valid temperature values" % orbit_number)
        elif len(nonzerotemperatures) ==0:
            print("WARNING: Orbit %i contains only zero values" % orbit_number)
        
        if len(validtemperatures) ==0:
            counts.append(0)
            averages.append(float('nan'))
            sigmas.append(float('nan'))
            maxima.append(float('nan'))
            minima.append(float('nan'))            
        else:
            # attempt to minimize effect of spurious zero values
            if len(nonzerotemperatures) < len(validtemperatures) and mean(nonzerotemperatures) < -10:
                validtemperatures = nonzerotemperatures
                print("WARNING: Orbit %i discarding zero values" % orbit_number)            
            counts.append(len(validtemperatures))
            averages.append(mean(validtemperatures))
            sigmas.append(std(validtemperatures))
            maxima.append(max(validtemperatures))
            minima.append(min(validtemperatures))
        
        if len(nonzerotemperatures) == 0:
            nonzeroaverages.append(float('nan'))
        else: 
            nonzeroaverages.append(mean(nonzerotemperatures))
        
    return 

# Plot orbit averages, with errorbars from the standard deviations of the values\
# Typically, a large standard deviation will indicate either a problem in the data, or more often an eclipse\
# This is an indication that further investigation required for the orbit
def plot_averages():
    f,(a0,a1) = subplots(2,1,gridspec_kw={'height_ratios': [3, 1]},figsize=(12,6))
    a0.plot(orbit_numbers,averages,'r.',label='mean')
    a0.errorbar(orbit_numbers,averages,yerr=sigmas,fmt='r',ecolor='0.9')
    a0.plot(orbit_numbers,maxima,'g.',label='max')
    a0.plot(orbit_numbers,minima,'b.',label='min')
    a0.grid()
    a0.set_ylabel("mean temperature (deg.C)")
    a0.legend()
    a1.plot(orbit_numbers,counts,'.',label='count')
    a1.grid()
    a1.legend()
    a1.set_xlabel("orbit number")
    a1.set_ylabel("counts")
    # f.tight_layout()        
    return

# In[19]:# process averages and stats
# this takes a long time
orbit_averages(spacecraft='1')

#%% Save the stats
# convert a list of lists to a numpy array
temperature_statistics = array([counts,averages,sigmas,maxima,minima])
save("./temperature_statistics", temperature_statistics)

#%% Load the stats
# Start here if orbit averages have already been processed
temperature_statistics = load('temperature_statistics.npy',allow_pickle=True)
counts = list(temperature_statistics[0][:])
averages = list(temperature_statistics[1][:])
sigmas = list(temperature_statistics[2][:])
maxima = list(temperature_statistics[3][:])
minima = list(temperature_statistics[4][:])
del temperature_statistics


# In[139]:
# make a plot of the temperature stats
plot_averages()
# xlim([2290,2460])
# it may be necessary to inspect using orbit_plot() then edit the .csv files to remove bad values and non-physical zeros
# orbits with zero averages: if no useable data returned from RDM, delete the .csv file?
# or an orbits to exclude list?


#%%

# return the index for an orbit number
def get_index(orbit_number):
    global orbit_numbers
    return orbit_numbers.index(orbit_number)

def remove_low_counts():
    global orbit_numbers,averages,counts,maxima,minima,sigmas
    expected_count = 54*60*60/5.152222 # expected number of values for 54h orbit
    threshold = 0.75 # minimum fraction of this
    for orbit_number in orbit_numbers:
        if counts[get_index(orbit_number)] !=0 and  counts[get_index(orbit_number)] < threshold * expected_count:
            print("Eliminating orbit %i" % orbit_number)
            averages[get_index(orbit_number)] = float('nan')
            maxima[get_index(orbit_number)] = float('nan')
            minima[get_index(orbit_number)] = float('nan')
            sigmas[get_index(orbit_number)] = float('nan')
    return

remove_low_counts()


#%% Orbit duration
def plot_duration():
    global orbit_numbers,orbit_end_times,orbit_start_times
    orbit_durations = []
    for orbit_number in orbit_numbers:
        orbit_duration = orbit_end_times[get_index(orbit_number)] - orbit_start_times[get_index(orbit_number)]
        orbit_durations.append(orbit_duration/timedelta(hours=1))
    plot(orbit_numbers,orbit_durations)
    grid()
    xlabel('orbit number')
    ylabel('duration [hours]')
    return

plot_duration()

#%% Cleanup
del temperature_statistics, nonzeroaverages, averages, counts, maxima, minima, sigmas
del orbit_numbers, orbit_end_times, orbit_start_times
