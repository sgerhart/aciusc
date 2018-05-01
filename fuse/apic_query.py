from __future__ import absolute_import, division, print_function
from builtins import *

from dbaccess import get_clusterinfo, buildvlanrecord, del_vlanrecord, get_vlanrecord

import requests


# Generic requests for REST Gets (FUSE is read only to ACI)
def json_get(url, auth_token):

    try:

        response = requests.get(url, cookies=auth_token, verify=False)

        # response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:

        print("http error: ", e)

    except requests.exceptions.ConnectionError as e:

        print("There is a connection issue: ", e)



# Refresh APICs Token
def refresh_apic(apic_ip,auth_token):

    apic_url = 'https://' + apic_ip + '/api/aaaRefresh.json'

    refreshed_auth = json_get(apic_url,auth_token)

    for r in refreshed_auth['imdata']:

        token = str(r['aaaLogin']['attributes']['token'])

        return {'APIC-Cookie': token}


# Build subscriptions for WebSocket
def build_subscription(url, auth_token):

    sub_ids = []

    # vpcif_subscr_url = url + 'class/vpcIf.json?subscription=yes'

    lnode_subscr_url = url + 'class/fabricLooseNode.json?subscription=yes'
    dom_subscr_url = url + 'class/fvRsDomAtt.json?subscription=yes'
    rvRsPath_url = url + 'class/fvRsPathAtt.json?subscription=yes'
    fvAEPg_url = url + 'class/fvAEPg.json?subscription=yes'

    url_subscr = {rvRsPath_url, lnode_subscr_url, dom_subscr_url, fvAEPg_url}

    for u in url_subscr:

        sub_info = json_get(u, auth_token)

        sub_ids.append(str(sub_info['subscriptionId']))

    return sub_ids


# Refresh subscriptions
def refresh_subscription(apic_ip, ids,auth_token):

    for i in ids:

        url = 'https://' + apic_ip + '/api/subscriptionRefresh.json?id=' + i

        # print(url)

        json_get(url, auth_token)


# This gets the protPathDN which provides the leafs and the interface policy group
# Could also query the protPathDN which will provide you interface policy group with the Property 'name'
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


# Find the Fabric Interconnects that are directly connected to ACI
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

    aep = json_get(url, auth_token)

    if aep:

        for a in aep['imdata']:

            lgp_name.append(a['vmmAccGrpCont']['attributes']['name'])

    return lgp_name


def get_vlans(apic_ip, auth_token, epg_dn, vmm_dn, vmmstatic):

    vlans = {}

    url = 'https://' + apic_ip + '/api/node/mo/' + vmm_dn + '.json?query-target=children&target-subtree-class=vmmEpPD'

    dn = json_get(url, auth_token)

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


def vmmconstructs(apic_ip, auth_token, event):

    node_ips = []
    epg_dn = ''
    vmm_dn = ''
    vlans = {}

    if 'fvRsDomAtt' in event:

        index_dn = event['fvRsDomAtt']['attributes']['dn'].index('/rsdom')

        # Provides the dn for the EPG path, so that you can query to determine the encap (vlan) used
        epg_dn = event['fvRsDomAtt']['attributes']['dn'][0: index_dn]
        print('The following EPG modified: ' + epg_dn)

        # Provides the VMM that was modified - The EPG and VMM will be used to find the VLANs, VNICs to be modified
        vmm_dn = event['fvRsDomAtt']['attributes']['tDn']
        print('The following VMM was modified: ' + vmm_dn)

    # Need to finish - This is for if change was made to EPG for Intra-EPG isolation
    elif 'fvAEPg' in event:

        epg_dn = event['fvAEPg']['attributes']['dn']

        return

    vlans = get_vlans(apic_ip, auth_token, epg_dn, vmm_dn, 'vmm')
    print('The following VLAN(s) will be added the UCS Cluster(s) ', vlans)

    ave_verify = get_aveinfo(vmm_dn, apic_ip,auth_token)

    if ave_verify is 'Y':

        print('AVE is currently not supported')

    aentityp = get_attachEnityP(apic_ip, str(vmm_dn), auth_token)
    lpg_name = get_accgrppol(apic_ip, str(vmm_dn), auth_token, aentityp)

    for l in lpg_name:

        value = get_clusterinfo(l)

        if value is not None:

            node_ips.append(value['members']['node1']['ip'])
            node_ips.append(value['members']['node2']['ip'])

            ucs_cluster_ip = (str(value['ip']))

            print('The following UCS clusters will be configured ', ucs_cluster_ip)

            srv_info = get_esxservers(apic_ip,auth_token,vmm_dn, node_ips)

            for key, value in srv_info.items():

                buildvlanrecord(epg_dn,vmm_dn, vlans, ucs_cluster_ip, key, value, 'vmm')


def remove_vmmcontructs(apic_ip, auth_token, event):

    # Get index to get epg out of the event
    epg_index_dn = event['fvRsDomAtt']['attributes']['dn'].index('/rsdom')

    # Provides the dn for the EPG path, so that you can query to determine the encap (vlan) used
    epg_dn = event['fvRsDomAtt']['attributes']['dn'][0: epg_index_dn]

    # Get index to get vmm domain
    vmm_index_value = str(event['fvRsDomAtt']['attributes']['dn']).index('[')
    vmm_index_value_end = str(event['fvRsDomAtt']['attributes']['dn']).index(']')

    vmm_name = event['fvRsDomAtt']['attributes']['dn'][vmm_index_value + 1:vmm_index_value_end]

    print(get_vlanrecord(epg_dn,vmm_name))

    del_vlanrecord(epg_dn,vmm_name)



def get_aveinfo(vmm_dn, apic_ip, auth_token):

    url = 'https://' + apic_ip + '/api/node/mo/' + vmm_dn + '.json?query-target=self'

    aep = json_get(url, auth_token)

    if aep:

        for a in aep['imdata']:

            if a['vmmDomP']['attributes']['enableAVE'] == 'yes':

                return 'Y'

            else:

                return 'N'


def get_esxservers(apic_ip, auth_token, vmm_dn, node_ips):

    server_inter = {}

    ctrlr_dom = get_compctrlrdn(apic_ip,auth_token,vmm_dn)

    url = 'https://' + apic_ip + '/api/node/mo/' + ctrlr_dom + '.json?query-target=children&target-subtree-class=compHv'

    servers = json_get(url, auth_token)

    if servers:

        for s in servers['imdata']:

            ifids = get_ifId(apic_ip,auth_token,s['compHv']['attributes']['dn'],node_ips)

            if len(ifids) >= 1:

                server_inter[str(s['compHv']['attributes']['dn'])] = ifids

    return server_inter


def get_compctrlrdn(apic_ip,auth_token, vmm_dn ):

    index = vmm_dn.find('dom-')

    vmm_domname = str((vmm_dn)[index + 4:])

    url = 'https://' + apic_ip + '/api/node/class/compCtrlr.json?query-target-filter=and(eq(compCtrlr.domName,"' + vmm_domname + '"))'

    ctrlrdn = json_get(url, auth_token)

    if ctrlrdn:

        for i in ctrlrdn['imdata']:

            return i['compCtrlr']['attributes']['dn']


def get_ifId(apic_ip, auth_token, server_dn, nodes_ips):

    ifids = {}

    hvs = ''

    mac = ''

    for n in nodes_ips:

        url = 'https://' + apic_ip + '/api/node/mo/' + server_dn + '.json?query-target=children&target-subtree-class=hvsAdj&rsp-subtree-include=relations&query-target-filter=and(eq(hvsAdj.nbrKey,"' + n + '"))'

        hvsAdjs = json_get(url, auth_token)

        if hvsAdjs:

            for h in hvsAdjs['imdata']:

                try:

                    if 'compHpNic' in h:

                        mac = str(h['compHpNic']['attributes']['mac'])

                    elif 'hvsAdj' in h:

                        hvs = str(h['hvsAdj']['attributes']['ifId'])

                except Exception as e:

                    # print(e)

                    pass

            ifids[hvs] = mac

    return ifids


def buildtopology():

    # Build VMM Topology

    # Build Static Port Topology

    pass


