#This code plots a chosen param against a telem for a range for a spacecraft for a season
#spacecraft [1,2,3,4]
#ranges [2,3,4,5,6,7]
#params [offset,gain,theta,phi]
#axes [x,y,z]
#all working is done in terms of the above thingies' array index as displayed
#%% IMPORTING THINGS
import numpy as np;
import datetime;
import matplotlib.pyplot as plt;
#%% DEFINING ORBITS
class Orbit: #Creating orbit class
    def __init__(self,orbitNumber,startTime,endTime): #Initiation function
        self.orbitNumber = orbitNumber; #Creating attributes to store each bit of required data
        self.startTime = startTime;
        self.endTime = endTime;
        self.calParams = np.empty((3,6,4,));#Calibration stats are set to nan as default; [axis][range][offset,gain,theta,phi]
        self.calParams[:] = np.nan;
    def setTemperature(self,temperature): #sets the temperature; done like this so that more params can be added later
        self.temperature = temperature; #temperature is the average temperature across an orbit
#%% IMPORTING ORBITS
uncleanedOrbits = np.load("./Inputs/uncleanedOrbitsArray.npy", allow_pickle = True);
#%% CREATE ARRAYS TO PLOT FROM ORBITS
def createArrayToPlot(orbits, startDatetime, endDatetime, sc, rng, axis, param): #sc, rng, axis, param as desired; orbits is the 2d array of orbits; start and end datetimes must be input as datetime objects
    orbitsInPeriod = []; #Create array of orbits in the relevant period
    outputArray = []; #This will be the output array; each value in the array will be a triple of [telem, param, datetime]
    for i in range(0,len(orbits[sc])): #Loops through orbits to choose ones in the relevant timeframes and add to the orbitsInPeriod array
        currentOrbit = orbits[sc][i]; #Extracting the orbit currently being treated
        currentOrbitTime = currentOrbit.startTime; #We will use the start times
        if((currentOrbitTime >= startDatetime) and (currentOrbitTime < endDatetime)): #Checking if the orbit is in the relevant timeframe
            orbitsInPeriod.append(currentOrbit); #If the orbit is in the relevant timeframe, it is appended to the array of orbits in the relevant period
    for i in range(0,len(orbitsInPeriod)):#Looping through the array of in-period orbits
        currentOrbit = orbitsInPeriod[i]; #Getting the orbit from orbitsInPeriod currently being treated for conciseness
        currentTime = currentOrbit.startTime; #Getting the current time from that orbit (we are using the start time for all)
        currentTelem = currentOrbit.temperature; #Currently, this is temperature, but this is general and can be altered
        currentParam = currentOrbit.calParams[axis][rng][param]; #Extracting the parameter based on the imputs from the Orbit objects parameter array
        currentOrbitNumber = currentOrbit.orbitNumber; #Getting the current orbit's orbit number so that the orbit's removed can be displayed
        if ((currentTelem == np.nan) and (currentParam == np.nan)): #If the data thing is invalid, it will not be added
            print("Orbit of orbit number ", currentOrbitNumber, " is invalid");
        else: #Else, the thing is valid
            triple = [currentTelem, currentParam, currentTime];#Creates the triple to append
            outputArray.append(triple);#Appends that triple to the output array
    print(len(orbitsInPeriod))
    return outputArray;
#%% PLOTTING 
def plotTelemParamVTime(data): #Takes in the output array of the createArrayToPlot function 
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True); #Creates the subplots
    telemValues = [];
    paramValues = [];
    datetimes = [];
    for i in range(0, len(data)):
        telemValues.append(data[i][0]);
        paramValues.append(data[i][1]);
        datetimes.append(data[i][2]);
    ax1.plot(datetimes, telemValues);
    ax1.set_ylabel('Telem');
    ax2.plot(datetimes, paramValues);
    ax2.set_ylabel('Param');
    fig.autofmt_xdate();
    plt.show();    
    
#%% RUN EVERYTHING
startDatetime = datetime.datetime(2015, 4, 1, 0, 0, 0); #The datetime of the start of the relevant period
endDatetime =  datetime.datetime(2017, 1, 31, 0, 0, 0); #The datetime of the end of  the relevant period
plotTelemParamVTime(createArrayToPlot(uncleanedOrbits,startDatetime, endDatetime, 0, 0, 2, 0));

