'''
AN-015 - Application note demonstrating automated control over Quarch Power Studio (QPS)

This example checks everything is working by connecting to QPS and listing the devices
available for connection.  This verifies QuarchPy, QPS and the connection to the module(s)

########### VERSION HISTORY ###########

05/06/2018 - Andy Norrie	- First Version

########### INSTRUCTIONS ###########

For localhost QPS, run the example as it is.
For remote QPS, comment out the 'startLocalQps()' command and specify the IP:Port in the qpsInterface(...) command
This can also be used if you want to use a different version of QPS and will run it yourself

####################################
'''

# Import QPS functions
from quarchpy import qpsInterface, isQpsRunning, startLocalQps
# OS allows us access to path data
import os

# Checks is QPS is running on the localhost
if isQpsRunning() == False:
    
    # Start the version on QPS installed with the quarchpy, Otherwise use start
    startLocalQps()

# Connect to the localhost QPS instance - you can also specify host='127.0.0.1' and port=*************************************??????? for remote control.
myQps = qpsInterface()

# Request a list of all USB and LAN accessible modules
devList = myQps.getDeviceList()

# Print the devices
print ("\nList of devices attached to QIS:\n")
for device in devList:
    print (device)