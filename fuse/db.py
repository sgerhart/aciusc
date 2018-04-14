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
        test = collection.find({"lpganame": lgp_name },{'ip': 1, 'members.node1.ip': 1,'members.node2.ip': 1, '_id': 0})

        for t in test:

                return t

    except Exception as e:

        print(e)


