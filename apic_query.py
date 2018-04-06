from __future__ import absolute_import, division, print_function
from builtins import *

from db import get_clusterip

import requests



def json_get(url, auth_token):

    try:

        response = requests.get(url, cookies=auth_token, verify=False)

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:

        print("http error: ", e)


def refresh_apic(apic_ip,auth_token):

    apic_url = 'https://' + apic_ip + '/api/aaaRefresh.json'

    refreshed_auth = json_get(apic_url,auth_token)

    for r in refreshed_auth['imdata']:

        token = str(r['aaaLogin']['attributes']['token'])

        return {'APIC-Cookie': token}


def build_subscription(url, auth_token):

    sub_ids = []

    # vpcif_subscr_url = url + 'class/vpcIf.json?subscription=yes'

    lnode_subscr_url = url + 'class/fabricLooseNode.json?subscription=yes'
    dom_subscr_url = url + 'class/fvRsDomAtt.json?subscription=yes'
    rvRsPath_url = url + 'class/fvRsPathAtt.json?subscription=yes'

    url_subscr = {rvRsPath_url, lnode_subscr_url, dom_subscr_url}

    for u in url_subscr:

        sub_info = json_get(u, auth_token)

        sub_ids.append(str(sub_info['subscriptionId']))

    return sub_ids


def refresh_subscription(apic_ip, ids,auth_token):

    for i in ids:

        url = 'https://' + apic_ip + '/api/subscriptionRefresh.json?id=' + i

        # print(url)

        json_get(url, auth_token)


def get_protpathdn(apic_ip, node_ips, auth_token):

    i = 0
    id = 'A'

    pathdns = {}

    for n in node_ips:

        pathdn_url = 'https://' + apic_ip + '/api/node/mo/topology/lsnode-' + n + '.json?query-target=children&target-subtree-class=fabricProtLooseLink'

        paths = json_get(pathdn_url, auth_token)

        if paths:

            for p in paths['imdata']:

                if i == 0:

                    index_value = str(p['fabricProtLooseLink']['attributes']['protPathDn']).index('[')
                    index_value_end = str(p['fabricProtLooseLink']['attributes']['protPathDn']).index(']')

                    name = (p['fabricProtLooseLink']['attributes']['protPathDn'])[index_value + 1:index_value_end]

                    pathdns[id]={'path': str(p['fabricProtLooseLink']['attributes']['protPathDn']), 'name': name}

                    i += 1

        id = 'B'
        i = 0

    return pathdns


def get_loosenodes(apic_ip, auth_token):

    nodes = []

    loosenode_url = 'https://' + apic_ip + '/api/class/fabricLooseNode.json'

    lnodes = json_get(loosenode_url, auth_token)

    if lnodes:

        for n in lnodes['imdata']:

            str_node = n['fabricLooseNode']['attributes']['id']

            #nodes.append(str(strNode))

    nodes.append('10.87.96.217')
    nodes.append('10.87.96.218')

    return nodes


def get_attachEnityP(apic_ip, dom_url, auth_token):

    aep_url = 'https://' + apic_ip + '/api/node/mo/' + dom_url + '.json?query-target=children&target-subtree-class=vmmAttEntityPCont'

    # print(aep_url)

    aep = json_get(aep_url, auth_token)

    if aep:

        for a in aep['imdata']:

            # print(a['vmmAttEntityPCont']['attributes']['name'])

            return a['vmmAttEntityPCont']['attributes']['name']


def get_accgrppol(apic_ip, dom_url, auth_token, aaep):

    lgp_name = []

    url = 'https://' + apic_ip + '/api/node/mo/' + dom_url + '/attentpcont-' + aaep + '.json?query-target=children&target-subtree-class=vmmAccGrpCont'

    # print(url)

    aep = json_get(url, auth_token)

    if aep:

        for a in aep['imdata']:

            lgp_name.append(a['vmmAccGrpCont']['attributes']['name'])

    return lgp_name

def get_vlans(apic_ip, auth_token, epg_dn, vmm_dn):

    vlans = {}

    url = 'https://' + apic_ip + '/api/node/mo/' + vmm_dn + '.json?query-target=children&target-subtree-class=vmmEpPD'

    dn = json_get(url, auth_token)

    # print(epg_dn)

    if dn:

        for i in dn['imdata']:

            if str(i['vmmEpPD']['attributes']['epgPKey']) == epg_dn:

                if i['vmmEpPD']['attributes']['primaryEncap'] == 'unknown':

                    vlans['primary'] = str(i['vmmEpPD']['attributes']['encap'])
                    vlans['Secondary'] = ''

                else:

                    vlans['primary'] = str(i['vmmEpPD']['attributes']['primaryEncap'])
                    vlans['Secondary'] = str(i['vmmEpPD']['attributes']['encap'])


        return vlans

def get_constructs(apic_ip, auth_token, event):

    vlans = {}

    ucs_cluster_ip = []

    index_dn = event['fvRsDomAtt']['attributes']['dn'].index('/rsdom')

    # Provides the dn for the EPG path, so that you can query to determine the encap (vlan) used
    epg_dn = event['fvRsDomAtt']['attributes']['dn'][0: index_dn]
    print('The following EPG modified: ' + epg_dn)

    # Provides the VMM that was modified - The EPG and VMM will be used to find the VLANs, VNICs to be modified
    vmm_dn = event['fvRsDomAtt']['attributes']['tDn']
    print('The following VMM was modified: ' + vmm_dn)

    ave_verify = get_aveinfo(vmm_dn, apic_ip,auth_token)

    if ave_verify is 'Y':

        print('AVE is currently not supported')


    aentityp = get_attachEnityP(apic_ip, str(event['fvRsDomAtt']['attributes']['tDn']), auth_token)
    lpg_name = get_accgrppol(apic_ip, str(event['fvRsDomAtt']['attributes']['tDn']), auth_token, aentityp)

    for l in lpg_name:

        value = get_clusterip(l)

        if value != None:

            ucs_cluster_ip.append(str(value['ip']))

    print('The follwoing UCS clusters will be configured ', ucs_cluster_ip)

    vlans = get_vlans(apic_ip,auth_token,epg_dn,vmm_dn)
    print('The following VLAN(s) will be added the UCS Cluster(s) ', vlans)




def get_aveinfo(vmm_dn, apic_ip, auth_token):


    url = 'https://' + apic_ip + '/api/node/mo/' + vmm_dn + '.json?query-target=self'

    print(url)

    aep = json_get(url, auth_token)

    print(aep)

    if aep:

        for a in aep['imdata']:

            if a['vmmDomP']['attributes']['enableAVE'] == 'yes':

                return 'Y'

            else:

                return 'N'
