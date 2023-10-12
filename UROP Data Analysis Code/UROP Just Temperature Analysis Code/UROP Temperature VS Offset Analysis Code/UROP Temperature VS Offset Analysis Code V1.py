#This code will plot the telem v param and telem&param v time and fits the curves for one OnPeriod
spacecraft = ["1","2","3","4"];
ranges = ["2","3","4","5","6","7"];
params = ["Offset","Gain","Theta","Phi"];
axes = ["X","Y","Z"];
#all working is done in terms of the above thingies' array index as displayed
#%% IMPORTING THINGS

import numpy as np;
import datetime;
import matplotlib.pyplot as plt;

#%% DEFINING ALL THE CLASSES

#The eclipse and command classes are not required for the plotting
class Orbit: #Creating orbit class
    def __init__(self,orbitNumber,startTime,endTime): #Initiation function
        self.orbitNumber = orbitNumber; #Creating attributes to store each bit of required data
        self.startTime = startTime;
        self.endTime = endTime;
        self.calParams = np.empty((3,6,4,));#Calibration stats are set to nan as default; [axes][range][offset,gain,theta,phi]
        self.calParams[:] = np.nan;
    def setTemperature(self,temperature): #sets the temperature; done like this so that more params can be added later
        self.temperature = temperature; #temperature is the average temperature across an orbit
        
class OnPeriod: #Object to store all the orbit data beween two switch-on moments; this will include the off period; however, because the data for the off periods will be NaN, it doesn't matter
    def __init__(self,startTime, endTime): #The start of the current on period and the start of the next on period 
        self.startTime = startTime; #Defining the start and ends so that the relevant orbits can be searched for
        self.endTime = endTime;
        self.periodOrbits = [];

#%% IMPORT THE ONPERIOD OBJECTS FOR ANALYSIS FROM THE NPY FILE

onPeriods = np.load("./Inputs/sortedCleanedOrbitsArray.npy", allow_pickle = True);

#%% PLOTTING FOR ONE TEMP-PARAM PAIR AGAINST EACH OTHER 

def plotTemperatureVParam(scIndex, axisIndex, paramIndex, rngIndex, onPeriod, threshold): #Plots one OnPeriod for a set of calibration data
    #Begin by pulling all the values out of the objects into arrays to plot
    arrayToPlot = []; #This will be the array that will be plotted later; it will be populated by the data from the orbits 
    orbitsInPeriod = onPeriod.periodOrbits; #Gets the relevant orbits from the onperiod
    for i in range(0,len(orbitsInPeriod)):#Looping through the array of in-period orbits
        currentOrbit = orbitsInPeriod[i]; #Getting the orbit from orbitsInPeriod currently being treated for conciseness
        currentTime = currentOrbit.startTime; #Getting the current time from that orbit (we are using the start time for all)
        currentTelem = float(currentOrbit.temperature); #Currently, this is temperature, but this is general and can be altered
        currentParam = float(currentOrbit.calParams[axisIndex][rngIndex][paramIndex]); #Extracting the parameter based on the imputs from the Orbit objects parameter array
        currentOrbitNumber = currentOrbit.orbitNumber; #Getting the current orbit's orbit number so that the orbit's removed can be displayed
        if ((str(currentTelem) == "nan") or (str(currentParam) == "nan")): #If the data thing is invalid, it will not be added
            print("Orbit of orbit number ", currentOrbitNumber, " is invalid"); #Error message
        else: #Else, the thing is valid
            triple = [currentTelem, currentParam, currentTime];#Creates the triple to append
            arrayToPlot.append(triple);#Appends that triple to the output array
    #Now, we plot the array
    if(len(arrayToPlot) >= threshold):#We only want to plot the onPeriods with more than the threshold number of orbits
        print(len(arrayToPlot))    
        periodStartTime = onPeriod.startTime; #Getting the period start time for the title
        periodEndTime = onPeriod.endTime; #Getting the period end time for the title
        spacecraftName = spacecraft[scIndex]; #Getting the string versions of all the indices
        rangeName = ranges[rngIndex];
        axisName = axes[axisIndex];
        paramName = params[paramIndex];
        fig, ax = plt.subplots(dpi = 100);
        title = "Temperature VS {} {} Axis Range {} Cluster {} for On-Period between {} and {}".format(paramName, axisName, rangeName, spacecraftName, periodStartTime, periodEndTime); #Formats the title string
        fig.suptitle(title); #Creates the title
        telemValues = []; #Creating arrays into which to put the data pulled from the triples
        paramValues = [];
        for i in range(0, len(arrayToPlot)): #Looping through the triples to pull the data and append them to the relevant arrays
            telemValues.append(arrayToPlot[i][0]);
            paramValues.append(arrayToPlot[i][1]);
        ax.scatter(telemValues, paramValues, marker = "x", color = "crimson"); #Plot the telemetry values
        plt.xlabel("Temperature")
        plt.ylabel("Offset")
        savetitle = "Temp V {}  for {} to {}".format(paramName, periodStartTime.date(), periodEndTime.date())
        filename = "./Outputs/{}/{}/{}/{}/{}.png".format(spacecraftName,axisName,paramName,rangeName, savetitle);
        plt.savefig(filename)
        plt.show(); #Show

def runTemperatureVParam(): #Function to do the plotting for every onPeriod for every spacecraft
    #rng = 0; #Fix the range to 0 rn
    param = 0; #Only the offset
    #axis = 0; #Fix on x axis
    #sc = 3; #Fix on cluster 4
    #onPeriodIndex = len(onPeriods[sc])-1
    #onPeriod  = onPeriods[sc][onPeriodIndex]
    threshold = 15; #Set the threshold value
    for sc in range(0,4): #Loops through the four spacecraft
        for onPeriod in onPeriods[sc]:
            for rng in range(0,6): #Loops through the 6 ranges
                #for param in range(0,4): #Loops through the 4 parameters
                    for axis in range(0,3): #Loops through the 3 axes
                        plotTemperatureVParam(sc, axis, param, rng, onPeriod, threshold);

#%% RUN EVERYTHING

#runTemperatureVParam();
