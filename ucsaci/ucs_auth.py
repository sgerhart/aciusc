from __future__ import (absolute_import, division, print_function, unicode_literals)

from builtins import *

import xml.etree.ElementTree as ET
import requests


def ucsm_auth(ucsm_ip, user, pwd):

    ucsfi_url = 'https://' + ucsm_ip + '/nuova'

    uname_pwd = '<aaaLogin inName="' + user + '" inPassword="' + pwd + '" />'

    headers = {'Content-Type': 'application/xml'}

    # suppress the certificate errors
    requests.packages.urllib3.disable_warnings()

    try:

        post_response = requests.post(ucsfi_url, data=uname_pwd, timeout=5, verify=False, headers=headers)

    except requests.RequestException as e:

        print('Error Logging into UCS FI at ' + ucsm_ip + '... \n', e)
        exit(1)


    root = ET.fromstring(post_response.text)

    # ucs login is only successful if connecting to main cluster node
    if root.attrib.get('errorCode') == 'ERR-secondary-node':
        return {'ucs-active' : 'n', 'ucs-cookie': '', 'ucs-ip': ucsm_ip}
    else:
        return {'ucs-active' : 'y', 'ucs-cookie': root.attrib.get('outCookie'), 'ucs-ip': ucsm_ip}


def ucsfi_auth_refresh(cookie, args):

    ucsfi_ip = args
    username = args
    password = args

    ucsfi_url = 'https://' + ucsfi_ip + '/nuova'

    unamepwd = '<aaaRefresh inName="' + username + '" inPassword="' + password + '" inCookie="' + cookie + '" />'

    headers = {'Content-Type': 'application/xml'}

    # suppress the certificate errors
    requests.packages.urllib3.disable_warnings()

    try:

        post_response = requests.post(ucsfi_url, data=unamepwd, timeout=5, verify=False, headers=headers)

    except requests.RequestException as e:

        print('Error refreshing login on UCS FI at ' + ucsfi_ip + '... \n', e)
        exit(1)

    root = ET.fromstring(post_response.text)

    # return Refresh UCS Cooking for Auth
    return {'ucs-cookie': root.attrib.get('outCookie')}


def ucsfi_auth_logout(ucsm_ip,cookie):


    ucsfi_url = 'https://' + ucsm_ip + '/nuova'

    unamepwd = '<aaaLogout inCookie="' + cookie + '" />'

    headers = {'Content-Type': 'application/xml'}

    # suppress the certificate errors
    requests.packages.urllib3.disable_warnings()

    try:

        post_response = requests.post(ucsfi_url, data=unamepwd, timeout=5, verify=False, headers=headers)

    except requests.RequestException as e:

        print('Error refreshing login on UCS FI at ' + ucsm_ip + '... \n', e)
        exit(1)

    root = ET.fromstring(post_response.text)

    # return Refresh UCS Cooking for Auth
    return {'ucs-cookie': root.attrib.get('outCookie')}