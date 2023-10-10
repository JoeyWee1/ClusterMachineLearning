#!/usr/bin/env python
# coding: utf-8

# Code download, decode and save sensor temperature data
# Will write output to .npy files
from numpy import array,load,isfinite;
from numpy import polyfit,poly1d,sqrt;
from matplotlib.pyplot import subplot,figure,plot,xlabel,ylabel,title,legend,grid,axvline
from matplotlib import pyplot
pyplot.rcParams['figure.figsize'] = [10, 4] # default 6,4
pyplot.rcParams['figure.dpi'] = 72 # default 72

#%% Global Variables
# orbit information from the orbit.info.txt file Load Orbit Info
global orbit_numbers, orbit_start_times, orbit_end_times
orbit_numbers = list(load("./orbit_numbers.npy",allow_pickle=True))
orbit_start_times = list(load("./orbit_start_times.npy",allow_pickle=True))
orbit_end_times = list(load("./orbit_end_times.npy",allow_pickle=True))


#%% Load the stats
temperature_statistics = load('temperature_statistics.npy',allow_pickle=True)
averages = list(temperature_statistics[1][:])
del temperature_statistics

#%% Get Calibration Parameters Range 2 2015/16 season
# load data from use of the extract_cal.py

global cal_times,cal_values,selected_orbits,selected_params
global spacecraft,ranges,params,axes

spacecraft = ['1','2','3','4']
ranges = ['2','3','4','5','6','7']
params = ['offset','gain','theta','phi']
axes = ['x','y','z']

cal_times = load('times.npy',allow_pickle=True)
cal_values = load('calvalues.npy',allow_pickle=True)

#%% Get Calibration Parameters - function definitions
#  get the start time for a given orbit number
def orbit_number_to_time(orbit_number):
    try:
        x = orbit_start_times[orbit_numbers.index(orbit_number)] 
    except ValueError:
        x = -1
    return x

# a function to ge a parameter value for a given orbit number
def get_param(orbit_number,sc,rng,param,axis):
    i = 72*sc+12*rng+3*param+axis
    thetimes = list(cal_times[i])
    thevalues = list(cal_values[i])
    thetime = orbit_number_to_time(orbit_number)
    if thetime == -1:
        print("ERROR: no time value for orbit number %i" % orbit_number)
        return -1
    else:
        theindex = thetimes.index(thetime)
        thevalue = thevalues[theindex]
        return thevalue

def build_param_list(sc,rng,param,axis):
    global selected_params
    selected_params = []
    for orbit_number in selected_orbits:
        selected_params.append(get_param(orbit_number,sc,rng,param,axis))
    return
    # keep an eye on the console for errors

# make a list of parameters for a given list of orbits
# NB range is inclusive of start but exclusive of end value
# setup 'selected_orbits' global variable
def temperarure_correlation(sc,rng,param,axis,titletext):
    build_param_list(sc,rng,param,axis)
    # get temperatures for the same list of orbit numbers
    selected_temperatures = []
    for orbit_number in selected_orbits:
        selected_temperatures.append(averages[orbit_numbers.index(orbit_number)])
    # make a plot
    figure(figsize=(8,8))
    subplot(2,1,1)
    title(titletext)
    labeltext = 'C'+spacecraft[sc]+' '+axes[axis]+'  axis '+params[param]+' range '+ranges[rng]
    plot(selected_orbits,selected_params,'x',label=labeltext)
    legend();grid();ylabel('nT')
    subplot(2,1,2)
    plot(selected_orbits,selected_temperatures,'o',label='temperature')
    legend();grid();ylabel('deg.C')
    xlabel('Orbit Number'); 


    # linear fit
    # polyfit doesn't like 'nan'
    # select only finite values from the temperature list
    # and the corresponding values from the parameter list
    x = array(selected_temperatures)[isfinite(selected_temperatures)]
    y = array(selected_params)[isfinite(selected_temperatures)]
    fit,cov = polyfit(x,y,1,cov=True)
    m = fit[0]
    c = fit[1]
    sig_m = sqrt(cov[0,0])
    sig_c = sqrt(cov[1,1])
    linear = poly1d(fit)

    # correlation plot
    figure(figsize=(8,8))
    plot(selected_temperatures,selected_params,'x',label=labeltext)
    labelstring = 'gradient {:2.3f} +/- {:2.3f} \nintercept {:2.3f} +/- {:2.3f}'.format(m, sig_m,c,sig_c)
    plot(selected_temperatures,linear(selected_temperatures),label=labelstring)
    del labelstring
    grid()
    xlabel('temperature [deg]')
    ylabel('offset [nT]')
    legend()
    title(titletext)

    return

# funtion to find the orbit number in which any time lies
def time_to_orbit_number(time):
    global orbit_end_times,orbit_start_times,orbit_numbers
    for i in range(0,len(orbit_numbers)):
        if time > orbit_start_times[i] and time < orbit_end_times[i]:
            break
    return orbit_numbers[i]




#%% Set params for correlation plots
sc=spacecraft.index('1')
rng=ranges.index('2')
param=params.index('offset')
axis=axes.index('y')
# axis=axes.index('z')

#%% Orbit range for the 2005/06 season
selected_orbits = [x for x in range(728,800+1)] + [x for x in range(804,871+1)]
temperarure_correlation(sc,rng,param,axis,titletext="2005/06 season")

#%% Orbit range for the 2015/16 season
selected_orbits = [x for x in range(2299,2372)] + [x for x in range(2377,2451)]
temperarure_correlation(sc,rng,param,axis,titletext="2015/16 season")

#%% both periods viewed together
selected_orbits = [x for x in range(728,800+1)] + [x for x in range(804,871+1)]\
    +[x for x in range(2299,2372)] + [x for x in range(2377,2451)]
temperarure_correlation(sc,rng,param,axis,titletext="2005/06 and 2015/16 seasons")



#%% make a plot with the power cycling added

titletext="2015/16 season"
build_param_list(sc,rng,param,axis)

global selected_temperatures
selected_temperatures = []
for orbit_number in selected_orbits:
    selected_temperatures.append(averages[orbit_numbers.index(orbit_number)])
    del orbit_number

figure(figsize=(8,8))
title(titletext)
labeltext = 'C'+spacecraft[sc]+' '+axes[axis]+'  axis '+params[param]+' range '+ranges[rng]
plot(selected_orbits,selected_params,'x',label=labeltext)
powercycles = [2318,2373,2374,2375,2376,2383,2409,2422]
for x in powercycles:
    axvline(x,color='r',linestyle='--')
axvline(x,color='r',linestyle='--',label='OFF to ON')
legend();grid();ylabel('nT')
del x,powercycles,titletext,labeltext

# subplot(2,1,2)
# plot(selected_orbits,selected_temperatures,'o',label='temperature')
# legend();grid();ylabel('deg.C')
# xlabel('Orbit Number'); 



#%% cleanup globals
del orbit_numbers, orbit_start_times, orbit_end_times, averages
del cal_times,cal_values,selected_orbits,selected_params
del spacecraft,ranges,params,axes
del axis,rng,sc,param
del selected_temperatures