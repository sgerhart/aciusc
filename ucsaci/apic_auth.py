from __future__ import (absolute_import, division, print_function, unicode_literals)

import requests

def apic_auth(args):

    apic_ip = args.aip
    username = args.auser
    password = args.apwd


    apic_url = 'https://' + apic_ip + '/api/aaaLogin.json'

    uname_pwd = {"aaaUser" : { "attributes" : {"name" : username, "pwd" : password }}}

    # suppress the certificate errors
    requests.packages.urllib3.disable_warnings()

    try:

        post_response = requests.post(apic_url, json=uname_pwd, timeout=5, verify=False)

    except requests.RequestException as e:

        print("Error Logging into APIC... \n", e)
        exit(1)

    auth = post_response.json()

    try:

        auth_token = auth['imdata'][0]['aaaLogin']['attributes']['token']

    except (KeyError, TypeError):

        print("Authenication Error or Bad Response: ", auth)
        exit(1)

    # create cookie array from token
    return {'APIC-Cookie': auth_token}


