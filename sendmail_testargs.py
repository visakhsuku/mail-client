import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import getpass
import sys
import argparse
import fileinput
import os
import time

parser = argparse.ArgumentParser()
parser.add_argument("-e","--emaillist", help="Email file list",required=True)
parser.add_argument("-b","--body", help="Body Contents File",required=True)
parser.add_argument("-a","--attachments",nargs='+', help="Attachments to the email",required=False)
args = parser.parse_args()

print("!!!!This program runs under the assumption that the sender email holds an account under Google!!!!")

#####################################################
#                                                   #
#                  SMTP Connections                 #
#                                                   #
#####################################################

try:
	mailobject = smtplib.SMTP('smtp.gmail.com',587)
	mailobject.starttls()
except:
	print("SMTP Connection failed")
	exit()
	
#####################################################
#                                                   #
#          Getting authentication details           #
#                                                   #
#####################################################

senderemail = raw_input("Enter sender email: ")
password=getpass.getpass('Enter password: ')

#####################################################
#                                                   #
#                  Authentication                   #
#                                                   #
#####################################################

try:
	mailobject.login(senderemail, password)
except:
	print("Login Failed")
	exit()
	
#####################################################
#                                                   #
#                  File descriptors                 #
#                                                   #
#####################################################

successful = open("Success",'a+')
failed = open("Failed",'a+')

#####################################################
#                                                   #
#                   Email Content                   #
#                                                   #
#####################################################

FROM = senderemail
SUBJECT = raw_input("Enter subject of email: ")
bodyContents = open(args.body,'r').read()
BODY = MIMEText(bodyContents, 'html')

#####################################################
#                                                   #
#                  Email Attachments                #
#                                                   #
#####################################################



#####################################################
#                                                   #
#                  Sending Email                    #
#                                                   #
#####################################################

emaillist = args.emaillist

f = open(emaillist,'r')
filedata = f.read()
f.close()

replaceddata = filedata.replace(",","\n")

f = open(emaillist,'w')
f.write(replaceddata)
f.close()

f = open(emaillist,'r+')
records = f.read().splitlines()
f.close()

emails = set(records)

alreadydone = successful.read().splitlines()

for email in emails:
	email = email.replace('"', '').strip().lower()
	if email in alreadydone:
		print("Duplicate")
		continue
	if '@' not in email or '.' not in email or len(email)<6:
		print("Invalid email")
		failed.seek(0,2)
		failed.write(email+'\n')
		continue
		
	emailContext = MIMEMultipart()
	emailContext['From'] = FROM
	emailContext['To'] = email
	emailContext['Subject'] = SUBJECT
	emailContext.attach(BODY)

        
	message = emailContext.as_string()
	try:
		mailobject.sendmail(senderemail,email,message)
		print("Email sent to "+email)
		successful.write(email+'\n')
		alreadydone.append(email)
	except:
		print("Failed to send email to "+email)
		failed.write(email+"\n")

os.system('cp Success '+'backups/Success'+time.ctime().replace(' ','-'))
mailobject.quit()
successful.close()
failed.close()
