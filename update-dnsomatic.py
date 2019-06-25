#!/usr/bin/env python

# cron runs This Python script at 15 minutes past each hour...
    
import datetime
import time
from base64 import encodestring
from socket import gethostbyname
from urllib import urlencode
from urllib2 import Request, urlopen
import logging
import sys

# for testing purposes, '-t' or '/t' on the command line forces an IP address update
testing = 0
for i in range (1,len(sys.argv)):
   if ((sys.argv[i] == "-t") or (sys.argv[i] == '/t')):
       testing = 1
       
logging.basicConfig(filename='/home/pi/scripts/update-dnsomatic.log', filemode='a', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S',level=logging.DEBUG)

# username, password and hostname here.
username='jim11662418@gmail.com'
password='@m2U6RN0T1x!'
hostname='all.dnsomatic.com'
duckdnsname ='jim11662418.duckdns.org'

#See https://www.dnsomatic.com/wiki/api for explanation of the
# following parameter values and options
wildcard='NOCHG'
mx='NOCHG'
backmx='NOCHG'

print '\nDNS-O-Matic.com updater is running...\n'

maxAttempts=5
duckdnsSuccess=False
attempts=0

while (duckdnsSuccess==False):
   #Get the current dynamic IP setting from duckdns.org
   attempts=attempts+1
   if (attempts > maxAttempts):
      exit()
   else:
      try:
         lookup=gethostbyname(duckdnsname)
      except:
         print 'Attempt '+str(attempts)+'. Unable to get the stored address from duckdns.org.'
         #logging.info('Attempt '+str(attempts)+'. Unable to get the stored address from duckdns.org')
         if (attempts != maxAttempts):
            print 'Sleeping for 5 seconds between attempts...'
            time.sleep(5)
      else:
         #logging.info('Attempt '+str(attempts)+'. IP address from duckdns.org is: '+lookup)
         print 'Attempt '+str(attempts)+'. The stored IP address from duckdns.org is:', lookup
         duckdnsSuccess=True
 

dnsomaticSuccess=False
attempts=0

while (dnsomaticSuccess==False):
   #Get current actual external IP from DNS-o-matic.com.
   attempts=attempts+1
   if (attempts > maxAttempts):
      exit()
   else:
      try:
         ip_external = urlopen('http://myip.dnsomatic.com')
         myip = ip_external.read()
      except:
         print 'Attempt '+str(attempts)+'. Unable to get current actual address from myip.dnsomatic.com'
         #logging.info('Attempt '+str(attempts)+'. Unable to get current actual address from myip.dnsomatic.com')
         if (attempts != maxAttempts):
            print 'Sleeping for 5 seconds between attempts...'
            time.sleep(5)
      else:
         ip_external.close()
         #logging.info('Attempt '+str(attempts)+'. The current actual IP address from myip.dnsomatic.com is: '+myip)
         print 'Attempt '+str(attempts)+'. The current actual IP address from myip.dnsomatic.com is:', myip
         dnsomaticSuccess=True


# if testing OR if the IPs addresses don't match OR if it is now 3:15AM, then update IP addresses...
if (testing) or ((lookup != myip) or (datetime.datetime.now().hour == 3)):
    #change the DNS entry
    data = {}
    data['hostname'] = hostname
    data['myip'] = myip
    data['wildcard'] = wildcard
    data['mx'] = mx
    data['backmx'] = backmx

    url_values = urlencode(data)

    url = 'https://updates.dnsomatic.com:443/nic/update?' + url_values
    request = Request(url)

    base64string = encodestring(username + ':' + password)[:-1]
    request.add_header("Authorization", "Basic %s" % base64string)
    request.add_header('User-Agent',username + ' - Home User - 1.0')

    htmlFile = urlopen(request)
    htmlData = htmlFile.read()
    htmlFile.close()

    results = htmlData.split()
    if results[0] == 'good':
        logging.info('DNS-O-Matic updated to: ' + results[1])    
        print "DNS-O-Matic updated to: " + results[1]
    else:
        logging.info("DNS-O-Matic update failed with error: " + results[0])        
        print 'DNS-O-Matic update failed with error: ', results[0]
else:
    logging.info('IP addresses match. No DNS update necessary.')
    print 'IP addresses match. No DNS update necessary.'






