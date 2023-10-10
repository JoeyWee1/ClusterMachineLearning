#DEALING WITH TEMP V OFFSET CORRELATION
#spacecraft [1,2,3,4]
#ranges [2,3,4,5,6,7]
#params [offset,gain,theta,phi]
#axes [x,y,z]
#%% IMPORTING LIBRARIES
import numpy as np;
import matplotlib.pyplot as plt;
from datetime import datetime;

#%% GLOBAL THINGIES
orbits = [[],[],[],[]]; #Creating an array in which to store Orbit objects; clusters 1-4
onPeriods = [[],[],[],[]]; #Creating an array in which to store period objects; one for each spacecraft
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

def loadOnTimes(onTimesLoc, satelliteNum):
    dateFormat = '%Y-%m-%d %H:%M:%S'; #Define the date-time format
    with open('C1_power_on_times.txt', 'r') as f: #Open the txt file
        lines = f.readlines(); #Read the lines in the file
    datetimes = []; #Create a list of datetime objects
    for line in lines: #Loop through each line of the text file
        datetimes.append(datetime.strptime(line.strip(), dateFormat)); #Create the datetime object using the format
    datetimes.append(datetime.datetime.now());
    return datetimes, satelliteNum -1; #Returns the array of datetimes and the relevant satellites array index
#%% PUTTING EACH ORBIT INTO AN ORBIT OBJECT IN AN ORBITS ARRAY
class Orbit: #Creating orbit class
    def __init__(self,orbitNumber,startTime,endTime): #Initiation function
        self.orbitNumber = orbitNumber; #Creating attributes to store each bit of required data
        self.startTime = startTime;
        self.endTime = endTime;
        self.calParams = np.empty((3,6,4,));#Calibration stats are set to nan as default; [axes][range][offset,gain,theta,phi]
        self.calParams[:] = np.nan;
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
#%% ADDING CALIBRATION PARAMETERS 
def addCalData(calData): #Takes in calibration data from loadCalibrationInfo for all 4 satellites
    calValues = calData[0]; #Takes out the calibration values
    calTimes = calData[1]; #Takes out the calibration times (match with start of orbit)
    for sc in range(0,4): #Loops through the four spacecraft
        for rng in range(0,6): #Loops through the 6 ranges
            for param in range(0,4): #Loops through the 4 parameters
                for axis in range(0,3): #Loops through the 3 axes
                    print("sc is ", sc,  ",range is ", rng, ",param is ", param, ",axis is ", axis,) #This is just a line for testing but it's really nice to watch run so it's being kept
                    i = (72*sc)+(12*rng)+(3*param)+(axis); #Calculates the strange index value for that combination
                    valueSet = calValues[i]; #Gets the set of calibration values for that combination
                    timeSet = calTimes[i]; #Gets the calibration times for that combination
                    for time in range(0,len(timeSet)): #Loops through each time in the timeSet to look for the orbit beginning at the correct time for the specified satellite
                        calValue = valueSet[time]; #Gets the calibration value to add once the right orbit has been matched to the time
                        searchTime = timeSet[time]; #The orbit start time being looked for
                        for j in range (0,len(orbits[sc])): #Loop through all the orbits in the relevant satellite's sub-array to find the sub-array index of the orbit where the times match
                            if(orbits[sc][j].startTime == searchTime): #Compares the start times to the search times
                                 orbits[sc][j].calParams[axis][rng][param] = calValue;
                                 break;
#%% CREATING OBJECT TO STORE THE ORBITS IN AN ON PERIOD
class OnPeriod: #Object to store all the orbit data beween two switch-on moments; this will include the off period; however, because the data for the off periods will be NaN, it doesn't matter
    def __init__(self,startTime, endTime): #The start of the current on period and the start of the next on period 
        self.startTime = startTime; #Defining the start and ends so that the relevant orbits can be searched for
        self.endTime = endTime;
    def addPeriodOrbits(self,periodOrbits): #All the orbits between these periods
        self.periodOrbits = periodOrbits; #Adding the relevant orbits
        
#Orbits are currently in order of number/start/end time in the orbits array so we can use the startOrbit and endOrbit to find the two extreme ends and add everything between them to the same on period
def createPeriods(onTimesInfo): #onTimesInfo is the output of the loadOnTimes function
    satelliteIndex = onTimesInfo[1]; #Pulling out the satellite's index in the orbits or onPeriods 2D array
    onTimes = onTimesInfo[0]; #Doing the same for the onTimes
    for i in range(0, len(onTimes)-1): #Loops through the onTimes to create the OnPeriod objects defined by each consecutive pair of onTimes
        newOnPeriod = OnPeriod(onTimes[i],onTimes[i+1]); #Creating each OnPeriod object, assigning their start and end times
        onPeriods[satelliteIndex].append(newOnPeriod);#Adds the temporary OnPeriod object to the global array of OnPeriods for the relevant satellite
    for j in range(0, len(onPeriods[satelliteIndex])): #Loop through each onPeriod
        startTime = onPeriods[satelliteIndex][j].startTime; #Extracts the startTime from the current onPeriod
        endTime = onPeriods[satelliteIndex][j].endTime; #Extracts the endTime from the current onPeriod
        for k in range(0, len(orbits[satelliteIndex])): #Loops through each orbit to check if they should be added to the current onPeriod
            tempPeriodOrbits = []; #Temporary array to store all the orbits in the 
            if ((orbits[satelliteIndex][k].startTime < endTime) and (orbits[satelliteIndex][k].startTime > startTime)):#Checks if the orbitStartTime is after the period start time and before the period end time
                tempPeriodOrbits.append(orbits[satelliteIndex][k]);
        onPeriods[j].addPeriodOrbits(tempPeriodOrbits);
    

#%% RUNNING ALL THE FUNCTIONS
for satellite in range(1,5): #The sattelites all orbit near each other so assume start times, end times, and orbit numbers are the same; this loops through all 4 spacecraft, using the information to create orbits for all 4
    createOrbits(loadOrbitInfo("./orbit_numbers.npy","./orbit_start_times.npy","./orbit_end_times.npy",satellite)); #To loop through four spacecraft, just rewrite loadFileInfo to take in the file names as params then loop through array
addTemperatures(loadTemperatureInfo("./temperature_statistics.npy",1));#add the other 3 and their file names later
addCalData(loadCalibrationInfo("./calvalues.npy","./times.npy"));







