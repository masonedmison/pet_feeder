0.) On welcome screen-> Hit next
Set country and language and time zone-> Next
Enter very secure password->next
Choose wifi->Next
Enter wifi password->Next
Skip updates (will do later) -> Hit skip
Hit reboot


1.) Starter settings
Start->Preferences->Raspberry pi Config->Interfaces->Enable VNC and Remote GPIO->Hit OK
sudo apt-get update
sudo apt-get upgrade (this my awhile. can skip for now)

2.) Remove bloatware (not required, but frees up space)
sudo apt-get purge wolfram-engine
sudo apt-get purge sonic-pi
sudo apt-get purge minecraft-pi
sudo apt-get purge libreoffice*

sudo apt-get clean
sudo apt-get autoremove

reboot machine

3.) Permissions 
(Add under Allow members of group sudo to execute any command)
sudo visudo
www-data ALL=(root) NOPASSWD: ALL

Ctrl-x to Exit and 'Y' to save and Enter


4.) set up python & feeder site
(Probaby already installed but doesnt hurt to run again)
sudo apt-get install python-dev
sudo apt-get install git
sudo apt-get install sqlite3
sudo apt-get install virtualenv

sudo mkdir /var/www
sudo chmod 777 -R /var/www
cd /var/www
virtualenv feeder
cd feeder
source bin/activate
pip install flask
pip install RPi.GPIO
git clone https://gitlab.com/DiyPetFeeder/feeder.git
python /var/www/feeder/feeder/createDB.py 
sudo chmod 777 -R /var/www/feeder

5.) Set up apache
sudo apt-get install apache2
sudo apt-get install libapache2-mod-wsgi
sudo a2enmod headers
sudo systemctl restart apache2

6.) give run permission
sudo usermod -a -G gpio www-data


7.) Edit apache config

sudo nano /etc/apache2/sites-available/000-default.conf


Remove 7070 for previous test


Listen 7070
NameVirtualHost *:7070

ServerName feeder.chefched.com

WSGIDaemonProcess feeder user=www-data group=www-data threads=5
  WSGIScriptAlias / /var/www/feeder/feeder/feeder.wsgi


    WSGIProcessGroup feeder
    Order allow,deny
    Allow from all
    Require all granted
  


       Order allow,deny
       Allow from all
  

ErrorLog /var/www/feeder/feeder/logs/apacheError.log
  CustomLog /var/www/feeder/feeder/logs/apacheAccess.log combined

Ctrl-x to Exit and 'Y' to save and Enter


9.) Service Setup
--button
sudo cp /var/www/feeder/feeder/feederButtonService.sh /etc/init.d/
cd /etc/init.d/
sudo chmod 755 feederButtonService.sh
sudo update-rc.d feederButtonService.sh defaults
sudo /etc/init.d/feederButtonService.sh start
--time
sudo cp /var/www/feeder/feeder/feederTimeService.sh /etc/init.d/
cd /etc/init.d/
sudo chmod 755 feederTimeService.sh
sudo update-rc.d feederTimeService.sh defaults
sudo /etc/init.d/feederTimeService.sh start
--Reboot to take affect!
sudo reboot

10.) Logrotate
sudo apt-get install logrotate
verify running wih command "logrotate"
Configurations and default options /etc/logrotate.conf
append to bottom-> sudo nano /etc/logrotate.d/apache2

/var/www/feeder/feeder/logs/apacheAccess.log
/var/www/feeder/feeder/logs/apacheError.log
{
    rotate 3
    daily
    missingok
    notifempty
    copytruncate
    su root adm
}

Ctrl-x to Exit and 'Y' to save and Enter
Note*:to force run a schedule -> sudo logrotate --force /etc/logrotate.d
Notice the apache logs will be rotated at /var/www/feeder/feeder/logs
The button and time service logs will be roated automatically through service themselves


11.) Verify everything working
Open internet browser
type 127.0.0.1
verify website shows up 
click feed now button and verify it shows on latest list (nothing else will happen as we have not connected parts to pi yet)
type 127.0.0.1/admin
enter admin/ChangeMe!
Under 'user logins' click add user
Enter user name and secure password
When completed delete default admin user

12.) Configure router for external access and static internal ip
get ip address -> ifconfig
if using wireless look for ipaddress of wlan0 section
set router so this machine always gets this IP address. This varies by router. Looks for something like 'DHCP reservations'. Reserve current IP so the pi will always get this internal address 
Next set router to port forward internet traffic from you external ip address to this reserved internal ip address on port 80. Look for a section on your router named 'port forwarding'. All web requests will now go to the pi
Most Internet Service provider does not provider a static external IP so youll need a better way to keep track when it changes
Setting up DuckDns is one many options out there. It is free and the following example will show you how to set it up
If you have a different provider or plan on buying a domain address you can do that as well, just skip next section

13.) Setup Duck DNS (/home/pi/Sites/duckDNS)
Go to duckdns.org and create an account
On you main account page create a subdomain (for example catfeeder-> catfeeder.duckdns.org)
Next click on install on top navagation bar
select pi from 'operating systems' section and the new subdomain from drop down
copy long string from the output section ex.) echo url="https://www.duckdns.org/update?domains=catfeeder&token=12efabcdef-375c-1234-9e36-567890ac0a&ip=" | curl -k -o ~/duckdns/duck.log -K -

from home directory (ex. /home/pi) open terminal
mkdir duckdns 
cd duckdns
sudo nano duck.sh
echo url="https://www.duckdns.org/update?domains=cjg342&token=12efabcdef-375c-1234-9e36-567890ac0a&ip=" | curl -k -o /home/pi/duckDNS/duck.log -K -
Ctrl-x to Exit and 'Y' to save and Enter

sudo chmod 777 -R /home/pi/duckdns
crontab -e
select 2 if prompted
*/5 * * * * /home/pi/duckdns/duck.sh >/dev/null 2>&1
Ctrl-x to Exit and 'Y' to save and Enter
Test by run ./duck.sh
sudo service cron start
Now every 5 minutes this script will update your duckdns name (ex. catfeeder.duckdns.org) with you external ip address.
On the site you should now see you external IP address stored
You should now be able to access the website by visiting your address
Test on another machine locally as well as one not locally on your current wifi to verify everything is working as expected

14.) Connecting without monitor attached (headless display).
Since we enabled VNC earlier you no longer need to connect the pi to a monitor. You can connect to the pi from another machine using vnc
Install the vnc viewer on another device. When prompted for a machine to connect to enter the internal ip address followed by ':5900' (ex 192.168.1.182:5900)
As is this will only work locally on same wifi network. To connect remotely you could simply port forward "5900" to the pi like web traffic is.

15.) Set up motion IO (If have camera) (Seperate doc: motionCameraIO_Setup)








