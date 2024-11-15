#!/usr/bin/python3

'''
/******************************************************************************
 *  
 * Filename: create_ssdp.py
 * 
 * Purpose:  python 3 file for creating ssdp xml file
 * 
 *   This file generates a ssdp XML file using /opt/files/configuration.json
 *                                             /opt/files/product-tta.json
 *                                         and network information.
 * Variable fields:
 *   <friendlyName> : "sysName" from configuration.json
 *   <modelName> : "modelOid" from product-tta.json
 *   <modelNumber> : "model" from product-tta.json
 *   <serialNumber> : "serialnumber" from configuration.json
 *   <UDN> : randomly generated from eth 1 mac address
 *
 *
 * License:   Copyright 2024, Tx Rx Inc.  All rights reserved.
 *			  This software is confidential and may not be used without 
 *			  the express written permission of Tx Rx.
 * 
 *****************************************************************************/
'''

import os
import json
import subprocess



#  Define default strings to load to the xml file  
#
header = '<?xml version=\"1.0\"?>\r\n'
header += '<root xmlns=\"urn:schemas-upnp-org:device-1-0\">\r\n'
header += '<specVersion>\r\n'
header += '    <major>1</major>\r\n'
header += '    <minor>0</minor>\r\n'
header += '</specVersion>\r\n'
header += '<device>\r\n'
device_type = '    <deviceType>urn:txrx-com:device:DASCollector:1</deviceType>\r\n'
friendly_name = '    <friendlyName>%s</friendlyName>\r\n'
manufacturer = '    <manufacturer>TX RX Systems</manufacturer>\r\n'
model_name = '    <modelName>model</modelName>\r\n'
model_number = '    <modelNumber>%s</modelNumber>\r\n'
serial_number = '    <serialNumber>%s</serialNumber>\r\n'
url = '    <presentationURL>http://%s/login.php</presentationURL>\r\n'
udn = '    <UDN>%s</UDN>\r\n'

#  Define default strings to load to the xml file  
#
footer = '</device>\r\n'
footer += '</root>\r\n'

#  friendly_name comes from 
# model_name is blank.
# model-number comes from "model" in product-tta.json
# friendly_name and serial_number come from /opt/files/configuration.json
# url comes from the ip address 
# UDN comes from /var/lib/misc/ssdpd.cache


''' main - load up the strings '''

# get serial number and friendly name
try:
    with open('/opt/files/configuration.json', 'r') as file:
        config_dict = json.load(file)
except FileNotFoundError:
    print("Error: Configuration file not found")
except json.JSONDecodeError:
    print("Error: Invalid JSON format in configuration file")
except Exception as e:
    print(f"Error: {str(e)}")

friendly_name = friendly_name % config_dict.get('sysName')
serial_number = serial_number % config_dict.get('serialnumber')

try:
    with open('/opt/files/product-tta.json', 'r') as file:
        sys_info = json.load(file)
except FileNotFoundError:
    print("Error: Sysinfo file not found")
except json.JSONDecodeError:
    print("Error: Invalid JSON format in Sysinfo file")
except Exception as e:
    print(f"Error: {str(e)}")

model_number = model_number % sys_info.get('model')

try: 
    with open('/var/lib/misc/ssdpd.cache',"r") as file:
        for line in file:
            if 'uuid:' in line:
                uuid_line = line.strip()
                break
    udn = udn % uuid_line

except:
    print("uuid cache not found")

try:
    # Run the ip command and capture its output
    result = subprocess.run(['ip', '-4', 'addr', 'show', 'eth0'], capture_output=True, text=True)
    
    # Extract the IPv4 address from the output
    for line in result.stdout.split('\n'):
        if 'inet' in line:
            eth0_address = line.split()[1].split('/')[0]
            url = url % eth0_address
            break
    else:
        print("No IPv4 address found for eth0")
except subprocess.CalledProcessError:
    print("Error running ip command")

try:
    with open('/var/www/html/ssdp.xml','w') as file:
        file.write(header)
        file.write(device_type)
        file.write(friendly_name)
        file.write(manufacturer)
        file.write(model_name)
        file.write(model_number)
        file.write(serial_number)
        file.write(url)
        file.write(udn)
        file.write(footer)
        file.close()
except:
    print("Could not open ssdpd.xml")



