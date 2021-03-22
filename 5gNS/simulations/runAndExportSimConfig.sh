#!/bin/bash

helpFunction()
{
   echo ""
   echo "Will run a single run from a single config and ini file."
   echo "Usage: $0 -i iniFile -c config -t numThreads"
   echo -e "\t-i Omnet++ INI file containing the congfig to run"
   echo -e "\t-c Config for the scenario you want to run"
   echo -e "\t-s Number of slices in the scenario you want to run"
   exit 1 # Exit script after printing help
}

while getopts "i:c:s:" opt
do
   case "$opt" in
      i ) iniFile="$OPTARG" ;;
      c ) config="$OPTARG" ;;
      s ) slices="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$iniFile" ] || [ -z "$config" ] || [ -z "$slices" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

###### Run a single simulation config. Note: The config should only have one run here!!! ######
###### You may need to relink the paths depending on your machine!!!!! ######

### Marcin's Version ###
opp_runall -j1 -b1 opp_run ${iniFile} -u Cmdenv -c ${config} -l ../../../omnetpp-5.5.1/samples/inet4/src/INET -m -n .:../src:../../../omnetpp-5.5.1/samples/inet4/src:../../../omnetpp-5.5.1/samples/inet4/examples:../../../omnetpp-5.5.1/samples/inet4/tutorials:../../../omnetpp-5.5.1/samples/inet4/showcases

### INET Server Version ###
# opp_runall -j1 -b1 opp_run ${iniFile} -u Cmdenv -c ${config} -l /home/marcin/omnetpp-5.5.1/samples/inet4/src/INET -m -n .:../src:/home/marcin/omnetpp-5.5.1/samples/inet4/src:/home/marcin/omnetpp-5.5.1/samples/inet4/examples:/home/marcin/omnetpp-5.5.1/samples/inet4/tutorials:/home/marcin/omnetpp-5.5.1/samples/inet4/showcases

### Vagrant 1 ###
# opp_run ${iniFile} -u Cmdenv -c ${config} -m -n .:../src:../../../../inet4/src:../../../../inet4/examples:../../../../inet4/tutorials:../../../../inet4/showcases -l ../../../../inet4/src/INET 2>&1 | tee  ${config}.txt # Vagrant 1

### Vagrant 2 ###
# opp_runall -j1 -b1 opp_run ${iniFile} -u Cmdenv -c ${config} -m -n .:../src:../../../../../inet4/src:../../../../../inet4/examples:../../../../../inet4/tutorials:../../../../../inet4/showcases -l ../../../../../inet4/src/INET 2>&1 | tee ${config}.txt # Vagrant 2

### Vagrant 3 ###
# opp_runall -j1 -b1 opp_run ${iniFile} -u Cmdenv -c ${config} -m -n .:../src:../../../../../inet4/src:../../../../../inet4/examples:../../../../../inet4/tutorials:../../../../../inet4/showcases -l ../../../../../inet4/src/INET 2>&1 | tee ${config}.txt # Vagrant 2

###### Export results from OMNet++ to csv ######
cd results
./export_results_individual_NS.sh -f 0 -l 0 -r ${slices} -s ${config} -o ../../../analysis/${config} -t ${config} -d ${config}
### Export some queue scalars as well ###
./export_results_individual_NS_onlyR1Queues.sh -f 0 -l 0 -r ${slices} -s ${config} -o ../../../analysis/${config} -t ${config} -d ${config}

###### Extract necessary information from the csv's ######
cd ../../../analysis/${config}
name=$(ls)
cd ../code
python3 parseResNE.py ${config} ${slices} ${name} # Extract required information from the scavetool csv's
# Fix possibly broken MOS scores of VoD, Live and SSH (Which are calculated using python scripts during simulation. These scripts may randomly fail...)
cd sshMOScalcFiles/code
python3 recalcQoE.py ${config} ${name} # First take care of SSH
cd ../../videoMOScalcFiles/code 
python3 recalcQoE.py ${config} ${name} # Now take care of both video clients
cd ../..
python3 remakeMOSexports.py ${config} ${name} # Remake the mos results to include recalculated values
# python3 parseResInvestigation.py ${config} ${slices} ${name}

###### Plot basic plots ######
python3 plotResNE.py ${config} ${slices} ${name} # Plot everything
# python3 plotResInvestigation.py ${config} ${slices} ${name} # Plot everything

echo "Simulation, exports and initial plots are complete for ${config}";