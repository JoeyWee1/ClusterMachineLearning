#This code learns and exports a 6 dimensional KNN model, which takes in 6 telems and returns the predicted offset param
#%% IMPORTING REQUIRED LIBRARIES
import numpy as np; 
from sklearn.model_selection import train_test_split;
from sklearn import neighbors;
from sklearn.metrics import mean_squared_error;
import matplotlib as plt; 

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
orbits = np.load("./Inputs/cleanedOrbitsArrayV4(OutOfBoundsImputation).npy", allow_pickle = True);

#%% CREATE FEATURE VECTOR AND OFFSET ARRAYS
#The feature vectors are the x values and the offsets are the y values
featureVectors = [];
offsets = []; #These two arrays are index matched
for sc in range(0,4):
    for orbit in orbits[sc]:
        featureVector = [orbit.F074, orbit.F034, orbit.F047, orbit.F048, orbit.F055];
        y = orbit.calParams[2][0][0]; #z axis range 2 offset
        if(str(y)=="NaN"):
            print("NaN error for satellite", sc)
        featureVectors.append(featureVector);
        offsets.append(y);

#%% CREATE TRAIN AND TEST DATASETS
xTrain, xTest, yTrain, yTest = train_test_split(featureVectors,offsets,test_size = 0.2);
#print(xTrain)

#%% TRAIN MODEL

k = 10; #Picking the number of nearest neighbours to consider
weights = "distance"; #Electing to weigh the neighbours by distance
model = neighbors.KNeighborsRegressor(n_neighbors=k,weights=weights);
model.fit(xTrain,yTrain);




