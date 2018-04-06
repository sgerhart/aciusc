from __future__ import absolute_import, division, print_function
from builtins import *

import requests
import xml.etree.ElementTree as ET
import apic_query

def getRequests(ucsm_ip, xml_content):

    ucsfi_url = 'https://' + ucsm_ip + '/nuova'

    headers = {'Content-Type': 'application/xml'}

    # suppress the certificate errors
    requests.packages.urllib3.disable_warnings()

    try:

        return requests.post(ucsfi_url, data=xml_content, timeout=5, verify=False, headers=headers)

    except requests.RequestException as e:

        print('Error Logging into UCS FI at ' + ucsm_ip + '... \n', e)
        exit(1)

# Retrieve Cluster Name, IP, Nodes(Name, IPs and Role)
def getClusterInfo(cookie, ucsm_ip):

    nodelist = []
    mgmtlist = []
    cluster = {}

    # Mongo DB Lookup first to see if matrix was created, then build new or modify old

    systemClassURL = '<configResolveClass cookie="' + cookie + '" classId="topSystem" inHierarchical="false"> </configResolveClass>'

    nodeInfoURL = '<configResolveClasses cookie="' + cookie + '" inHierarchical="false"> <inIds> <Id value="networkElement"/> <Id value="mgmtEntity"/> </inIds> </configResolveClasses>'


    treeSystem = ET.fromstring(getRequests(ucsm_ip, systemClassURL).text)

    nodeInfo = ET.fromstring(getRequests(ucsm_ip, nodeInfoURL).text)

    for child in treeSystem.iter(tag='topSystem'):

        systemlist = child.attrib

        cluster['cluster']={'name': systemlist['name'] , 'ip': systemlist['address']}

    for child in nodeInfo.iter(tag='networkElement'):

        nodelist = child.attrib

        for childmgmt in nodeInfo.iterfind('outConfigs/mgmtEntity[@id="' + nodelist['id'] + '"]'):

            mgmtlist = childmgmt.attrib

        cluster[nodelist['id']]={'ip': nodelist['oobIfIp'] , 'mac': nodelist['oobIfMac'] , 'role': mgmtlist['leadership']}

    return cluster

