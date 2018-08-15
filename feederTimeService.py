#!/var/www/feeder/bin/python
import sys
sys.path.extend(['/var/www/feeder/feeder'])
import logging.handlers
import argparse
import time
import signal
import commonTasks
import ConfigParser
import os
import datetime

#Find config file
dir = os.path.dirname(__file__)  # os.getcwd()
configFilePath = os.path.abspath(os.path.join(dir, "app.cfg"))
configParser = ConfigParser.RawConfigParser()
configParser.read(configFilePath)

#Read in config variables
secondDelay =configParser.get('feederConfig', 'Seconds_Delay_Between_Schedule_Checks')
LOG_TimeService_FILENAME=configParser.get('feederConfig', 'Log_TimeService_Filename')
hopperGPIO =str(configParser.get('feederConfig', 'Hopper_GPIO_Pin'))
hopperTime =str(configParser.get('feederConfig', 'Hopper_Spin_Time'))
motionVideoDirPath = str(configParser.get('feederConfig', 'Motion_Video_Dir_Path'))
nowMinusXDays = str(configParser.get('feederConfig', 'Number_Days_Of_Videos_To_Keep'))

# Define and parse command line arguments
parser = argparse.ArgumentParser(description="My simple Python service")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_TimeService_FILENAME + "')")

# If the log file is specified on the command line then override the default
args = parser.parse_args()
if args.log:
        LOG_FILENAME = args.log

# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)
# Set the log level to LOG_LEVEL
logger.setLevel(logging.INFO) # Could be e.g. "DEBUG" or "WARNING")
# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(LOG_TimeService_FILENAME, when="midnight", backupCount=3)
# Format each log message like this
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
# Attach the formatter to the handler
handler.setFormatter(formatter)
# Attach the handler to the logger
logger.addHandler(handler)

# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
        def __init__(self, logger, level):
                """Needs a logger and a logger level."""
                self.logger = logger
                self.level = level

        def write(self, message):
                # Only log if there is a message (not just a new line)
                if message.rstrip() != "":
                        self.logger.log(self.level, message.rstrip())

# Replace stdout with logging to file at INFO level
sys.stdout = MyLogger(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
sys.stderr = MyLogger(logger, logging.ERROR)


class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self,signum, frame):
    self.kill_now = True

print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
print("Starting up")
print("Time delay default is: "+str(secondDelay)+" seconds")
print("Create Gracekiller class")
killer = GracefulKiller()
print("End Start up. Starting while loop")
print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
while True:

    updatescreen = commonTasks.print_to_LCDScreen(commonTasks.get_last_feedtime_string())
    #print "Message Display return status: " + updatescreen

    #print "Begin checking if scheduled events."
    upcomingXNumberFeedTimes = commonTasks.db_get_scheduled_feedtimes(50)
    finalUpcomingFeedTimeList = []
    for x in upcomingXNumberFeedTimes:
        x = list(x)
        dateobject = datetime.datetime.strptime(x[0], '%Y-%m-%d %H:%M:%S')
        x = tuple(x)
        finalUpcomingFeedTimeList.append(x[0])

    for x in finalUpcomingFeedTimeList:
        present = datetime.datetime.now()
        value = datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
        c = present - value
        d = divmod(c.days * 86400 + c.seconds, 60)

        if d[0] > 1:
            print 'Scheduled record found past due'
            print "Current time: "+str(present)
            print "Scheduled time: "+str(value)
            print "Minutes difference: "+str(d[0])

            dateNowObject = datetime.datetime.now()

            spin = commonTasks.spin_hopper(hopperGPIO, hopperTime)
            if spin <> 'ok':
                print 'Error! The ladies have not been feed! Error Message: ' + spin, 'error'

            dbInsert = commonTasks.db_insert_feedtime(dateNowObject, 3)
            if dbInsert <> 'ok':
                print 'Warning. Database did not update: ' + dbInsert, 'warning'

            updatescreen = commonTasks.print_to_LCDScreen(commonTasks.get_last_feedtime_string())
            if updatescreen <> 'ok':
                print 'Warning. Screen feedtime did not update: ' + updatescreen

            print 'Auto feed success!'

            #Delete one off scheduled feeds now. Keep reoccuring feed schedules in DB.
            #Reoccuring daily feed times have date 2000-01-01 as placeholder in DB
            #If x contains 2000-01-01 can assume it is a reoccuring schedule and can skip
            if '2000-01-01' not in x:
                # Not a scheduled time. Can delete
                # Delete old scheduled records from DB
                con = commonTasks.connect_db()
                cur = con.execute("""delete from feedtimes where feeddate=?""", [str(x), ])
                con.commit()
                cur.close()
                con.close()

                print 'Deleted old record from DB'
            else:
                print 'Date contains 2000-01-01. This is date placeholder for scheduled daily feed times. Do not delete as scheduled will therefore be deleted. Deleted scheduled times through UI.'



            break

    #Remove files older then specified days
    now = time.time()
    nowMinusSpecifiedDays = now - int(nowMinusXDays) * 86400
    # Loop and remove
    for f in os.listdir(motionVideoDirPath):
        if f != '.gitkeep':
                f = os.path.join(motionVideoDirPath, f)
                if os.stat(f).st_mtime < nowMinusSpecifiedDays:
                    if os.path.isfile(f):
                        print 'removing file: '+str(f)
                        os.remove(os.path.join(motionVideoDirPath, f))

    time.sleep(float(secondDelay))
    if killer.kill_now:break

print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
print "End of the program. I was killed gracefully :)"
print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
