## Installation

## Install Conda
* TODO: 


## Install Bigquery
- conda install -c conda-forge google-cloud-sdk 
- conda install -c conda-forge google-cloud-automl 
- conda install -c conda-forge/label/cf201901 google-cloud-core 
- conda install -c conda-forge/label/cf202003 google-cloud-core 
- conda install -c conda-forge google-cloud-bigquery 
- conda install -c conda-forge/label/gcc7 google-cloud-bigquery
- conda install -c conda-forge/label/cf201901 google-cloud-bigquery
- conda install -c conda-forge/label/cf202003 google-cloud-bigquery 

## Bug-Fixes
> cookiajar: main.py change in init (:43):
> sql = 'select %s from cookies where hex(encrypted_value)!="" and host_key like ?' % sql_fields 


## Other
- postgres: increase max number of connections
- postgres: update time