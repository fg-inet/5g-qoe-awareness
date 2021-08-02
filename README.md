# Using 5G QoS Mechanisms to Achieve QoE-Aware Resource Allocation

Git repository which includes:
1. The Omnet++ Project for simulations with and without HTB-based QoS control and network slicing (`5gNS` folder)
2. Additional files for the INET framework that include all custom applications used in the simulation (`inetCorrections` folder)
3. Scripts for configuration generation for simulations used in the publication (in the `algorithm` folder)
5. Configurations for Experiments run for the "Using 5G QoS Mechanisms to Achieve QoE-Aware Resource Allocation" publication. (in `5gNS/simulations` folder and its subfolders)
6. Some scripts used to calculate the MOS of VoD, Live, and SSH applications (in the `postProcessingMOS` folder)

Requirements for Omnet++ simulation:
1. Omnet++ version 5.5.1 - download here: https://omnetpp.org/download/old
2. INET framework version 4.2.0 - download here: https://inet.omnetpp.org/Download.html
3. Python 3.6.9 - Tested with this version. Probably fine with other versions as well

Installation steps (list may be incomplete):
1. Download and Compile Omnet++ - follow the guide https://doc.omnetpp.org/omnetpp/InstallGuide.pdf
2. Download, unzip and copy the INET framework to the samples folder of Omnet++
3. Merge the `inetCorrections/inet4` folder into the inet4 folder that you copied in step 2
4. Compile the INET framework. You can do that by:
  1. Running the Omnet++ IDE. You need to change into main Omnet++ directory, type in `. setenv` and then type `omnetpp`
  2. Go to File -> Import -> choose "Existing Projects into Workspace" -> browse for the inet4 project in the Omnet++ samples folder -> hit finish
  3. Right-click the inet4 project in project explorer and select "build project". This should compile the framework
  4. You can also compile the framework from console. To do that look at the INSTALL textfile you'll find in the INET folder.
 
To run the simulation from IDE open an INI file from 5gNS folder (bestEffort.ini should be a safe first bet) in Omnet++ IDE and click the green run button. When the simulation starts a configuration can be selected. For the first run, I recommend using the `bestEffortAdmCon_R100_Q35_M100_C100` configuration which will start a simulation with clients for each of VoIP, SSH, VoD, live video and file download applications.

You can also use the `runAndExportSimConfig.sh` script present in the `5gNS/simulations` folder to run and immediately export simulation results.
