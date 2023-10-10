#This code learns and exports a 6 dimensional KNN model, which takes in 6 telems and returns the predicted offset param
#%% IMPORTING REQUIRED LIBRARIES
import numpy as np; 
from sklearn.model_selection import train_test_split;
from sklearn import neighbors;
from sklearn.metrics import mean_squared_error;
from sklearn.metrics import mean_absolute_error;
import matplotlib.pyplot as plt; 

#%% DEFINING REQUIRED OBJECTS
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

#%% IMPORTING THE ORBITS
orbits = np.load("./Inputs/cleanedOrbitsArrayV2(MoreData).npy", allow_pickle = True);

#%% CREATE FEATURES
def createAndSplitData(orbits, scIndex):
    featureVectors = [];
    offsets = []; #These two arrays are index matched
    sc = 3; #Select a spacecraft
    for orbit in orbits[sc]: #Loop through every orbit for each spacecraft
            dataCleanliness = True; #Stores if the data is clean and whether or not it should be added to the arrays
            featureVector = [orbit.F074, orbit.F055]; #For each orbit, create a feature vector composed of the spacecraft/instrument telems
            y = orbit.calParams[2][0][0]; #Gets the z axis range 2 offset
            for i in range (0, len(featureVector)): #Looping through the coordinates in the feature vector to check for nan values for removal
                if (str(featureVector[i]) =="nan"): #Checking for the nan values
                    dataCleanliness = False; #Setting cleanliness to false, so the data is not appended
            if (str(y) == "nan"):#Checks the y values for nan
                dataCleanliness = False;#Replaces it with an out of bounds value
            if (dataCleanliness == True):
                featureVectors.append(featureVector);
                offsets.append(y);
            else:
                #print("Data point rejected");
                pass;
    xTrain, xTest, yTrain, yTest = train_test_split(featureVectors,offsets,test_size = 0.2);
    #Convert everything in np arrays
    xTrain = np.array(xTrain);
    xTest = np.array(xTest);
    yTrain = np.array(yTrain);
    yTest = np.array(yTest);
    return xTrain, xTest, yTrain, yTest, scIndex;

#%% TRAIN AND PLOT MODEL
def trainAndPlotModel(splitData, k):
    xTrain = splitData[0];
    xTest = splitData[1];
    yTrain = splitData[2];
    yTest = splitData[3];
    scIndex = splitData[4];
    weights = "distance"; #Electing to weigh the neighbours by distance
    model = neighbors.KNeighborsRegressor(n_neighbors=k,weights=weights);
    model.fit(xTrain,yTrain);
    pred = model.predict(xTest);
    #error = np.sqrt(mean_squared_error(yTest, pred));
    error = mean_absolute_error(yTest, pred);
    errorList = []
    for prediction in range(0,len(yTest)):
        error = np.abs(yTest[prediction] - pred[prediction]);
        errorList.append(error);
    print("The mean absolute error of the offset  for k = ", k," is ", error);
    fig = plt.figure()
    plt.rcParams["figure.dpi"] = 200
    ax = fig.add_subplot(111, projection='3d')
    ax.view_init(30, 90) #Changes the angle
    #ax.set_xlim(-10, 10)
    ax.set_ylim(7.5, 20)
    #ax.set_zlim(-10, 10)
    ax.scatter(xTrain[:, 0], xTrain[:, 1],yTrain, color = "orange",s = 0.5, label = "Training")
    ax.scatter(xTest[:, 0],  xTest[:, 1],yTest , color = 'red', s = 0.5, label = "Test")
    ax.scatter(xTest[:, 0],  xTest[:, 1],pred , color = 'blue', s = 0.5, label = "Prediction")
    plt.legend();
    #print(xTest[1])
    #print(yTest[1])
    #print(pred[1])
    #print(xTrain[1])
    #print(yTrain[1])
    #ax.scatter(xTrain[:0], xTrain[:1],yTrain, color = "orange", s=0.1)
    title = "Cluster {}; K = {}; MeanAbsError = {:.2f}".format(scIndex+1,k,error);
    ax.set_title(title)
    ax.set_xlabel('F074')
    ax.set_zlabel('Offset')
    ax.set_ylabel('F055')
    plt.show()
    #print(errorList)
    return error;

#%% OPTIMISE K HYPERPARAMETER
def optimiseK(sc, minK, maxK):
    splitData = createAndSplitData(orbits, sc-1);
    lowestError = 1e4;
    bestK = np.nan;
    for k in range(minK,maxK+1):
        error = trainAndPlotModel(splitData, k)
        if(error<lowestError):
            bestK = k;
            lowestError = error;
    print("The best K is ", bestK, " with an error of ", lowestError);


    
#%% RUN EVERYTHING

optimiseK(4,1,2)


