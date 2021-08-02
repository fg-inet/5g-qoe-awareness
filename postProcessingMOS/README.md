# Using 5G QoS Mechanisms to Achieve QoE-Aware Resource Allocation

## MOS post-processing

!NOTE!: These scripts are just an example on how to use the MOS calculation!!

You can use them to calculate MOS of VoD, Live and SSH clients.

### SSH
Go to `sshMOScalcFiles/code` folder. There you can run `python3 recalcQoE.py <config> <name>` script to calculate the MOS of SSH. `<config>` is the name of "Config" from the OMNeT++ ini file. `<name>` is the name of the export folder of the experiment run (e.g. `qosFlowsV55SlicesHTB_R100_Q35_M100_C100_105_VID42_LVD21_FDO5_SSH5_VIP32`).

IMPORTANT: You may need to adjust the path in `importDF` function to fit your system!

The MOS calculation for SSH is based on:
P. Casas, M. Seufert, S. Egger, and R. Schatz, 
“Quality of experience in remote virtual desktop services,” 
in IFIP/IEEE International Symposium on Integrated Network Management. 
IEEE, 2013, pp. 1352–1357.

### VoD/Live
Go to `videoMOScalcFiles/code` folder. There you can run `python3 recalcQoE.py <config> <name>` script to calculate the MOS of VoD and Live clients. `<config>` is the name of "Config" from the OMNeT++ ini file. `<name>` is the name of the export folder of the experiment run (e.g. `qosFlowsV55SlicesHTB_R100_Q35_M100_C100_105_VID42_LVD21_FDO5_SSH5_VIP32`).

IMPORTANT: You may need to adjust the path in `importDF` function to fit your system!

The MOS calculation for VoD/Live uses the ITU-T P.1203 Model.