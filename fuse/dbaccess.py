from __future__ import absolute_import, division, print_function
from builtins import *

import time

from pymongo import MongoClient


def dbconnect():

    client = MongoClient(port=27017)

    db = client.ucsaci

    return db


def dropDB(conn, collection):

    try:

        collection = conn[collection]
        cursor = collection.drop({})

    except Exception as e:

        print(e)


def insertDB(conn, collection, cluster):

    return 0


def get_clusterinfo(lgp_name):

    dbconn = dbconnect()

    collection = dbconn['ucscluster']

    try:

        # ISSUE - This only will search for the FI A side (Should also search for FI B) - Both will return same cluster
        # id
        ip = collection.find({"lpganame": lgp_name },{'ip': 1, 'members.node1.ip': 1,'members.node2.ip': 1, '_id': 0})

        for i in ip:

                return i

    except Exception as e:

        print(e)


def buildvlanrecord(epg_dn,vmm_dn, vlans, ucs_cluster_ip, server, veths, vmm_static):

    dbconn = dbconnect()

    # dropDB(dbconn, 'vlaninfo')

    vlaninfo = {
        'epg': epg_dn,
        'vmm-name': vmm_dn,
        'type': vmm_static,
        'ucs-cluster': ucs_cluster_ip,
        'server-name': server,
        'vlans': vlans,
        'veths': veths,
        'timestamp': time.time()
    }

    bd = dbconn

    results = bd.vlaninfo.insert_one(vlaninfo)

    # print(results)


def get_vlanrecord(epg_dn, vmm_dn):

    ucs_info = []

    dbconn = dbconnect()

    collection = dbconn['vlaninfo']

    try:

        result = collection.find({"epg": epg_dn, "vmm-name": vmm_dn}, {'ucs-cluster': 1, 'veths': 1, 'vlans': 1, '_id': 0})

        for i in result:

            ucs_info.append(i)

    except Exception as e:

        print(e)

    return ucs_info

    dbconn.logout()


def del_vlanrecord(epg_dn, vmm_dn):

    dbconn = dbconnect()

    collection = dbconn['vlaninfo']

    try:

        collection.delete_many({"epg": epg_dn, "vmm-name": vmm_dn})

    except Exception as e:

        print(e)

    dbconn.logout()
