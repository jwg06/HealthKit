#Healthkit Import
#Automated process using Dropbox to import Apple Healthkit data into InfluxDB for use with Grafana
#Note: Depending on how much data you have, it can take awhile to complete the process.  Also, you can create new if blocks with the specific HKValues.  This is just the selection I decided to use.
#Initial idea for this came from https://github.com/Evs91/HealthkitImportInfluxDB

**Usage**
1. Edit healthkitcnf.py with Database info and Dropbox Access Token.
2. Export your Apple Health data from device and select Dropbox.
3. Run script.

**TODO**
- Speed up XML import process.
- Create better process / function for healthkit_xml() to find all values listed in HKValues.csv instead of predefined.
- Find full list of HK Values, export all data to InfluxDB.
- Exceptions / Error Reporting
- CRON Job?