import healthkitfn
import healthkitcnf
import zipfile
import os
import shutil
import dropbox
from influxdb import InfluxDBClient
from datetime import datetime
from xml.dom import minidom
import csv

#Initiate Logging
logger = healthkitfn.init_logging()
#Temp time for tracking
startTime = datetime.now()

###################
# Start Functions #
###################

#Dropbox Download export.zip Function
def healthkit_import():
    #Connect To Dropbox
    dbx = dropbox.Dropbox(healthkitcnf.access_token)
    #Clean Existing Files
    if os.path.isdir(healthkitcnf.ExportDir):
        shutil.rmtree(healthkitcnf.ExportDir)
        logger.info(f"Removed {healthkitcnf.ExportDir}")
    if os.path.isfile(healthkitcnf.ExportZip):
        os.remove(healthkitcnf.ExportZip)
        logger.info(f"Removed {healthkitcnf.ExportZip}")
    if os.path.isfile(healthkitcnf.ExportXML):
        os.remove(healthkitcnf.ExportXML)
        logger.info(f"Removed {healthkitcnf.ExportXML}")
    #Download New export.zip and unzip
    with open("export.zip", "wb") as f:
        metadata, res = dbx.files_download(path="/export.zip")
        f.write(res.content)
        logger.info('Downloaded export.zip Successfully')
        zip_ref = zipfile.ZipFile(healthkitcnf.ExportZip, 'r')
        zip_ref.extractall()
        zip_ref.close()
        logger.info("Unzipped export.zip Successfully")
        shutil.copy("apple_health_export/export.xml", healthkitcnf.ExportXML)
        logger.info("Copied export.xml to primary directory")
    return logger.info('Download and Copy Completed')

#Connect to Database
def healthkit_db():
        client = InfluxDBClient(healthkitcnf.IP, healthkitcnf.PORT, healthkitcnf.USERNAME, healthkitcnf.PASSWORD, healthkitcnf.DB_NAME)
        client.create_database(healthkitcnf.DB_NAME)
        logger.info('Connected to Database Successfully')
        return client

#Load HK Type Values Into Array
def healthkit_text():
        f = open('HKValues.txt', 'r')
        HKValues = f.readlines()
        f.close()
        return HKValues

def healthkit_csv():
        with open('HKValues.csv', newline='') as csvfile:
                HKValues = list(csv.reader(csvfile))
        return HKValues

#Send Notification once completed
def healthkit_notify():
    try:
        email_ssl = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        email_ssl.ehlo
        email_ssl.login(healthkitcnf.email_user, healthkitcnf.email_pass)
        sent_from = healthkitcnf.email_user  
        send_to = healthkitcnf.email_sendto  
        subject = healthkitcnf.email_subject
        email_text = healthkitcnf.email_body
        email_ssl.sendmail(sent_from, send_to, email_text)
        email_ssl.close()
        logger.info("Notification Sent")
    except:
        logger.debug("Failed to send completed notification.")
    return (logger.info("Email sent"))

#XML Parse / Import HKValues.txt / Update DB
def healthkit_xml():
        NAME = healthkitcnf.NAME
        #Stat Keeping
        NUMRECORDS = 12
        RECORDINC = 1

        #Setup XML Parse
        logger.info("Importing XML Into Record List")
        xmldoc = minidom.parse('export.xml')
        recordlist = xmldoc.getElementsByTagName('Record')
        logger.info('Imported XML Records Successfully')
        #Import Healthkit Values Into Array
        #HKValues = healthkit_csv()
        #logger.info('Imported Health Kit Type Values')

        logger.info("Starting Heart Rate Export")
        for s in recordlist:
            if s.attributes['type'].value == "HKQuantityTypeIdentifierHeartRate":
                client.write_points([{"measurement": "heartrate","tags": {"service": "HealthKit","person": healthkitcnf.NAME},"time": s.attributes['startDate'].value,"fields": {"watch_heartrate": float(s.attributes['value'].value)}}])
            else:
                pass
        TEMPTIME = datetime.now() - startTime
        logger.info(f"Heart Rate Completed in {TEMPTIME} ({RECORDINC}/{NUMRECORDS})")
        RECORDINC += 1

        #Resting Heart Rate
        logger.info("Starting Resting Heart Rate Export")
        for restingHeart in recordlist:
            if restingHeart.attributes['type'].value == "HKQuantityTypeIdentifierRestingHeartRate":
                client.write_points([{"measurement": "restingheartrate","tags": {"service": "HealthKit","person": healthkitcnf.NAME},"time": restingHeart.attributes['startDate'].value,"fields": {"resting_heartrate": float(restingHeart.attributes['value'].value)}}])
            else:
                pass
        TEMPTIME = datetime.now() - startTime
        logger.info(f"Resting Heart Rate Completed in {TEMPTIME} ({RECORDINC}/{NUMRECORDS})")
        RECORDINC += 1

        #Walking Heart Rate
        logger.info("Starting Walking Heart Rate Export")
        for walkingHeart in recordlist:
            if walkingHeart.attributes['type'].value == "HKQuantityTypeIdentifierWalkingHeartRateAverage":
                client.write_points([{"measurement": "walkingHeart","tags": {"service": "HealthKit","person": healthkitcnf.NAME},"time": walkingHeart.attributes['startDate'].value,"fields": {"walking_heartrate": float(walkingHeart.attributes['value'].value)}}])
            else:
                pass
        TEMPTIME = datetime.now() - startTime
        logger.info(f"Walking Heart Rate Completed in {TEMPTIME} ({RECORDINC}/{NUMRECORDS})")
        RECORDINC += 1

        #distance walked
        logger.info("Starting Distance Walked Export")
        for distance in recordlist:
            if distance.attributes['type'].value == 'HKQuantityTypeIdentifierDistanceWalkingRunning':
                client.write_points([{"measurement": "distance","tags": {"service": "HealthKit","person": healthkitcnf.NAME},"time": distance.attributes['startDate'].value,"fields": {"distance": float(distance.attributes['value'].value)}}])
            else:
                pass
        TEMPTIME = datetime.now() - startTime
        logger.info(f"Distance Walked Rate Completed in {TEMPTIME} ({RECORDINC}/{NUMRECORDS})")
        RECORDINC += 1

        #basal calories
        logger.info("Starting Basal Calories Export")
        for basal in recordlist:
            if basal.attributes['type'].value == 'HKQuantityTypeIdentifierBasalEnergyBurned':
                client.write_points([{"measurement": "basal","tags": {"service": "HealthKit","person": healthkitcnf.NAME},"time": basal.attributes['startDate'].value,"fields": {"basal": float(basal.attributes['value'].value)}}])
            else:
                pass
        TEMPTIME = datetime.now() - startTime
        logger.info(f"Basal Calories Completed in {TEMPTIME} ({RECORDINC}/{NUMRECORDS})")
        RECORDINC += 1

        #active calories
        logger.info("Starting Active Calories Export")
        for active in recordlist:
            if active.attributes['type'].value == 'HKQuantityTypeIdentifierActiveEnergyBurned':
                client.write_points([{"measurement": "active","tags": {"service": "HealthKit","person": healthkitcnf.NAME},"time": active.attributes['startDate'].value,"fields": {"active": float(active.attributes['value'].value)}}])
            else:
                pass
        TEMPTIME = datetime.now() - startTime
        logger.info(f"Active Calories Completed in {TEMPTIME} ({RECORDINC}/{NUMRECORDS})")
        RECORDINC += 1

        #BMI
        logger.info("Starting BMI Export")
        for bmi in recordlist:
            if bmi.attributes['type'].value == 'HKQuantityTypeIdentifierBodyMassIndex':
                client.write_points([{"measurement": "bmi","tags": {"service": "HealthKit","person": healthkitcnf.NAME},"time": bmi.attributes['startDate'].value,"fields": {"bmi": float(bmi.attributes['value'].value)}}])
            else:
                pass
        TEMPTIME = datetime.now() - startTime
        logger.info(f"BMI Completed in {TEMPTIME} ({RECORDINC}/{NUMRECORDS})")
        RECORDINC += 1

        #WEIGHT
        logger.info("Starting Weight Export")
        for weight in recordlist:
            if weight.attributes['type'].value == 'HKQuantityTypeIdentifierBodyMass':
                client.write_points([{"measurement": "weight","tags": {"service": "HealthKit","person": healthkitcnf.NAME},"time": weight.attributes['startDate'].value,"fields": {"weight": float(weight.attributes['value'].value)}}])
            else:
                pass
        TEMPTIME = datetime.now() - startTime
        logger.info(f"Weight Completed in {TEMPTIME} ({RECORDINC}/{NUMRECORDS})")
        RECORDINC += 1

        #BodyFatPercentage
        print("Starting Body Fat Percentage Export")
        for bodyfat in recordlist:
            if bodyfat.attributes['type'].value == 'HKQuantityTypeIdentifierBodyFatPercentage':
                client.write_points([{"measurement": "bodyfat","tags": {"service": "HealthKit","person": healthkitcnf.NAME},"time": bodyfat.attributes['startDate'].value,"fields": {"bodyfat": float(bodyfat.attributes['value'].value)}}])
            else:
                pass
        TEMPTIME = datetime.now() - startTime
        logger.info(f"Body Fat Percentage Completed in {TEMPTIME} ({RECORDINC}/{NUMRECORDS})")
        RECORDINC += 1

        #LeanBodyMass
        logger.info("Starting Lean Body Mass Export")
        for leanmass in recordlist:
            if leanmass.attributes['type'].value == 'HKQuantityTypeIdentifierLeanBodyMass':
                client.write_points([{"measurement": "leanmass","tags": {"service": "HealthKit","person": healthkitcnf.NAME},"time": leanmass.attributes['startDate'].value,"fields": {"leanmass": float(leanmass.attributes['value'].value)}}])
            else:
                pass
        TEMPTIME = datetime.now() - startTime
        logger.info(f"Lean Body Mass Completed in {TEMPTIME} ({RECORDINC}/{NUMRECORDS})")
        RECORDINC += 1

        #Systolic BP
        logger.info("Starting Systolic BP Export")
        for systolic in recordlist:
            if systolic.attributes['type'].value == 'HKQuantityTypeIdentifierBloodPressureSystolic':
                client.write_points([{"measurement": "systolic","tags": {"service": "HealthKit","person": healthkitcnf.NAME},"time": systolic.attributes['startDate'].value,"fields": {"systolic": float(systolic.attributes['value'].value)}}])
            else:
                pass
        TEMPTIME = datetime.now() - startTime
        logger.info(f"Systolic BP Completed in {TEMPTIME} ({RECORDINC}/{NUMRECORDS})")
        RECORDINC += 1

        #Diastolic BP
        logger.info("Starting Diastolic BP Export")
        for diastolic in recordlist:
            if diastolic.attributes['type'].value == 'HKQuantityTypeIdentifierBloodPressureDiastolic':
                client.write_points([{"measurement": "diastolic","tags": {"service": "HealthKit","person": healthkitcnf.NAME},"time": diastolic.attributes['startDate'].value,"fields": {"diastolic": float(diastolic.attributes['value'].value)}}])
            else:
                pass
        TEMPTIME = datetime.now() - startTime
        logger.info(f"Diastolic Completed in {TEMPTIME} ({RECORDINC}/{NUMRECORDS})")
        RECORDINC += 1


        TEMPTIME = datetime.now() - startTime
        return logger.info(f"Export Completed in {TEMPTIME}")


healthkit_import()
client = healthkit_db()
healthkit_xml()
healthkit_notify()