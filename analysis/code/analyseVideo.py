import pandas
import csv
import statistics
from termcolor import colored

maxSimTime = 400
DEBUG = 1
def calculateThroughputPerSecond(df):
    df = df.rename(columns={str(df.columns[0]) : "ts", str(df.columns[1]) : "bytes"})
    tB = [0,1] # time bounds for calculation
    tpList = []
    while tB[1] <= maxSimTime:
        if DEBUG: print(tB, end =" -> Throughput: ")
        throughput = df.loc[(df['ts'] > tB[0]) & (df['ts'] <= tB[1])]["bytes"].sum()
        tpList.append(throughput*8/1000)
        if DEBUG: print(throughput*8/1000, end=" kbps\n")
        # print(df.loc[(df['ts'] > tB[0]) & (df['ts'] <= tB[1])]["bytes"])
        tB = [x+1 for x in tB]
    # if DEBUG: print(tpList)
    return tpList

def importDF(testName, numCLI, dataType):
    # File that will be read
    fullScenarioName = str(testName) + '_' + str(numCLI)
    file_to_read = '../' + str(testName) + '/' + fullScenarioName + '/vectors/' + fullScenarioName + '_' + str(dataType) + '_vec.csv'
    print("Results from run: " + file_to_read)
    # Read the CSV
    return pandas.read_csv(file_to_read)

def filterDFTypeClient(df, filterType, hostNum):
    # filterType = type
    filterHost = 'stdHost[' + str(hostNum) + ']'
    return df.filter(like=filterType).filter(like=filterHost)

# Extract the link throughput on a per-second basis in each direction from the simple test
def extractLinkThroughputPerSecond(testName, numCLI):
    # File that will be read
    fullScenarioName = str(testName) + '_' + str(numCLI)
    file_to_read = '../' + str(testName) + '/' + fullScenarioName + '/vectors/' + fullScenarioName + '_link_vec.csv'
    print("Results from run: " + file_to_read)

    # Read the CSV
    df = pandas.read_csv(file_to_read) #, usecols=['Module','rcvdPk:sum(packetBytes)','rxPkOk:sum(packetBytes)','sentPk:sum(packetBytes)','txPk:sum(packetBytes)'], comment='*')
    # print(df.columns)
    bandwidthsr0r1 = []
    bandwidthsr1r0 = []

    # Calculate the avg. Throughput from router0 to router1
    # print (df.filter(like='sentPacketToUpperLayer:vector(packetBytes)').columns)
    if (len(df.filter(like='txPk:vector(packetBytes)').columns)):
        print("Getting throughputs from router0 to router1")
        col_no_bytes = df.columns.get_loc(df.filter(like='txPk:vector(packetBytes)').columns[0])
        new_df = df.iloc[:,[col_no_bytes,col_no_bytes+1]].dropna()
        bandwidthsr0r1 = calculateThroughputPerSecond(new_df)
    else:
        bandwidthsr0r1 = [0 for x in range(0,maxSimTime)]
        print ("Unable to get the throughputs from router0 to router1")
    
    # # Calculate the avg. Throughput from router1 to router0
    # # print (df.filter(like='receivedPacketFromUpperLayer:vector(packetBytes)').columns)
    if (len(df.filter(like='rxPkOk:vector(packetBytes)').columns)):
        print("Getting throughputs from router1 to router0")
        col_no_bytes = df.columns.get_loc(df.filter(like='rxPkOk:vector(packetBytes)').columns[0])
        new_df = df.iloc[:,[col_no_bytes,col_no_bytes+1]].dropna()
        bandwidthsr1r0 = calculateThroughputPerSecond(new_df)
    else:
        bandwidthsr1r0 = [0 for x in range(0,maxSimTime)]
        print ("Unable to get the bandwidth from router1 to router0")

    return [bandwidthsr0r1, bandwidthsr1r0]

# Get all link throughputs from a test scenario
def exportThroughputsPerSecondToCsv(testName, numCLIs):
    for numCLI in numCLIs:
        resRun = extractLinkThroughputPerSecond(testName, numCLI)
        # print(resRun)
        filename = '../exports/psThroughputs/' + str(testName) + '_' + str(numCLI) + '.csv'
        with open(filename, 'w', newline='') as myfile:
            wr = csv.writer(myfile)#, quoting=csv.QUOTE_ALL)
            wr.writerow(["Throughput r0r1", "Throughput r1r0"])
            for i in range(0,maxSimTime):
                wr.writerow([resRun[0][i], resRun[1][i]])
            # wr.writerow(resRun[1])

def extractMOS(testName, numCLI):
    df = importDF(testName, numCLI, 'mos_all') # import the data
    mosVals = []
    for cliNum in range(numCLI):
        filteredDF = filterDFTypeClient(df, 'mos', cliNum)
        mosValue = 1
        if (len(filteredDF.columns)):
            col_no_mosTS = df.columns.get_loc(filteredDF.columns[0])
            # print(df.iloc[:,col_no_mosTS+1])
            mosValue = df.iloc[:,col_no_mosTS+1].iat[0]
            print(colored('[   OK   ]', 'green'), end=' ')
        else:
            print(colored('[ NO VAL ]', 'red'), end=' ')
        mosVals.append(mosValue)
        print("Mos value for client " + str(cliNum) + ": " + str(mosValue))
    return mosVals

# Get all MOS values from a simulation scenario
def exportMOSValuesToCsv(testName, numCLIs):
    for numCLI in numCLIs:
        resRun = extractMOS(testName, numCLI)
        # print(resRun)
        filename = '../exports/mosValues/' + str(testName) + '_' + str(numCLI) + '.csv'
        with open(filename, 'w') as myfile:
            wr = csv.writer(myfile)
            wr.writerow(["MOS Value"])
            for mosVal in resRun:
                wr.writerow([mosVal])

def extractVBRs(testName, numCLI):
    df = importDF(testName, numCLI, 'vbr_all') # import the data
    vbrVals = []
    for cliNum in range(numCLI):
        filteredDF = filterDFTypeClient(df, 'DASHVideoBitrate', cliNum)
        vbrValues = []
        if (len(filteredDF.columns)):
            col_no_vbrTS = df.columns.get_loc(filteredDF.columns[0])
            # print(df.iloc[:,col_no_mosTS+1])
            vbrValues = [int(x) for x in df.iloc[:,col_no_vbrTS+1].dropna().tolist()]
            print(colored('[   OK   ]', 'green'), end=' ')
        else:
            print(colored('[ NO VAL ]', 'red'), end=' ')
        vbrVals.append(vbrValues)
        print("VBR values for client " + str(cliNum) + ": " + str(vbrValues))
    print("In " + testName + " with " + str(numCLI) + " clients extracted " + str(len(vbrVals)) + " elements")
    return vbrVals

# Get all Video Bitrate values from a simulation scenario
def exportVBRValuesToCsv(testName, numCLIs):
    for numCLI in numCLIs:
        resRun = extractVBRs(testName, numCLI)
        # print(resRun)
        filename = '../exports/vbrValues/' + str(testName) + '_' + str(numCLI) + '.csv'
        with open(filename, 'w', newline='') as myfile:
            wr = csv.writer(myfile)
            wr.writerow(["Video Bitrates"])
            for bitrates in resRun:
                wr.writerow([bitrates])

def extractVPS(testName, numCLI):
    df = importDF(testName, numCLI, 'vps_all') # import the data
    vpsVals = []
    for cliNum in range(numCLI):
        filteredDF = filterDFTypeClient(df, 'DASHVideoPlaybackStatus', cliNum)
        videoStartTime = -1
        videoStopTime = -1
        stallVals = []
        if (len(filteredDF.columns)):
            col_no_vpsTS = df.columns.get_loc(filteredDF.columns[0])
            statusList = list(df.iloc[:,col_no_vpsTS+1].dropna())
            timesList = list(df.iloc[:,col_no_vpsTS].dropna())
            # print(statusList)
            # print(timesList)
            # print(colored('[   OK   ]', 'green'), end=' ')
            if statusList.count(1.0) >= 1 and statusList[-1] == 0.0:
                vstIndex = statusList.index(1.0)
                videoStartTime = timesList[vstIndex]
                videoStopTime = timesList[-1]
                # print("Video start: " + str(videoStartTime) + "; Video stop: " + str(videoStopTime) + "; Number of entries: " + str(len(statusList)))
                if statusList.count(1.0) > 1:
                    del timesList[0:vstIndex+1]
                    del statusList[0:vstIndex+1]
                    del timesList[-1]
                    del statusList[-1]
                    # print(timesList)
                    # print(statusList)
                    
                    while len(timesList) > 0:
                        # print(statusList)
                        stallEndIndex = statusList.index(1.0)
                        stallBeginIndex = statusList.index(0.0)
                        stallStartTime = timesList[stallBeginIndex]
                        stallStopTime = timesList[stallEndIndex]
                        del timesList[0:stallEndIndex+1]
                        del statusList[0:stallEndIndex+1]
                        stallDuration = stallStopTime - stallStartTime
                        # print("\tStalling -> Start: " + str(stallStartTime) + "; End: " + str(stallStopTime) + "; Duration: " + str(stallDuration))
                        stallVals.append([stallStartTime, stallStopTime, stallDuration])
                print(colored('[   OK   ]', 'green'), end=' ')
            else:    
                print(colored('[ NV VID ]', 'red'), end=' ')     
        else:
            print(colored('[ NO VAL ]', 'red'), end=' ')
        vpsVals.append([videoStartTime, videoStopTime, stallVals])
        print("VBR values for client " + str(cliNum) + ": " + str([videoStartTime, videoStopTime, stallVals]))
    print("In " + testName + " with " + str(numCLI) + " clients extracted " + str(len(vpsVals)) + " elements")
    return vpsVals #[[videoStartTime, videoStopTime, [[stallStartTime, stallStopTime, stallDuration]]]]

# Get all Video Bitrate values from a simulation scenario
def exportVPSValuesToCsv(testName, numCLIs):
    for numCLI in numCLIs:
        resRun = extractVPS(testName, numCLI)
        # print(resRun)
        filename = '../exports/vpsValues/' + str(testName) + '_' + str(numCLI) + '.csv'
        with open(filename, 'w', newline='') as myfile:
            wr = csv.writer(myfile)
            wr.writerow(["Video Start Time","Video Stop Time","Stallings"])
            for vps in resRun:
                wr.writerow(vps)

def extractMultiMOS(testName, numCLI):
    df = importDF(testName, numCLI, 'mos_all') # import the data
    mosVals = []
    for cliNum in range(int(str(numCLI).split('_')[0])):
        filteredDF = filterDFTypeClient(df, 'mos', cliNum)
        mosValue = 1
        if (len(filteredDF.columns)):
            col_no_mosTS = df.columns.get_loc(filteredDF.columns[0])
            # print(df.iloc[:,col_no_mosTS+1].tolist())
            mosValue = df.iloc[:,col_no_mosTS+1].dropna().tolist()
            print(colored('[   OK   ]', 'green'), end=' ')
        else:
            print(colored('[ NO VAL ]', 'red'), end=' ')
        mosVals.extend(mosValue)
        print("Mos value for client " + str(cliNum) + ": " + str(mosValue))
    return mosVals

# Get all MOS values from a simulation scenario
def exportMultiMOSValuesToCsv(testName, numCLIs):
    for numCLI in numCLIs:
        resRun = extractMultiMOS(testName, numCLI)
        # print(resRun)
        filename = '../exports/mosValues/' + str(testName) + '_' + str(numCLI) + '.csv'
        with open(filename, 'w') as myfile:
            wr = csv.writer(myfile)
            wr.writerow(["MOS Value"])
            for mosVal in resRun:
                wr.writerow([mosVal])

def extractMultiMOSperCli(testName, numCLI):
    df = importDF(testName, numCLI, 'mos_all') # import the data
    mosVals = []
    for cliNum in range(int(str(numCLI).split('_')[0])):
        filteredDF = filterDFTypeClient(df, 'mos', cliNum)
        mosValue = 1
        if (len(filteredDF.columns)):
            col_no_mosTS = df.columns.get_loc(filteredDF.columns[0])
            # print(df.iloc[:,col_no_mosTS+1].tolist())
            mosValue = df.iloc[:,col_no_mosTS+1].dropna().tolist()
            print(colored('[   OK   ]', 'green'), end=' ')
        else:
            print(colored('[ NO VAL ]', 'red'), end=' ')
        mosVals.append(mosValue)
        print("Mos value for client " + str(cliNum) + ": " + str(mosValue))
    print(mosVals)
    return mosVals

# Get all MOS values from a simulation scenario
def exportMultiMOSValuesperCliToCsv(testName, numCLIs):
    for numCLI in numCLIs:
        resRun = extractMultiMOSperCli(testName, numCLI)
        # print(resRun)
        filename = '../exports/mosValues/' + str(testName) + '_' + str(numCLI) + '.csv'
        with open(filename, 'w') as myfile:
            wr = csv.writer(myfile)
            wr.writerow(["MOS Value"])
            for mosVal in resRun:
                wr.writerow([mosVal])

## Testing
# extractMOS("tcpVideoClientTestV3a", 300)
# extractVBRs("tcpVideoClientTestV3a", 300)
# extractVPS("tcpVideoClientTestV3a", 300)

### For TCP Video Client ###

# exportMOSValuesToCsv("tcpVideoClientTestV3a", [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,240,250,260,270,280,290,300])
# exportMOSValuesToCsv("tcpVideoClientTestV3b", [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,240,250,260,270,280,290,300])

# exportVBRValuesToCsv("tcpVideoClientTestV3a", [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,240,250,260,270,280,290,300])
# exportVBRValuesToCsv("tcpVideoClientTestV3b", [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,240,250,260,270,280,290,300])

# exportVPSValuesToCsv("tcpVideoClientTestV3a", [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,240,250,260,270,280,290,300])
# exportVPSValuesToCsv("tcpVideoClientTestV3b", [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,240,250,260,270,280,290,300])

# exportThroughputsPerSecondToCsv("tcpVideoClientTestV3a", [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,240,250,260,270,280,290,300])
# exportThroughputsPerSecondToCsv("tcpVideoClientTestV3b", [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,240,250,260,270,280,290,300])

# exportMOSValuesToCsv("fileDownloadClientTest", [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40])
# exportMOSValuesToCsv("fileDownloadClientTest_ext1", [60,80,100])
# exportThroughputsPerSecondToCsv("fileDownloadClientTest", [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40])
# exportThroughputsPerSecondToCsv("fileDownloadClientTest_ext1", [60,80,100])

# tempNumCLIList = []
# for numCli in [1,50]:
#     for delay in [10,100,1000,10000,100000,1000000,2000000,3000000,4000000,5000000,6000000,7000000,8000000,9000000,10000000,11000000,12000000,13000000,14000000,15000000,16000000,17000000,18000000,19000000,20000000,30000000,40000000,50000000,60000000,70000000,80000000,90000000,100000000,200000000,300000000,400000000,500000000,600000000,700000000,800000000,900000000,1000000000]:
#         tempNumCLIList.append(str(numCli) + "_" + str(delay))
# exportMultiMOSValuesToCsv("sshClientTestV3", tempNumCLIList)
# exportThroughputsPerSecondToCsv("sshClientTestV3", tempNumCLIList)
# extractMultiMOS("sshClientTestV3", '50_100')

# tempNumCLIList = []
# for numCli in [1,50]:
#     for delay in [10,100,1000,10000,100000,1000000,2000000,3000000,4000000,5000000,6000000,7000000,8000000,9000000,10000000,11000000,12000000,13000000,14000000,15000000,16000000,17000000,18000000,19000000,20000000,30000000,40000000,50000000,60000000,70000000,80000000,90000000,100000000,200000000,300000000,400000000,500000000,1000000000]:
#         tempNumCLIList.append(str(numCli) + "_" + str(delay))
# exportMultiMOSValuesToCsv("voipCliSrvTestV2", tempNumCLIList)
# exportThroughputsPerSecondToCsv("voipCliSrvTestV2", tempNumCLIList)
# tempNumCLIList = []
# for numCli in [1,50]:
#     for delay in [600000000,700000000,800000000,900000000]:
#         tempNumCLIList.append(str(numCli) + "_" + str(delay))
# exportMultiMOSValuesToCsv("voipCliSrvTestV2_ext1", tempNumCLIList)
# exportThroughputsPerSecondToCsv("voipCliSrvTestV2_ext1", tempNumCLIList)


# exportMultiMOSValuesToCsv("voipCliSrvTest", [1,2,3,4,5,10,15,20,30,40,50,60,70,80,90,100,110])
# exportThroughputsPerSecondToCsv("voipCliSrvTest", [1,2,3,4,5,10,15,20,30,40,50,60,70,80,90,100,110])

# exportMultiMOSValuesToCsv("sshClientTest", [1,5,10,15,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300])
# exportMultiMOSValuesToCsv("sshClientTest_ext1", [1000,1500,2000,2500,3000,3500,4000])
# exportThroughputsPerSecondToCsv("sshClientTest", [1,5,10,15,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300])
# exportThroughputsPerSecondToCsv("sshClientTest_ext1", [1000,1500,2000,2500,3000,3500,4000])

# exportThroughputsPerSecondToCsv("baselineTest", [120])
exportMultiMOSValuesperCliToCsv("baselineTest", [120])