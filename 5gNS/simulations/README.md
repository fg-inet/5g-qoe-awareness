# Using 5G QoS Mechanisms to Achieve QoE-Aware Resource Allocation

## Used simulations

### Simulation configurations
This folder contains simulation configurations used in the publication, as well as the commands used to run these simulations.

For commands used to run the parameter studies look at the `parameterStudy*V2.txt` files. 
The respective configurations are in `parameterStudyConfiguration.ini`.

For commands used to run the experiments with QoE-based, QoS-based, and Best-Effort settings look at the `runCommandsFlowsV5.txt` file.
Respective configurations are contained within the `qosFlowsConfig.ini` (or `bestEffort.ini` for best effort scenarios).

The configurations for experiments experiments used to generate the heat maps are contained within the `baselineTestV3.ini` file. CAUTION: These experiments won't export properly when run with `runAndExportSimConfig.sh` script. For their export, please use the `results/export_results_heatMap.sh` script.

