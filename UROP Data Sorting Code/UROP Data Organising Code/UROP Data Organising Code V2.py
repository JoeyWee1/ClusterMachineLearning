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
#%% LOADING INFORMATION FROM FILES
def loadOrbitInfo(numbersLoc,startTimesLoc,endTimesLoc,satelliteNum): #Loads the orbit information for one satellite from three file locations
    orbitNumbers = np.load(numbersLoc, allow_pickle=True); #Loads the orbit numbers; a few are missing for when the instrument wasn't switched on
    orbitStartTimes = np.load(startTimesLoc,allow_pickle=True); #Loads the orbit start times in Date-time objects in [year,month,day,hour,minute,second] format
    orbitEndTimes = np.load(endTimesLoc,allow_pickle=True); #Loads the orbit end times; at the time of commenting, these appear useless but will be imported just in case
    return orbitNumbers, orbitStartTimes, orbitEndTimes, satelliteNum-1; #Returns all information

def loadTemperatureInfo(temperaturesLoc,satelliteNum): #Loads the temperature information for one satellite
    temperatureInformation = np.load(temperaturesLoc,allow_pickle=True); #Loads temperature information from files
    temperatureOrbitAverages = temperatureInformation[1][:]; #Takes averages from each temperatureInformation set and puts them into a separate array
    return temperatureOrbitAverages, satelliteNum-1; #Returns the average temperatures for each orbit consecutively; satellite num -1 to get index

def loadCalibrationInfo(valuesLoc, timesLoc): #Loads the calibration info for all four satellites
    calTimes = np.load(timesLoc,allow_pickle=True); #Loads the start times for the orbits linked to the calibration data in a file structure that makes me want to cry
    calValues = np.load(valuesLoc,allow_pickle=True); #Loads the calibration values for for each combination. The index of each calibration links to the start times. Later, we will use the times to add them to the orbits.
    return calValues, calTimes; #Returns all values
#%% PUTTING EACH ORBIT INTO AN ORBIT OBJECT IN AN ORBITS ARRAY
class Orbit: #Creating orbit class
    def __init__(self,orbitNumber,startTime,endTime): #Initiation function
        self.orbitNumber = orbitNumber; #Creating attributes to store each bit of required data
        self.startTime = startTime;
        self.endTime = endTime;
        self.calParams = [np.nan,np.nan,np.nan,np.nan] #Calibration stats are set to nan as default; [axes][range][offset,gain,theta,phi]
    def setTemperature(self,temperature): #sets the temperature; done like this so that more params can be added later
        self.temperature = temperature; #temperature is the average temperature across an orbit
    
        
#Creating Orbit objects from the arrays and adding them to the orbits array; does this for one satellite, specified in loadOrbitInfo; satellite treated in loadOrbitInfo is passed in as a param
def createOrbits(orbitInfo): #Creates orbits from file info; orbitInfo from loadOrbitInfo function
    orbitNumbers = orbitInfo[0]; #Separating the outputs of the loadOrbitInfo function
    orbitStartTimes = orbitInfo[1];
    orbitEndTimes = orbitInfo[2]; #These three have the same length :>
    satelliteNumIndex = orbitInfo[3]; #One has already been subtracted from the satellite number to get its index in the orbits array
    satelliteOrbits = []; #Temporary array to store all the satellite orbits 
    for orbit in range (0,len(orbitNumbers)): #Looping through all array objects for one satellite as passed in, creating an orbit object for each orbit, and adding them to satelliteOrbits array
        tempOrbitNumber = orbitNumbers[orbit]; #Gets the current orbit number
        tempStartTime = orbitStartTimes[orbit]; #Gets the start time of the current orbit
        tempEndTime = orbitEndTimes[orbit]; #Gets the end time of the current orbit
        newOrbit = Orbit(tempOrbitNumber,tempStartTime,tempEndTime); #Creates an orbit with all that information
        satelliteOrbits.append(newOrbit); #Adds the new orbit to the temporary satellite orbits array
    orbits[satelliteNumIndex] = satelliteOrbits; #Adds all the newly created orbits in the satellite orbits array to the correct satellite in the orbits array 
        
#%% ADDING TEMPERATURES AND OTHER TELEMETRY DATA
def addTemperatures(temperatureInfo): #Adds temperature data to each orbit for one satellite as specified by the temperature info from loadTemperatureInfo function, which is the only param
    temperatureOrbitAverages = temperatureInfo[0]; #Separating the outputs of the loadTemperatureInfo function
    satelliteNumIndex = temperatureInfo[1]; #loadTemperatureInfo already subtracts one to get to the index of the satellite in the orbits array
    for i in range (0, len(temperatureOrbitAverages)): #Loops through each orbit average temperature; the length is the same as the number of orbits as they match sequentially
        orbits[satelliteNumIndex][i].setTemperature(temperatureOrbitAverages[i]); #For the correct satellite, each orbit recorded has the orbit average temperature added to it
#%% ADDING CALIBRATION PARAMETERS #EDIT TO LOOP THROUGH ORBITS ARRAY
def addCalData(calData): #Takes in calibration data from loadCalibrationInfo for all 4 satellites
    calValues = calData[0]; #Takes out the calibration values
    calTimes = calData[1]; #Takes out the calibration times (match with start of orbit)
    for sc in range(0,3): #Loops through the three spacecraft
        for rng in range(0,5): #Loops through the 6 ranges
            for params in range(0,3): #Loops through the 4 parameters
                for axis in range(0,2): #Loops through the 3 axes
                    i = (72*sc)+(12*rng)+(3*params)+(axis); #Calculates the strange index value for that combination
                    valueSet = calValues[i]; #Gets the set of calibration values for that combination
                    timeSet = calTimes[i]; #Gets the calibration times for that combination
                    for time in range(0,len(timeSet)): #Loops through each time in the timeSet to look for the orbit beginning at the correct time for the specified satellite
                        calValue = valueSet[time]; #Gets the calibration value to add once the right orbit has been matched to the time
                        searchTime = timeSet[time]; #The orbit start time being looked for
                        orbitIndexFound = -1; #The index of the orbit in the satellite sub-array where the searchTime matches the orbit's startTime
                        for j in range (0,len(orbits[sc])): #Loop through all the orbits in the relevant satellite's sub-array to find the sub-array index of the orbit where the times match
                            if(orbits[sc][j].startTime == searchTime): #Compares the start times to the search times
                                orbitIndexFound = j; #Once the right one is found the index is recorded and the loop is broken
                                break;
                        orbits[sc][orbitIndexFound].calParams[params]
                                
                        

#%% RUNNING ALL THE FUNCTIONS
createOrbits(loadOrbitInfo("./orbit_numbers.npy","./orbit_start_times.npy","./orbit_end_times.npy",1)); #To loop through four spacecraft, just rewrite loadFileInfo to take in the file names as params then loop through array
addTemperatures(loadTemperatureInfo("./temperature_statistics.npy",1));
#addCalData(loadCalibrationInfo("./calvalues.npy","./times.npy"))







