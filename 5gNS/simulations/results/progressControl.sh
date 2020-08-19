#!/bin/bash

helpFunction()
{
   echo ""
   echo "Usage: $0 -s simOutFile -i interval -t simTime"
   exit 1 # Exit script after printing help
}

while getopts "s:i:t:" opt
do
   case "$opt" in
      s ) simOutFile="$OPTARG" ;;
      i ) interval="$OPTARG" ;;
      t ) maxSimTime="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$simOutFile" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi
clear
tput cup 0 0
echo -e "Current progress of simulation $simOutFile:"
tput cup 2 7
echo -e "|---------------------------------------------------------------|"
tput cup 9 7
echo -e "|---------------------------------------------------------------|"

tput cup 3 71
echo -e "|"
tput cup 3 7
echo -e "|"
tput cup 4 71
echo -e "|"
tput cup 5 71
echo -e "|"
tput cup 6 71
echo -e "|"
tput cup 7 71
echo -e "|"
tput cup 8 71
echo -e "|"
tput cup 8 7
echo -e "|"
lastElapsed=0
while true
do
    tailOut=$( tail -3 $simOutFile | grep t= )
    breakThingy="$(cut -d' ' -f1 <<< $tailOut)"
    
    simTime=$(bc <<<"scale=2; $(cut -d'=' -f2 <<< $(cut -d' ' -f4 <<< $tailOut))")
    elapsed=$(bc <<<"scale=2; $(cut -d's' -f1 <<< $(cut -d' ' -f6 <<< $tailOut))")
    targetMulti=$(bc <<<"scale=2; $maxSimTime / $simTime")
    approxTotTime=$(bc <<<"scale=2; $elapsed * $targetMulti")
    timeLeft=$(bc <<<"scale=2; $approxTotTime - $elapsed")
    timeLeftMin=$(bc <<<"scale=2; $timeLeft / 60")
    tput cup 4 7
    echo -e "|  Time simulated: $simTime seconds (out of $maxSimTime seconds)"
    tput cup 5 7
    echo -e "|  Time elapsed: $elapsed seconds"
    tput cup 6 7
    echo -e "|  Time simulation will take (approx.): $approxTotTime seconds      "
    tput cup 7 7
    echo -e "|  Time left (approx.): $timeLeft seconds = $timeLeftMin minutes      "
    tput cup 10 0
    lastElapsed=$elapsed
    if [ "$breakThingy" != "**" ]; then
       clear
       tput cup 0 0
       echo -e "Simulation $simOutFile has finished"
       break
    fi

    sleep $interval
done