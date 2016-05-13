import boto3.ec2
from tkinter import *
from boto3.session import Session
from datetime import datetime,timedelta
from operator import itemgetter
from prettytable import PrettyTable
import time
import matplotlib
matplotlib.use('TkAgg')
import os
import boto.ec2
import paramiko
import boto.ec2
import tkinter as Tk
from tkinter import ttk


def instance_mon():
    
    ec2 = boto3.resource('ec2' )
    
    stopped_instances = []
    running_instances = []
    
    # Dictionary defined to store the private DNS values.
    
    DNS = {}
    
    # Check the running and stopped instances and store the private_DNS in the Dictionary
    
    
    for i in ec2.instances.all():
        temp = str(i.state)
        if 'stopped' in temp:
            d = str(i).find('=')
            e = str(i)[d+2:-2]
            stopped_instances.append(e)
            DNS[i.instance_id] = i.private_dns_name
            
        if 'running' in temp:
            m = str(i).find('=')
            f = str(i)[m+2:-2]
            running_instances.append(f)
            DNS[i.instance_id] = i.private_dns_name
            
    
    conn = boto.ec2.connect_to_region("us-west-2",
            aws_access_key_id='AKIAJNRMJ4YDZF5HGGRQ',
    aws_secret_access_key='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')
    
            
    print('Running Instance is : ' + running_instances[0] + '\n')
    print('Stopped Instance is : ' +  stopped_instances[0] + '\n')
    
    now = datetime.utcnow()
    past = now - timedelta(minutes=10)
    future = now + timedelta(minutes=20)
    
    # CloudWatch session created 
    
    session = Session(aws_access_key_id='AKIAJNRMJ4YDZF5HGGRQ',
    aws_secret_access_key='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',
    region_name='us-west-2')
    
    cw = session.client('cloudwatch')
       
    count = 0
    
    results = []
    CPU_utilization = {}
    results_1 = []
    Status_Check_Failed = {} 
   
    # Continuous loop which monitors the CPU_utlization and the Status_Check value for the EC2-instance
       
    while True :
            
        if count == 2:
            break
                
        time.sleep(2)
        
        # Below code would get the Average CPU_Utilisation of the running instances.
            
        results = cw.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'InstanceId', 'Value': running_instances[0]}],
            StartTime = past,
            EndTime = future,
            Period = 60,
            Statistics=['Average'])
        
        try :
            datapoints = results['Datapoints'] # Extract the value of datapoints and store it in a dictionary called as datapoints.
            last_datapoint = sorted(datapoints, key=itemgetter('Timestamp'))[-1]
            timestamp = str(last_datapoint['Timestamp'])
            CPU_utilization[timestamp] = last_datapoint['Average']
            print(" CPU Load is {} at {}".format(last_datapoint['Average'], timestamp))
            count = count + 1;
        except :
            print ("No datapoints available. Kindly wait for the instance to initialize")
            sys.exit()
        
        # Below code would get the Status_Check values for the running instances. Value of 0 indicate status check has passed.
        # whereas value of 1 indicates that the status check has failed for the instance.        
        results_1 = cw.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='StatusCheckFailed',
            Dimensions=[{'Name': 'InstanceId', 'Value': running_instances[0]}],
            StartTime = past,
            EndTime = future,
            Period=60,
            Statistics=['Maximum'])
        
        try :                    
            datapoints_1 = results_1['Datapoints']
            last_datapoint_1 = sorted(datapoints_1, key=itemgetter('Timestamp'))[-1]
            timestamp = str(last_datapoint_1['Timestamp'])
            Status_Check_Failed[timestamp] = last_datapoint_1['Maximum']
            print("System_check value is {} at {}".format(last_datapoint_1['Maximum'] , timestamp))
        except :
            print("No datapoints available. Kindly wait for the instance to initialize.")
            sys.exit()
        
        
        if (last_datapoint['Average'] > 0.6 or last_datapoint_1['Maximum'] != 0.0 ):
            
            print('Executing Failover Scenario: \n')
            
            x = []
            x.append(stopped_instances[0]) # Stop and start commands only accept tuples, list . The do not accept String values.
            ec2.instances.filter(InstanceIds= x).start()# This will start the instances'''
            print('Waiting for the backup instance to Fire up \n')
            print ('Please wait for 20 seconds !! \n')
            
            # Storing the private DNS value of the instance
            
            command = DNS[x[0]]
            
            time.sleep(20)
            
            instance = conn.get_all_instances(running_instances[0])[0].instances[0]
            
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            time.sleep(1)
            ssh.connect(str(instance.ip_address), username='ec2-user', key_filename='aws_test1.pem')
            
            
            print("Backup Instance is up !! \n")
            print('Running Rsync :- \n') # Executing RSync which keeps the instances in sync.
                                   
            stdin, stdout, stderr = ssh.exec_command('rsync -avz /var/www/ -e "ssh -i ./aws_test1.pem" ec2-user@'+command+':/var/www/')   
            stdin.flush()
            print(stdout.readlines())              
            ssh.close()   
            y = []
            y.append(running_instances[0])
            
            ec2.instances.filter(InstanceIds = y).stop()
            break;  
            
    print('Analysis Complete')
    sys.exit()

def endWindow():
    root.destroy()

root = Tk.Tk()
root.geometry('600x400')
root.configure(background = 'white')


y = Label(root , text = " GUI FOR EC2 FAILOVER SCENARIO. " , font= ("Times", 20, "bold italic") , bg = 'white')
y.pack()
y.grid(row = 0 , column = 1 , columnspan = 3 , ipadx = "80")

bg_image = PhotoImage(file ="aws_4.png")
v = Label (image = bg_image)
v.grid(row = 1 , column = 1)

bg_image_1 = PhotoImage(file ="aws_3.png")
k = Label (image = bg_image_1)
k.grid(row = 1, column = 2)

buttonA = Button(root , text ="Start Monitoring" , font=("Arial",15,"bold") , command=lambda: instance_mon(), bg = 'cyan' )
buttonB = Button(root , text ="End Monitoring"  , font=("Arial",15,"bold"), command=lambda: endWindow(), bg = 'red')

buttonA.grid(row=2 , column = 1)
buttonB.grid(row=2 , column = 2)

root.mainloop()

