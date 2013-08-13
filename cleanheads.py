#!/usr/bin/env python

import os, ConfigParser
from nsnitro import *

config_file=os.path.dirname(os.path.realpath(__file__))+'/config'
if(not os.path.isfile(config_file)):
 print "Config file does not exit!"
 exit()

config = ConfigParser.ConfigParser()
config.read(config_file)
#password = config.get('osu-sig','password')
#user = config.get('osu-sig','user')
#host=config.get('osu-sig','host')

lb = NSNitro(config.get('osu-sig','host'),config.get('osu-sig','password'),config.get('osu-sig','user'))

#nitro = NSNitro(host,password,user)
lb.login()
