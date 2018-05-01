from __future__ import absolute_import, division, print_function
from builtins import *

import argparse

from apic_auth import apic_auth
from ucsm_build import clustermatrix
from listener import start
from apic_query import buildtopology


def main(inargs):

    auth_token = apic_auth(inargs)
    apic_ip = inargs.aip
    uuser = inargs.uuser
    upwd = inargs.upwd

    apic_url = 'https://' + apic_ip + '/api/'

    # This builds the UCS cluster matrix from Fabric Interconnects found connected to the ACI Fabric
    clustermatrix(uuser, upwd, auth_token, apic_ip)

    # Placeholder for getting the current vlan, veths, epg and vmm mappings
    # VMWare Currently and Static
    # build_topology()

    # This Starts the Threads
    start(apic_ip,auth_token,apic_url, uuser, upwd)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='ACIUCS')

    parser.add_argument('-i', dest='aip', type=str, default='172.16.1.1',
                        help='APIC IP: x.x.x.x')

    parser.add_argument('-p', dest='apwd', type=str, default='password',
                        help='APIC Password')

    parser.add_argument('-u', dest='auser', type=str, default='admin',
                        help='APIC Username. "admin" defaulted')

    parser.add_argument('-up', dest='upwd', type=str, default='password1',
                        help='UCS Password')

    parser.add_argument('-uu', dest='uuser', type=str, default='admin1',
                        help='UCS Username. "admin" defaulted')

    inargs = parser.parse_args()

    main(inargs)