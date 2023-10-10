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
eclipses = [[],[],[],[]]; #Creating an array in which to store the eclipses experienced by each spacrcraft 
cleanedOrbits = [[],[],[],[]]; #Creating an array in which to store the orbits not affected by the eclipses
onPeriods = [[],[],[],[]]; #Creating an array in which to store period objects; one for each spacecraft
reconstitutedOrbits = [[],[],[],[]]; #Creating an array in which to store the orbits reconstituted from the OnPeriods

#%% CREATING ALL REQUIRED CLASSES (OBJECTS)

class Orbit: #Creating orbit class
    def __init__(self,orbitNumber,startTime,endTime): #Initiation function
        self.orbitNumber = orbitNumber; #Creating attributes to store each bit of required data
        self.startTime = startTime;
        self.endTime = endTime;
        self.calParams = np.empty((3,6,4,));#Calibration stats are set to nan as default; [axes][range][offset,gain,theta,phi]
        self.calParams[:] = 1e4;
        self.F074 = 1e4;
        self.F034 = 1e4;
        self.F047 = 1e4;
        self.F048 = 1e4;
        self.F055 = 1e4;
        self.J236 = 1e4;
    def setF074(self,F074): #Sets the FGM temperature (F074); done like this so that more params can be added later
        self.F074 = F074; #All telems are the averages across an orbit
    def setF034(self,F034): #-12V voltage line
        self.F034 = F034;
    def setF047(self,F047): #+5V voltage line
        self.F047 = F047;
    def setF048(self,F048): #+12V voltage line
        self.F048 = F048;
    def setF055(self,F055): #PSU temp
        self.F055 = F055;
    def setJ236(self,J236): #Instrument current
        self.J236 = J236;
        
class OnPeriod: #Object to store all the orbit data beween two switch-on moments; this will include the off period; however, because the data for the off periods will be NaN, it doesn't matter
    def __init__(self,startTime, endTime): #The start of the current on period and the start of the next on period 
        self.startTime = startTime; #Defining the start and ends so that the relevant orbits can be searched for
        self.endTime = endTime;
        self.periodOrbits = [];
        
class Eclipse: #Creating a class called Eclipse to store the start and end times of the eclipses
    def __init__(self, startTime, endTime):
        self.startTime = startTime;
        self.endTime = endTime;
        
class Command: #Object to store each command
    def __init__(self,command,datetime):
        self.command = command;
        self.datetime = datetime;

#%% LOADING INFORMATION FROM FILES

def loadOrbitInfo(numbersLoc,startTimesLoc,endTimesLoc,satelliteNum): #Loads the orbit information for one satellite from three file locations
    orbitNumbers = np.load(numbersLoc, allow_pickle = True); #Loads the orbit numbers; a few are missing for when the instrument wasn't switched on
    orbitStartTimes = np.load(startTimesLoc, allow_pickle = True); #Loads the orbit start times in Date-time objects in [year,month,day,hour,minute,second] format
    orbitEndTimes = np.load(endTimesLoc, allow_pickle = True); #Loads the orbit end times; at the time of commenting, these appear useless but will be imported just in case 
    return orbitNumbers, orbitStartTimes, orbitEndTimes, satelliteNum-1; #Returns all information

def loadTelemInfo(telemDataLoc,satelliteNum): #Loads the temperature information for one satellite
    telemInformation = np.load(telemDataLoc, allow_pickle = True); #Loads temperature information from files
    telemOrbitAverages = telemInformation[1][:]; #Takes averages from each temperatureInformation set and puts them into a separate array
    return telemOrbitAverages, satelliteNum-1; #Returns the average temperatures for each orbit consecutively; satellite num -1 to get index

def loadCalibrationInfo(valuesLoc, timesLoc): #Loads the calibration info for all four satellites
    calTimes = np.load(timesLoc, allow_pickle = True); #Loads the start times for the orbits linked to the calibration data in a file structure that makes me want to cry
    calValues = np.load(valuesLoc, allow_pickle = True); #Loads the calibration values for for each combination. The index of each calibration links to the start times. Later, we will use the times to add them to the orbits.
    return calValues, calTimes; #Returns all values

def loadPeriodInfo(commandHistoryLoc, satelliteNum): #Loads the period info into a datetimes array of alternating on and off times
    satelliteIndex = satelliteNum - 1; #Gets the array index of the satellite being treated
    commandHistory = np.load(commandHistoryLoc, allow_pickle = True)[satelliteIndex]; #Gets the command history of the relevant satellite
    datetimes = []; #The datetimes array to be returned
    for i in range(0,len(commandHistory)):
        currentTime = commandHistory[i].datetime;
        datetimes.append(currentTime);
    datetimes.append(datetime.now()); #Adding the datetime of now to create the final period
    return datetimes, satelliteIndex;

def loadAndCreateEclipses(moonEclipseTimesLoc,earthEclipseTimesLoc,satelliteNum): #Loads and creates Eclipse objects for a single satellite; Eclipse times are stored on individual lines in the file, with each line alternating between start time and stop time, beginning with a start time
    dateFormat = '%Y-%m-%d %H:%M:%S'; #Define the date-time format
    satelliteIndex = satelliteNum - 1; #Gets the satellite's array index
    moonEclipseDatetimes = []; #Array in which to store the datetime converted versions of the moon eclipse times
    earthEclipseDatetimes = []; #Array in which to store the datetime converted versions of the earth eclipse time
    with open (moonEclipseTimesLoc, 'r') as f: #Open the text file of moon elcipse times
        moonEclipseTimes = f.readlines(); #Reads the moon elcipse times line by line
    for moonEclipseTime in moonEclipseTimes: #Goes through those moon eclipse times
        moonEclipseDatetimes.append(datetime.strptime(moonEclipseTime.strip(),dateFormat)); #Reads the text of each moon eclipse time and converts it into a datetime object, adding it to the array 
    with open (earthEclipseTimesLoc, 'r') as f: #Open the text file of earth eclipse times
        earthEclipseTimes = f.readlines(); #Reads the earth eclipse times line by line
    for earthEclipseTime in earthEclipseTimes: #Goes through all of the earth eclipse times
        earthEclipseDatetimes.append(datetime.strptime(earthEclipseTime.strip(),dateFormat)); #Reads the text of each earth eclipse time and converts it into a datetime object, adding it to the relevant array    
    for i in range(0,len(moonEclipseDatetimes)-1,2): #Goes through each pair of start and stop times in the moonEclipseDatetimes array
        eclipseStartTime = moonEclipseDatetimes[i]; #Gets the eclipse start time
        eclipseEndTime = moonEclipseDatetimes[i+1]; #The next line has the eclipse end time
        tempEclipse = Eclipse(eclipseStartTime,eclipseEndTime); #Creates an eclipse object from those start and end times
        eclipses[satelliteIndex].append(tempEclipse); #Adds that eclipse object to the array of eclipses for the relevant satellite
    for i in range(0,len(earthEclipseDatetimes)-1,2): #Goes through each pair of start and stop times in the earthEclipseDatetimes array
        eclipseStartTime = earthEclipseDatetimes[i]; #Gets the eclipse start time
        eclipseEndTime = earthEclipseDatetimes[i+1]; #The next line has the corresponding eclipse end time
        tempEclipse = Eclipse(eclipseStartTime,eclipseEndTime); #Creates an eclipse object from those start and end times
        eclipses[satelliteIndex].append(tempEclipse); #Adds that eclipse object to the array of exlipses for the relevant satellites
        
#%% PUTTING EACH ORBIT INTO AN ORBIT OBJECT IN AN ORBITS ARRAY

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

def addF074(F074Info): #Adds F074 data to each orbit for one satellite as specified by the F074 info from loadTelemInfo function, which is the only argument
    F074OrbitAverages = F074Info[0]; #Separating the outputs of the loadTelemInfo function
    satelliteNumIndex = F074Info[1]; #loadTelemInfo already subtracts one to get to the index of the satellite in the orbits array
    for i in range (0, len(F074OrbitAverages)): #Loops through each orbit average F074; the length is the same as the number of orbits as they match sequentially
        orbits[satelliteNumIndex][i].setF074(F074OrbitAverages[i]); #For the correct satellite, each orbit recorded has the orbit average F074 added to it
        
def addF034(F034Info): #See addF074 comments
    F034OrbitAverages = F034Info[0]; 
    satelliteNumIndex = F034Info[1]; 
    for i in range (0, len(F034OrbitAverages)): 
        orbits[satelliteNumIndex][i].setF034(F034OrbitAverages[i]); 
        
def addF047(F047Info): #See addF074 comments
    F047OrbitAverages = F047Info[0]; 
    satelliteNumIndex = F047Info[1]; 
    for i in range (0, len(F047OrbitAverages)): 
        orbits[satelliteNumIndex][i].setF047(F047OrbitAverages[i]); 
        
def addF048(F048Info): #See addF074 comments
    F048OrbitAverages = F048Info[0]; 
    satelliteNumIndex = F048Info[1]; 
    for i in range (0, len(F048OrbitAverages)): 
        orbits[satelliteNumIndex][i].setF048(F048OrbitAverages[i]); 
        
def addF055(F055Info): #See addF074 comments
    F055OrbitAverages = F055Info[0]; 
    satelliteNumIndex = F055Info[1]; 
    for i in range (0, len(F055OrbitAverages)): 
        if (str(F055OrbitAverages[i]) == "nan" ):
            orbits[satelliteNumIndex][i].setF055(1e4); 
        else:
            orbits[satelliteNumIndex][i].setF055(F055OrbitAverages[i]); 
        
def addJ236(J236Info): #See addF074 comments
    J236OrbitAverages = J236Info[0]; 
    print("J236 value of ", J236OrbitAverages, "read")
    satelliteNumIndex = J236Info[1]; 
    for i in range (0, len(J236OrbitAverages)): 
        orbits[satelliteNumIndex][i].setJ236(J236OrbitAverages[i]); 
        
#%% ADDING CALIBRATION PARAMETERS 

def addCalData(calData): #Takes in calibration data from loadCalibrationInfo for all 4 satellites
    calValues = calData[0]; #Takes out the calibration values
    calTimes = calData[1]; #Takes out the calibration times (match with start of orbit)
    for sc in range(0,4): #Loops through the four spacecraft
        for rng in range(0,6): #Loops through the 6 ranges
            for param in range(0,4): #Loops through the 4 parameters
                for axis in range(0,3): #Loops through the 3 axes
                    print("sc is ",sc, ", range is ",rng,", param is ", param,", axis is ", axis) #This is just a line for testing but it's really nice to watch run so it's being kept
                    i = (72*sc)+(12*rng)+(3*param)+(axis); #Calculates the strange index value for that combination
                    valueSet = calValues[i]; #Gets the set of calibration values for that combination
                    timeSet = calTimes[i]; #Gets the calibration times for that combination
                    for time in range(0,len(timeSet)): #Loops through each time in the timeSet to look for the orbit beginning at the correct time for the specified satellite
                        calValue = valueSet[time]; #Gets the calibration value to add once the right orbit has been matched to the time
                        searchTime = timeSet[time]; #The orbit start time being looked for
                        for j in range (0,len(orbits[sc])): #Loop through all the orbits in the relevant satellite's sub-array to find the sub-array index of the orbit where the times match
                            if(orbits[sc][j].startTime == searchTime): #Compares the start times to the search times
                                 orbits[sc][j].calParams[axis][rng][param] = calValue; #If the start time matches the search time, the calibration value is added to the relevant orbit
                                 break; #Break out of loop for conciseness
                                 
#%% REMOVING ECLIPSE AFFECTED DATA

def createCleanedOrbits(orbits, eclipses): #Goes through every orbit for every spacecraft and checks the orbit for any overlaps with any of the recorded eclipses for that spacecraft
    for i in range(0,4): #Loops through the 4 spacecraft
        for j in range(0,len(orbits[i])): #Loops through every orbit for that spacecraft
            currentOrbit =  orbits[i][j]; #Pulls out the current orbit
            orbitStartTime = currentOrbit.startTime; #Gets the current orbit's start time
            orbitEndTime = currentOrbit.endTime; #Gets the current orbit's end time
            orbitCleanliness = True; #Orbit is innocent until proven guilty: if an overlap if found, this will flip to false. After looping through the eclipses, if this is still true the orbit will be added to the cleanedOrbits array
            for k in range(0,len(eclipses[i])): #Loops through every eclipse for the spacecraft for each orbit to check if that orbit is affected by any eclipses
                currentEclipse = eclipses[i][k]; #Pulls out the current eclipse
                eclipseStartTime = currentEclipse.startTime; #Gets the eclipse's start time
                eclipseEndTime = currentEclipse.endTime; #Gets the eclipse's end time
                if ((eclipseStartTime < orbitStartTime) and (eclipseEndTime > orbitEndTime)):#Check for a total period eclipse (EST<OST&&EET>OET)
                    #print("Total Eclipse"); #Total eclipse warning
                    orbitCleanliness = False; #This orbit is dirty and will not be added
                    break; #Because an overlap has already been found, the following eclipses will have no effect on the result. So, break to increase code speed. 
                elif ((eclipseStartTime > orbitStartTime) and (eclipseEndTime < orbitEndTime)):#Check for enclosed eclipse (EST>OST&&EET<OET)
                    #print("Enclosed Eclipse"); #Enclosed eclipse warning
                    orbitCleanliness = False; #This orbit is dirty
                    break; #Break for conciseness
                elif((eclipseStartTime < orbitStartTime) and ((eclipseEndTime > orbitStartTime) and (eclipseEndTime < orbitEndTime))): #Check for type 1 partial eclipse (EST<OST&&(EET>OST&&EET<OET))
                    #A type 1 partial eclipse is when the eclipse begins before an orbit but ends during it
                    #print("Type 1 Partial Eclipse"); #Warning
                    orbitCleanliness = False; #Orbit is dirty
                    break; #Break for conciseness
                elif(((eclipseStartTime > orbitStartTime) and (eclipseEndTime < orbitEndTime)) and (eclipseEndTime > orbitEndTime)): #Check for type 2 partial eclipse
                    #A type 2 partial eclipse is when the eclipse begins during an obit and ends after it
                    #print("Type 2 Partial Eclipse"); #Warning
                    orbitCleanliness = False; #Orbit is dirty
                    break; #Break for conciseness
                else: #The case when no eclipse overlap is detected for this particular combination of orbit and eclipse
                    pass; #Don't do anything
            if(orbitCleanliness == True):#Once all the eclipses have been searched, if there hasn't been an eclipse overlap found for this orbit, it is added to the cleaned array
                cleanedOrbits[i].append(currentOrbit); #Current orbit is appended
            else: #Else for exceptions
                #print("Orbit {} for satellite {} excluded".format(j+1,i+1)); #Output
                pass
                
#%% CREATING OBJECT TO STORE THE ORBITS IN AN ON PERIOD

#Orbits are currently in order of number/start/end time in the orbits array so we can use the startOrbit and endOrbit to find the two extreme ends and add everything between them to the same on period
def createPeriods(onTimesInfo): #onTimesInfo is the output of the loadOnTimes function
    satelliteIndex = onTimesInfo[1]; #Pulling out the satellite's index in the orbits or onPeriods 2D array
    #print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    onOffTimes = onTimesInfo[0]; #Doing the same for the onOffTimes
    for i in range(0, len(onOffTimes)-1,2): #Loops through the onTimes to create the OnPeriod objects defined by each consecutive pair of onTimes
        newOnPeriod = OnPeriod(onOffTimes[i],onOffTimes[i+1]); #Creating each OnPeriod object, assigning their start and end times (start and end times are the consecutive in the datetimes array)
        onPeriods[satelliteIndex].append(newOnPeriod);#Adds the temporary OnPeriod object to the global array of OnPeriods for the relevant satellite
    for j in range(0, len(onPeriods[satelliteIndex])): #Loop through each onPeriod
        startTime = onPeriods[satelliteIndex][j].startTime; #Extracts the startTime from the current onPeriod
        endTime = onPeriods[satelliteIndex][j].endTime; #Extracts the endTime from the current onPeriod
        #count = 0
        for k in range(0, len(orbits[satelliteIndex])): #Loops through each orbit to check if they should be added to the current onPeriod
            if ((orbits[satelliteIndex][k].startTime < endTime) and (orbits[satelliteIndex][k].startTime > startTime)):#Checks if the orbitStartTime is after the period start time and before the period end time
                onPeriods[satelliteIndex][j].periodOrbits.append(orbits[satelliteIndex][k])
                #count += 1
        #print(count)
        
#%% RECONSTITUTE ORBIT ARRAYS FROM ONPERIODS

def reconstituteOrbits():
    for sc in range(0,4): #Loop through the 4 onPeriods
        for onPeriod in onPeriods[sc]: #Loop through the onPeriods for each spacecraft
            orbitsToAdd = onPeriod.periodOrbits;#For each onPeriod, extract the embedded array of orbits and append to the reconstituted orbits array for that spacecraft
            for orbitToAdd in orbitsToAdd:
                reconstitutedOrbits[sc].append(orbitToAdd);
                
#%% RUNNING ALL THE FUNCTIONS

#Creating the orbits for each satellite
for satellite in range(1,5): #The sattelites all orbit near each other so assume start times, end times, and orbit numbers are the same; this loops through all 4 spacecraft, using the information to create orbits for all 4
    createOrbits(loadOrbitInfo("./Inputs/OrbitData/orbit_numbers.npy","./Inputs/OrbitData/orbit_start_times.npy","./Inputs/OrbitData/orbit_end_times.npy",satellite)); #To loop through four spacecraft, just rewrite loadFileInfo to take in the file names as params then loop through array
    
#Adding F074 telemetry
addF074(loadTelemInfo("./Inputs/TelemStatistics/F074_statistics_C1.npy",1));
addF074(loadTelemInfo("./Inputs/TelemStatistics/F074_statistics_C2.npy",2));
addF074(loadTelemInfo("./Inputs/TelemStatistics/F074_statistics_C3.npy",3));
addF074(loadTelemInfo("./Inputs/TelemStatistics/F074_statistics_C4.npy",4));

#Adding F048 telemetry
addF048(loadTelemInfo("./Inputs/TelemStatistics/F048_statistics_C1.npy",1));
addF048(loadTelemInfo("./Inputs/TelemStatistics/F048_statistics_C2.npy",2));
addF048(loadTelemInfo("./Inputs/TelemStatistics/F048_statistics_C3.npy",3));
addF048(loadTelemInfo("./Inputs/TelemStatistics/F048_statistics_C4.npy",4));

#Adding F034 telemetry
addF034(loadTelemInfo("./Inputs/TelemStatistics/F034_statistics_C1.npy",1));
addF034(loadTelemInfo("./Inputs/TelemStatistics/F034_statistics_C2.npy",2));
addF034(loadTelemInfo("./Inputs/TelemStatistics/F034_statistics_C3.npy",3));
addF034(loadTelemInfo("./Inputs/TelemStatistics/F034_statistics_C4.npy",4));

#Adding F047 telemetry
addF047(loadTelemInfo("./Inputs/TelemStatistics/F047_statistics_C1.npy",1));
addF047(loadTelemInfo("./Inputs/TelemStatistics/F047_statistics_C2.npy",2));
addF047(loadTelemInfo("./Inputs/TelemStatistics/F047_statistics_C3.npy",3));
addF047(loadTelemInfo("./Inputs/TelemStatistics/F047_statistics_C4.npy",4));

#Adding F055 telemetry
addF055(loadTelemInfo("./Inputs/TelemStatistics/F055_statistics_C1.npy",1));
addF055(loadTelemInfo("./Inputs/TelemStatistics/F055_statistics_C2.npy",2));
addF055(loadTelemInfo("./Inputs/TelemStatistics/F055_statistics_C3.npy",3));
addF055(loadTelemInfo("./Inputs/TelemStatistics/F055_statistics_C4.npy",4));

#Adding J236 telemetry
addJ236(loadTelemInfo("./Inputs/TelemStatistics/J236_statistics_C1.npy",1));
addJ236(loadTelemInfo("./Inputs/TelemStatistics/J236_statistics_C2.npy",2));
addJ236(loadTelemInfo("./Inputs/TelemStatistics/J236_statistics_C3.npy",3));
addJ236(loadTelemInfo("./Inputs/TelemStatistics/J236_statistics_C4.npy",4));

#Adding all of the calibration data
addCalData(loadCalibrationInfo("./Inputs/CalData/calvalues.npy","./Inputs/CalData/times.npy"));

#Create all the eclipses for each satellite
loadAndCreateEclipses("./Inputs/Eclipses/C1_moon_eclipse_times.txt", "./Inputs/Eclipses/C1_earth_eclipse_times.txt", 1);
loadAndCreateEclipses("./Inputs/Eclipses/C2_moon_eclipse_times.txt", "./Inputs/Eclipses/C2_earth_eclipse_times.txt", 2);
loadAndCreateEclipses("./Inputs/Eclipses/C3_moon_eclipse_times.txt", "./Inputs/Eclipses/C3_earth_eclipse_times.txt", 3);
loadAndCreateEclipses("./Inputs/Eclipses/C4_moon_eclipse_times.txt", "./Inputs/Eclipses/C4_earth_eclipse_times.txt", 4);

#Populating the cleanedOrbits array with non-eclipse orbits
createCleanedOrbits(orbits,eclipses);

#Creating the OnPeriod objects and putting them in the onPeriods array
createPeriods(loadPeriodInfo("./Inputs/OnOffTimes/cleanCommandsArray.npy",1));
createPeriods(loadPeriodInfo("./Inputs/OnOffTimes/cleanCommandsArray.npy",2));
createPeriods(loadPeriodInfo("./Inputs/OnOffTimes/cleanCommandsArray.npy",3));
createPeriods(loadPeriodInfo("./Inputs/OnOffTimes/cleanCommandsArray.npy",4));

#Reconstitute orbits
reconstituteOrbits();

#%% TEST

#%% EXPORTING THE ORBIT ARRAY

npReconstitutedOrbits  = np.array(reconstitutedOrbits);#converts orbits into a numpy array to export
filePath = "cleanedOrbitsArrayV4(OutOfBoundsImputation).npy";
np.save(filePath, npReconstitutedOrbits);
