import gspread
from oauth2client.service_account import ServiceAccountCredentials
import configparser
import datetime
import commonTasks

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('PetFeederTimes_secret.json', scope)
client = gspread.authorize(creds)
sheet = client.open('PetFeederTimes').sheet1

configParser = configparser.RawConfigParser()
configParser.read('/var/www/feeder/feeder/app.cfg')
# Read in config variables
hopperGPIO = str(configParser.get('feederConfig', 'Hopper_GPIO_Pin'))
hopperTime = str(configParser.get('feederConfig', 'Hopper_Spin_Time'))

# example calls
# times = sheet.get_all_records()
# feedingNeeded = sheet.row_values(1)
# sheet.update_cell(2,4,"false")

def spreadsheetFeed():
    dateNowObject = datetime.datetime.now()
    spin = commonTasks.spin_hopper(hopperGPIO, hopperTime)

    if spin != 'ok':
        return 'Error! No feed activated! Error Message: ' + str(spin)

    dbInsert = commonTasks.db_insert_feedtime(dateNowObject, 6)  # FeedType 6=Spreadsheet
    if dbInsert != 'ok':
        return 'Warning. Database did not update. Message returned: ' + str(dbInsert)

    return 'Feed success!'


triggerFeeding = sheet.cell(2,4).value #Check if box is checked to do a feeding
if triggerFeeding=='TRUE':
    output=spreadsheetFeed() #do feed

    if str(output)=='Feed success!': #update spreadsheet if successfull else update with error

        # Set box back to false to allow another feeding to occur
        sheet.update_cell(2, 4, "FALSE")

        #Update latest feed times to spreadsheet
        latestXNumberFeedTimes=commonTasks.db_get_last_feedtimes(7)
        rowCounter=2 #Row 1 has column titles, dont want to overwrite
        finalFeedTimeList = []
        for time in latestXNumberFeedTimes:
            time = list(time)
            dateobject = datetime.datetime.strptime(time[0], '%Y-%m-%d %H:%M:%S')
            time[0] = dateobject.strftime("%m-%d-%y %I:%M %p")
            time = tuple(time)
            # print (time[0])
            # print(time[1])
            sheet.update_cell(rowCounter, 1, time[0])
            sheet.update_cell(rowCounter, 2, time[1])
            rowCounter += 1

        #Update latest scheduled feedtimes to spreadsheet
        scheduledFeedtimes=commonTasks.db_get_scheduled_feedtimes(10)
        rowCounter=2 #Row 1 has column titles, dont want to overwrite
        finalUpcomingFeedTimeList = []
        for scheduledFeedTime in scheduledFeedtimes:
            scheduledFeedTime = list(scheduledFeedTime)
            dateobject = datetime.datetime.strptime(scheduledFeedTime[0], '%Y-%m-%d %H:%M:%S')
            finalString = dateobject.strftime("%m-%d-%y %I:%M %p")

            # 1900-01-01 default placeholder date for daily reoccuring feeds
            if str(scheduledFeedTime[2]) == '5':  # Repeated schedule. Strip off Date
                finalString = finalString.replace("01-01-00", "Daily at")
            # print (finalString)
            sheet.update_cell(rowCounter, 6, finalString)
            rowCounter += 1
    else: #feed was not success dump error to spreadsheet
        sheet.update_cell(2, 8, str(output))




