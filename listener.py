#!/usr/bin/env python

###############################################################################
#
#
#       FILE: listener.py
#       DATE: 2013 Nov. 15
#       AUTHOR: Brendon Walter
#
#       DESCTIPTION: listener.py uses psutil to listen to the CPU, memory, 
#       network information, and disk space and logs it to a file called 
#       listenerLog.log. It also checks the current directory to see what files
#       are currently in it and checks it against a list of files that need to
#       be there, as stated in the listernerConfig.py. These files that need
#       to be here should be in the form of a list. It should look like as 
#       follows: files = ["hosts.txt", "config.py"]. 
#       If either of those items are not found in the current directoy, it will
#       return a critical error that should be checked as soon as possible.
#
#       USAGE: run the listener by:
#               python listener.py <-v>
#       or:
#               ./listener.py <-v>
#       running the listener in verbose mode (-v) will print out information
#       for debugging purposes. 
#
#	The listenerConfig contains the name of the log that will store all 
#	errors, the number of items per line, which will determine how many
#	items are stored on each line (such as, if this number is set at 60,
#	the history of the CPU (and every part) will go back 60 items into its
#	past.) The delayTime will determine how often (in seconds) the program
#	will run through, and files is a list of every file that is supposed to
#	be in the folder in which the listener is running.
#       
#
###############################################################################

import psutil, time, sys, logging, os, re, listenerConfig
import functionLibrary as fL

# import debugging
fL.debug()

##########################

#    V A R I A B L E S   #

##########################

# The time that the program waits before running again is given in an argument.
delayTime = listenerConfig.delayTime

# name of the log in which all of the (non-error related) information
# is stored.
logName = listenerConfig.logName
logging.debug("Name of listen log: " + logName)

# "files" is a list of files that need to be in the directory. 
files = listenerConfig.files

for x in files: logging.debug("Files in config: " + x)

totItems = listenerConfig.numberOfItemsPerLine
logging.debug(str(totItems) + " items per line in log.")


###########################

#    F U N C T I O N S    #

###########################

def logInfo(lineNum, info):
	# logs info from each of the below functions into a listener log

	# try to read the listener log from the line specified
	with open(logName, 'r') as r:
		# take the data in the line and split it into a list
		data = r.readlines()
	logging.debug("read " + str(data) + " from the log.")

	if data == []:
		l = []

	# if the file is empty, there should be some way of handling this!!

	else: 
		# take the data from the log and split it into a list at the | and \n
		try:
			l = re.split('[|\n]', data[int(lineNum)])
		except IndexError:
			l = [0]
	
		# the list 2 items are empty strings (at least for the CPU). This will have 
		# to be removed depending on what happens with the other functions.
		del l[-1]
		
	# if the list has more elements than it should, delte them until it has the
	# right number
	while len(l) > totItems:
		del l[0]
	# if the list already has the number of items that it should,
	if len(l) == totItems:
		logging.debug("Line " + str(lineNum) + " was longer than " + str(totItems))
		# delete the first item
		del l[0]
	else: logging.debug("Line " + str(lineNum) + " was too short. Adding new item.")

	# append the new data to the list
	l.append(str(info))
	logging.debug("appended " + str(info) + " to the list.")

	# turn that list into a string
	newData = '|'.join(l)

	# add a new line character to the end of the string
	try:
		if data == []:
			data = newData + '\n'
		else: 
			data[int(lineNum)] = newData + '\n'

	except IndexError:
		data.append(newData + '\n')
	
	# write new data to the log
	with open(logName, 'w') as w:
		w.writelines(data)
	
def getCPU():
	# gets the percent of the CPU in use
	lineNum = 0 # the line of the log in which all of the CPU information is stored
	cpuPercent = psutil.cpu_percent()
	logging.debug("CPU percent : " + str(cpuPercent))
	logInfo(lineNum, cpuPercent)

def getMemory():
	# gets the percent of virtual memory in use
	lineNum = 1
	vm = psutil.virtual_memory()
	# pick out the percent from the psutil output
	vmPercent = vm.percent
	# log the information
	logging.debug("Virtual memory percent : " + str(vmPercent))
	logInfo(lineNum, vmPercent)

def getNetwork():
	# gets the number of bytes sent and recieved over the network
	lineNum = 2
	network = psutil.net_io_counters()
	# get the sent information
	sent = network.bytes_sent
	# and the received information
	receieved = network.bytes_recv
	info = str(sent) + '/' + str(receieved)
	logInfo(lineNum, info)

def getDisk():
	# gets the space used and space available from the disk
	# the output is logged in the form of : USED / AVAILABLE
	lineNum = 3
	disk = psutil.disk_usage('/')
	# get the disk used from the psutil output
	u = str(disk.used)
	# remove the last character ('L') so that the data is only numbers
	used = u[:-1]
	logging.debug("Disk used : " + str(used))
	# get the free space from the psutil output
	f = str(disk.free)
	# remove 'L'
	free = f[:-1]
	logging.debug("Disk free : " + str(free))
	info = used + '/' + free
	logInfo(lineNum, info)

def filesMissing():
        # reads the local directory  and checks to make sure that the files
        # that are supposed to be there are there

        # put the name of all the files present in the directory into a list
        # called currentFiles created below
        currentFiles = []
        for current in os.listdir('.'):
                currentFiles.append(current)
        logging.debug("The current files in the directory are: " + str(currentFiles))
        # for debugging purposes
        for item in files:
                logging.debug("The files that should be here are: " + str(item))

	missing = []
	# compare the files that are supposed to be here to files that actually
	# are here.
	for val in files:
		if val not in currentFiles:
			# if a file that is supposed to be here is not here, add
			# the name of the file to a list called missing
			missing.append(val)

	# if there is nothing in the list of missing files
	if missing == []:
		# everything is fine
		logging.debug("Every file that is supposed to be here is here.")
	else:
		for item in missing:	
			# for each item that is missing, log a critical error
			logging.critical("File " + str(item) + " is missing!!")


###########################

#    M A I N   L O O P    #

###########################

logging.debug("Starting main loop.........")

if __name__ == '__main__':
	while 1:
		getCPU()
		getMemory()
		getNetwork()
		getDisk()
		filesMissing()
		time.sleep(delayTime)
