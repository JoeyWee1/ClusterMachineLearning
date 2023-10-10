#DEALING WITH TEMP V OFFSET CORRELATION
#spacecraft [1,2,3,4]
#ranges [2,3,4,5,6,7]
#params [offset,gain,theta,phi]
#axes [x,y,z]
#%% IMPORTING LIBRARIES
import numpy as np;
import matplotlib.pyplot as plt;
#%% GLOBAL THINGIES
orbits = [[],[],[],[]]; #Creating an array in which to store Orbit objects; clusters 1-4
#%% SETTING STANDARD FIGURE PARAMETERS
def setFigParams(figsize,dpi):
    plt.rcParams['figure.figsize'] = figsize;
    plt.rcParams['figure.dpi'] = dpi;
#%% LOADING INFORMATION FROM FILES
def loadOrbitInfo(numbersLoc,startTimesLoc,endTimesLoc,satelliteNum): 
    orbitNumbers = np.load(numbersLoc, allow_pickle=True);
    orbitStartTimes = np.load(startTimesLoc,allow_pickle=True); #Load in Datetimes
    orbitEndTimes = np.load(endTimesLoc,allow_pickle=True); #Datetimes in [year,month,day,hour,minute,second] format
    return orbitNumbers, orbitStartTimes, orbitEndTimes, satelliteNum-1;

def loadTemperatureInfo(temperaturesLoc,satelliteNum):
    temperatureInformation = np.load(temperaturesLoc,allow_pickle=True);
    temperatureOrbitAverages = temperatureInformation[1][:]; #Takes averages from each temperatureInformation set and puts them into a separate array
    return temperatureOrbitAverages, satelliteNum-1;

def loadCalibrationInfo(valuesLoc, timesLoc):
    calTimes = np.load(timesLoc,allow_pickle=True); #This file structure makes me want to cry
    calValues = np.load(valuesLoc,allow_pickle=True); #This one too- these are becoming 4D array of arrays: 5D array!
    return calValues, calTimes;
#%% PUTTING EACH ORBIT INTO AN ORBIT OBJECT IN AN ORBITS ARRAY
#Creating orbit class
class Orbit:
    def __init__(self,orbitNumber,startTime,endTime): 
        self.orbitNumber = orbitNumber;
        self.startTime = startTime;
        self.endTime = endTime;
        self.calParams = [np.nan,np.nan,np.nan,np.nan] #Calibration stats are set to - as default; [offset,gain,theta,phi]
    def setTemperature(self,temperature): #sets the temperature; done like this so that more params can be added later
        self.temperature = temperature; #temperature is the average temperature across a day
    
        
#Creating Orbit objects from the arrays and adding them to the orbits array
def createOrbits(orbitInfo): #Creates orbits from file info
    orbitNumbers = orbitInfo[0];
    orbitStartTimes = orbitInfo[1];
    orbitEndTimes = orbitInfo[2]; #These three have the same length :>
    satelliteNumIndex = orbitInfo[3];
    satelliteOrbits = [];
    for orbit in range (0,len(orbitNumbers)): #Looping through all array objects
        tempOrbitNumber = orbitNumbers[orbit];
        tempStartTime = orbitStartTimes[orbit];
        tempEndTime = orbitEndTimes[orbit];
        newOrbit = Orbit(tempOrbitNumber,tempStartTime,tempEndTime);
        satelliteOrbits.append(newOrbit);
        orbits[satelliteNumIndex]=satelliteOrbits;
        
#%% ADDING TEMPERATURES AND OTHER TELEMETRY DATA
def addTemperatures(temperatureInfo): #Adds temperature data to each orbit
    temperatureOrbitAverages = temperatureInfo[0];
    satelliteNumIndex = temperatureInfo[1];   
    print(len(orbits[0]))
    print(len(temperatureOrbitAverages))
    #print(len(orbits[satelliteNumIndex]))
    for i in range (0, len(temperatureOrbitAverages)):
        orbits[satelliteNumIndex][i].setTemperature(temperatureOrbitAverages[i]);
#%% ADDING CALIBRATION PARAMETERS
def addCalData(calData):
    calValues = calData[0];
    calTimes = calData[1];
    for sc in range(0,3):
        for rng in range(0,5):
            for params in range(0,3):
                for axis in range(0,2):
                    i = (72*sc)+(12*rng)+(3*params)+(axis);
                    valueSet = calValues[i];
                    timeSet = calTimes[i];
                    for time in range(0,len(timeSet)):
                        calValue = valueSet[i][time]
                        
                    
                    


#%% RUNNING ALL THE FUNCTIONS
createOrbits(loadOrbitInfo("./orbit_numbers.npy","./orbit_start_times.npy","./orbit_end_times.npy",1)); #To loop through four spacecraft, just rewrite loadFileInfo to take in the file names as params then loop through array
addTemperatures(loadTemperatureInfo("./temperature_statistics.npy",1));
#addCalData(loadCalibrationInfo("./calvalues.npy","./times.npy"))







