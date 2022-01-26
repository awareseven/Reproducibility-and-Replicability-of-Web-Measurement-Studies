#!/bin/bash

{ # try

    git pull
    #save your output

} || { # catch
    echo 'git pull fails'
} 



{ # try

     pkill -f firefox
    #save your output

} || { # catch
    echo 'firefox not found'
} 

{ # try

     pkill -f firefox-bin
    #save your output

} || { # catch
    echo 'firefox not found'
} 

{ # try

     pkill -f geckodriver
    #save your output

} || { # catch
    echo 'firefox not found'
} 

{ # try
     pkill -f chrome

} || { # catch
    echo 'chrome not found'
} 

{ # try
     pkill python

} || { # catch
    echo 'python not found'
} 

{ # try
     pkill python3

} || { # catch
    echo 'python3 not found'
} 


   source ~/miniconda3/etc/profile.d/conda.sh &&
   conda activate openwpm &&   
   pip install pyre2 &&  
   pip install adblockparser &&
   #pkill -f QueueManager.py  &&
   python3 /home/user/Desktop/repo/2021-webMeasurements/QueueManager.py