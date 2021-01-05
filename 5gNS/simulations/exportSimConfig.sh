#!/bin/bash

helpFunction()
{
   echo ""
   echo "Will run a single run from a single config and ini file."
   echo "Usage: $0 -i iniFile -c config -t numThreads"
   echo -e "\t-c Config for the scenario you want to run"
   echo -e "\t-s Number of slices in the scenario you want to run"
   exit 1 # Exit script after printing help
}

while getopts "c:s:" opt
do
   case "$opt" in
      c ) config="$OPTARG" ;;
      s ) slices="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$config" ] || [ -z "$slices" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

cd ../../analysis/${config}
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
python3 plotResNE.py ${config} ${slices} ${name} # Plot everything

echo "Exports are complete for ${config}";