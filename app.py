#!/home/pi/venv/feeder/bin/python
from __future__ import with_statement
import sys
sys.path.extend(['/var/www/feeder/feeder/logs'])
import sqlite3
from flask import Flask, flash, Markup, redirect, render_template, request,Response, session, url_for,abort
import subprocess
import commonTasks
import os
import ConfigParser
import datetime
from werkzeug import check_password_hash, generate_password_hash
from stat import S_ISREG, ST_CTIME, ST_MODE
import os, sys, time

app = Flask(__name__)

#Find config file
dir = os.path.dirname(__file__)  # os.getcwd()
configFilePath = os.path.abspath(os.path.join(dir, "app.cfg"))
configParser = ConfigParser.RawConfigParser()
configParser.read(configFilePath)

#Read in config variables
SECRETKEY = str(configParser.get('feederConfig', 'Secretkey'))
hopperGPIO =str(configParser.get('feederConfig', 'Hopper_GPIO_Pin'))
hopperTime =str(configParser.get('feederConfig', 'Hopper_Spin_Time'))
DB = str(configParser.get('feederConfig', 'Database_Location'))
latestXNumberFeedTimesValue = str(configParser.get('feederConfig', 'Number_Feed_Times_To_Display'))
upcomingXNumberFeedTimesValue = str(configParser.get('feederConfig', 'Number_Scheduled_Feed_Times_To_Display'))
motionVideoDirPath = str(configParser.get('feederConfig', 'Motion_Video_Dir_Path'))
latestXNumberVideoFeedTimesValue = str(configParser.get('feederConfig', 'Number_Videos_To_Display'))
localCameraSiteAddress = str(configParser.get('feederConfig', 'Local_Camera_Site_Address'))
remoteCameraSiteAddress = str(configParser.get('feederConfig', 'Remote_Camera_Site_Address'))
nowMinusXDays = str(configParser.get('feederConfig', 'Number_Days_Of_Videos_To_Keep'))
localIpStart = str(configParser.get('feederConfig', 'Local_IP_Start'))

#####################################################################################
##########################################HOME PAGE##################################
#####################################################################################
@app.route('/', methods=['GET', 'POST'])
def home_page():
    try:

        latestXNumberFeedTimes=commonTasks.db_get_last_feedtimes(latestXNumberFeedTimesValue)
        upcomingXNumberFeedTimes=commonTasks.db_get_scheduled_feedtimes(upcomingXNumberFeedTimesValue)

        finalFeedTimeList = []
        for x in latestXNumberFeedTimes:
            x = list(x)
            dateobject = datetime.datetime.strptime(x[0], '%Y-%m-%d %H:%M:%S')
            x[0] = dateobject.strftime("%m-%d-%y %I:%M %p")
            x = tuple(x)
            finalFeedTimeList.append(x)

        finalUpcomingFeedTimeList = []
        for x in upcomingXNumberFeedTimes:
            x = list(x)
            dateobject = datetime.datetime.strptime(x[0], '%Y-%m-%d %H:%M:%S')
            x[0] = dateobject.strftime("%m-%d-%y %I:%M %p")
            x = tuple(x)
            finalUpcomingFeedTimeList.append(x)

        ipAddress = request.remote_addr
        cameraSiteAddress=''
        localOrRemote=''
        if str(ipAddress).startswith(localIpStart):
            cameraSiteAddress=localCameraSiteAddress
            localOrRemote='local'
        else:
            cameraSiteAddress = remoteCameraSiteAddress
            localOrRemote='remote'

        # #latestXVideoFeedTimes
        latestXVideoFeedTimes = []
        for path, subdirs, files in os.walk(motionVideoDirPath):
            for name in sorted(files, key=lambda name:
            os.path.getmtime(os.path.join(path, name))):
                if name.endswith('.mkv'):
                    vidDisplayDate=datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(path, name))).strftime('%m-%d-%y %I:%M %p')
                    vidFileName=name
                    vidFileSize = str(round(os.path.getsize(os.path.join(path, name)) / (1024 * 1024.0), 1))
                    latestXVideoFeedTimes.append([vidDisplayDate,vidFileName,vidFileSize])

        latestXVideoFeedTimes = latestXVideoFeedTimes[:int(latestXNumberVideoFeedTimesValue)]
        latestXVideoFeedTimes=latestXVideoFeedTimes[::-1] #Reverse so newest first

        cameraStatusOutput = DetectCamera()
        #cameraStatusOutput = 'supported=0 detected=1'
        if "detected=1" not in cameraStatusOutput:
            cameraStatus='0'
        else:
            cameraStatus='1'

        #Return page
        return render_template('home.html',latestXNumberFeedTimes=finalFeedTimeList
                               ,upcomingXNumberFeedTimes=finalUpcomingFeedTimeList
                               ,cameraSiteAddress=cameraSiteAddress
                               ,localOrRemote=localOrRemote
                               ,latestXVideoFeedTimes=latestXVideoFeedTimes
                               ,cameraStatus=cameraStatus
                               )

    except Exception,e:
        return render_template('error.html',resultsSET=e)


@app.route('/feedbuttonclick', methods=['GET', 'POST'])
def feedbuttonclick():
    try:
        dateNowObject = datetime.datetime.now()

        spin = commonTasks.spin_hopper(hopperGPIO, hopperTime)
        if spin <> 'ok':
            flash('Error! The ladies have not been feed! Error Message: ' + spin,'error')
            return redirect(url_for('home_page'))

        dbInsert=commonTasks.db_insert_feedtime(dateNowObject,2)
        if dbInsert <> 'ok':
            flash('Warning. Database did not update: '+dbInsert,'warning')

        updatescreen = commonTasks.print_to_LCDScreen(commonTasks.get_last_feedtime_string())
        if updatescreen <> 'ok':
            flash('Warning. Screen feedtime did not update: '+updatescreen)

        flash('Feed success!')

        return redirect(url_for('home_page'))
    except Exception,e:
        return render_template('error.html',resultsSET=e)


@app.route('/feedbuttonclickSmartHome', methods=['GET', 'POST'])
def feedbuttonclickSmartHome():
    try:
        dateNowObject = datetime.datetime.now()

        spin = commonTasks.spin_hopper(hopperGPIO, hopperTime)
        if spin <> 'ok':
            flash('Error! The ladies have not been feed! Error Message: ' + spin,'error')
            return redirect(url_for('home_page'))

        dbInsert=commonTasks.db_insert_feedtime(dateNowObject,4)
        if dbInsert <> 'ok':
            flash('Warning. Database did not update: '+dbInsert,'warning')

        updatescreen = commonTasks.print_to_LCDScreen(commonTasks.get_last_feedtime_string())
        if updatescreen <> 'ok':
            flash('Warning. Screen feedtime did not update: '+updatescreen)

        flash('Feed success!')

        return redirect(url_for('home_page'))
    except Exception,e:
        return render_template('error.html',resultsSET=e)


@app.route('/scheduleDatetime', methods=['GET', 'POST'])
def scheduleDatetime():
    try:
        scheduleDatetime = [request.form['scheduleDatetime']][0]
        dateobject=datetime.datetime.strptime(scheduleDatetime,'%Y-%m-%dT%H:%M')
        dbInsert = commonTasks.db_insert_feedtime(dateobject, 0)
        if dbInsert <> 'ok':
            flash('Error! The time has not been scheduled! Error Message: ' + dbInsert,'error')
            return redirect(url_for('home_page'))

        flash("Time Scheduled")
        return redirect(url_for('home_page'))
    except Exception,e:
        return render_template('error.html',resultsSET=e)


@app.route('/deleteRow/<history>', methods=['GET', 'POST'])
def deleteRow(history):
    try:
        dateObj = datetime.datetime.strptime(history, "%m-%d-%y %I:%M:%S %p")
        deleteRowFromDB=deleteUpcomingFeedingTime(str(dateObj))
        if deleteRowFromDB <> 'ok':
            flash('Error! The row has not been deleted! Error Message: ' + deleteRowFromDB,'error')
            return redirect(url_for('home_page'))

        flash("Scheduled time "+str(history)+" deleted")


        return redirect(url_for('home_page'))

    except Exception,e:
        return render_template('error.html',resultsSET=e)

def deleteUpcomingFeedingTime(dateToDate):
    try:
        con = commonTasks.connect_db()
        cur = con.execute("""delete from feedtimes where feeddate=?""", [str(dateToDate), ])
        con.commit()
        cur.close()
        con.close()
        return 'ok'
    except Exception, e:
        return render_template('error.html', resultsSET=e)


@app.route('/video/<videoid>', methods=['GET', 'POST'])
def video_page(videoid):
    try:
        valid=0

        for f in os.listdir(motionVideoDirPath):
            if f == videoid:
                valid=1

        if valid==1:
            return render_template('video.html',videoid=videoid)
        else:
            abort(404)
    except Exception, e:
        return render_template('error.html', resultsSET=e)


def DetectCamera():
    try:

        process = subprocess.Popen(["vcgencmd", "get_camera"],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
        return process.stdout.read()
    except Exception,e:
        return e

######################################################################################
##########################################ADMIN PAGE##################################
######################################################################################

@app.route('/adminLogin', methods=['GET', 'POST'])
def admin_login_page():
    try:

        if 'userLogin' in session:
            return redirect(url_for('admin_page'))
        else:
            return render_template('login.html')

    except Exception,e:
        return render_template('error.html',resultsSET=e)


@app.route('/login', methods=['GET', 'POST'])
def login_verify():
    try:

        if 'userLogin' in session:
            return redirect(url_for('admin_page'))
        else:

            if not request.form['usrname']:
                return render_template('error.html',resultsSET="Enter Username")
            elif not request.form['psw']:
                return render_template('error.html',resultsSET="Enter Password")

            user=[request.form['usrname']]
            username=user[0]

            pw=[request.form['psw']]
            password=pw[0]

            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute('''select pw_hash from user where username=?''',[username,])
            pw_hash = c.fetchone()
            c.close()
            conn.close()

            #Invalid Username (not in DB)
            if not pw_hash:
                con = sqlite3.connect(DB)
                cur = con.execute('''insert into loginLog (loginName,loginPW,loginDate) values (?,?,?)''',[username, password, datetime.datetime.now()])
                con.commit()
                cur.close()
                con.close()
                return render_template('error.html', resultsSET="Invalid Credentials")
            else:
                pw_hash=pw_hash[0]

            #User in DB (invalid PW)
            if not check_password_hash(pw_hash,password):
                con=sqlite3.connect(DB)
                cur=con.execute('''insert into loginLog (loginName,loginPW,loginDate) values (?,?,?)''',[username,password,datetime.datetime.now()])
                con.commit()
                cur.close()
                con.close()
                return render_template('error.html',resultsSET="Invalid Credentials")


            session['userLogin'] = str(username)

            return redirect(url_for('admin_login_page'))

    except Exception, e:
      return render_template('error.html',resultsSET=e)


@app.route('/logout',methods=['GET', 'POST'])
def logout():
    session.pop('userLogin', None)
    return redirect(url_for('admin_login_page'))


@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    try:
        if 'userLogin' in session:
            buttonServiceFullOutput = ControlService('feederButtonService', 'status')
            buttonServiceFinalStatus = CleanServiceStatusOutput(buttonServiceFullOutput)

            timeServiceFullOutput = ControlService('feederTimeService', 'status')
            timeServiceFinalStatus = CleanServiceStatusOutput(timeServiceFullOutput)

            sshServiceFullOutput = ControlService('ssh', 'status')
            sshServiceFinalStatus = CleanServiceStatusOutput(sshServiceFullOutput)

            webcameraServiceFullOutput = ControlService('motion', 'status')
            webcameraServiceFinalStatus = CleanServiceStatusOutput(webcameraServiceFullOutput)

            ipAddress = request.remote_addr
            cameraSiteAddress=''
            localOrRemote = ''
            if str(ipAddress).startswith(localIpStart):
                cameraSiteAddress = localCameraSiteAddress
                localOrRemote = 'local'
            else:
                cameraSiteAddress = remoteCameraSiteAddress
                localOrRemote = 'remote'

            #Bad login log
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute("select loginName, loginPW, loginDate from LoginLog;")
            invalidLogins = c.fetchall()
            #Return none of no rows so UI knows what to display
            if len(invalidLogins) <= 0:
                invalidLogins=None
            conn.commit()
            conn.close()

            #Current Admins
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute("select user_id, username from user;")
            userLogins = c.fetchall()
            #Return none of no rows so UI knows what to display
            if len(userLogins) <= 0:
                userLogins=None
            conn.commit()
            conn.close()


            return render_template('admin.html'
                                   ,buttonServiceFinalStatus=buttonServiceFinalStatus
                                   ,timeServiceFinalStatus=timeServiceFinalStatus
                                   ,cameraSiteAddress=cameraSiteAddress
                                   ,localOrRemote=localOrRemote
                                   ,invalidLogins=invalidLogins
                                   ,sshServiceFinalStatus=sshServiceFinalStatus
                                   ,webcameraServiceFinalStatus=webcameraServiceFinalStatus
                                   ,userLogins=userLogins
                                   )

        else:
            return redirect(url_for('admin_login_page'))
    except Exception,e:
        return render_template('error.html',resultsSET=e)


@app.route('/clearBadLoginList', methods=['GET', 'POST'])
def clearBadLoginList():
    try:
        if 'userLogin' in session:

            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute("delete from loginLog")
            conn.commit()
            c.close()
            conn.close()

            flash('List cleared')

            return redirect(url_for('admin_page'))
        else:
            return redirect(url_for('admin_login_page'))
    except Exception, e:
        return render_template('error.html', resultsSET=e)

@app.route('/startWebcamService', methods=['GET', 'POST'])
def startWebcamService():
    try:
        if 'userLogin' in session:

            process = subprocess.Popen(["sudo", "motion", "-c", "/home/pi/.motion/motion.conf"],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)

            startWebcamServiceFullOutput=ControlService('motion','start')

            flash('Webcam Service Started!')
            return redirect(url_for('admin_page'))
        else:
            return redirect(url_for('admin_login_page'))
    except Exception,e:
        return render_template('error.html',resultsSET=e)

@app.route('/stopWebcamService', methods=['GET', 'POST'])
def stopWebcamService():
    try:
        if 'userLogin' in session:
            stopWebcamServiceFullOutput=ControlService('motion','stop')

            process = subprocess.Popen(["sudo", "pkill", "-f", "motion.conf"],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)

            flash('Webcam Service Stopped!')
            return redirect(url_for('admin_page'))
        else:
            return redirect(url_for('admin_login_page'))
    except Exception,e:
        return render_template('error.html',resultsSET=e)

@app.route('/startButtonService', methods=['GET', 'POST'])
def startButtonService():
    try:
        if 'userLogin' in session:
            myLogTimeServiceFullOutput=ControlService('feederButtonService','start')

            flash('Button Service Started!')
            return redirect(url_for('admin_page'))
        else:
            return redirect(url_for('admin_login_page'))
    except Exception,e:
        return render_template('error.html',resultsSET=e)

@app.route('/stopButtonService', methods=['GET', 'POST'])
def stopButtonService():
    try:
        if 'userLogin' in session:
            myLogTimeServiceFullOutput=ControlService('feederButtonService','stop')

            flash('Button Service Stopped!')
            return redirect(url_for('admin_page'))
        else:
            return redirect(url_for('admin_login_page'))
    except Exception,e:
        return render_template('error.html',resultsSET=e)

@app.route('/startTimeService', methods=['GET', 'POST'])
def startTimeService():
    try:
        if 'userLogin' in session:
            myLogTimeServiceFullOutput = ControlService('feederTimeService', 'start')

            flash('Time Service Started!')
            return redirect(url_for('admin_page'))
        else:
            return redirect(url_for('admin_login_page'))
    except Exception, e:
        return render_template('error.html', resultsSET=e)

@app.route('/stopTimeService', methods=['GET', 'POST'])
def stopTimeService():
    try:
        if 'userLogin' in session:
            myLogTimeServiceFullOutput = ControlService('feederTimeService', 'stop')

            flash('Time Service Stopped!')
            return redirect(url_for('admin_page'))
        else:
            return redirect(url_for('admin_login_page'))
    except Exception, e:
        return render_template('error.html', resultsSET=e)

@app.route('/startSshService', methods=['GET', 'POST'])
def startSshService():
    try:
        if 'userLogin' in session:
            sshServiceFullOutput = ControlService('ssh', 'start')

            flash('SSH Service Started!')
            return redirect(url_for('admin_page'))
        else:
            return redirect(url_for('admin_login_page'))
    except Exception, e:
        return render_template('error.html', resultsSET=e)

@app.route('/stopSshService', methods=['GET', 'POST'])
def stopSshService():
    try:
        if 'userLogin' in session:
            sshServiceFullOutput = ControlService('ssh', 'stop')

            flash('SSH Service Stopped!')
            return redirect(url_for('admin_page'))
        else:
            return redirect(url_for('admin_login_page'))
    except Exception, e:
        return render_template('error.html', resultsSET=e)


def ControlService(serviceToCheck,command):
    try:

        process = subprocess.Popen(["sudo", "service", serviceToCheck, command],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
        return process.stdout.read()
    except Exception,e:
        return render_template('error.html',resultsSET=e)


def CleanServiceStatusOutput(serviceOutput):
    try:

        buttonServiceStartString = serviceOutput.find('Active:') + len('Active:')
        buttonServiceEndString = serviceOutput.find('\n', buttonServiceStartString)
        buttonServiceFinalStatus = serviceOutput[buttonServiceStartString:buttonServiceEndString]
        buttonServiceStartString = buttonServiceFinalStatus.find('since')
        buttonServiceEndString = buttonServiceFinalStatus.find('; ', buttonServiceStartString)
        buttonServiceFinalStatus = str(buttonServiceFinalStatus).replace(
        buttonServiceFinalStatus[buttonServiceStartString:buttonServiceEndString], '')

        return buttonServiceFinalStatus
    except Exception,e:
        return render_template('error.html',resultsSET=e)

@app.route('/history', methods=['GET', 'POST'])
def history_page():
    try:
        if 'userLogin' in session:

            latestXNumberFeedTimes = commonTasks.db_get_last_feedtimes(500)

            finalFeedTimeList = []
            for x in latestXNumberFeedTimes:
                x = list(x)
                dateobject = datetime.datetime.strptime(x[0], '%Y-%m-%d %H:%M:%S')
                x[0] = dateobject.strftime("%m-%d-%y %I:%M:%S %p")
                x = tuple(x)
                finalFeedTimeList.append(x)

            return render_template('history.html'
                                   ,latestXNumberFeedTimes=finalFeedTimeList
                                   )
        else:
            return redirect(url_for('admin_login_page'))
    except Exception,e:
        return render_template('error.html',resultsSET=e)


@app.route('/deleteUser/<id>', methods=['GET', 'POST'])
def deleteUser(id):
    try:
        if 'userLogin' in session:

            con = commonTasks.connect_db()
            cur = con.execute("""delete from user where username=?""", [str(id), ])
            con.commit()
            cur.close()
            con.close()

            flash('User deleted')

            return redirect(url_for('admin_page'))

        else:
            return redirect(url_for('admin_login_page'))
    except Exception, e:
        return render_template('error.html', resultsSET=e)

@app.route('/User', methods=['GET', 'POST'])
def User():
    try:
        if 'userLogin' in session:

            return render_template('user.html')

        else:
            return redirect(url_for('admin_login_page'))
    except Exception, e:
        return render_template('error.html', resultsSET=e)


@app.route('/addUser', methods=['GET', 'POST'])
def addUser():
    try:
        if 'userLogin' in session:

            if not request.form['usrname']:
                return render_template('error.html',resultsSET="Enter Username")
            elif not request.form['psw']:
                return render_template('error.html',resultsSET="Enter Password")

            user=[request.form['usrname']]
            username=user[0]

            pw=[request.form['psw']]
            password=pw[0]

            # Does exists already
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute('''select username from user where username=?''',[username,])
            userName = c.fetchone()
            c.close()
            conn.close()

            if userName:
                return render_template('error.html', resultsSET="User Name Already Exists")

            #Add to DB
            con = sqlite3.connect(DB)
            cur = con.execute('''insert into user (username,email,pw_hash) values (?,?,?)''',[username,'', generate_password_hash(password)])
            con.commit()
            cur.close()
            con.close()
            flash('User Created')

            return redirect(url_for('admin_page'))

        else:
            return redirect(url_for('admin_login_page'))
    except Exception, e:
        return render_template('error.html', resultsSET=e)


app.secret_key = SECRETKEY


#main
if __name__ == '__main__':
    app.debug=False #reload on code changes. show traceback
    app.run(host='0.0.0.0',threaded=True)
