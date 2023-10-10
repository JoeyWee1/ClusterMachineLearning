#%% IMPORTING LIBRARIES
from pandas import read_csv,to_datetime;
from os import system;
from os.path import exists;
from numpy import load,mean,std,array,save;
from matplotlib.pyplot import subplots,plot,xlabel,ylabel,title,grid;
from matplotlib import pyplot;

#%% GLOBAL VARIABLES
global orbit_numbers, orbit_start_times, orbit_end_times;

#%% LOAD ORBIT INFO
orbit_numbers = list(load("./orbit_numbers.npy",allow_pickle=True));
orbit_start_times = list(load("./orbit_start_times.npy",allow_pickle=True));
orbit_end_times = list(load("./orbit_end_times.npy",allow_pickle=True));

#%% WRITE PARAMETER FILE
def writeParamsFile(start_time,end_time,spacecraft, telem):
    pstring = '{"date_from": "';
    pstring += start_time.replace(tzinfo=None).isoformat(timespec='minutes')+"Z";
    pstring += '","date_to": "' ;
    pstring += end_time.replace(tzinfo=None).isoformat(timespec='minutes')+"Z";
    pstring += '","sc": ';
    pstring += spacecraft;
    pstring += ',"parameters": ["';
    pstring += telem;
    pstring += '"]}';
    # write the string into the file params.txt
    file = open("params.txt","w");
    file.truncate(); # erase content
    file.write(pstring);
    file.close();
    
#%% GENERATE FILE NAME
def telemFilename(spacecraft,orbit_number,telem):
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
        
#%% FUNCTION TO LOOP THROUGH ORBITS, DOWNLOADING DATA
def getTelemFiles(spacecraft,telem):
    for i in range(0,len(orbit_numbers)):
        orbit_number = orbit_numbers[i];
        start_time = orbit_start_times[i];
        end_time = orbit_end_times[i];
        writeParamsFile(start_time,end_time,spacecraft);
        filename = telemFilename(spacecraft,orbit_number,telem);
        print("Getting orbit "+str(orbit_number)+" for spacecraft "+spacecraft+" from "+start_time.isoformat()+" to "+end_time.isoformat());
        getRDM(filename);
    
#%% CREATE ORBIT AVERAGES AND SIGMAS
def orbitAverages(spacecraft,telem):
    global averages, maxima, minima, counts, sigmas;
    global nonzeroaverages;
    nonzeroaverages = [];    
    averages = [];
    sigmas = [];
    maxima = [];
    minima = [];
    counts = [];
    for orbit_number in orbit_numbers:
        filename = telemFilename(spacecraft,orbit_number,telem);
        pathstring = "./CSVs/"+filename;
        if exists(pathstring):        
            data = read_csv(pathstring);
            dictReference = str(spacecraft)+telem;
            telems = data[dictReference][:];
        else:
            print("WARNING: Filename %s does not exist" % filename);
     #Check for file integrity
        validtelems = [x for x in telems if x<20 and x>-80];
        nonzerotelems = [x for x in validtelems if x != 0];
        if len(telems) == 0:
            print("WARNING: Orbit %i file is empty" % orbit_number);
        elif len(validtelems) ==0:
            print("WARNING: Orbit %i contains no valid temperature values" % orbit_number);
        elif len(nonzerotelems) ==0:
            print("WARNING: Orbit %i contains only zero values" % orbit_number);
        
        if len(validtelems) ==0:
            counts.append(0);
            averages.append(float('nan'));
            sigmas.append(float('nan'));
            maxima.append(float('nan'));
            minima.append(float('nan'));          
        else:
            # attempt to minimize effect of spurious zero values
            if len(nonzerotelems) < len(validtelems) and mean(nonzerotelems) < -10:
                validtelems = nonzerotelems;
                print("WARNING: Orbit %i discarding zero values" % orbit_number);            
            counts.append(len(validtelems));
            averages.append(mean(validtelems));
            sigmas.append(std(validtelems));
            maxima.append(max(validtelems));
            minima.append(min(validtelems));
        
        if len(nonzerotelems) == 0:
            nonzeroaverages.append(float('nan'));
        else: 
            nonzeroaverages.append(mean(nonzerotelems));

#%% RUN THINGS
getTelemFiles(1, "F_074");
orbitAverages(spacecraft='1');
telemStatistics = array([counts,averages,sigmas,maxima,minima]);
save("./telemStatistics", telemStatistics);

















