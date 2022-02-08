# pypsa-eur-results

This repository contains the result nc files of the runs with different configurations of PyPSA-eur. The configurations are:
* sllimccs: scaled load to WITCH level, limits for conventional capacities and renewable minimum capacities, introlduction of CCS, spatial resolution 37 nodes (one per country), temporal resolution 3h time steps
* sllimccs128: sllimccs with increased spatial resolution of 128 nodes
* sllimccs256: sllimccs with increased spatial resolution of 256 nodes
* sllimccsnoco2lim: sllimccs with no CO2 limit
* independence0.85: sllimccs and each country has to fulfill at least 85% of their energy needs domestically
* independence1: sllimccs and each country has to fulfill their energy needs completely alone

In each on the configuration folders 3 result files can be found according to 3 scenarios with different CO2 targets (Co2L0.011533: low emission target, Co2L0.067468: medium CO2 emission target, Co2L0.33865: high CO2 emission target). 

Furthermore the folder FILES and contain subfolders with changed scripts and input data files, which needed to be adjusted in order to make the described configurations possible.
