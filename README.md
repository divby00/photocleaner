# PhotoCleaner
Python 2.7 small script to remove duplicated photos in a given folder. It works by analyzing the histogram of each photo that
the script founds by recursively walking the input folder -it just searches for *.jpg, *.jpeg and *.png files-
With the histogram, the script creates a hash that is associated to each photography, the hash is what is used to check
if 2 photos are the same. 

## How to use
This script needs a python 2.7 full installation and the following dependencies:    

  * psutils
  * PIL
    
You can run it with the following command:     
    
    ./photocleaner.py input_folder output_folder

Windows users: if you don't want to install Python, a MS Windows standalone executable is provided.
