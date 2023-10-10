#This code takes in a split date and splits the spacecraft's OnPeriods into testing and training periods. It then plots the data vs a model for the test period.

#region IMPORTING REQUIRED LIBRARIES

import numpy as np; 
from sklearn.model_selection import train_test_split;
from sklearn import neighbors;
from sklearn.metrics import mean_squared_error;
from sklearn.metrics import mean_absolute_error;
import matplotlib.pyplot as plt; 
import math;
import datetime;
from sklearn.svm import SVR;

#endregion

#region DEFINING REQUIRED OBJECTS
#The only required objects are the Orbits and OnPeriods

class Orbit: #Creating orbit class
    def __init__(self,orbitNumber,startTime,endTime): #Initiation function
        self.orbitNumber = orbitNumber; #Creating attributes to store each bit of required data
        self.startTime = startTime;
        self.endTime = endTime;
        self.calParams = np.empty((3,6,4,));#Calibration stats are set to nan as default; [axes][range][offset,gain,theta,phi]
        self.calParams[:] = np.nan;
    def setTelemInfo(self,telemInfo):
        #The telems are indexed in the order of "F_055", "F_074", "F_047", "F_048", "F_034", "J_236", "J_106", "J_213", "J_216"
        #These will just extract the averages; we don't really care about the other statistics.
        self.F055 = telemInfo[0][1];
        self.F074 = telemInfo[1][1];
        self.F047 = telemInfo[2][1];
        self.F048 = telemInfo[3][1];
        self.F034 = telemInfo[4][1];
    
class OnPeriod: #Object to store all the orbit data beween two switch-on moments; this will include the off period; however, because the data for the off periods will be NaN, it doesn't matter
    def __init__(self,startTime, endTime): #The start of the current on period and the start of the next on period 
        self.startTime = startTime; #Defining the start and ends so that the relevant orbits can be searched for
        self.endTime = endTime;
        self.periodOrbits = [];

#endregion
        
#region IMPORTING THE ORBITS AND DECLARING GLOBAL VARIABLES

onPeriods = np.load("./Inputs/sortedCleanedOrbitsArrayV5(RecompiledRange2).npy", allow_pickle = True);
firstOrbitStartTime = datetime.datetime(2000, 8, 24, 8, 56, 52); #First orbit start time
axes = ["X", "Y", "Z"];

#endregion

#region CREATE FEATURES

def createAndSplitData(onPeriods,sc,trainingYears,axis,features): #Features is an array of the orbit attributes as strings
    #Defining arrays
    trainOnPeriods = []; #Array of OnPeriod objects in the training set, before the split time
    testOnPeriods = []; #Array of OnPeriod objects in the testing set, after the split time
    xTrain = []; #Feature vectors of the training set
    yTrain = []; #Labels (offsets) of the training set
    timeTrain = []; #Start times of all the training orbits
    xTest = []; #Feature vectors of the testing set
    yTest = []; #Labels (offsets) of the testing set
    timeTest = []; #Start times of all the testing orbits
    onTimes = []; #Stores the on times of the onPeriods in the test set
    offTimes = []; #Stores the off times of the onPeriods in the test set
    #Calculating the desired split time with which to split the onPeriods
    splitTime = firstOrbitStartTime + datetime.timedelta(seconds = (trainingYears * 31557600));#Defines the split time based on the number of training years
    #Loop through the onPeriods and add the to testing and training arrays
    for onPeriod in onPeriods[sc]:
       #All on periods with start times before the split time will be added to the training set
       periodStartTime = onPeriod.startTime; #Gets the period's start time
       if (periodStartTime < splitTime): #If the period's start time is before the split time
           trainOnPeriods.append(onPeriod); #Adding the period to the training onPeriod set
       else: #Otherwise, the period is after the split time: test set
           testOnPeriods.append(onPeriod); #Adding the period to the testing onPeriod set
    #Looping through the onPeriod arrays to create clean test and train x and y sets
    for trainOnPeriod in trainOnPeriods:
        periodOrbits = trainOnPeriod.periodOrbits; #Gets the array of the period's orbits
        for periodOrbit in periodOrbits: #Loop through the orbits in the period to check cleanliness
            #Creating the label and feature vector
            label = periodOrbit.calParams[axis][0][0]; #Gets the label for the range 2 offset data
            featureVector = []; #The blank feature vector for the orbit
            for feature in features: #Looping through the desired features and retrieving them
                coordinate = getattr(periodOrbit,feature); #Gets the value of each feature
                featureVector.append(coordinate); #Adds the value of the coordinate to the feature vector
            #Check for data cleanliness    
            dataCleanlinessMarker = True; #If true, the data is clean (no NAN)
            for i in range (0, len(featureVector)): #Looping through the coordinates in the feature vector to check for nan values for removal
                if (str(featureVector[i]) =="nan"): #Checking for the nan values
                    dataCleanlinessMarker = False; #Setting cleanliness to false, so the data will not be appended
            if (str(label) == "nan"):#Checks the y values for nan
                dataCleanlinessMarker = False; #Sets cleanliness to false 
            #Add data to the training arrays if clean
            if(dataCleanlinessMarker == True): #Adding if data is clean
                xTrain.append(featureVector);
                yTrain.append(label);
                timeTrain.append(periodOrbit.startTime)
            else: #Data is dirty; don't do anything
                pass;
    for testOnPeriod in testOnPeriods:
        periodOrbits = testOnPeriod.periodOrbits; #Gets the array of the period's orbits
        periodStartTime = testOnPeriod.startTime;
        periodEndTime = testOnPeriod.endTime;
        for periodOrbit in periodOrbits: #Loop through the orbits in the period to check cleanliness
            #Creating the label and feature vector
            label = periodOrbit.calParams[axis][0][0]; #Gets the label for the range 2 offset data
            featureVector = []; #The blank feature vector for the orbit
            for feature in features: #Looping through the desired features and retrieving them
                coordinate = getattr(periodOrbit,feature); #Gets the value of each feature
                featureVector.append(coordinate); #Adds the value of the coordinate to the feature vector
            #Check for data cleanliness    
            dataCleanlinessMarker = True; #If true, the data is clean (no NAN)
            for i in range (0, len(featureVector)): #Looping through the coordinates in the feature vector to check for nan values for removal
                if (str(featureVector[i]) =="nan"): #Checking for the nan values
                    dataCleanlinessMarker = False; #Setting cleanliness to false, so the data will not be appended
            if (str(label) == "nan"):#Checks the y values for nan
                dataCleanlinessMarker = False; #Sets cleanliness to false 
            #Add data to the training arrays if clean
            if(dataCleanlinessMarker == True): #Adding if data is clean
                xTest.append(featureVector);
                yTest.append(label);
                timeTest.append(periodOrbit.startTime);
            else: #The data is dirty; don't do anything
                pass;
        onTimes.append(periodStartTime);
        offTimes.append(periodEndTime);
    print("Data split")
    print("Training set length: {}".format(len(xTrain)));
    return  xTrain, yTrain, timeTrain, xTest, yTest, timeTest, onTimes, offTimes, sc, axis, trainingYears, splitTime, features;

#endregion

#region CREATE AND TRAIN MODEL ON TRAINING DATASET

def createAndTrainModel(splitData, c, gamma): #The splitData argument is the output of the createAndSplitData function
    xTrain = splitData[0]; #Pull out the x training data from the splitData
    yTrain = splitData[1]; #Pull out the y training data from the splitData
    model = SVR(kernel="rbf", C=c, gamma=gamma); #Creating the model
    model.fit(xTrain,yTrain); #Training the model on the data
    print("Model created")
    return model; #The model is an object and can be returned

#endregion

#region PLOT DATA AGAINST TIME WITH THE PREDICTIONS OVERLAID AND ONPERIOD RED LINES

def plotDataAndPredictionsVTime(splitData,model, telem):
    width = 0.5;
    #Extract all the data from the split data input
    xTest = splitData[3]; #The feature vectors to use to test the model
    yTest = splitData[4]; #The reference correct y values
    timeTest = splitData[5]; #The common x axis on the plots
    onTimes, offTimes = splitData[6], splitData[7]; #The on and off times to add to the figure
    sc = str(splitData[8]+1);
    axis = axes[splitData[9]];
    trainingYears = splitData[10];
    features = splitData[12];
    #Use the model to predict the y data
    yPred = model.predict(xTest);
    #Calculate the model error
    error = mean_absolute_error(yTest, yPred);
    #Plot the data
    saveTitle = "Test Period Data and Predictions for C{} {} axis; Training Years {}".format(sc, axis, trainingYears);
    title = " {} Single Feature Predictions for C{} {} axis; Training Years {}".format(telem[0], sc, axis, trainingYears);
    fig, ax1 = plt.subplots(1, 1, dpi=200);
    fig.suptitle(title);
    plt.rcParams['font.family'] = 'sans serif'
    ax1.set_xlabel("Test Set Data Split");
    ax1.set_ylabel("Offset");
    ax1.scatter(timeTest, yTest, marker = "x", color = "blue", label = "Reference");
    ax1.scatter(timeTest, yPred, marker = "x", color = "red", label = "Predicted");
    ax1.set_xlim(timeTest[0],timeTest[-1])
    ax1.axvline(onTimes[0], color = "lime",  linewidth=width, linestyle='--', label = "Power On/Off");
    ax1.axvline(offTimes[0], color = "aqua", linewidth=width, linestyle= "--");
    for i in range(1,len(onTimes)):
        ax1.axvline(onTimes[i], color = "lime",  linewidth=width, linestyle='--');
        ax1.axvline(offTimes[i], color = "aqua", linewidth=width, linestyle= "--");
    ax1.scatter(timeTest[0],yTest[0], color = "white", label = "Error: {:.3f}".format(error));
    ax1.scatter(timeTest[0],yPred[0], color = "white", label = "{}".format(features));
    fig.autofmt_xdate(); #This formats the x axis dates
    plt.legend(loc="lower left", fontsize = 5)
    print("Figure plotted")
    plt.show()
    #plt.savefig("./Outputs All Telems/{}/{}.png".format(features[0],saveTitle));

#endregion  
    
#region TEST

c = 0.1 #Between 0 and infinity
gamma = 0.1 #Between 0 and 1

#The telems are indexed in the order of "F_055", "F_074", "F_047", "F_048", "F_034", "J_236", "J_106", "J_213", "J_216"
telems = [ "F034", "F074"];
for telem in telems:
    for scIndex in range(0,4):
        for axisIndex in (1,2):
            splitData = createAndSplitData(onPeriods, scIndex, 15, axisIndex, [telem]);
            model = createAndTrainModel(splitData, c, gamma);
            plotDataAndPredictionsVTime(splitData, model, [telem]);
            del splitData, model

#endregion
         
            















