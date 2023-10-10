#%% IMPORTING LIBRARIES
import numpy as np;
from datetime import datetime;
import time;

#%% GLOBALS
commands = [[],[],[],[]];
cleanCommands = [[],[],[],[]];

#%% CLASSES
class OnPeriod: #Object to store all the orbit data beween two switch-on moments; this will include the off period; however, because the data for the off periods will be NaN, it doesn't matter
    def __init__(self,startTime, endTime): #The start of the current on period and the start of the next on period 
        self.startTime = startTime; #Defining the start and ends so that the relevant orbits can be searched for
        self.endTime = endTime;
        self.periodOrbits = [];
        
class Command: #Object to store each command
    def __init__(self,command,datetime):
        self.command = command;
        self.datetime = datetime;

#%% 

def readDirtyTimes(onOffTimesLoc,satelliteNum):
    dateFormat = '%Y-%m-%d %H:%M:%S'; #Define the date-time format
    satelliteIndex = satelliteNum - 1; #Gets the satellite's array index
    with open (onOffTimesLoc, 'r') as f: #Open the text file of on-off times
        onOffTimes = f.readlines(); #Reads the file line by line
    for onOffTime in onOffTimes: #Loops through each onOffTime to parse each line
        tempTimeText = onOffTime[0:18]; #Parses out the datetime as text
        tempCommand = onOffTime[20]; #Parses out the on or off command as text
        tempTime = datetime.strptime(tempTimeText.strip(),dateFormat);#Convert the datetime text into a datetime object        
        currentCommand = Command(tempCommand, tempTime); #Creates a command object out of the command and the time
        commands[satelliteIndex].append(currentCommand); #Adds the command to the list of commands

#%% 

def produceCleanTimes(satelliteNumber): #Produces the clean times for one satellite
    currentState = False; #Satellite begins in OFF state
    satelliteIndex = satelliteNumber-1;
    print("Initial: 0")
    for i in range (0,len(commands[satelliteIndex])): #Loops through the commands to find the duplicates
        currentCommand = commands[satelliteIndex][i]; 
        currentRequestedState = currentCommand.command;
        currentRequestDate = currentCommand.datetime;
        print("Requested: ", currentRequestedState, " at ", currentRequestDate);
        if(currentState == False):
            if(currentRequestedState == "1"):
                print("Current: 0; Requested 1; Appended")
                cleanCommands[satelliteIndex].append(currentCommand);
                currentState = True;
            else:
                print("Current: 0; Requested 0: Rejected")
        elif(currentState == True):
            if(currentRequestedState == "0"):
                print("Current: 1; Requested 0; Appended")
                cleanCommands[satelliteIndex].append(currentCommand);
                currentState = False;
            else:
                print("Current 1; Requested 1; Rejected")
        
    

#%% RUN
readDirtyTimes("./Inputs/C1_on_off_times.txt", 1);
readDirtyTimes("./Inputs/C1_on_off_times.txt", 2);
readDirtyTimes("./Inputs/C1_on_off_times.txt", 3);
readDirtyTimes("./Inputs/C1_on_off_times.txt", 4);

produceCleanTimes(1);
produceCleanTimes(2);        
produceCleanTimes(3);        
produceCleanTimes(4);       

#%% OUTPUT CLEAN COMMANDS

npCleanCommands  = np.array(cleanCommands);#converts orbits into a numpy array to export
filePath = "cleanCommandsArray.npy";
np.save(filePath, npCleanCommands); 
        
        
        
        
        