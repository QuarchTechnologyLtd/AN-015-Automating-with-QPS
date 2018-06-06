'''
AN-015 - Application note demonstrating automated control over Quarch Power Studio (QPS)

This example demonstrates

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
import os, time

'''
File paths for the example are set here, and can be altered to put your data files in a different location
The path must be writable via a standar OS path
'''
filePath = os.path.dirname(os.path.realpath(__file__))

# Checks is QPS is running on the localhost
if isQpsRunning() == False:
    
    # Start the version on QPS installed with the quarchpy, Otherwise use start
    startLocalQps()

# Connect to the localhost QPS instance - you can also specify host='127.0.0.1' and port=*************************************??????? for remote control.
# This is used to access the basic functions, allowing us to scan for devices.  This step can be skipped if you already know the ID
# string of the device you want to connect to
myQps = qpsInterface()

# Request a list of all USB and LAN accessible modules
devList = myQps.getDeviceList()

# Print the devices, so the user can choose one to connect to
print ("\nList of devices attached to QIS:\n")
for idx, device in enumerate(devList, start=1):
    print (str(idx) + " : " + device)

# Get the user to select the device to control
moduleId = raw_input ("Enter the index number of the module to use: ")
myDeviceID = device[moduleId]

# Create the device connection, as a QPS connected device
myQpsDevice = quarchDevice (myDeviceID, ConType = "QPS")

# Prints out connected module information
print ("Running QPS Automation Example")
print ("Module Name:")
print (myQpsDevice.sendCommand ("hello?"))

# Setup the volatge mode and enable the outputs
setupPowerOutput (myQpsDevice)

# Set the averaging rate for the module.  This sets the resolution of data to record
# This is done via a direct command to the power module
print (myQpsDevice.sendCommand ("record:averaging 8k"))

# Start a stream, using the local folder of the script and a time-stamp file name in this example
fileName = time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
myStream = myQpsDevice.startStream (filePath + fileName)

'''
Example of adding annotations to the trace.  This can be used to hilight events, errors or
changes from one part of a test to another.

Annotations can be added in real time, or placed anywhere on the trace as part of post-processing,
using a timestamp
'''
time.sleep (2)
myStream.addAnnotation ('Adding an example annotation\nIn real time!')
time.sleep (1)
myStream.addAnnotation ('Adding an example annotation\nAt a specific time!', time.time())


'''
Example of adding arbitary data to the trace.  This allows IOPS, Temperature and similar to be added
where the data may be polled live from another process, or added in post-process

Channels need a name (T1 in this example) a 'group' name and a unit of measure
The final boolean will create auto SI unit ranges (milli/micro...) automatically if set to true
'''

myStream.addAnnotation ('Starting temperature measurement here!')
# Create new channel to record data into
myStream.createChannel ('T1', 'Temp', 'C', False)
myStream.createChannel ('T2', 'Temp', 'C', False)
# Write some example data into the channel
writeArbitaryData (myStream, 'T1', 'Temp')

# End the stream
myStream.stopStream ()





'''
Simple function to check the output mode of the power module, setting it to 3v3 if required
then enabling the outputs if not already done.  This will result in the module being turned on
and supplying power
'''
def setupPowerOutput (myModule):

    # Output mode is set automatically on HD modules using an HD fixture, otherwise we will chose 3v3 mode for this example
    if (myModule.sendCommand ("config:output Mode?") == "DISABLED"):
        print ("Either using an HD without an intelligent fixture or an XLC. Manually setting voltage to 3v3")
        print (myModule.sendCommand ("config:output:mode 3V3"))
    
    # Check the state of the module and power up if necessary
    print ("Checking the state of the device and power up if necessary")
    powerState = myModule.sendCommand ("run power?")
    print ("State of the Device: " + (powerState))    
    # If outputs are off
    if powerState == "OFF":
        # Power Up
        print (myModule.sendCommand ("run:power up"))

'''
Example function to write data to an arbitary channel that has been previously created
This data would normally come from another process such as drive monitor software or
a traffic generator
'''
def writeArbitaryData (myStream, channelName, groupName):
    print ("Writings 10 seconds worth of (made up) temperature data, please wait...")

    # Add a few temperature points to the stream at 1 second intervals
    driveTemp = 18
    for x in range(0, 10):
        myStream.addDataPoint (channelName, groupName, str(driveTemp))
        driveTemp = driveTemp + 0.8
        time.sleep (1)
    time.sleep (1)

    # Add a final time point at a specific time to demonstrate random addition of points
    myStream.addDataPoint (channelName, groupName, str(driveTemp), time.time())