#This code plots a chosen param against a telem for a range for a spacecraft for a season
spacecraft = ["1","2","3","4"];
ranges = ["2","3","4","5","6","7"];
params = ["Offset","Gain","Theta","Phi"];
axes = ["X","Y","Z"];
telems = ["F074","F034","F047","F048","F055"];
#all working is done in terms of the above thingies' array index as displayed
#%% IMPORTING THINGS
import numpy as np;
import datetime;
import matplotlib.pyplot as plt;
#%% DEFINING ORBITS
#The only required objects are the Orbits and OnPeriods
class Orbit: #Creating orbit class
    def __init__(self,orbitNumber,startTime,endTime): #Initiation function
        self.orbitNumber = orbitNumber; #Creating attributes to store each bit of required data
        self.startTime = startTime;
        self.endTime = endTime;
        self.calParams = np.empty((3,6,4,));#Calibration stats are set to nan as default; [axes][range][offset,gain,theta,phi]
        self.calParams[:] = np.nan;
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
#%% IMPORTING ORBITS
uncleanedOrbits = np.load("./Inputs/cleanedOrbitsArrayV2(MoreData).npy", allow_pickle = True);
#%% CREATE ARRAYS TO PLOT FROM ORBITS
def createArrayToPlot(orbits, sc, rng, axis, param, telem): #sc, rng, axis, param as desired; orbits is the 2d array of orbits; start and end datetimes must be input as datetime objects
    orbitsInPeriod = []; #Create array of orbits in the relevant period
    outputArray = []; #This will be the output array; each value in the array will be a triple of [telem, param, datetime]
    for i in range(0,len(orbits[sc])): #Loops through orbits to choose ones in the relevant timeframes and add to the orbitsInPeriod array
        currentOrbit = orbits[sc][i]; #Extracting the orbit currently being treated
        #currentOrbitTime = currentOrbit.startTime; #We will use the start times
        #if((currentOrbitTime >= startDatetime) and (currentOrbitTime < endDatetime)): #Checking if the orbit is in the relevant timeframe
        orbitsInPeriod.append(currentOrbit); #If the orbit is in the relevant timeframe, it is appended to the array of orbits in the relevant period
    for i in range(0,len(orbitsInPeriod)):#Looping through the array of in-period orbits
        currentOrbit = orbitsInPeriod[i]; #Getting the orbit from orbitsInPeriod currently being treated for conciseness
        currentTime = currentOrbit.startTime; #Getting the current time from that orbit (we are using the start time for all)
        currentTelem = getattr(currentOrbit, telem); #Currently, this is temperature, but this is general and can be altered
        currentParam = currentOrbit.calParams[axis][rng][param]; #Extracting the parameter based on the imputs from the Orbit objects parameter array
        #currentOrbitNumber = currentOrbit.orbitNumber; #Getting the current orbit's orbit number so that the orbit's removed can be displayed
        #if ((currentTelem == np.nan) and (currentParam == np.nan)): #If the data thing is invalid, it will not be added
            #print("Orbit of orbit number ", currentOrbitNumber, " is invalid");
        #else: #Else, the thing is valid
        triple = [currentTelem, currentParam, currentTime];#Creates the triple to append
        outputArray.append(triple);#Appends that triple to the output array
    return outputArray,sc,rng,axis,param;
#%% PLOTTING 
def plotTelemParamVTime(arrayData): #Takes in the output array of the createArrayToPlot function to plot the temperatures and a param against time; can be altered once more telems are added
    data = arrayData[0]; #Pulling out all the data from the output of the createArrayToPplot function
    scIndex = arrayData[1];
    rngIndex = arrayData[2];
    axisIndex = arrayData[3];
    paramIndex = arrayData[4];
    startTime = arrayData[5];
    endTime = arrayData[6];
    startYear = startTime.year-2000; #Subtracting 2000 from the years to get the abbreviated version
    endYear = endTime.year-2000;
    sc = spacecraft[scIndex]; #Gets the string versions of all the information from the arrays
    rng = ranges[rngIndex];
    axis = axes[axisIndex];
    param = params[paramIndex];
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, dpi = 200); #Creates the subplots
    title = "Temperature-{} VS Time {} Axis Range {} Cluster {} {}'-{}' Season".format(param, axis, rng, sc, startYear, endYear); #Formats the title string
    fig.suptitle(title); #Creates the title
    telemValues = []; #Creating arrays into which to put the data pulled from the triples
    paramValues = [];
    datetimes = [];
    for i in range(0, len(data)): #Looping through the triples to pull the data and append them to the relevant arrays
        telemValues.append(data[i][0]);
        paramValues.append(data[i][1]);
        datetimes.append(data[i][2]);
    ax1.scatter(datetimes, telemValues, marker = "x", color = "crimson"); #Plot the telemetry values
    ax1.set_ylabel("Temperature"); #Set the label to temperature; the only telem rn is temperature so this is the format
    ax2.scatter(datetimes, paramValues, marker = "x", color = "crimson"); #Plot the calibration parameter
    ax2.set_ylabel(param); #Labelling the param
    fig.autofmt_xdate(); #This formats the x axis dates
    #filename = "./Outputs/" +sc+"/"+axis+"/"+param"/"+rng+"/"+ title + ".png";
    filename = "./Outputs/{}/{}/{}/{}/{}.png".format(sc,axis,param,rng,title);
    print(filename)
    plt.savefig(filename)
    plt.show(); #Show the plot

def plotTelemVParam(arrayData): #Takes in the output array of the createArrayToPlot function to plot the temperatures against a param; can be altered once more telems are added
    data = arrayData[0]; #Pulling out all the data from the output of the createArrayToPplot function
    scIndex = arrayData[1];
    rngIndex = arrayData[2];
    axisIndex = arrayData[3];
    paramIndex = arrayData[4];
    #startTime = arrayData[5];
    #endTime = arrayData[6];
    #startYear = startTime.year-2000; #Subtracting 2000 from the years to get the abbreviated version
    #endYear = endTime.year-2000;
    sc = spacecraft[scIndex]; #Gets the string versions of all the information from the arrays
    rng = ranges[rngIndex];
    axis = axes[axisIndex];
    param = params[paramIndex];
    fig, ax = plt.subplots(dpi = 200);
    title = "{} VS {}  {} Axis Range {} Cluster {} All Time".format(telem, param, axis, rng, sc); #Formats the title string
    fig.suptitle(title); #Creates the title
    telemValues = []; #Creating arrays into which to put the data pulled from the triples
    paramValues = [];
    for i in range(0, len(data)): #Looping through the triples to pull the data and append them to the relevant arrays
        telemValues.append(data[i][0]);
        paramValues.append(data[i][1]);
    ax.scatter(telemValues, paramValues, marker = "x", color = "crimson"); #Plot the telemetry values
    filename = "./Outputs/{}/{}/{}/{}/{}.png".format(sc,axis,param,rng,title);
    print(filename)
    plt.savefig(filename)
    plt.show(); #Show the plot

#%% RUN EVERYTHING

for sc in range(0,4): #Loops through the four spacecraft
        #for rng in range(0,6): #Loops through the 6 ranges
        rng = 0;   
        #for param in range(0,4): #Loops through the 4 parameters
        param = 0;    
        for axis in range(1,3): #Loops through the 3 axes
            for telem in telems:
                plotTelemVParam(createArrayToPlot(uncleanedOrbits, sc, rng, axis, param, telem));
#plotTelemVParam(createArrayToPlot(uncleanedOrbits,startDatetime, endDatetime, 0, 0, 2, 0));

