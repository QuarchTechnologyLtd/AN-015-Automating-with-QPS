'''
AN-015 - Application note demonstrating automated control over Quarch Power Studio (QPS)

This example demonstrates adding annotations and datapoints to a QPS stream.

########### VERSION HISTORY ###########

05/06/2018 - Andy Norrie    - First Version
02/10/2018 - Matt Holsey    - Updated Script for updated QuarchPy Methods.
15/10/2020 - Pedro Cruz     - Updated Script for PAM.

########### INSTRUCTIONS ###########

For localhost QPS, run the example as it is.
For remote QPS, comment out the 'startLocalQps()' command and specify the IP:Port in the qpsInterface(...) command
This can also be used if you want to use a different version of QPS and will run it yourself

####################################
'''

# Import QPS functions
import quarchpy
from quarchpy.qps import *
from quarchpy.device import *
# OS allows us access to path data
import os, time

'''
Simple function to check the output mode of the power module, setting it to 3v3 if required
then enabling the outputs if not already done.  This will result in the module being turned on
and supplying power
'''
def setupPowerOutput (myModule):
    # Output mode is set automatically on HD modules using an HD fixture, otherwise we will chose 5V mode for this example
    if "DISABLED" in myModule.sendCommand("config:output Mode?"):
        try:
            drive_voltage = raw_input("\n Either using an HD without an intelligent fixture or an XLC.\n \n>>> Please select a voltage [3V3, 5V]: ") or "3V3" or "5V"
        except NameError:
            drive_voltage = input("\n Either using an HD without an intelligent fixture or an XLC.\n \n>>> Please select a voltage [3V3, 5V]: ") or "3V3" or "5V"

        myModule.sendCommand("config:output:mode:"+ drive_voltage)
    
    # Check the state of the module and power up if necessary
    powerState = myModule.sendCommand ("run power?")
    # If outputs are off
    if "OFF" in powerState:
        # Power Up
        print ("\n Turning the outputs on:"), myModule.sendCommand ("run:power up"), "!"

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


# Version 2.0.0 or higher expected for this appliation note
quarchpy.requiredQuarchpyVersion ("2.0.0")

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

#Display and choose module from found modules
myDeviceID = GetQpsModuleSelection (myQps)

#convert module to quarch module
myQuarchDevice = quarchDevice (myDeviceID, ConType = "QPS")

# Create the device connection, as a QPS connected device
myQpsDevice = quarchQPS(myQuarchDevice)
myQpsDevice.openConnection()

# Prints out connected module information
print ("Running QPS Automation Example")
print ("Module Name:")
print (myQpsDevice.sendCommand ("hello?"))

# Setup the volatge mode and enable the outputs
# Comment it out for PAM modules
#setupPowerOutput (myQpsDevice)

# Set the averaging rate for the module.  This sets the resolution of data to record
# This is done via a direct command to the power module
print (myQpsDevice.sendCommand ("record:averaging 32k"))

# Start a stream, using the local folder of the script and a time-stamp file name in this example
fileName = time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
myStream = myQpsDevice.startStream (filePath + fileName)

'''
Example of adding annotations to the trace.  This can be used to highlight events, errors or
changes from one part of a test to another.

Annotations can be added in real time, or placed anywhere on the trace as part of post-processing,
using a timestamp
'''
time.sleep (2)
myStream.addAnnotation ('Adding an example annotation\\nIn real time!')
print(myStream.get_stats())
time.sleep (1)
myStream.addAnnotation ('Adding an example annotation\\nAt a specific time!', time.time())
print(myStream.get_stats())
time.sleep(1)

'''
Example of adding arbitary data to the trace.  This allows IOPS, Temperature and similar to be added
where the data may be polled live from another process, or added in post-process

Channels need a name (T1 in this example) a 'group' name and a unit of measure
The final boolean will create auto SI unit ranges (milli/micro...) automatically if set to true
'''

myStream.addAnnotation ('Starting temperature measurement here!')

print(myStream.get_stats())
# Create new channel to record data into
myStream.createChannel ('T1', 'Temp', 'C', False)
myStream.createChannel ('T2', 'Temp', 'C', False)
# Write some example data into the channel
writeArbitaryData (myStream, 'T1', 'Temp')

# End the stream
myStream.stopStream ()

