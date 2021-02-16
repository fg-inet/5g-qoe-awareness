#!/bin/bash

helpFunction()
{
   echo ""
   echo "Usage: $0 -n numRuns -s sourceFolder -o resultsFolder -t resultsSubfolder -d experimentDescriptor"
   echo -e "\t-f Number of the first run to export"
   echo -e "\t-l Number of the first run to exports"
   echo -e "\t-r Number of slices in the experiment"
   echo -e "\t-s Folder which contains the source .vec and .sca files"
   echo -e "\t-o Destination folder"
   echo -e "\t-t Destination subfolder"
   echo -e "\t-d Descriptor of the experiment"
   exit 1 # Exit script after printing help
}

while getopts "f:l:r:s:o:t:d:" opt
do
   case "$opt" in
      f ) firstRun="$OPTARG" ;;
      l ) lastRun="$OPTARG" ;;
      r ) numSlices="$OPTARG" ;;
      s ) sourceFolder="$OPTARG" ;;
      o ) resultsFolder="$OPTARG" ;;
      t ) resultsSubfolder="$OPTARG" ;;
      d ) experimentDescriptor="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$firstRun" ] || [ -z "$lastRun" ] || [ -z "$sourceFolder" ] || [ -z "$resultsFolder" ] || [ -z "$resultsSubfolder" ] || [ -z "$experimentDescriptor" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

if [ -d "${sourceFolder}" ] 
then
    echo "Source directory ${sourceFolder} exists. Continuing..." 
else
    echo "Error: Source directory ${sourceFolder} does not exist. Quitting..."
    exit 2
fi

if [ -d "${resultsFolder}" ] 
then
    echo "Results directory ${resultsFolder} exists. Continuing..." 
else
    echo "Results directory ${resultsFolder} does not exist. Creating the directory..."
    mkdir ${resultsFolder}
    if [ -d "${resultsFolder}" ] 
    then
        echo "Results directory ${resultsFolder} successfully created. Continuing..." 
    else
        echo "Error: Results directory ${resultsFolder} Couldn't be created. Quitting..."
        exit 3
    fi
fi

firstResult=0

for run_num in $(eval echo "{$firstRun..$lastRun}")
do
    nVID=$(perl -nle'print $& while m{(?<=nVID )[0-9]+}g' ${sourceFolder}/*-${run_num}.vci)
    nLVD=$(perl -nle'print $& while m{(?<=nLVD )[0-9]+}g' ${sourceFolder}/*-${run_num}.vci)
    nFDO=$(perl -nle'print $& while m{(?<=nFDO )[0-9]+}g' ${sourceFolder}/*-${run_num}.vci)
    nSSH=$(perl -nle'print $& while m{(?<=nSSH )[0-9]+}g' ${sourceFolder}/*-${run_num}.vci)
    nVIP=$(perl -nle'print $& while m{(?<=nVIP )[0-9]+}g' ${sourceFolder}/*-${run_num}.vci)

    lastVID=$(($nVID - 1))
    lastLVD=$(($nLVD - 1))
    lastFDO=$(($nFDO - 1))
    lastSSH=$(($nSSH - 1))
    lastVIP=$(($nVIP - 1))
    lastSlice=$(($numSlices - 1))

    totalNum=$(($nVID + $nFDO + $nSSH + $nVIP + $nLVD))

    echo "Total number of clients in run: $totalNum. This includes:"
    echo -e "\t- $nVID video clients"
    echo -e "\t- $nLVD live video clients"
    echo -e "\t- $nFDO file download clients"
    echo -e "\t- $nSSH SSH clients"
    echo -e "\t- $nVIP VoIP clients"

    subfolderName="${resultsSubfolder}_${totalNum}_VID${nVID}_LVD${nLVD}_FDO${nFDO}_SSH${nSSH}_VIP${nVIP}"
    echo "Subfolder name: $subfolderName"
    if [ -d "${resultsFolder}/${subfolderName}" ] 
    then
        echo "Vectors directory ${resultsFolder}/${subfolderName} exists. Continuing..." 
    else
        echo "Results directory ${resultsFolder}/${subfolderName} does not exist. Creating the directory..."
        mkdir ${resultsFolder}/${subfolderName}
        if [ -d "${resultsFolder}/${subfolderName}" ] 
        then
            echo "Results directory ${resultsFolder}/${subfolderName} successfully created. Continuing..." 
        else
            echo "Error: Results directory ${resultsFolder}/${subfolderName} Couldn't be created. Quitting..."
            exit 4
        fi
    fi
    
    if [ -d "${resultsFolder}/${subfolderName}/vectors" ] 
    then
        echo "Vectors directory ${resultsFolder}/${subfolderName}/vectors exists. Continuing..." 
    else
        echo "Results directory ${resultsFolder}/${subfolderName}/vectors does not exist. Creating the directory..."
        mkdir ${resultsFolder}/${subfolderName}/vectors
        if [ -d "${resultsFolder}/${subfolderName}/vectors" ] 
        then
            echo "Results directory ${resultsFolder}/${subfolderName}/vectors successfully created. Continuing..." 
        else
            echo "Error: Results directory ${resultsFolder}/${subfolderName}/vectors Couldn't be created. Quitting..."
            exit 4
        fi
    fi

    if [ -d "${resultsFolder}/${subfolderName}/scalars" ] 
    then
        echo "Vectors directory ${resultsFolder}/${subfolderName}/scalars exists. Continuing..." 
    else
        echo "Results directory ${resultsFolder}/${subfolderName}/scalars does not exist. Creating the directory..."
        mkdir ${resultsFolder}/${subfolderName}/scalars
        if [ -d "${resultsFolder}/${subfolderName}/scalars" ] 
        then
            echo "Results directory ${resultsFolder}/${subfolderName}/scalars successfully created. Continuing..." 
        else
            echo "Error: Results directory ${resultsFolder}/${subfolderName}/scalars Couldn't be created. Quitting..."
            exit 4
        fi
    fi
    
    echo "Exporting run $run_num which has $totalNum clients..."
    for sliNum in $(eval echo "{$firstResult..$lastSlice}")
    do
        # echo -e "\tExporting queues for router 0 and resource link $sliNum:\t\t\c"
        # scavetool export -f "module(*router0.ppp[$sliNum].ppp.queue*)"  -F CSV-S -o ${resultsFolder}/${subfolderName}/vectors/${experimentDescriptor}_${totalNum}_VID${nVID}_LVD${nLVD}_FDO${nFDO}_SSH${nSSH}_VIP${nVIP}_R0ral${sliNum}_vec.csv ${sourceFolder}/*-${run_num}.vec
        echo -e "\tExporting scalars for queues for router 0 and resource link $sliNum:\t\t\c"
        scavetool export -f "module(*router0.ppp[$sliNum].ppp.queue*)"  -F CSV-S -o ${resultsFolder}/${subfolderName}/scalars/${experimentDescriptor}_${totalNum}_VID${nVID}_LVD${nLVD}_FDO${nFDO}_SSH${nSSH}_VIP${nVIP}_R0ral${sliNum}_sca.csv ${sourceFolder}/*-${run_num}.sca
        # echo -e "\tExporting queues for router 1 and resource link $sliNum:\t\t\c"
        # scavetool export -f "module(*router1.ppp[$sliNum].ppp.queue*)"  -F CSV-S -o ${resultsFolder}/${subfolderName}/vectors/${experimentDescriptor}_${totalNum}_VID${nVID}_LVD${nLVD}_FDO${nFDO}_SSH${nSSH}_VIP${nVIP}_R1ral${sliNum}_vec.csv ${sourceFolder}/*-${run_num}.vec
        echo -e "\tExporting scalars for queues for router 1 and resource link $sliNum:\t\t\c"
        scavetool export -f "module(*router1.ppp[$sliNum].ppp.queue*)"  -F CSV-S -o ${resultsFolder}/${subfolderName}/scalars/${experimentDescriptor}_${totalNum}_VID${nVID}_LVD${nLVD}_FDO${nFDO}_SSH${nSSH}_VIP${nVIP}_R1ral${sliNum}_sca.csv ${sourceFolder}/*-${run_num}.sca
    done
    # scavetool export -f "(module(*router0.ppp[0]*) AND name(*xPk*)) OR (module(*router0.ppp[1]*) AND name(*xPk*)) OR (module(*router0.ppp[2]*) AND name(*xPk*)) OR (module(*router0.ppp[3]*) AND name(*xPk*))"  -F CSV-S -o ${resultsFolder}/${subfolderName}/vectors/${experimentDescriptor}_${totalNum}_VID${nVID}_FDO${nFDO}_SSH${nSSH}_VIP${nVIP}_links_vec.csv ${sourceFolder}/*-${run_num}.vec
    # echo -e "\tExporting for server serverSSH:\t\t\c"
    # scavetool export -f "(module(*serverSSH*) AND name(*RTO*)) OR (module(*serverSSH*) AND name(*advertised*))" -F CSV-S -o ${resultsFolder}/${subfolderName}/vectors/${experimentDescriptor}_${totalNum}_VID${nVID}_LVD${nLVD}_FDO${nFDO}_SSH${nSSH}_VIP${nVIP}_serverSSH_vec.csv ${sourceFolder}/*-${run_num}.vec
    # echo -e "\tExporting for router0:\t\t\c"
    # scavetool export -f "module(*router0.ppp[0]*)"  -F CSV-S -o ${resultsFolder}/${subfolderName}/vectors/${experimentDescriptor}_${totalNum}_VID${nVID}_LVD${nLVD}_FDO${nFDO}_SSH${nSSH}_VIP${nVIP}_router0_vec.csv ${sourceFolder}/*-${run_num}.vec
    # echo -e "\tExporting for router1:\t\t\c"
    # scavetool export -f "module(*router1.ppp[0]*)"  -F CSV-S -o ${resultsFolder}/${subfolderName}/vectors/${experimentDescriptor}_${totalNum}_VID${nVID}_LVD${nLVD}_FDO${nFDO}_SSH${nSSH}_VIP${nVIP}_router1_vec.csv ${sourceFolder}/*-${run_num}.vec
    
    # for cli_num in $(eval echo "{$firstResult..$lastVID}")
    # do
    #     echo -e "\tExporting for video client $cli_num:\t\t\c"
    #     scavetool export -f "module(*hostVID[$cli_num]*)"  -F CSV-S -o ${resultsFolder}/${subfolderName}/vectors/${experimentDescriptor}_${totalNum}_VID${nVID}_LVD${nLVD}_FDO${nFDO}_SSH${nSSH}_VIP${nVIP}_hostVID${cli_num}_vec.csv ${sourceFolder}/*-${run_num}.vec
    # done
    # for cli_num in $(eval echo "{$firstResult..$lastLVD}")
    # do
    #     echo -e "\tExporting for live video client $cli_num:\t\t\c"
    #     scavetool export -f "module(*hostLVD[$cli_num]*)"  -F CSV-S -o ${resultsFolder}/${subfolderName}/vectors/${experimentDescriptor}_${totalNum}_VID${nVID}_LVD${nLVD}_FDO${nFDO}_SSH${nSSH}_VIP${nVIP}_hostLVD${cli_num}_vec.csv ${sourceFolder}/*-${run_num}.vec
    # done
    # for cli_num in $(eval echo "{$firstResult..$lastFDO}")
    # do
    #     echo -e "\tExporting for file download client $cli_num:\t\c"
    #     scavetool export -f "module(*hostFDO[$cli_num]*)"  -F CSV-S -o ${resultsFolder}/${subfolderName}/vectors/${experimentDescriptor}_${totalNum}_VID${nVID}_LVD${nLVD}_FDO${nFDO}_SSH${nSSH}_VIP${nVIP}_hostFDO${cli_num}_vec.csv ${sourceFolder}/*-${run_num}.vec
    # done
    # for cli_num in $(eval echo "{$firstResult..$lastSSH}")
    # do
    #     echo -e "\tExporting for SSH client $cli_num:\t\t\c"
    #     scavetool export -f "module(*hostSSH[$cli_num]*)"  -F CSV-S -o ${resultsFolder}/${subfolderName}/vectors/${experimentDescriptor}_${totalNum}_VID${nVID}_LVD${nLVD}_FDO${nFDO}_SSH${nSSH}_VIP${nVIP}_hostSSH${cli_num}_vec.csv ${sourceFolder}/*-${run_num}.vec
    # done
    # for cli_num in $(eval echo "{$firstResult..$lastVIP}")
    # do
    #     echo -e "\tExporting for VoIP client $cli_num:\t\t\c"
    #     scavetool export -f "module(*hostVIP[$cli_num]*)"  -F CSV-S -o ${resultsFolder}/${subfolderName}/vectors/${experimentDescriptor}_${totalNum}_VID${nVID}_LVD${nLVD}_FDO${nFDO}_SSH${nSSH}_VIP${nVIP}_hostVIP${cli_num}_vec.csv ${sourceFolder}/*-${run_num}.vec
    # done

done

echo -e "Exports complete :)"
