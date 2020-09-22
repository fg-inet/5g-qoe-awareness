# Evaluating the Benefits of Network Slicing for QoE-awareness in 5G Networks

Git repository which includes:
1. The Omnet++ Project for simulations with and without approximated network slicing
2. Additional files for the INET framework that include all applications used in the simulation
3. Scripts for export and evaluation of simulated data - without any documentation
4. Scripts for the optimization algorithm which include some inline documentation

Requirements for Omnet++ simulation:
1. Omnet++ version 5.5.1 - download here: https://omnetpp.org/download/old
2. INET framework version 4.2.0 - download here: https://inet.omnetpp.org/Download.html
3. Python 3.6.9 - Tested with this version

Installation steps (list may be incomplete):
1. Download and Compile Omnet++ - follow the guide https://doc.omnetpp.org/omnetpp/InstallGuide.pdf
2. Download, unzip and copy the INET framework to the samples folder of Omnet++
3. Merge the inetCorrections/inet4 folder into the inet4 folder that you copied in step 2
4. Compile the INET framework. You can do that by:
  1. Running the Omnet++ IDE. You need to change into main Omnet++ directory, type in '. setenv' and then type omnetpp
  2. Go to File -> Import -> choose "Existing Projects into Workspace" -> browse for the inet4 project in the Omnet++ samples folder -> hit finish
  3. Right-click the inet4 project in project explorer and select "build project". This should compile the framework
  4. You can also compile the framework from console. To do that look at the INSTALL textfile you'll find in the INET folder.
 
To run the simulation from IDE open an INI file from 5gNS folder (baselineTest.ini should be a safe first bet) in Omnet++ IDE and click the green run button. When the simulation starts a configuration can be selected. For the first run, I reccomend using the "baselineTestTemp" configuration which will start a simulation with 10 clients for each of VoIP, SSH, VoD, live video and file download applications.

For questions contact Marcin: marcin.l.bosk@campus.tu-berlin.de
