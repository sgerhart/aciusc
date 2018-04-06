from __future__ import absolute_import, division, print_function
from builtins import *

import time

from ucs_auth import ucsm_auth
from ucsm_query import getClusterInfo
# from pymongo import MongoClient
from db import dbconnect, dropDB, insertDB

from apic_query import get_protpathdn, get_loosenodes


def clustermatrix(user, pwd, apicauth, apic_ip):

    loosenodes = get_loosenodes(apic_ip, apicauth)

    dbconn = dbconnect()

    dropDB(dbconn, 'ucscluster')

    for ip in loosenodes:

        ucsfi = (ucsm_auth(ip, user, pwd))

        if ucsfi['ucs-active'] == 'y':

            clusteritems = getClusterInfo(ucsfi['ucs-cookie'], ucsfi['ucs-ip'])

            nodes = get_protpathdn(apic_ip, [clusteritems['A']['ip'],clusteritems['B']['ip']], apicauth)

            cluster = {
                'name': clusteritems['cluster']['name'],
                'ip': clusteritems['cluster']['ip'],
                'fabapath': nodes['A']['path'],
                'lpganame': nodes['A']['name'],
                'fabbpath': nodes['B']['path'],
                'lpgbname': nodes['B']['name'],
                'uname': '',
                'pword': '',
                'members': {
                    'node1': {
                        'mac': clusteritems['A']['mac'],
                        'ip': clusteritems['A']['ip'],
                        'role': clusteritems['A']['role']
                     },
                    'node2': {
                        'mac': clusteritems['B']['mac'],
                        'ip': clusteritems['B']['ip'],
                        'role': clusteritems['B']['role']
                    }
                },
                'timestamp': time.time()
            }

            # print(cluster)

            bd = dbconn

            results = bd.ucscluster.insert_one(cluster)

            # print(results)












