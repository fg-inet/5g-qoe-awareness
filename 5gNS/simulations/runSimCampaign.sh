#!/bin/bash

helpFunction()
{
   echo ""
   echo "Usage: $0 -i iniFile -c config -t numThreads"
   echo -e "\t-i Omnet++ INI file containing the congfig to run"
   echo -e "\t-c Config for the scenario you want to run"
   echo -e "\t-t Number of threads to paralellize the simulation"
   exit 1 # Exit script after printing help
}

while getopts "i:c:t:" opt
do
   case "$opt" in
      i ) iniFile="$OPTARG" ;;
      c ) config="$OPTARG" ;;
      t ) numThreads="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$iniFile" ] || [ -z "$config" ] || [ -z "$numThreads" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

opp_runall -j${numThreads} -b1 opp_run ${iniFile} -u Cmdenv -c ${config} -l ../../../omnetpp-5.5.1/samples/inet4/src/INET -m -n .:../src:../../../omnetpp-5.5.1/samples/inet4/src:../../../omnetpp-5.5.1/samples/inet4/examples:../../../omnetpp-5.5.1/samples/inet4/tutorials:../../../omnetpp-5.5.1/samples/inet4/showcases
# opp_runall -j7 -b1 opp_run simpleNHost1ServerLinkUtilizationTest.ini -u Cmdenv -c voipCliSrvTestV2 -l ../../../../../installs/omnetpp-5.5.1/samples/inet4/src/INET -m -n .:../src:../../../../../installs/omnetpp-5.5.1/samples/inet4/src:../../../../../installs/omnetpp-5.5.1/samples/inet4/examples:../../../../../installs/omnetpp-5.5.1/samples/inet4/tutorials:../../../../../installs/omnetpp-5.5.1/samples/inet4/showcases -r $setDelay>9000000
# opp_runall -j7 -b1 opp_run simpleNHost1ServerLinkUtilizationTest.ini -u Cmdenv -c sshClientTestV3 -l ../../../../../installs/omnetpp-5.5.1/samples/inet4/src/INET -m -n .:../src:../../../../../installs/omnetpp-5.5.1/samples/inet4/src:../../../../../installs/omnetpp-5.5.1/samples/inet4/examples:../../../../../installs/omnetpp-5.5.1/samples/inet4/tutorials:../../../../../installs/omnetpp-5.5.1/samples/inet4/showcases -r0..41
