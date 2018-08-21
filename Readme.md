


### Setup Instructions:

1. Download and install latest 'Desktop' image of Raspbian onto Pi  
    - [Link to latest Desktop Raspbian image](https://www.raspberrypi.org/downloads/raspbian/)
    - [Link to installing image onto SD card](https://www.raspberrypi.org/documentation/installation/installing-images/README.md)

2. After pi turns on, run through welcome wizard
    - Set country, language, and time zone
    - Enter ***secure password***
    - Connect to wifi
    - Skip updates when prompted. This can takes awhile and will do later.
    - Reboot machine

3. After reboot, enable interfaces
    - Start> Preferences> Raspberry Pi Config> Interfaces
        - Enable VNC and Remote GPIO
    
4. Update system
    - Run following commands to from terminal to update system
        - ***This may take awhile. Can be run later.***
    ```shell
    sudo apt-get update
    sudo apt-get upgrade
    ```

5. Remove bloatware
    - Not required step. Can be skipped. Removes unneeded software that takes up alot of SD card space  
    ```shell
    sudo apt-get purge wolfram-engine
    sudo apt-get purge sonic-pi
    sudo apt-get purge minecraft-pi
    sudo apt-get purge libreoffice*
    sudo apt-get clean
    sudo apt-get autoremove
    ```
    - Restart machine
    ```shell
    sudo reboot
    ```


5. Remove bloatware
    - Not required step. Can be skipped. Removes unneeded software that takes up alot of SD card space  
```shell
sudo apt-get purge wolfram-engine
sudo apt-get purge sonic-pi
sudo apt-get purge minecraft-pi
sudo apt-get purge libreoffice*
sudo apt-get clean
sudo apt-get autoremove
```

5. Remove bloatware
- Not required step. Can be skipped. Removes unneeded software that takes up alot of SD card space  
```shell
sudo apt-get purge wolfram-engine
sudo apt-get purge sonic-pi
sudo apt-get purge minecraft-pi
sudo apt-get purge libreoffice*
sudo apt-get clean
sudo apt-get autoremove
```


5. reeeeeeeeeeeeeeeeeeee
     ```shell
    sudo reboot
    ```   

5. reeeeeeeeeeeeeeeeeeee
     ```shell
    sudo apt-get purge wolfram-engine
    sudo apt-get purge sonic-pi
    sudo apt-get purge minecraft-pi
    sudo apt-get purge libreoffice*
    sudo apt-get clean
    sudo apt-get autoremove
    ```   
    
6. Install additional software
    ```shell
    sudo apt-get install python-dev
    sudo apt-get install git
    sudo apt-get install sqlite3
    sudo apt-get install virtualenv
    sudo apt-get install logrotate
    sudo apt-get install apache2
    sudo apt-get install libapache2-mod-wsgi
    sudo a2enmod headers
    sudo systemctl restart apache2
    ```

7. Set up feeder website
    - From terminal
    ```shell
    sudo mkdir /var/www
    sudo chmod 777 -R /var/www
    cd /var/www
    virtualenv feeder
    cd feeder
    source bin/activate
    pip install flask
    pip install RPi.GPIO
    git clone https://gitlab.com/DiyPetFeeder/feeder.git
    cd feeder
    python createFiles.py 
    ```  
    
8. Set up permissions 
    - From terminal open Sudoers file
    ```shell
    sudo visudo
    ```
    - Add under section "Allow members of group sudo to execute any command"
    ```text
    www-data ALL=(root) NOPASSWD: ALL
    ```
    - Exit file: Ctrl-x> 'Y'> Enter to confirm
    - From terminal
    ```shell
    sudo usermod -a -G gpio www-data
    sudo usermod -aG video www-data
    sudo systemctl apache2 restart
    ```

9. Configure Apache
    - From terminal
    ```shell
    sudo nano /etc/apache2/sites-available/000-default.conf
    ```
    - Replace file with following. Update ServerName as needed.
    ```text
    Listen 80
    NameVirtualHost *:80
    
    ServerName UpdateYourServername.com
    
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
    ```
    - Exit file: Ctrl-x> 'Y'> Enter to confirm

10. Setup feeder background button service
    - From terminal
    ```shell
    sudo cp /var/www/feeder/feeder/feederButtonService.sh /etc/init.d/
    cd /etc/init.d/
    sudo chmod 755 feederButtonService.sh
    sudo update-rc.d feederButtonService.sh defaults
    sudo /etc/init.d/feederButtonService.sh start
    ```

11. Setup feeder background time service
    - From terminal
    ```shell
    sudo cp /var/www/feeder/feeder/feederTimeService.sh /etc/init.d/
    cd /etc/init.d/
    sudo chmod 755 feederTimeService.sh
    sudo update-rc.d feederTimeService.sh defaults
    sudo /etc/init.d/feederTimeService.sh start
    ```

12. Restart system
    ```shell
    sudo reboot
    ```

13. Configure Logrotate
    - From terminal
    ```shell
    sudo nano /etc/logrotate.d/apache2
    ```
    - Append to bottom of file
    ```text
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
    ```
    - Exit file: Ctrl-x> 'Y'> Enter to confirm
    - Note: To force run a test to ensure logs are rotating correctly execute following from terminal
    ```shell
    sudo logrotate --force /etc/logrotate.d
    ```
    - Notice the apache logs will be rotated at /var/www/feeder/feeder/logs
    -   Note: button and time service log rotation are handled within service themselves

14. Verify feeder site is working
    - Open internet browser
    - Type [127.0.0.1](http://127.0.0.1/) into navagation bar
    - Verify website shows up 
    - Click feed now button and verify feed time is poplated in site
        - Nothing else will happen if hardware is not connected yet
    - Type [127.0.0.1/admin](127.0.0.1/admin) into navagation bar
        - Default user/password is admin/ChangeMe!
        - Under 'user logins' click add user
        - Enter user name and secure password
        - Login to admin page again and delete default user
        - Verify time and button services are running
            - Ok for other services to not be working

15. Configure router to assign static internal IP to pi
    - From terminal type
    ```shell
    ifconfig
    ```
    - Assuming using built in wireless write down ipaddress of wlan0 section
        - Typically starts with 192.168.
    - Configure your router so pi always gets assigned this IP address 
        - This varies by router. Check your routers documentation
            - Typically under a section similar sounding to 'DHCP' or 'Reservations'
   
16. Configure router to point external web traffic to pi
    - From router port forward internet traffic (port 80) to reserved internal ip address set above
    - This varies by router. Check your routers documentation
        - Look for a section similar sounding to 'port forwarding'

17. Configure DNS
    - To check current external IP
        - Go to Google and search 'my ip address'. This is your external IP address
        ![Find public IP](/home/testbox/ipAddress.png)
    - Most ISP do not provider a static external IP. So you will need a better way to keep track when it changes
    - Setting up DuckDns is one many options out there. It is free and the following example will show you how to set it up.
    - If you have a different provider or plan on buying a domain address you can do that as well, just skip next section

18. Setup Duck DNS
    - Go to [duckdns.org](http://www.duckdns.org/) and create an account 
    - On you main account page create a subdomain (for example petfeeder > petfeeder.duckdns.org)
    - Next click on install on top navagation bar
    - Select pi from 'operating systems' section and the new subdomain from drop down
    - Copy long string from the output section 
    ```text
    echo url="https://www.duckdns.org/update?domains=petfeeder&token=23feabcdef-375c-1234-9e36-567890ac0a&ip=" | curl -k -o ~/duckdns/duck.log -K -
    ```
    - From home directory (ex. /home/pi) open terminal
    ```shell
    mkdir duckdns 
    cd duckdns
    sudo nano duck.sh
    ```
    - Paster text copied above into duck.sh 
    ```text
    echo url="https://www.duckdns.org/update?domains=petfeeder&token=23feabcdef-375c-1234-9e36-567890ac0a&ip=" | curl -k -o ~/duckdns/duck.log -K -
    ```
    - Exit file: Ctrl-x> 'Y'> Enter to confirm
    - From terminal
    ```shell
    sudo chmod 777 -R /home/pi/duckdns
    crontab -e
    ```
    -Select 2 if prompted
    -Paster following into file
    ```text
    */5 * * * * /home/pi/duckdns/duck.sh >/dev/null 2>&1
    ```
    - Exit file: Ctrl-x> 'Y'> Enter to confirm
    - To test run from home directory terminal
    ```shell
    ./duck.sh
    sudo service cron start
    ```
    - Now, every 5 minutes, duck dns script update your duckdns name (ex. petfeeder.duckdns.org) with you external ip address.
    - On the [duckdns.org](http://www.duckdns.org/) site you should now see you external IP address stored
    - You will no longer need to know if/when you IP address changes. You can externally visit the feeder site through this link (ex. petfeeder.duckdns.org)
    - You should now be able to access the website by visiting your address
    - Test on another machine locally as well as one not locally on your current wifi to verify everything is working as expected

19. Connecting to pi without monitor (headless display).
    - With VNC enabled earlier you no longer need to connect the pi to a monitor. You can connect to the pi from another machine using vnc
    - To do this Install the vnc viewer on another device. 
        - VNC install found [here](https://www.realvnc.com/en/connect/download/viewer/)
    - After installed, when prompted for a machine to connect to enter the internal ip address followed by ':5900' (ex 192.168.1.182:5900)
    - Using internal IP address this will only work locally on same wifi network 
        - To connect remotely you could simply port forward "5900" to the pi like web traffic is

20. Set up motion IO 
    - If have camera installed on pi the following steps will configure software to capture video
        - Pet feeder site is designed to work with motion IO only as of now
    - To set up motion IO, from terminal home directory (ex. /home/pi)
    ```shell
    wget github.com/Motion-Project/motion/releases/download/release-4.1.1/pi_jessie_motion_4.1.1-1_armhf.deb
    sudo apt-get install gdebi-core
    sudo gdebi pi_stretch_motion_4.1.1-1_armhf.deb
    mkdir ~/.motion
    cp /etc/motion/motion.conf ~/.motion/motion.conf
    sudo nano ~/.motion/motion.conf
    ```
    With config open in nano tweak config to your desired modifcations to get desired performance. A few suggestions include
    ```text
    width 320 > width 640
    height 240 > height 480
    framerate 2 > framerate 20
    post_capture 0 > post_capture 100
    max_movie_time 0 > max_movie_time 120
    target_dir /tmp/motion > target_dir /var/www/feeder/feeder/static/video
    stream_quality 50 > stream_quality 80
    stream_maxrate 1 > stream_maxrate 15
    stream_localhost on > stream_localhost off
    ```
    - Open /etc/modules-load.d /etc/modules
    ```shell
    sudo nano /etc/modules
    ``` 
    - Add line
    ```text
    bcm2835-v4l2
    ```
    - From terminal open
    ```shell
    sudo nano /etc/rc.local
    ```
    - Add command below the comment, but leave the line exit 0 at the end
   	```text
   	motion -c /home/pi/.motion/motion.conf
   	```

    - To disable pi camera red light, from terminal
    ```shell
    sudo nano /boot/config.txt
    ```
    - Add to last line
    ```text
    disable_camera_led=1
    ```







































