## README

This repository consists of gameplays for Avegotchi gotchiverse. Each of the gameplays give you a strategy for how to play your gotchis and deploy to which parcels

#### code structure

The folder structure is as follows:
- src - This consists of the code for the APIs of the gameplays
- data - This consists of helper data which would be used for computations
- experiment-notebooks - This is the collection of notebooks where initial algorithms are tested before being deployed as APIs


#### gameplays information

Currently, there are 2 gameplays for altaar harvesting. Both the gameplays take as input the parcels and gotchis which the user currently has.
- gameplay_v5 - This gameplay returns the levels to which you should upgrade you parcels for optimal yields. 
- gameplay_v7 - This gameplay doesn't aim at getting optimal yield, instead it tries to minimize user effort by spreading the gotchis across parcels as widely as possible