#author : TeamAWS
#name   : aws_dashboard.py
#purpose: A program to fetch EC2 metrics and cretae a dashboard
#date   : 2016.04.03
#version: 1.0

#Importing required modules
import boto3.ec2
import boto3
from boto3.session import Session
from datetime import datetime,timedelta
import time
from distutils.command.install import install
import os
import csv
from operator import itemgetter
import operator
from dateutil import tz
import sys
from email.mime.multipart import MIMEMultipart
from email import *
from email.mime.text import *
from email.mime.base import *
from email import encoders
import smtplib
from fileinput import filename
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as nm
from matplotlib.backends.backend_pdf import PdfPages
import glob

#Function to clean up existing metric files
def removeExistingFiles():
    for f in glob.glob("*.csv"):
        if (f.endswith(".csv")):
            os.remove(f)
    print("Existing metric files removed.")

#Function to parse the config file
def parseConfFile(conffileName):
    try:
        f=open(conffileName,'r')
    except:
        print("The file "+conffileName+"is not present.")
        sys.exit()
    else:
        fileContent=f.readlines()
        instanceList=[]
        aws_access_key=fileContent[0].split(":")[1].strip('\n')
        aws_secret_access_key=fileContent[1].split(":")[1].strip('\n')
        instanceBuffer=fileContent[2].split(":")[1].strip('\n')
        instanceList=instanceBuffer.split(",")
        period=int(fileContent[3].split(":")[1].strip('\n'))
        region=fileContent[4].split(":")[1].strip('\n')
        hour=int(fileContent[5].split(":")[1].strip('\n'))
        print("Configuration file parsed successfully.")
        return aws_access_key,aws_secret_access_key,instanceList,period,region,hour

#Function to connect to AWS and start a CloudWatch monitoring session
def startMonitorSess(aws_access_key,aws_secret_access_key,region):
        session = Session(aws_access_key,aws_secret_access_key,region_name=region)
        cloudWatch = session.client('cloudwatch')
        print("CloudWatch session connected.")
        return cloudWatch

#Function to fetch CPU Utilization metric for multiple instances
def getCpuUtil(cloudWatch,instanceID,metricFilename,hour,period):
    
    #Defining time period for retrieval
    now=datetime.utcnow()
    past = now - timedelta(hours=hour)
    
    #Fetching metric for EC2 instance
    results = cloudWatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'InstanceId', 'Value':instanceID}],
            StartTime = past,
            EndTime = now,
            Period=period,
            Statistics=['Average'])
    datapoints = results['Datapoints'] 
    
    CPUUtilization={}
    for i in range(0,len(datapoints)):
        timestamp = str(datapoints[i]['Timestamp'])
        CPUUtilization[timestamp] = datapoints[i]['Average']
    
    #Time zone conversion and storing of datapoints in a csv file
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    
    for timestamp,CPUUtilization in sorted(CPUUtilization.items(),key=operator.itemgetter(0)):
        timestamp=timestamp.split("+")[0]
        utc = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        utc = utc.replace(tzinfo=from_zone)
        central = utc.astimezone(to_zone)
        central=str(central).split("-06:00")[0]
        central= datetime.strptime(str(central), '%Y-%m-%d %H:%M:%S')
        dataStr=instanceID+','+str(central)+','+str(CPUUtilization)+'\n'
        
        f=open(metricFilename,'a')
        f.write(dataStr)
        f.close()
    print("CPU Utilization metric fetched for EC2 instance "+instanceID+" and stored in file "+metricFilename)
    
#Function to fetch Network In metric for multiple instances        
def getNetIn(cloudWatch,instanceID,metricFilename,hour,period):
    now=datetime.utcnow()
    past = now - timedelta(hours=hour)
    results = cloudWatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='NetworkIn',
            Dimensions=[{'Name': 'InstanceId', 'Value':instanceID}],
            StartTime = past,
            EndTime = now,
            Period=period,
            Statistics=['Average'])
    datapoints = results['Datapoints'] 
    
    NetworkIn={}
    for i in range(0,len(datapoints)):
        timestamp = str(datapoints[i]['Timestamp'])
        NetworkIn[timestamp] = datapoints[i]['Average']
    
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    
    for timestamp,NetworkIn in sorted(NetworkIn.items(),key=operator.itemgetter(0)):
        timestamp=timestamp.split("+")[0]
        utc = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        utc = utc.replace(tzinfo=from_zone)
        central = utc.astimezone(to_zone)
        central=str(central).split("-06:00")[0]
        central= datetime.strptime(str(central), '%Y-%m-%d %H:%M:%S')
        dataStr=instanceID+','+str(central)+','+str(NetworkIn)+'\n'
        f=open(metricFilename,'a')
        f.write(dataStr)
        f.close()
    print("Network In metric fetched for EC2 instance "+instanceID+" and stored in file "+metricFilename)   
    
    
#Function to fetch Network Out metric for multiple instances
def getNetOut(cloudWatch,instanceID,metricFilename,hour,period):
    now=datetime.utcnow()
    past = now - timedelta(hours=hour)
    results = cloudWatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='NetworkOut',
            Dimensions=[{'Name': 'InstanceId', 'Value':instanceID}],
            StartTime = past,
            EndTime = now,
            Period=period,
            Statistics=['Average'])
    datapoints = results['Datapoints'] 
    
    NetworkOut={}
    for i in range(0,len(datapoints)):
        timestamp = str(datapoints[i]['Timestamp'])
        NetworkOut[timestamp] = datapoints[i]['Average']
    
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    
    for timestamp,NetworkOut in sorted(NetworkOut.items(),key=operator.itemgetter(0)):
        timestamp=timestamp.split("+")[0]
        utc = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        utc = utc.replace(tzinfo=from_zone)
        central = utc.astimezone(to_zone)
        central=str(central).split("-06:00")[0]
        central= datetime.strptime(str(central), '%Y-%m-%d %H:%M:%S')
        dataStr=instanceID+','+str(central)+','+str(NetworkOut)+'\n'
        f=open(metricFilename,'a')
        f.write(dataStr)
        f.close()
    
    print("Network Out metric fetched for EC2 instance "+instanceID+" and stored in file "+metricFilename)

removeExistingFiles()
aws_access_key,aws_secret_access_key,instanceList,period,region,hour=parseConfFile("dashboard_info.txt")
client=startMonitorSess(aws_access_key,aws_secret_access_key,region)
metricFilename1="cpuUtil.csv"
for i in range(0,len(instanceList)):
    instanceID=instanceList[i]
    getCpuUtil(client, instanceID, metricFilename1,hour,period)
    
metricFilename2="netIn.csv"
for i in range(0,len(instanceList)):
    instanceID=instanceList[i]
    getNetIn(client, instanceID, metricFilename2,hour,period)

metricFilename3="netOut.csv"
for i in range(0,len(instanceList)):
    instanceID=instanceList[i]
    getNetOut(client, instanceID, metricFilename3,hour,period)

#Defining Dashboard file
dashfileName="AWS_Dashboard.pdf"
mpl.rcParams['font.size'] = 10.0

def plotMetrics(metricFilename1,metricFilename2,metricFilename3,dashfileName):
    filetoattach = PdfPages(dashfileName)
    
    try:
        csvfile=open(metricFilename1,'r')
    except:
        print("File not found.")
        sys.exit()
    else:
        timeST=[]
        metric1=[]
        metric2=[]
        metric3=[]
        reader=csv.reader(csvfile)
        
        for row in reader:
                if (row[0]==instanceList[0]):
                    timeST.append(row[1])
                    metric1.append(float(row[2]))
                elif(row[0]==instanceList[1]):
                    metric2.append(float(row[2]))
                elif (row[0]==instanceList[2]):
                    metric3.append(float(row[2]))
    
        groups=len(timeST)
        index=nm.arange(groups)
        plt.plot(metric1)
        plt.plot(metric2)
        plt.plot(metric3)
        plt.legend([instanceList[0], instanceList[1],instanceList[2]], loc='upper right')
        plt.ylabel("Average CPU Utilization (in percentage)")
        plt.xlabel("TimeStamp")
        plt.title("CPU Utilization")
        plt.xticks(index,timeST,rotation='vertical')
        plt.margins(0.25)
        subplt=plt.gcf()
        subplt.subplots_adjust(bottom=0.3)
        plt.savefig(filetoattach, format='pdf')
        plt.close()
    
    try:
        csvfile=open(metricFilename2,'r')
    except:
        print("File not found.")
        sys.exit()
    else:
        timeST=[]
        metric1=[]
        metric2=[]
        metric3=[]
        reader=csv.reader(csvfile)
        
        for row in reader:
                if (row[0]==instanceList[0]):
                    timeST.append(row[1])
                    metric1.append(float(row[2]))
                elif(row[0]==instanceList[1]):
                    metric2.append(float(row[2]))
                elif (row[0]==instanceList[2]):
                    metric3.append(float(row[2]))
        
               
        groups=len(timeST)
        index=nm.arange(groups)
        barWidth=0.2
        plt.bar(index+0.2, metric1, barWidth, color='blue')
        plt.bar(index, metric2, barWidth, color='red')
        plt.bar(index-0.2, metric3, barWidth, color='gray')
        plt.legend([instanceList[0], instanceList[1],instanceList[2]], loc='upper right')
        plt.ylabel("Average Network In (in bytes)")
        plt.xlabel("TimeStamp")
        plt.title("Network In")
        plt.xticks(index,timeST,rotation='vertical')
        plt.margins(0.25)
        subplt=plt.gcf()
        subplt.subplots_adjust(bottom=0.3)
        plt.savefig(filetoattach, format='pdf')
        plt.close()
        
    try:
        csvfile=open(metricFilename3,'r')
    except:
        print("File not found.")
        sys.exit()
    else:
        timeST=[]
        metric1=[]
        metric2=[]
        metric3=[]
        reader=csv.reader(csvfile)
        
        for row in reader:
                if (row[0]==instanceList[0]):
                    timeST.append(row[1])
                    metric1.append(float(row[2]))
                elif(row[0]==instanceList[1]):
                    metric2.append(float(row[2]))
                elif (row[0]==instanceList[2]):
                    metric3.append(float(row[2]))
        
               
        groups=len(timeST)
        index=nm.arange(groups)
        barWidth=0.2
        plt.bar(index+0.2, metric1, barWidth, color='blue')
        plt.bar(index, metric2, barWidth, color='red')
        plt.bar(index-0.2, metric3, barWidth, color='gray')
        plt.legend([instanceList[0], instanceList[1],instanceList[2]], loc='upper right')
        plt.ylabel("Average Network Out (in bytes)")
        plt.xlabel("TimeStamp")
        plt.title("Network Out")
        plt.xticks(index,timeST,rotation='vertical')
        plt.margins(0.25)
        subplt=plt.gcf()
        subplt.subplots_adjust(bottom=0.3)
        plt.savefig(filetoattach, format='pdf')
        plt.close()
        filetoattach.close()
    print("Dashboard created and saved.")
        
    
def mailFile(filetoattach):
    fromaddr = "netmans16@gmail.com"
    toaddr = "sagh8257@colorado.edu"
    
    msg = MIMEMultipart()
    
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "AWS Dashboard" 
    
    body = "Hi All,\n\nPFA the AWS CloudWatch metrics report for EC2 instances.\n\n\nRegards,\n\nTeamAWS"   
    msg.attach(MIMEText(body,'plain'))
    
    filename = filetoattach
    attachment = open(filetoattach, "rb")
    part = MIMEBase('application','octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',"attachment; filename= %s" % filename)
    
    msg.attach(part)
    
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login(fromaddr, "awsboto3")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr.split(","),text)
    server.quit()   
    print("Dashboard mailed successfully.") 
        
        
#Creating and mailing dashboard
filetoattach=plotMetrics(metricFilename1,metricFilename2,metricFilename3,dashfileName)   
mailFile(dashfileName)