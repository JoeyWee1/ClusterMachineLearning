#%% IMPORTING LIBRARIES
from pandas import read_csv,to_datetime;
from os import system;
from os.path import exists;
from numpy import load,mean,std,array,save;
from matplotlib.pyplot import subplots,plot,xlabel,ylabel,title,grid;
from matplotlib import pyplot;
import numpy as np;

#%% GLOBAL VARIABLES
global orbit_numbers, orbit_start_times, orbit_end_times;

#%% LOAD ORBIT INFO
orbit_numbers = list(load("./orbit_numbers.npy",allow_pickle=True)); 
orbit_start_times = list(load("./orbit_start_times.npy",allow_pickle=True));
orbit_end_times = list(load("./orbit_end_times.npy",allow_pickle=True));

#%% WRITE PARAMETER FILE
def writeParamsFile(start_time,end_time,spacecraft): #Creates a 'param' file containing the orbit specific part of the command
    pstring = '{"date_from": "';
    pstring += start_time.replace(tzinfo=None).isoformat(timespec='minutes')+"Z";
    pstring += '","date_to": "' ;
    pstring += end_time.replace(tzinfo=None).isoformat(timespec='minutes')+"Z";
    pstring += '","sc": ';
    pstring += spacecraft;
    pstring += ',"parameters": [';
    pstring += '"F_050", "F_055", "F_074", "F_047", "F_048", "F_034", "J_236", "J_106", "J_213", "J_216"';
    pstring += ']}';
    # write the string into the file params.txt
    file = open("params.txt","w");
    file.truncate(); # erase content
    file.write(pstring);
    file.close();

#%% GENERATE FILE NAME
def generateFilename(spacecraft,orbit_number,telem):
    filename = telem+"_C" + spacecraft + "_orbit_" + str(orbit_number) + ".csv";
    return filename;

#%% FUNCTION TO RETRIEVE DATA
#Will retrieve data according to the contents of an (assumed to exist) params.txt file
#Save according to string 'filename', which is to be supplied with a .csv extension
#Will abort if file exists
def getRDM(filename):
    relativepath = "./CSVs/" + filename;
    #Check for existing csv file
    if exists(relativepath):
        print("Aborting: %s exists" % relativepath);
    else:
        relativepath += ".gz";
        parameter_string = 'curl -X GET https://caa.esac.esa.int/rdm-hk/api/data/ -H "Content-Type: application/json" -d @params.txt -o ' + relativepath;
        system(parameter_string);
        parameter_string = 'gunzip ' + relativepath;
        system(parameter_string);
        
#%% FUNCTION TO LOOP THROUGH ORBITS AND TELEMS, DOWNLOADING DATA
def getTelemFiles(spacecraft,startOrbit,endOrbit):
    telems = ["F_050", "F_055", "F_074", "F_047", "F_048", "F_034", "J_236", "J_106", "J_213", "J_216"];
    for telem in telems:
        for i in range(startOrbit,endOrbit):
            orbit_number = orbit_numbers[i];
            start_time = orbit_start_times[i];
            end_time = orbit_end_times[i];
            writeParamsFile(start_time,end_time,spacecraft);
            filename = generateFilename(spacecraft,orbit_number,telem);
            print("Getting orbit "+str(orbit_number)+" for spacecraft "+spacecraft+" from "+start_time.isoformat()+" to "+end_time.isoformat());
            getRDM(filename);
            
#%% CREATE ORBIT AVERAGES AND SIGMAS
def orbitAverages(spacecraft):
    telems = ["F_055", "F_074", "F_047", "F_048", "F_034", "J_236", "J_106", "J_213", "J_216"]; #The telems for which to process data
    spacecraftTelemStatistics = [];
    for orbitNumber in orbit_numbers:
        rangeFilename = generateFilename(spacecraft,orbitNumber,"F_050"); #Gets the filename for the range data for that orbit
        rangePathstring = "./CSVs/" + rangeFilename;
        data = read_csv(rangePathstring);
        dictReference = str(spacecraft)+"F_050";
        rangeData = data[dictReference][:];
        orbitTelemStatistics = [];
        for telem in telems:
            telemFilename = generateFilename(spacecraft,orbitNumber,telem); #Gets the filename for the telem data for that orbit
            telemPathstring = "./CSVs/" + telemFilename;
            data = read_csv(telemPathstring);
            dictReference = str(spacecraft)+telem;
            allTelemData = data[dictReference][:];
            range2TelemData = [];
            for i in (0, len(rangeData)):
                if (rangeData[i] == 2):
                    range2TelemData.append(allTelemData[i]);
            validTelemData = [x for x in range2TelemData if x<20 and x>-80];
            nonZeroTelemData = [x for x in validTelemData if x != 0]; 
            if len(range2TelemData) == 0:
                print("WARNING: Orbit %i file has no range 2 values" % orbitNumber);
            elif len(validTelemData) ==0:
                print("WARNING: Orbit %i contains no valid temperature values" % orbitNumber);
            elif len(nonZeroTelemData) ==0:
                print("WARNING: Orbit %i contains only zero values" % orbitNumber);
            if (len(range2TelemData)==0):
                count = 0;
                average = np.nan;
                sigma = np.nan;
                maximum = np.nan;
                minimum = np.nan;
            else:
                #Minimises the effects of strange 0 values
                if ((len(nonZeroTelemData)<len(validTelemData)) and (mean(nonZeroTelemData)<-10)):
                    validTelemData = nonZeroTelemData;
                    print("WARNING: Orbit %i discarding zero values" % orbitNumber);   
                count = len(validTelemData);
                average = mean(validTelemData);
                sigma = std(validTelemData);
                maximum = max(validTelemData);
                minimum = min(validTelemData);
            telemStatistic = [count,average,sigma,maximum,minimum];
            orbitTelemStatistics.append(telemStatistic);
        spacecraftTelemStatistics.append(orbitTelemStatistics);    
    return spacecraftTelemStatistics;
            
#%% RUN THINGS
getTelemFiles(1,0,3650);
spacecraftTelemStatistics = orbitAverages(spacecraft='1'); #In the order ["F_055", "F_074", "F_047", "F_048", "F_034", "J_236", "J_106", "J_213", "J_216"]
save("./telemStatistics", spacecraftTelemStatistics);












