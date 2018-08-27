### Setup Instructions:

1. On a second machine, with SD card writing capabilities, download and install latest 'Desktop' image of Raspbian onto Pi
    - Directions written for 'Desktop' and NOT 'Lite' version of Raspbian  
    - [Link to latest Desktop Raspbian image](https://www.raspberrypi.org/downloads/raspbian/)
    - [Link to installing image onto SD card](https://www.raspberrypi.org/documentation/installation/installing-images/README.md)
    - [Link to Etcher- free SD card flashing software](https://etcher.io/)

2. After SD card is installed and Pi boots, run through welcome wizard
    - Set country, language, and time zone
    - Enter ***secure password***
    - Connect to wifi
    - Skip updates when prompted. This can takes awhile and will do later.
    - Restart machine

3. After reboot, enable interfaces
    - Start (Raspberry icon)> Preferences> Raspberry Pi Configuration
        - On 'System' tab adjust 'Resolution' if needed
        - On 'Interfaces' tab enable 'VNC' and 'Remote GPIO'
        - Restart if needed
    
4. Update system
    - From terminal run commands to update system
	- A shortcut to terminal should be on taskbar, otherwise Start> Accessories> Terminal
        - ***This may take awhile depending wifi and SD card speed***
    
    ```shell
    sudo apt-get update
    sudo apt-get upgrade
    sudo reboot
    ```

5. Remove bloatware
    - Not required step. Can be skipped. Removes unneeded software that takes up alot of SD card space  
    
    ```shell
    sudo apt-get purge wolfram-engine
    sudo apt-get purge libreoffice*
    sudo apt-get purge sonic-pi
    sudo apt-get purge minecraft-pi
    sudo apt-get clean
    sudo apt-get autoremove
    ```
    - Restart machine
    
    ```shell
    sudo reboot
    ```

6. Install additional software
    - From terminal
    
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
    sudo mkdir /var/www -p
    cd /var/www
    sudo virtualenv feeder
    sudo chown -R pi:www-data /var/www/feeder/
    sudo chmod 750 -R /var/www/feeder/
    #sudo chmod g+s /var/www/feeder/
    cd /var/www/feeder/
    source bin/activate
    pip install flask
    pip install RPi.GPIO
    git clone https://gitlab.com/DiyPetFeeder/feeder.git
    cd /var/www/feeder/feeder/
    python createFiles.py 
    sudo chown -R pi:www-data /var/www/feeder/
    sudo chmod 770 -R /var/www/feeder/feeder/
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
    sudo usermod -aG gpio www-data
    sudo usermod -aG video www-data
    ```

9. Configure Apache
    - From terminal
    
    ```shell
    sudo nano /etc/apache2/sites-available/000-default.conf
    ```
    - Replace all text in file with following. ServerName can be updated later.
    
    ```text
    <VirtualHost *:80>
    ServerName feeder.duckdns.org
    
    WSGIDaemonProcess feeder user=www-data group=www-data threads=5
    WSGIScriptAlias / /var/www/feeder/feeder/feeder.wsgi

    <Directory /var/www/feeder/feeder>
    WSGIProcessGroup feeder
    Order allow,deny
    Allow from all
    Require all granted
    </Directory>

    <Files feeder.wsgi>
    Order allow,deny
    Allow from all
    </Files>

    ErrorLog /var/www/feeder/feeder/logs/apacheError.log
    CustomLog /var/www/feeder/feeder/logs/apacheAccess.log combined
    </VirtualHost>
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
    -   Note: button and time service log rotation are handled within service themselves and will not rotate with this command

14. Verify feeder site is working
    - Open internet browser
    - Type [127.0.0.1](http://127.0.0.1/) into navigation bar
    - Verify website shows up 
    - Click feed now button and verify feed time is poplated in site
        - Nothing else will happen if hardware is not connected yet
    - Type [127.0.0.1/admin](127.0.0.1/admin) into navigation bar
        - Default user/password is admin/ChangeMe!
        - Under 'user logins' click add user
        - Enter user name and secure password
        - Login to admin page again with new user and delete original default user
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
    - ***Example below. Copy your actual string from site!*** 
    
    ```text
    echo url="https://www.duckdns.org/update?domains=YourCustomDomainHere&token=23feabcdef-375c-1234-9e36-567890ac0a&ip=" | curl -k -o ~/duckdns/duck.log -K -
    ```
    - From home directory (ex. /home/pi) open terminal
    
    ```shell
    mkdir duckdns 
    cd duckdns
    sudo nano duck.sh
    ```
    - Paste 'echo url' text copied above into duck.sh 
    - Exit file: Ctrl-x> 'Y'> Enter to confirm
    - From terminal
    
    ```shell
    sudo chown -R pi:pi /home/pi/duckdns/
    sudo chmod 700 /home/pi/duckdns/duck.sh
    crontab -e
    ```
    -Select 2 if prompted
    -Paste following into file
    
    ```text
    */5 * * * * /home/pi/duckdns/duck.sh >/dev/null 2>&1
    ```
    - Exit file: Ctrl-x> 'Y'> Enter to confirm
    - To test run from home directory terminal
    
    ```shell
    cd /home/pi/duckdns/
    ./duck.sh
    cat /home/pi/duckdns/duck.log
    sudo service cron start
    ```
    - If KO is returned versus OK, then there is an issue. Check token and domain are correct.
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
        - Currently designed to only work with motion IO
    - To set up motion IO, from terminal home directory (ex. /home/pi)
    
    ```shell
    wget github.com/Motion-Project/motion/releases/download/release-4.1.1/pi_stretch_motion_4.1.1-1_armhf.deb
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
    - Open /etc/modules
    
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
    - Add command right above line 'exit 0' at the end of file
   	
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





































<html><head><meta content="text/html; charset=UTF-8" http-equiv="content-type"><style type="text/css">@import url('https://themes.googleusercontent.com/fonts/css?kit=lhDjYqiy3mZ0x6ROQEUoUw');ol.lst-kix_rnq49x5ii498-1.start{counter-reset:lst-ctn-kix_rnq49x5ii498-1 0}ol.lst-kix_g5krlfpm8sk2-2.start{counter-reset:lst-ctn-kix_g5krlfpm8sk2-2 0}.lst-kix_g5krlfpm8sk2-4>li{counter-increment:lst-ctn-kix_g5krlfpm8sk2-4}.lst-kix_rnq49x5ii498-0>li{counter-increment:lst-ctn-kix_rnq49x5ii498-0}ol.lst-kix_p8d3kf13cskb-3.start{counter-reset:lst-ctn-kix_p8d3kf13cskb-3 0}ol.lst-kix_g5krlfpm8sk2-7.start{counter-reset:lst-ctn-kix_g5krlfpm8sk2-7 0}ol.lst-kix_p8d3kf13cskb-6.start{counter-reset:lst-ctn-kix_p8d3kf13cskb-6 0}ol.lst-kix_p8d3kf13cskb-0.start{counter-reset:lst-ctn-kix_p8d3kf13cskb-0 0}.lst-kix_p8d3kf13cskb-1>li{counter-increment:lst-ctn-kix_p8d3kf13cskb-1}.lst-kix_g5krlfpm8sk2-5>li{counter-increment:lst-ctn-kix_g5krlfpm8sk2-5}.lst-kix_rnq49x5ii498-2>li{counter-increment:lst-ctn-kix_rnq49x5ii498-2}ol.lst-kix_rnq49x5ii498-7.start{counter-reset:lst-ctn-kix_rnq49x5ii498-7 0}.lst-kix_g5krlfpm8sk2-2>li{counter-increment:lst-ctn-kix_g5krlfpm8sk2-2}ol.lst-kix_rnq49x5ii498-4.start{counter-reset:lst-ctn-kix_rnq49x5ii498-4 0}ol.lst-kix_rnq49x5ii498-3.start{counter-reset:lst-ctn-kix_rnq49x5ii498-3 0}ol.lst-kix_g5krlfpm8sk2-4.start{counter-reset:lst-ctn-kix_g5krlfpm8sk2-4 0}ol.lst-kix_p8d3kf13cskb-2.start{counter-reset:lst-ctn-kix_p8d3kf13cskb-2 0}.lst-kix_g5krlfpm8sk2-8>li{counter-increment:lst-ctn-kix_g5krlfpm8sk2-8}ol.lst-kix_p8d3kf13cskb-4{list-style-type:none}ol.lst-kix_p8d3kf13cskb-5{list-style-type:none}ol.lst-kix_g5krlfpm8sk2-8.start{counter-reset:lst-ctn-kix_g5krlfpm8sk2-8 0}ol.lst-kix_p8d3kf13cskb-6{list-style-type:none}ol.lst-kix_p8d3kf13cskb-7{list-style-type:none}ol.lst-kix_p8d3kf13cskb-8{list-style-type:none}.lst-kix_g5krlfpm8sk2-1>li{counter-increment:lst-ctn-kix_g5krlfpm8sk2-1}.lst-kix_rnq49x5ii498-3>li{counter-increment:lst-ctn-kix_rnq49x5ii498-3}ol.lst-kix_p8d3kf13cskb-0{list-style-type:none}ol.lst-kix_p8d3kf13cskb-1{list-style-type:none}.lst-kix_g5krlfpm8sk2-7>li{counter-increment:lst-ctn-kix_g5krlfpm8sk2-7}ol.lst-kix_p8d3kf13cskb-2{list-style-type:none}ol.lst-kix_p8d3kf13cskb-3{list-style-type:none}ol.lst-kix_rnq49x5ii498-2.start{counter-reset:lst-ctn-kix_rnq49x5ii498-2 0}.lst-kix_p8d3kf13cskb-0>li{counter-increment:lst-ctn-kix_p8d3kf13cskb-0}ol.lst-kix_p8d3kf13cskb-1.start{counter-reset:lst-ctn-kix_p8d3kf13cskb-1 0}.lst-kix_p8d3kf13cskb-3>li{counter-increment:lst-ctn-kix_p8d3kf13cskb-3}ol.lst-kix_g5krlfpm8sk2-3.start{counter-reset:lst-ctn-kix_g5krlfpm8sk2-3 0}.lst-kix_p8d3kf13cskb-6>li{counter-increment:lst-ctn-kix_p8d3kf13cskb-6}ol.lst-kix_p8d3kf13cskb-8.start{counter-reset:lst-ctn-kix_p8d3kf13cskb-8 0}ol.lst-kix_g5krlfpm8sk2-6.start{counter-reset:lst-ctn-kix_g5krlfpm8sk2-6 0}.lst-kix_rnq49x5ii498-6>li{counter-increment:lst-ctn-kix_rnq49x5ii498-6}ol.lst-kix_p8d3kf13cskb-7.start{counter-reset:lst-ctn-kix_p8d3kf13cskb-7 0}.lst-kix_p8d3kf13cskb-4>li:before{content:"" counter(lst-ctn-kix_p8d3kf13cskb-4,lower-latin) ". "}.lst-kix_g5krlfpm8sk2-2>li:before{content:"" counter(lst-ctn-kix_g5krlfpm8sk2-2,lower-roman) ". "}.lst-kix_rnq49x5ii498-4>li:before{content:"" counter(lst-ctn-kix_rnq49x5ii498-4,lower-latin) ". "}.lst-kix_rnq49x5ii498-5>li:before{content:"" counter(lst-ctn-kix_rnq49x5ii498-5,lower-roman) ". "}ol.lst-kix_rnq49x5ii498-5.start{counter-reset:lst-ctn-kix_rnq49x5ii498-5 0}.lst-kix_p8d3kf13cskb-2>li:before{content:"" counter(lst-ctn-kix_p8d3kf13cskb-2,lower-roman) ". "}.lst-kix_p8d3kf13cskb-3>li:before{content:"" counter(lst-ctn-kix_p8d3kf13cskb-3,decimal) ". "}.lst-kix_g5krlfpm8sk2-3>li:before{content:"" counter(lst-ctn-kix_g5krlfpm8sk2-3,decimal) ". "}.lst-kix_g5krlfpm8sk2-4>li:before{content:"" counter(lst-ctn-kix_g5krlfpm8sk2-4,lower-latin) ". "}.lst-kix_rnq49x5ii498-7>li:before{content:"" counter(lst-ctn-kix_rnq49x5ii498-7,lower-latin) ". "}.lst-kix_p8d3kf13cskb-5>li{counter-increment:lst-ctn-kix_p8d3kf13cskb-5}.lst-kix_p8d3kf13cskb-0>li:before{content:"" counter(lst-ctn-kix_p8d3kf13cskb-0,decimal) ". "}.lst-kix_p8d3kf13cskb-1>li:before{content:"" counter(lst-ctn-kix_p8d3kf13cskb-1,lower-latin) ". "}.lst-kix_g5krlfpm8sk2-5>li:before{content:"" counter(lst-ctn-kix_g5krlfpm8sk2-5,lower-roman) ". "}.lst-kix_g5krlfpm8sk2-6>li:before{content:"" counter(lst-ctn-kix_g5krlfpm8sk2-6,decimal) ". "}.lst-kix_rnq49x5ii498-6>li:before{content:"" counter(lst-ctn-kix_rnq49x5ii498-6,decimal) ". "}.lst-kix_rnq49x5ii498-8>li:before{content:"" counter(lst-ctn-kix_rnq49x5ii498-8,lower-roman) ". "}ol.lst-kix_rnq49x5ii498-8.start{counter-reset:lst-ctn-kix_rnq49x5ii498-8 0}ol.lst-kix_p8d3kf13cskb-4.start{counter-reset:lst-ctn-kix_p8d3kf13cskb-4 0}.lst-kix_p8d3kf13cskb-5>li:before{content:"" counter(lst-ctn-kix_p8d3kf13cskb-5,lower-roman) ". "}.lst-kix_g5krlfpm8sk2-1>li:before{content:"" counter(lst-ctn-kix_g5krlfpm8sk2-1,lower-latin) ". "}.lst-kix_rnq49x5ii498-5>li{counter-increment:lst-ctn-kix_rnq49x5ii498-5}.lst-kix_p8d3kf13cskb-6>li:before{content:"" counter(lst-ctn-kix_p8d3kf13cskb-6,decimal) ". "}.lst-kix_p8d3kf13cskb-7>li:before{content:"" counter(lst-ctn-kix_p8d3kf13cskb-7,lower-latin) ". "}.lst-kix_g5krlfpm8sk2-0>li:before{content:"" counter(lst-ctn-kix_g5krlfpm8sk2-0,decimal) ". "}ol.lst-kix_g5krlfpm8sk2-0{list-style-type:none}.lst-kix_p8d3kf13cskb-4>li{counter-increment:lst-ctn-kix_p8d3kf13cskb-4}ol.lst-kix_g5krlfpm8sk2-3{list-style-type:none}.lst-kix_p8d3kf13cskb-8>li:before{content:"" counter(lst-ctn-kix_p8d3kf13cskb-8,lower-roman) ". "}ol.lst-kix_g5krlfpm8sk2-4{list-style-type:none}ol.lst-kix_g5krlfpm8sk2-1{list-style-type:none}ol.lst-kix_g5krlfpm8sk2-1.start{counter-reset:lst-ctn-kix_g5krlfpm8sk2-1 0}ol.lst-kix_g5krlfpm8sk2-2{list-style-type:none}.lst-kix_rnq49x5ii498-8>li{counter-increment:lst-ctn-kix_rnq49x5ii498-8}.lst-kix_p8d3kf13cskb-7>li{counter-increment:lst-ctn-kix_p8d3kf13cskb-7}ol.lst-kix_g5krlfpm8sk2-7{list-style-type:none}ol.lst-kix_g5krlfpm8sk2-8{list-style-type:none}ol.lst-kix_g5krlfpm8sk2-5{list-style-type:none}ol.lst-kix_g5krlfpm8sk2-6{list-style-type:none}ol.lst-kix_rnq49x5ii498-6.start{counter-reset:lst-ctn-kix_rnq49x5ii498-6 0}ol.lst-kix_rnq49x5ii498-7{list-style-type:none}ol.lst-kix_rnq49x5ii498-8{list-style-type:none}ol.lst-kix_rnq49x5ii498-0.start{counter-reset:lst-ctn-kix_rnq49x5ii498-0 0}ol.lst-kix_rnq49x5ii498-3{list-style-type:none}ol.lst-kix_rnq49x5ii498-4{list-style-type:none}ol.lst-kix_rnq49x5ii498-5{list-style-type:none}.lst-kix_p8d3kf13cskb-8>li{counter-increment:lst-ctn-kix_p8d3kf13cskb-8}ol.lst-kix_rnq49x5ii498-6{list-style-type:none}ol.lst-kix_rnq49x5ii498-0{list-style-type:none}ol.lst-kix_rnq49x5ii498-1{list-style-type:none}ol.lst-kix_rnq49x5ii498-2{list-style-type:none}ol.lst-kix_g5krlfpm8sk2-0.start{counter-reset:lst-ctn-kix_g5krlfpm8sk2-0 0}.lst-kix_p8d3kf13cskb-2>li{counter-increment:lst-ctn-kix_p8d3kf13cskb-2}ol.lst-kix_g5krlfpm8sk2-5.start{counter-reset:lst-ctn-kix_g5krlfpm8sk2-5 0}.lst-kix_g5krlfpm8sk2-6>li{counter-increment:lst-ctn-kix_g5krlfpm8sk2-6}.lst-kix_rnq49x5ii498-7>li{counter-increment:lst-ctn-kix_rnq49x5ii498-7}.lst-kix_g5krlfpm8sk2-7>li:before{content:"" counter(lst-ctn-kix_g5krlfpm8sk2-7,lower-latin) ". "}.lst-kix_g5krlfpm8sk2-8>li:before{content:"" counter(lst-ctn-kix_g5krlfpm8sk2-8,lower-roman) ". "}.lst-kix_rnq49x5ii498-1>li{counter-increment:lst-ctn-kix_rnq49x5ii498-1}.lst-kix_rnq49x5ii498-4>li{counter-increment:lst-ctn-kix_rnq49x5ii498-4}.lst-kix_g5krlfpm8sk2-0>li{counter-increment:lst-ctn-kix_g5krlfpm8sk2-0}.lst-kix_g5krlfpm8sk2-3>li{counter-increment:lst-ctn-kix_g5krlfpm8sk2-3}.lst-kix_rnq49x5ii498-3>li:before{content:"" counter(lst-ctn-kix_rnq49x5ii498-3,decimal) ". "}.lst-kix_rnq49x5ii498-2>li:before{content:"" counter(lst-ctn-kix_rnq49x5ii498-2,lower-roman) ". "}.lst-kix_rnq49x5ii498-1>li:before{content:"" counter(lst-ctn-kix_rnq49x5ii498-1,lower-latin) ". "}ol.lst-kix_p8d3kf13cskb-5.start{counter-reset:lst-ctn-kix_p8d3kf13cskb-5 0}.lst-kix_rnq49x5ii498-0>li:before{content:"" counter(lst-ctn-kix_rnq49x5ii498-0,decimal) ". "}ol{margin:0;padding:0}table td,table th{padding:0}.c1{border-right-style:solid;padding:5pt 5pt 5pt 5pt;border-bottom-color:#000000;border-top-width:0pt;border-right-width:0pt;border-left-color:#000000;vertical-align:top;border-right-color:#000000;border-left-width:0pt;border-top-style:solid;background-color:#f0f0f0;border-left-style:solid;border-bottom-width:0pt;width:468pt;border-top-color:#000000;border-bottom-style:solid}.c19{color:#000000;font-weight:400;text-decoration:none;vertical-align:baseline;font-size:16pt;font-family:"Arial";font-style:normal}.c3{padding-top:0pt;padding-bottom:0pt;line-height:1.15;orphans:2;widows:2;text-align:left;height:11pt}.c0{color:#000000;font-weight:400;text-decoration:none;vertical-align:baseline;font-size:11pt;font-family:"Arial";font-style:normal}.c10{color:#000000;font-weight:400;text-decoration:none;vertical-align:baseline;font-size:26pt;font-family:"Arial";font-style:normal}.c17{color:#434343;font-weight:400;text-decoration:none;vertical-align:baseline;font-size:14pt;font-family:"Arial";font-style:normal}.c21{padding-top:0pt;padding-bottom:3pt;line-height:1.15;page-break-after:avoid;text-align:left}.c8{padding-top:16pt;padding-bottom:4pt;line-height:1.15;page-break-after:avoid;text-align:left}.c18{padding-top:18pt;padding-bottom:6pt;line-height:1.15;page-break-after:avoid;text-align:left}.c12{margin-left:108pt;padding-left:0pt;orphans:2;widows:2}.c11{border-spacing:0;border-collapse:collapse;margin-right:auto}.c15{text-decoration-skip-ink:none;-webkit-text-decoration-skip:none;color:#1155cc;text-decoration:underline}.c4{background-color:#f0f0f0;font-family:"Consolas";color:#444444;font-weight:400}.c9{margin-left:72pt;padding-left:0pt;orphans:2;widows:2}.c6{padding-top:0pt;padding-bottom:0pt;line-height:1.15;text-align:left}.c16{background-color:#ffffff;max-width:468pt;padding:72pt 72pt 72pt 72pt}.c14{margin-left:36pt;padding-left:0pt}.c13{orphans:2;widows:2}.c5{padding:0;margin:0}.c7{color:inherit;text-decoration:inherit}.c2{height:0pt}.c20{margin-left:72pt}.title{padding-top:0pt;color:#000000;font-size:26pt;padding-bottom:3pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;orphans:2;widows:2;text-align:left}.subtitle{padding-top:0pt;color:#666666;font-size:15pt;padding-bottom:16pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;orphans:2;widows:2;text-align:left}li{color:#000000;font-size:11pt;font-family:"Arial"}p{margin:0;color:#000000;font-size:11pt;font-family:"Arial"}h1{padding-top:20pt;color:#000000;font-size:20pt;padding-bottom:6pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;orphans:2;widows:2;text-align:left}h2{padding-top:18pt;color:#000000;font-size:16pt;padding-bottom:6pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;orphans:2;widows:2;text-align:left}h3{padding-top:16pt;color:#434343;font-size:14pt;padding-bottom:4pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;orphans:2;widows:2;text-align:left}h4{padding-top:14pt;color:#666666;font-size:12pt;padding-bottom:4pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;orphans:2;widows:2;text-align:left}h5{padding-top:12pt;color:#666666;font-size:11pt;padding-bottom:4pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;orphans:2;widows:2;text-align:left}h6{padding-top:12pt;color:#666666;font-size:11pt;padding-bottom:4pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;font-style:italic;orphans:2;widows:2;text-align:left}</style></head><body class="c16"><p class="c21 title" id="h.fepwnrud2nf7"><span class="c10">Overview</span></p><p class="c6 c13"><span class="c0">Building DiyPetFeeder can be separated into the main section listed below. Each section has detailed instructions which follow. Sections should be completed in order below. </span></p><ol class="c5 lst-kix_rnq49x5ii498-0 start" start="1"><li class="c6 c13 c14"><span class="c0">Gather materials and tools</span></li><li class="c6 c14 c13"><span class="c0">Setup Pi</span></li><li class="c6 c14 c13"><span class="c0">Setup Wired Components</span></li><li class="c6 c14 c13"><span class="c0">Setup Box</span></li><li class="c6 c14 c13"><span class="c0">Final Assembly</span></li></ol><h2 class="c18" id="h.koxak42scqd"><span class="c19">Materials and Tools</span></h2><p class="c6 c13"><span class="c0">Before starting the following materials and tools are needed to construct DiyPetFeeder. Links are attached for suggestions on where to purchase. It is encouraged to exact product as subsequent directions are tailored toward these specific products. Items marked as optional are not needed to fully build DiyPetFeeder. &nbsp;However, they will greatly simplify the building process and are suggested. </span></p><h3 class="c8" id="h.djq63ltqnipq"><span class="c17">Required Materials</span></h3><h3 class="c8" id="h.xqpx74n6x87d"><span class="c17">Optional Materials</span></h3><h2 class="c18" id="h.x76ni6rgc60x"><span class="c19">Setup Pi</span></h2><ol class="c5 lst-kix_g5krlfpm8sk2-0 start" start="1"><li class="c6 c14 c13"><span class="c0">On a second machine, with SD card writing capabilities, download and install latest &#39;Desktop&#39; image of Raspbian onto Pi</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1 start" start="1"><li class="c9 c6"><span class="c0">Ensure image is &#39;Desktop&#39; and not &#39;Lite&#39; version of Raspbian &nbsp;</span></li><li class="c9 c6"><span class="c15"><a class="c7" href="https://www.google.com/url?q=https://www.raspberrypi.org/downloads/raspbian/&amp;sa=D&amp;ust=1535406325048000">Link to latest Desktop Raspbian image</a></span></li><li class="c9 c6"><span class="c15"><a class="c7" href="https://www.google.com/url?q=https://www.raspberrypi.org/documentation/installation/installing-images/README.md&amp;sa=D&amp;ust=1535406325048000">Link to installing image onto SD card</a></span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-2 start" start="1"><li class="c12 c6"><span class="c15"><a class="c7" href="https://www.google.com/url?q=https://etcher.io/&amp;sa=D&amp;ust=1535406325048000">Link to Etcher- free SD card flashing software</a></span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-0" start="2"><li class="c6 c14 c13"><span class="c0">After SD card is flashed install into Pi connect Pi to monitor via HDMi cable </span></li><li class="c6 c14 c13"><span class="c0">Connect power to Pi. Pi will boot and raspberry should display on screen</span></li><li class="c6 c14 c13"><span class="c0">After Pi finishes initial boot, run through welcome wizard</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1 start" start="1"><li class="c9 c6"><span class="c0">Set country, language, and time zone</span></li><li class="c9 c6"><span class="c0">Enter ***secure password***</span></li><li class="c9 c6"><span class="c0">Connect to wifi</span></li><li class="c9 c6"><span class="c0">Skip updates when prompted</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-2 start" start="1"><li class="c12 c6"><span class="c0">Occasionally this freezes setup. Will be run later from terminal</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="5"><li class="c9 c6"><span class="c0">Restart machine when prompted</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-0" start="5"><li class="c6 c14 c13"><span class="c0">After reboot, enable interfaces</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1 start" start="1"><li class="c9 c6"><span class="c0">Start (Raspberry icon)&gt; Preferences&gt; Raspberry Pi Configuration</span></li><li class="c9 c6"><span class="c0">(Optional) On &#39;System&#39; tab adjust &#39;Resolution&#39; if display not to your liking</span></li><li class="c9 c6"><span class="c0">(Required) On &#39;Interfaces&#39; tab enable &#39;VNC&#39; and &#39;Remote GPIO&#39;</span></li><li class="c9 c6"><span class="c0">Restart if prompted</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-0" start="6"><li class="c6 c14 c13"><span class="c0">Update system</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1 start" start="1"><li class="c9 c6"><span class="c0">From terminal run commands to update system</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-2 start" start="1"><li class="c12 c6"><span class="c0">A shortcut to terminal should be on taskbar</span></li><li class="c12 c6"><span class="c0">Otherwise Start&gt; Accessories&gt; Terminal</span></li><li class="c12 c6"><span>T</span><span class="c0">his may take awhile depending wifi and SD card speed</span></li></ol><a id="t.3879898e69a379a59959aad9c40ec4d079339754"></a><a id="t.0"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp;</span><span class="c4">&nbsp; &nbsp;sudo apt-get update<br> &nbsp; &nbsp;sudo apt-get upgrade<br> &nbsp; &nbsp;sudo reboot</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-0" start="7"><li class="c6 c14 c13"><span>(Optional) </span><span class="c0">Remove bloatware</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1 start" start="1"><li class="c9 c6"><span class="c0">Not required step. Removes unneeded software that takes up SD card space &nbsp;</span></li></ol><a id="t.938d836ce08d81fd156faa08ce663bfc33e15d1c"></a><a id="t.1"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; sudo apt-get purge wolfram-engine<br> &nbsp; &nbsp;sudo apt-get purge libreoffice*<br> &nbsp; &nbsp;sudo apt-get purge sonic-pi<br> &nbsp; &nbsp;sudo apt-get purge minecraft-pi<br> &nbsp; &nbsp;sudo apt-get clean<br> &nbsp; &nbsp;sudo apt-get autoremove</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="2"><li class="c9 c6"><span class="c0">Restart machine</span></li></ol><a id="t.471410d2c2135eb095f5a0e56142d60cb88f268a"></a><a id="t.2"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; sudo reboot</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-0" start="8"><li class="c6 c14 c13"><span class="c0">Install additional software</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1 start" start="1"><li class="c9 c6"><span class="c0">From terminal</span></li></ol><a id="t.4e3afbe6390a93b7bace7fc5d4f929500e325e03"></a><a id="t.3"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; sudo apt-get install python-dev<br> &nbsp; &nbsp;sudo apt-get install git<br> &nbsp; &nbsp;sudo apt-get install sqlite3<br> &nbsp; &nbsp;sudo apt-get install virtualenv<br> &nbsp; &nbsp;sudo apt-get install logrotate<br> &nbsp; &nbsp;sudo apt-get install apache2<br> &nbsp; &nbsp;sudo apt-get install libapache2-mod-wsgi<br> &nbsp; &nbsp;sudo a2enmod headers<br> &nbsp; &nbsp;sudo systemctl restart apache2</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-0" start="9"><li class="c6 c14 c13"><span class="c0">Set up feeder website</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1 start" start="1"><li class="c9 c6"><span class="c0">From terminal</span></li></ol><a id="t.2b72560c97bd0679c916edbe0d7b9acd6ca61b9f"></a><a id="t.4"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; sudo mkdir /var/www -p<br> &nbsp; &nbsp;cd /var/www<br> &nbsp; &nbsp;sudo virtualenv feeder<br> &nbsp; &nbsp;sudo chown -R pi:www-data /var/www/feeder/<br> &nbsp; &nbsp;sudo chmod 750 -R /var/www/feeder/<br> &nbsp; &nbsp;cd /var/www/feeder/<br> &nbsp; &nbsp;source bin/activate<br> &nbsp; &nbsp;pip install flask<br> &nbsp; &nbsp;pip install RPi.GPIO<br> &nbsp; &nbsp;git clone https://gitlab.com/DiyPetFeeder/feeder.git<br> &nbsp; &nbsp;cd /var/www/feeder/feeder/<br> &nbsp; &nbsp;python createFiles.py <br> &nbsp; &nbsp;sudo chown -R pi:www-data /var/www/feeder/<br> &nbsp; &nbsp;sudo chmod 770 -R /var/www/feeder/feeder/</span></p></td></tr></tbody></table><p class="c3 c20"><span class="c0"></span></p><ol class="c5 lst-kix_g5krlfpm8sk2-0" start="10"><li class="c6 c14 c13"><span class="c0">Set up permissions</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1 start" start="1"><li class="c9 c6"><span>&nbsp;</span><span class="c0">From terminal open Sudoers file</span></li></ol><a id="t.2ec8e2bb572da0a780b3e3e862350a04dcd3af5d"></a><a id="t.5"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; sudo visudo</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="2"><li class="c9 c6"><span class="c0">Add under section &quot;Allow members of group sudo to execute any command&quot;</span></li></ol><a id="t.a958dcd8e0f155f7534c246a476c687161218e36"></a><a id="t.6"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; www-data ALL=(root) NOPASSWD: ALL</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="3"><li class="c9 c6"><span class="c0">Exit file: Ctrl-x&gt; &#39;Y&#39;&gt; Enter to confirm</span></li><li class="c9 c6"><span class="c0">From terminal</span></li></ol><a id="t.8c147ea71dfc73952dc1e9efcf7511cdc6a2a2d6"></a><a id="t.7"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; sudo usermod -aG gpio www-data<br> &nbsp; &nbsp;sudo usermod -aG video www-data</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-0" start="11"><li class="c6 c14 c13"><span class="c0">Configure Apache</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1 start" start="1"><li class="c9 c6"><span class="c0">From terminal</span></li></ol><a id="t.faeb66db9a86c2c41343e5b057ff0c2a1c6c3b25"></a><a id="t.8"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; sudo nano /etc/apache2/sites-available/000-default.conf</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="2"><li class="c9 c6"><span class="c0">Replace all text in file with following. ServerName can be updated later.</span></li></ol><a id="t.ecae389fb4e4346337ab2586e19283c0979d161a"></a><a id="t.9"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; &lt;VirtualHost *:80&gt;<br> &nbsp; &nbsp;ServerName feeder.duckdns.org<br> &nbsp; &nbsp;<br> &nbsp; &nbsp;WSGIDaemonProcess feeder user=www-data group=www-data threads=5<br> &nbsp; &nbsp;WSGIScriptAlias / /var/www/feeder/feeder/feeder.wsgi<br><br> &nbsp; &nbsp;&lt;Directory /var/www/feeder/feeder&gt;<br> &nbsp; &nbsp;WSGIProcessGroup feeder<br> &nbsp; &nbsp;Order allow,deny<br> &nbsp; &nbsp;Allow from all<br> &nbsp; &nbsp;Require all granted<br> &nbsp; &nbsp;&lt;/Directory&gt;<br><br> &nbsp; &nbsp;&lt;Files feeder.wsgi&gt;<br> &nbsp; &nbsp;Order allow,deny<br> &nbsp; &nbsp;Allow from all<br> &nbsp; &nbsp;&lt;/Files&gt;<br><br> &nbsp; &nbsp;ErrorLog /var/www/feeder/feeder/logs/apacheError.log<br> &nbsp; &nbsp;CustomLog /var/www/feeder/feeder/logs/apacheAccess.log combined<br> &nbsp; &nbsp;&lt;/VirtualHost&gt;</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="3"><li class="c9 c6"><span class="c0">Exit file: Ctrl-x&gt; &#39;Y&#39;&gt; Enter to confirm</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-0" start="12"><li class="c6 c14 c13"><span class="c0">Setup feeder background button service</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1 start" start="1"><li class="c9 c6"><span class="c0">From terminal</span></li></ol><a id="t.b2ad0677743cb0fb4c57bfb0ae0d467c7f6f2d50"></a><a id="t.10"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; sudo cp /var/www/feeder/feeder/feederButtonService.sh /etc/init.d/<br> &nbsp; &nbsp;cd /etc/init.d/<br> &nbsp; &nbsp;sudo chmod 755 feederButtonService.sh<br> &nbsp; &nbsp;sudo update-rc.d feederButtonService.sh defaults<br> &nbsp; &nbsp;sudo /etc/init.d/feederButtonService.sh start</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-0" start="13"><li class="c6 c14 c13"><span class="c0">Setup feeder background time service</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1 start" start="1"><li class="c6 c9"><span class="c0">From terminal</span></li></ol><a id="t.09caa7eeb9289337eee7e8eb93166f8588f1b3b4"></a><a id="t.11"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; sudo cp /var/www/feeder/feeder/feederTimeService.sh /etc/init.d/<br> &nbsp; &nbsp;cd /etc/init.d/<br> &nbsp; &nbsp;sudo chmod 755 feederTimeService.sh<br> &nbsp; &nbsp;sudo update-rc.d feederTimeService.sh defaults<br> &nbsp; &nbsp;sudo /etc/init.d/feederTimeService.sh start</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-0" start="14"><li class="c6 c14 c13"><span class="c0">Restart system</span></li></ol><a id="t.471410d2c2135eb095f5a0e56142d60cb88f268a"></a><a id="t.12"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; sudo reboot</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-0" start="15"><li class="c6 c14 c13"><span class="c0">Configure Logrotate</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1 start" start="1"><li class="c9 c6"><span class="c0">From terminal</span></li></ol><a id="t.d0c698dff5d93e5b255aeee50645492a71dd1385"></a><a id="t.13"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; sudo nano /etc/logrotate.d/apache2</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="2"><li class="c9 c6"><span class="c0">Append to bottom of file</span></li></ol><a id="t.13a1b7dd395d4103fccd96b93455ed89d3f30979"></a><a id="t.14"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; /var/www/feeder/feeder/logs/apacheAccess.log<br> &nbsp; &nbsp;/var/www/feeder/feeder/logs/apacheError.log<br> &nbsp; &nbsp;{<br> &nbsp; &nbsp; &nbsp; &nbsp;rotate 3<br> &nbsp; &nbsp; &nbsp; &nbsp;daily<br> &nbsp; &nbsp; &nbsp; &nbsp;missingok<br> &nbsp; &nbsp; &nbsp; &nbsp;notifempty<br> &nbsp; &nbsp; &nbsp; &nbsp;copytruncate<br> &nbsp; &nbsp; &nbsp; &nbsp;su root adm<br> &nbsp; &nbsp;}</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="3"><li class="c9 c6"><span class="c0">Exit file: Ctrl-x&gt; &#39;Y&#39;&gt; Enter to confirm</span></li><li class="c9 c6"><span class="c0">Force run a test to ensure logs are rotating correctly</span></li><li class="c9 c6"><span class="c0">From terminal</span></li></ol><a id="t.4fb51a77a55b5e27afc40938c9a9d61e08eac866"></a><a id="t.15"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; sudo logrotate --force /etc/logrotate.d</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="6"><li class="c9 c6"><span class="c0">Notice the apache logs will be rotated at /var/www/feeder/feeder/logs</span></li><li class="c9 c6"><span class="c0">Note: button and time service log rotation are handled within service themselves and will not rotate with this command</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-0" start="16"><li class="c6 c14 c13"><span class="c0">Verify feeder site is working</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1 start" start="1"><li class="c9 c6"><span class="c0">Open internet browser</span></li><li class="c9 c6"><span>Type </span><span class="c15"><a class="c7" href="https://www.google.com/url?q=http://127.0.0.1&amp;sa=D&amp;ust=1535406325062000">127.0.0.1</a></span><span class="c0">&nbsp;into navigation bar</span></li><li class="c9 c6"><span class="c0">Verify website appears </span></li><li class="c9 c6"><span class="c0">Click &lsquo;Feed Now&rsquo; button and verify feed time is populated in site</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-2 start" start="1"><li class="c12 c6"><span class="c0">Note: Nothing else will happen as hardware is not connected yet</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="5"><li class="c9 c6"><span>Type </span><span class="c15"><a class="c7" href="https://www.google.com/url?q=http://127.0.0.1/admin&amp;sa=D&amp;ust=1535406325063000">127.0.0.1/admin</a></span><span class="c0">&nbsp;into navigation bar</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-2 start" start="1"><li class="c6 c12"><span class="c0">Default user/password is admin/ChangeMe!</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="6"><li class="c9 c6"><span class="c0">Under &lsquo;User Logins&#39; click &lsquo;Add User&rsquo;</span></li><li class="c9 c6"><span class="c0">Enter unique user name and secure password</span></li><li class="c9 c6"><span class="c0">Login to admin page again with new user </span></li><li class="c9 c6"><span class="c0">Delete original default user</span></li><li class="c9 c6"><span class="c0">Verify time and button services are running</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-2 start" start="1"><li class="c12 c6"><span class="c0">Ok for other services to not be working</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-0" start="17"><li class="c6 c14 c13"><span class="c0">Configure router to assign static internal IP to Pi</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1 start" start="1"><li class="c9 c6"><span class="c0">From terminal</span></li></ol><a id="t.54dc2add0ab42f39d0e6172bbca00bd694663d95"></a><a id="t.16"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; ifconfig</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="2"><li class="c9 c6"><span class="c0">&nbsp;Assuming using built in wireless write down ip address of wlan0 section</span></li><li class="c9 c6"><span class="c0">Typically starts with 192.168. (ex. 192.168.1.182)</span></li><li class="c9 c6"><span class="c0">Configure your router so Pi always gets assigned this IP address</span></li><li class="c9 c6"><span class="c0">This varies by router. Check your router&#39;s documentation</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-2 start" start="1"><li class="c12 c6"><span class="c0">Typically under a section similar sounding to &#39;DHCP&#39; or &#39;Reservations&#39;</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-0" start="18"><li class="c6 c14 c13"><span class="c0">Configure router to point external web traffic to pi</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1 start" start="1"><li class="c9 c6"><span class="c0">From router port forward internet traffic (port 80) to reserved internal ip address set above</span></li><li class="c9 c6"><span class="c0">This varies by router. Check your router&#39;s documentation</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-2 start" start="1"><li class="c12 c6"><span class="c0">Look for a section similar sounding to &#39;port forwarding&#39;</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-0" start="19"><li class="c6 c14 c13"><span class="c0">Configure DNS</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1 start" start="1"><li class="c9 c6"><span class="c0">To check current external IP go to Google and search &#39;my ip address&#39;. This is your external IP address. Most ISP do not provider a static external IP. So you will need a better way to keep track when it changes. Setting up DuckDns is one many options out there. It is free and the following example will show you how to set it up.</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-2 start" start="1"><li class="c12 c6"><span class="c0">If you have a different provider or plan on buying a domain you can do that as well, just skip next section</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-0" start="20"><li class="c6 c14 c13"><span class="c0">Setup Duck DNS</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1 start" start="1"><li class="c9 c6"><span>Go to </span><span class="c15"><a class="c7" href="https://www.google.com/url?q=http://www.duckdns.org/&amp;sa=D&amp;ust=1535406325067000">duckdns.org</a></span><span class="c0">&nbsp;and create an account</span></li><li class="c9 c6"><span class="c0">On your main account page create a subdomain (ex.&rdquo;petfeeder&rdquo; &gt; petfeeder.duckdns.org)</span></li><li class="c9 c6"><span class="c0">Next click on &ldquo;install&rdquo; on top navigation bar</span></li><li class="c9 c6"><span class="c0">Select Pi from &#39;operating systems&#39; section and your subdomain from drop down</span></li><li class="c9 c6"><span class="c0">Copy long string from the output section</span></li><li class="c9 c6"><span class="c0">Example below. Copy your actual string from site</span></li></ol><a id="t.fc6596d06df949aed0eacadf0f20691aa5d6ee14"></a><a id="t.17"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; echo url=&quot;https://www.duckdns.org/update?domains=YourCustomDomainHere&amp;token=23feabcdef-375c-1234-9e36-567890ac0a&amp;ip=&quot; | curl -k -o ~/duckdns/duck.log -K -</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="7"><li class="c9 c6"><span class="c0">From home directory (ex. /home/pi) open terminal</span></li></ol><a id="t.d94984b92dbc408da0d12c4a54d807c021007096"></a><a id="t.18"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; mkdir duckdns <br> &nbsp; &nbsp;cd duckdns<br> &nbsp; &nbsp;sudo nano duck.sh</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="8"><li class="c9 c6"><span class="c0">Paste your &#39;echo url...&#39; text copied above into duck.sh </span></li><li class="c9 c6"><span class="c0">Exit file: Ctrl-x&gt; &#39;Y&#39;&gt; Enter to confirm</span></li><li class="c9 c6"><span class="c0">From terminal</span></li></ol><a id="t.bd98c8f25e5732c8f2a4b74c81fa3ec738cd042b"></a><a id="t.19"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; sudo chown -R pi:pi /home/pi/duckdns/<br> &nbsp; &nbsp;sudo chmod 700 /home/pi/duckdns/duck.sh<br> &nbsp; &nbsp;crontab -e</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="11"><li class="c9 c6"><span class="c0">Select 2 if prompted</span></li><li class="c9 c6"><span class="c0">Paste following into file</span></li></ol><a id="t.f992acb8cacdaab1e51c7b41729644fde2301e1b"></a><a id="t.20"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; */5 * * * * /home/pi/duckdns/duck.sh &gt;/dev/null 2&gt;&amp;1</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="13"><li class="c9 c6"><span class="c0">Exit file: Ctrl-x&gt; &#39;Y&#39;&gt; Enter to confirm</span></li><li class="c9 c6"><span class="c0">To test run from home directory terminal</span></li></ol><a id="t.bd59bc108436e0c474968bda084e0e8e4cfdd728"></a><a id="t.21"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; cd /home/pi/duckdns/<br> &nbsp; &nbsp;./duck.sh<br> &nbsp; &nbsp;cat /home/pi/duckdns/duck.log<br> &nbsp; &nbsp;sudo service cron start</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="15"><li class="c9 c6"><span class="c0">If KO is returned versus OK, then there is an issue. Check token and domain are correct.</span></li><li class="c9 c6"><span class="c0">Now, every 5 minutes, duck dns will update your address (ex. petfeeder.duckdns.org) with you external ip address.</span></li><li class="c9 c6"><span>On the </span><span class="c15"><a class="c7" href="https://www.google.com/url?q=http://www.duckdns.org/%255C&amp;sa=D&amp;ust=1535406325071000">duckdns.org</a></span><span class="c0">&nbsp;site you should now see you external IP address stored</span></li><li class="c9 c6"><span class="c0">You will no longer need to know if/when you IP address changes. You can externally visit the feeder site through this link (ex. petfeeder.duckdns.org)</span></li><li class="c9 c6"><span class="c0">You should now be able to access the website by visiting your address</span></li><li class="c9 c6"><span class="c0">Test on another machine locally as well as one not locally on your current wifi to verify everything is working as expected</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-0" start="21"><li class="c6 c14 c13"><span class="c0">Connecting to pi without monitor (headless display).</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1 start" start="1"><li class="c9 c6"><span class="c0">With VNC enabled earlier you no longer need to connect the pi to a monitor. You can connect to the pi from another machine using vnc</span></li><li class="c9 c6"><span class="c0">To do this Install the vnc viewer on another device. </span></li><li class="c9 c6"><span class="c15"><a class="c7" href="https://www.google.com/url?q=https://www.realvnc.com/en/connect/download/viewer/&amp;sa=D&amp;ust=1535406325072000">Link VNC Viewer install</a></span></li><li class="c9 c6"><span class="c0">After installed on other device, when prompted for a machine to connect to enter the internal ip address followed by &#39;:5900&#39; (ex 192.168.1.182:5900)</span></li><li class="c9 c6"><span class="c0">Using internal IP address will only work locally on same wifi network</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-2 start" start="1"><li class="c12 c6"><span class="c0">To connect remotely you could simply port forward &quot;5900&quot; to the pi like web traffic is</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-0" start="22"><li class="c6 c14 c13"><span class="c0">Set up motion IO</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1 start" start="1"><li class="c9 c6"><span class="c0">If have camera installed on pi the following steps will configure software to capture video on DiyPetFeeder</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-2 start" start="1"><li class="c12 c6"><span class="c0">Designed work with motion IO</span></li></ol><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="2"><li class="c9 c6"><span class="c0">To set up motion IO, from terminal home directory (ex. /home/pi)</span></li></ol><a id="t.c1f2f3e5b4eececd62069a807130daac5d889486"></a><a id="t.22"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; wget github.com/Motion-Project/motion/releases/download/release-4.1.1/pi_stretch_motion_4.1.1-1_armhf.deb<br> &nbsp; &nbsp;sudo apt-get install gdebi-core<br> &nbsp; &nbsp;sudo gdebi pi_stretch_motion_4.1.1-1_armhf.deb<br> &nbsp; &nbsp;mkdir ~/.motion<br> &nbsp; &nbsp;cp /etc/motion/motion.conf ~/.motion/motion.conf<br> &nbsp; &nbsp;sudo nano ~/.motion/motion.conf</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="3"><li class="c9 c6"><span class="c0">With config open in nano tweak config to your desired modifications to get desired performance. A few suggestions include</span></li></ol><a id="t.6450bb0aa52bfb3f1fdcd32128b331072ed7a71d"></a><a id="t.23"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; width 320 &gt; width 640<br> &nbsp; &nbsp;height 240 &gt; height 480<br> &nbsp; &nbsp;framerate 2 &gt; framerate 20<br> &nbsp; &nbsp;post_capture 0 &gt; post_capture 100<br> &nbsp; &nbsp;max_movie_time 0 &gt; max_movie_time 120<br> &nbsp; &nbsp;target_dir /tmp/motion &gt; target_dir /var/www/feeder/feeder/static/video<br> &nbsp; &nbsp;stream_quality 50 &gt; stream_quality 80<br> &nbsp; &nbsp;stream_maxrate 1 &gt; stream_maxrate 15<br> &nbsp; &nbsp;stream_localhost on &gt; stream_localhost off</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="4"><li class="c9 c6"><span class="c0">Open /etc/modules</span></li></ol><a id="t.cb212dd7cd92aa719304972f81fdfd7a47af77ea"></a><a id="t.24"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; sudo nano /etc/modules</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="5"><li class="c9 c6"><span class="c0">Add line</span></li></ol><a id="t.9fa8b5cb0674c55aa16acffe3dca126d14e6a337"></a><a id="t.25"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; bcm2835-v4l2</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="6"><li class="c9 c6"><span class="c0">From terminal open</span></li></ol><a id="t.7fdfe8369675d13baa7b3acddc5740e7b461ee37"></a><a id="t.26"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; sudo nano /etc/rc.local</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="7"><li class="c9 c6"><span class="c0">Add command right above line &#39;exit 0&#39; at the end of file</span></li></ol><a id="t.d94470208e2602a765118c33b3b7e9d871e002c4"></a><a id="t.27"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; motion -c /home/pi/.motion/motion.conf</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="8"><li class="c9 c6"><span class="c0">To disable pi camera red light, from terminal</span></li></ol><a id="t.6fd32c3282b038e1178b7df88541fa06fb2c4a11"></a><a id="t.28"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; sudo nano /boot/config.txt</span></p></td></tr></tbody></table><ol class="c5 lst-kix_g5krlfpm8sk2-1" start="9"><li class="c9 c6"><span class="c0">&nbsp;Add to last line of file</span></li></ol><a id="t.1a37bbb4a7e71d13750ec0683c4a64bfdc02de5a"></a><a id="t.29"></a><table class="c11"><tbody><tr class="c2"><td class="c1" colspan="1" rowspan="1"><p class="c6"><span class="c4">&nbsp; &nbsp; disable_camera_led=1</span></p></td></tr></tbody></table><p class="c6 c13"><span class="c0">&nbsp; </span></p><p class="c3"><span class="c0"></span></p><p class="c3"><span class="c0"></span></p><p class="c3"><span class="c0"></span></p><p class="c3"><span class="c0"></span></p><p class="c3"><span class="c0"></span></p><p class="c3"><span class="c0"></span></p><p class="c3"><span class="c0"></span></p><h2 class="c18" id="h.7u1svx3j3v4q"><span class="c19">Setup Wired Components</span></h2><h2 class="c18" id="h.ebz1dxhpidc1"><span class="c19">Setup Box</span></h2><h2 class="c18" id="h.n5c7j2q674o7"><span class="c19">Final Assembly</span></h2><h2 class="c18" id="h.xfpey9melz72"><span class="c19">FAQ</span></h2><p class="c3"><span class="c0"></span></p><p class="c3"><span class="c0"></span></p></body></html>