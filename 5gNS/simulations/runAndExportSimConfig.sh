#!/bin/bash

helpFunction()
{
   echo ""
   echo "Will run a single run from a single config and ini file."
   echo "Usage: $0 -i iniFile -c config -t numThreads"
   echo -e "\t-i Omnet++ INI file containing the congfig to run"
   echo -e "\t-c Config for the scenario you want to run"
   echo -e "\t-s Number of slices in the scenario you want to run"
#    echo -e "\t-t Number of threads to paralellize the simulation"
   exit 1 # Exit script after printing help
}

while getopts "i:c:s:" opt
do
   case "$opt" in
      i ) iniFile="$OPTARG" ;;
      c ) config="$OPTARG" ;;
      s ) slices="$OPTARG" ;;
    #   t ) numThreads="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$iniFile" ] || [ -z "$config" ] || [ -z "$slices" ] #|| [ -z "$numThreads" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

opp_runall -j1 -b1 opp_run ${iniFile} -u Cmdenv -c ${config} -l ../../../omnetpp-5.5.1/samples/inet4/src/INET -m -n .:../src:../../../omnetpp-5.5.1/samples/inet4/src:../../../omnetpp-5.5.1/samples/inet4/examples:../../../omnetpp-5.5.1/samples/inet4/tutorials:../../../omnetpp-5.5.1/samples/inet4/showcases

cd results
./export_results_individual_NS.sh -f 0 -l 0 -r ${slices} -s ${config} -o ../../../analysis/${config} -t ${config} -d ${config}

cd ../../../analysis/${config}
name=$(ls)
cd ../code
python3 parseResNE.py ${config} ${slices} ${name}
python3 plotResNE.py ${config} ${slices} ${name}

echo "Simulation and exports are complete for ${config}";