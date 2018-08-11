#!/var/www/feeder/bin/python
import sys
sys.path.extend(['/var/www/feeder/feeder'])
import subprocess
import sqlite3
import os
from werkzeug import generate_password_hash

try:
    dbPath='/var/www/feeder/feeder/feeder.db'

    if os.path.isfile(dbPath):
        raise ValueError ('DB already exists. To create again first delete current copy') 
    else:
        print ('Creating DB. Please wait.')
        con = sqlite3.connect(dbPath)
        cur = con.execute("""CREATE TABLE feedtimes (feedid integer primary key autoincrement,feeddate string,feedtype integer);""")
        cur = con.execute("""CREATE TABLE feedtypes (feedtype integer primary key,description string);""")
        cur = con.execute("""CREATE TABLE loginLog (loginLogID integer primary key autoincrement,loginName text null,loginPW text null,loginDate text null);""")
        cur = con.execute("""CREATE TABLE user (user_id integer primary key autoincrement,username text not null,email text not null,pw_hash text not null);""")
        cur = con.execute("""insert into feedtypes (feedtype,description) values ("0","Scheduled");""")
        cur = con.execute("""insert into feedtypes (feedtype,description) values ("1","Button");""")
        cur = con.execute("""insert into feedtypes (feedtype,description) values ("2","Web Feed");""")
        cur = con.execute("""insert into feedtypes (feedtype,description) values ("3","Scheduled");""")
        cur = con.execute("""insert into feedtypes (feedtype,description) values ("4","Smart Home");""")
        cur = con.execute('''insert into user (username,email,pw_hash) values (?,?,?)''',['admin','',generate_password_hash('ChangeMe!')])
        cur = con.execute('''insert into feedtimes (feeddate,feedtype) select datetime('now'),1''')
        con.commit()
        cur.close()
        con.close()
        process = subprocess.Popen(["sudo", "chmod", "777", "-R", "/var/www/feeder"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        print ('DB created')
except Exception as e:
    print ('Error: '+str(e))