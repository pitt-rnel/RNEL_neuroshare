# RNEL_neuroshare
This repository contains a set of MATLAB and python functions to read neuroshare files written via the Ripple Grapevine NIP and the 
Ripple Nomad. 

### MATLAB
The MATLAB file readers are based on the open source Neuroshare API that accompanies the Ripple Trellis install.  

#### *Setup*  
Clone or download this repository to your local machine and add the *functions* and *wrappers* folders to your matlab path. No additional 
configuration is required. The *functions* folder contains the native neuroshare ns_* functions and the *wrappers* folder contain the 
following functions:  
* read_continuousData.m  
* read_digitalEvents.m  
* read_spikeEvents.m  
* read_stimEvents.m  

these functions call the neuroshare functions when reading the specified channels/function inputs. The usage and description for each 
function is included at the beginning of each *.m file.
  
### Python
The python library was created by [mfliu](https://github.com/mfliu) and is based on the NEVspec documentation that accompanies the 
Ripple Trellis install. 
