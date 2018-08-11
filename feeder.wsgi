import os, sys
 
activate_this = '/var/www/feeder/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

sys.path.append('/var/www/feeder/feeder')
 
from app import app as application

home='/var/www/feeder/feeder'
