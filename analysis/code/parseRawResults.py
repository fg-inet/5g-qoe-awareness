import pandas
import csv
import statistics
from termcolor import colored

maxSimTime = 400
DEBUG = 0

downlink = ['Downlink', 'rxPkOk:vector(packetBytes)']
uplink = ['Uplink', 'txPk:vector(packetBytes)']

def importDF(testName, numCLI, nodeIdent):
    # File that will be read
    fullScenarioName = str(testName) + '_' + str(numCLI)
    file_to_read = '../' + str(testName) + '/' + fullScenarioName + '/vectors/' + fullScenarioName + '_' + str(nodeIdent) + '_vec.csv'
    print("Results from run: " + file_to_read)
    # Read the CSV
    return pandas.read_csv(file_to_read)

def filterDFType(df, filterType):
    return df.filter(like=filterType)

def getFilteredDFtypeAndTS(df, filterType):
    filteredDF = filterDFType(df, filterType)
    if len(filteredDF.columns):
        colNoTS = df.columns.get_loc(df.filter(filteredDF).columns[0])
        return df.iloc[:,[colNoTS,colNoTS+1]].dropna()
    else:
        return pandas.DataFrame(columns=['ts', 'tp'])

def calculateThrougputPerSecondDirection(df, direction, nodeIdent):
    dirDF = getFilteredDFtypeAndTS(df, direction[1])
    # print(dirDF)
    dirDF = dirDF.rename(columns={str(dirDF.columns[0]) : "ts", str(dirDF.columns[1]) : "bytes"})
    tB = [0,1] # time bounds for calculation
    colName = direction[0] + ' Throughput ' + nodeIdent
    tpDirDF = pandas.DataFrame(columns=[colName])
    while tB[1] <= maxSimTime:
        if DEBUG: print(tB, end =" -> Throughput: ")
        throughput = dirDF.loc[(dirDF['ts'] > tB[0]) & (dirDF['ts'] <= tB[1])]["bytes"].sum()
        tpDirDF = tpDirDF.append({colName : throughput*8/1000}, ignore_index=True)
        if DEBUG: print(throughput*8/1000, end=" kbps\n")
        tB = [x+1 for x in tB]
    # print(tpDirDF.columns)
    return tpDirDF

def extractNodeThroughputDirection(testName, numCLI, nodeIdent, direction):
    nodeDF = importDF(testName,numCLI,nodeIdent)
    return calculateThrougputPerSecondDirection(nodeDF, direction, nodeIdent)

# extractNodeThroughputDirection('baselineTest', 120, 'cli100', uplink)

def extractAllThroughputsDirection(testName, numCLI, direction):
    nodeIdents = []
    nodeIdents.append('link')
    tpDFall = pandas.DataFrame()
    for i in range(numCLI):
        nodeIdents.append('cli'+str(i))
    for nodeIdent in nodeIdents:
        tpDFall = pandas.concat([tpDFall,extractNodeThroughputDirection(testName, numCLI, nodeIdent,direction)],axis=1,ignore_index=False)

    tpDFall.to_csv(path_or_buf='../exports/extracted/throughputs/'+str(testName)+'_'+str(numCLI)+'_'+direction[0]+'.csv')


def extractNodeMOS(testName, numCLI, nodeIdent):
    nodeDF = importDF(testName,numCLI,nodeIdent)
    mosDF = getFilteredDFtypeAndTS(nodeDF,'mos')
    mosDF = mosDF.rename(columns={str(mosDF.columns[0]) : nodeIdent+" Mos TS", str(mosDF.columns[1]) : nodeIdent+" Mos Val"})
    # print(mosDF)
    return mosDF

def extractAllMOS(testName, numCLI):
    nodeIdents = []
    mosDFall = pandas.DataFrame()
    for i in range(numCLI):
        nodeIdents.append('cli'+str(i))
    for nodeIdent in nodeIdents:
        mosDFall = pandas.concat([mosDFall,extractNodeMOS(testName, numCLI, nodeIdent)],axis=1,ignore_index=False)
    
    mosDFall.to_csv(path_or_buf='../exports/extracted/mos/'+str(testName)+'_'+str(numCLI)+'.csv')

def extractNodeRTT(testName, numCLI, nodeIdent):
    nodeDF = importDF(testName,numCLI,nodeIdent)
    rttDF = getFilteredDFtypeAndTS(nodeDF,'roundTripTime')
    rttDF = rttDF.rename(columns={str(rttDF.columns[0]) : nodeIdent+" RTT TS", str(rttDF.columns[1]) : nodeIdent+" RTT Val"})
    return rttDF

def extractRTT(testName, numCLI, range):
    nodeIdents = []
    rttDFall = pandas.DataFrame()
    for i in range:
        nodeIdents.append('cli'+str(i))
    for nodeIdent in nodeIdents:
        rttDFall = pandas.concat([rttDFall,extractNodeRTT(testName, numCLI, nodeIdent)],axis=1,ignore_index=False)
    
    rttDFall.to_csv(path_or_buf='../exports/extracted/rtt/'+str(testName)+'_'+str(numCLI)+'.csv')
    
def extractNodeE2ED(testName, numCLI, nodeIdent):
    nodeDF = importDF(testName,numCLI,nodeIdent)
    e2edDF = getFilteredDFtypeAndTS(nodeDF,'endToEndDelay')
    e2edDF = e2edDF.rename(columns={str(e2edDF.columns[0]) : nodeIdent+" E2ED TS", str(e2edDF.columns[1]) : nodeIdent+" E2ED Val"})
    return e2edDF

def extractE2ED(testName, numCLI, range):
    nodeIdents = []
    e2edDFall = pandas.DataFrame()
    for i in range:
        nodeIdents.append('cli'+str(i))
    for nodeIdent in nodeIdents:
        e2edDFall = pandas.concat([e2edDFall,extractNodeE2ED(testName, numCLI, nodeIdent)],axis=1,ignore_index=False)
    
    e2edDFall.to_csv(path_or_buf='../exports/extracted/e2ed/'+str(testName)+'_'+str(numCLI)+'.csv')

def extractRTO(testName, numCLI, serverIdent):
    nodeDF = importDF(testName, numCLI, serverIdent)
    # print(nodeDF)
    filteredDF = filterDFType(nodeDF, 'RTO ')
    rtos = []
    colTSList = nodeDF.filter(filteredDF).columns
    for col in colTSList:
        colNoTS = nodeDF.columns.get_loc(col)
        rtos.extend(nodeDF.iloc[:,colNoTS+1].dropna().tolist())
    # print(rtos)
    # print(nodeDF.filter(filteredDF).columns[0])
    filteredDFnumSes = filterDFType(nodeDF, 'advertised window')
    numSession = len(list(filteredDFnumSes))
    print('Total Number of sessions at the SSH server: ' + str(numSession))
    filteredDF2 = filterDFType(nodeDF, 'RTOs ')
    # print(list(filteredDF2))
    numSessionWithRTO = len(list(filteredDF2))
    print('Number of sessions at the SSH server where at least one retransmission timeout occured: ' + str(numSessionWithRTO))

    with open('../exports/extracted/rto/'+str(testName)+'_'+str(numCLI)+'.csv', mode='w') as writeFile:
        fw = csv.writer(writeFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        fw.writerow(rtos)
        fw.writerow([numSession])
        fw.writerow([numSessionWithRTO])

def extractNodePkLossRate(testName, numCLI, nodeIdent):
    nodeDF = importDF(testName,numCLI,nodeIdent)
    pklrDF = getFilteredDFtypeAndTS(nodeDF,'packetLossRate')
    pklrDF = pklrDF.rename(columns={str(pklrDF.columns[0]) : nodeIdent+" PkLR TS", str(pklrDF.columns[1]) : nodeIdent+" PkLR Val"})
    return pklrDF

def extractPkLossRate(testName, numCLI, range):
    nodeIdents = []
    pklrDFall = pandas.DataFrame()
    for i in range:
        nodeIdents.append('cli'+str(i))
    for nodeIdent in nodeIdents:
        pklrDFall = pandas.concat([pklrDFall,extractNodePkLossRate(testName, numCLI, nodeIdent)],axis=1,ignore_index=False)
    
    pklrDFall.to_csv(path_or_buf='../exports/extracted/pklr/'+str(testName)+'_'+str(numCLI)+'.csv')

# extractRTO('baselineTestSSHrto', 120, 'server2')

def extractAll(testName, numCLI):
    extractAllThroughputsDirection(testName, numCLI, downlink)
    extractAllThroughputsDirection(testName, numCLI, uplink)
    extractAllMOS(testName, numCLI)
    appCli = int(numCLI/3)
    # extractRTT(testName, numCLI, range(2*appCli,3*appCli,1))
    # extractE2ED(testName, numCLI, range(3*appCli,4*appCli,1))
    # extractPkLossRate(testName, numCLI, range(3*appCli,4*appCli,1))
    extractE2ED(testName, numCLI, range(2*appCli,3*appCli,1))
    extractPkLossRate(testName, numCLI, range(2*appCli,3*appCli,1))
    # extractRTT(testName, numCLI, [0])
    # extractRTO(testName, numCLI, 'server2')

# extractAllThroughputsDirection('baselineTest', 120, downlink)
# extractAllThroughputsDirection('baselineTest', 120, uplink)
# extractAllMOS('baselineTest', 120)

# extractAllThroughputsDirection('baselineTestNo2', 100, downlink)
# extractAllThroughputsDirection('baselineTestNo2', 100, uplink)
# extractAllMOS('baselineTestNo2', 100)

# extractAllThroughputsDirection('baselineTestNo3', 80, downlink)
# extractAllThroughputsDirection('baselineTestNo3', 80, uplink)
# extractAllMOS('baselineTestNo3', 80)

# extractAllThroughputsDirection('baselineTestNo3newFDconfig', 80, downlink)
# extractAllThroughputsDirection('baselineTestNo3newFDconfig', 80, uplink)
# extractAllMOS('baselineTestNo3newFDconfig', 80)

# extractAllThroughputsDirection('baselineTestNo3newFDlongerVid', 80, downlink)
# extractAllThroughputsDirection('baselineTestNo3newFDlongerVid', 80, uplink)
# extractAllMOS('baselineTestNo3newFDlongerVid', 80)

# extractAllThroughputsDirection('baselineTestNo3newFDlongRecVid30App', 120, downlink)
# extractAllThroughputsDirection('baselineTestNo3newFDlongRecVid30App', 120, uplink)
# extractAllMOS('baselineTestNo3newFDlongRecVid30App', 120)
# extractRTT('baselineTestNo3newFDlongRecVid30App', 120, range(60,90,1))

# extractAllThroughputsDirection('baselineTestNo3newFDlongRecVid30AppShortRecon', 120, downlink)
# extractAllThroughputsDirection('baselineTestNo3newFDlongRecVid30AppShortRecon', 120, uplink)
# extractAllMOS('baselineTestNo3newFDlongRecVid30AppShortRecon', 120)
# extractRTT('baselineTestNo3newFDlongRecVid30AppShortRecon', 120, range(60,90,1))
# extractE2ED('baselineTestNo3newFDlongRecVid30AppShortRecon', 120, range(90,120,1))
# extractAll('baselineTestNo3newFDlong300sVid30AppShortRecon', 120)
# extractAll('baselineTestNo3newFDlong300sVid30AppShortReconVarDel_10ns', 120)
# extractAll('baselineTestNo3newFDlong300sVid30AppShortReconVarDel_100ns', 120)
# extractAll('baselineTestNo3newFDlong300sVid30AppShortReconVarDel_10ms', 120)
# extractAll('baselineTestNo3newFDlong300sVid30AppShortReconVarDel_100ms', 120)

# extractAll('baselineTestDelayAnalysis_100ms', 120)
# extractAll('baselineTestDelayAnalysis_10ms', 120)
# extractAll('baselineTestDelayAnalysis_100us', 120)
# extractAll('baselineTestDelayAnalysis_10us', 120)
# extractAll('baselineTest30App300sVid', 120)
# extractAll('baselineTest30App100sVid', 120)
# extractAll('baselineTestSSHstaggeredStart300ms', 120)
# extractAll('baselineTestSSHmultiServApp', 120)
# extractAll('baselineTestSSHrto', 120)

# extractAll('baselineTest10', 40)
# extractAll('baselineTest20', 80)
# extractAll('baselineTest30', 120)
# extractAll('baselineTest40', 160)
# extractAll('baselineTest50', 200)

# extractAll('baselineTestNoVoIP10', 30)
# extractAll('baselineTestNoVoIP20', 60)
# extractAll('baselineTestNoVoIP30', 90)
# extractAll('baselineTestNoVoIP40', 120)
# extractAll('baselineTestNoVoIP50', 150)

extractAll('baselineTestNoSSH10', 30)
extractAll('baselineTestNoSSH20', 60)
extractAll('baselineTestNoSSH30', 90)
extractAll('baselineTestNoSSH40', 120)
extractAll('baselineTestNoSSH50', 150)

# extractAll('baselineTestSSHfd', 6)
# extractAll('baselineTestSSHfd', 11)
# extractAll('baselineTestSSHfd', 21)
# extractAll('baselineTestSSHfd', 31)
# extractAll('baselineTestSSHfd', 41)
# extractAll('baselineTestSSHfd', 51)

# extractAll('baselineTestSSHvid', 6)
# extractAll('baselineTestSSHvid', 11)
# extractAll('baselineTestSSHvid', 21)
# extractAll('baselineTestSSHvid', 31)
# extractAll('baselineTestSSHvid', 41)
# extractAll('baselineTestSSHvid', 51)