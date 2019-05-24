#Zip Import / Export Config
#NO NEED TO CHANGE
ExportZip = "export.zip"
ExportDir = "apple_health_export"
ExportXML = "export.xml"

#Dropbox Config
access_token = '*************************'

#InfluxDB Server
IP = 'XXX.XXX.XXX.XXX'
PORT = '8086'
USERNAME = 'user'
PASSWORD = 'password'
DB_NAME = 'database'
NAME = 'Me' #Name of persons data

vCount = 0

#SMTP Config - For Gmail.  Email password is an app password generated from your security settings if using 2 factor auth.
email_user = 'email'
email_pass = 'password'
email_sendto = 'sendto email'
email_subject = 'Healthkit Import Notification'
email_body = 'SUBJECT: Healthkit Import Completed Successfully!'