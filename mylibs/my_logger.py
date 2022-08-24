
import os
import sys
import os.path as path
import logging


# ToDo get vars from project general configuraiton file

# Vars
script_file="parseGwsOutputJson.py"
mypath = path.abspath(path.join(__file__, ".."))
#log_file=mypath + "/../logs/logs.log"
log_file=mypath + "logs.log"
fileHandlerLevel=logging.DEBUG
streamHandlerLevel=logging.DEBUG
#fileHandlerLevel=logging.INFO
#streamHandlerLevel=logging.INFO

# Create logger instance 
log = logging.getLogger(script_file)
log.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler(log_file)
fh.setLevel(fileHandlerLevel)
# create console handler with a higher log level
ch = logging.StreamHandler()
# ch.setLevel(logging.ERROR)
ch.setLevel(streamHandlerLevel)
# create formatter and add it to the handlers
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
log.addHandler(fh)
log.addHandler(ch)

# Get script path