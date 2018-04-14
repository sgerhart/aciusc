
import threading
import json
import ssl
import time


from datetime import datetime
from websocket import WebSocket, create_connection
from apic_auth import apic_auth
from apic_query import build_subscription, refresh_subscription,refresh_apic,get_constructs
from ucsm_build import clustermatrix

ssl._create_default_https_context = ssl._create_unverified_context

# This class is used for refreshing the subscriptions
class worker(threading.Thread):

   def __init__(self, apic_ip, subscript_ids, token):

      threading.Thread.__init__(self)
      self.subids = subscript_ids
      self.apic_ip = apic_ip
      self.token = token
      #self.uname = uname
      #self.upwd = upwd


   def run(self):

       # refresh_subs(self.apic_ip, self.subids, self.token, self.uname, self.upwd)

       refresh_subs(self.apic_ip, self.subids, self.token)


# This class is used for the getting the subscriptions - websocket
class listener(threading.Thread):

   def __init__(self, apic_ip, cookie,uname, upwd):

        threading.Thread.__init__(self)
        self.apic_ip = apic_ip
        self.cookie = cookie
        self.name = "Testing Listener"
        self.uname = uname
        self.upwd = upwd

   def run(self):

        # print "Starting " + self.name
        try:

            get_subscription(self.apic_ip, self.cookie, self.uname,self.upwd)

        except Exception as e:

            print(e)


# Used to refresh the subscriptions - Called by the worker thread
def refresh_subs(apic_ip, subids, token):

    global refreshed_token
    global refreshed

    new_token = ''

    min = 0

    while True:

        time.sleep(45)

        print(str(datetime.now()))

        #print('refreshing')

        #print(refreshed_token)

        if refreshed_token == '':

            print("Refreshing Subscriptions with Original Token")
            refresh_subscription(apic_ip, subids, token)

        else:

            print("Refreshing Subscriptions with Refreshed_Token")
            refresh_subscription(apic_ip, subids, refreshed_token)

        if min == 10:

            refreshed = 1

            if new_token == '':

                new_token = refresh_apic(apic_ip,token)

                min = 0

                # clustermatrix(uname,upwd,new_token,apic_ip)

            else:

                new_token = refresh_apic(apic_ip, refreshed_token)

                min = 0

                # clustermatrix(uname, upwd, new_token, apic_ip)
        else:

            min += 1

        refreshed_token = new_token

        # print(refreshed_token)

# Opens up a websocket for subscription events (vpcIf, fabricLooseNode, fvRsDomAtt) This is called by the listener class
def get_subscription(apic_ip, cookie, uname, upwd):

        settest = set({})

        url = 'wss://' + apic_ip + '/socket' + cookie['APIC-Cookie']

        ws = create_connection(url, sslopt={"cert_reqs": ssl.CERT_NONE, })

        while True:

            event = ws.recv()
            result = json.loads(event)

            for i in result['imdata']:

                if 'fvRsDomAtt' in i:

                    s = 'vmmp-VMware'

                    try:

                        if str(i['fvRsDomAtt']['attributes']['status']) == 'deleted':

                            if refreshed_token == '':

                                print("Delete Event Detected")

                                # print(i)

                            else:

                                print("Delete Event Detected")

                                # print(i)


                        elif str(i['fvRsDomAtt']['attributes']['tDn']).find(s) and str(i['fvRsDomAtt']['attributes']['status']) == 'created':

                            if refreshed_token == '':

                                print("Create Event Detected")

                                get_constructs(apic_ip,cookie,i)

                            else:

                                print("Create Event Detected")

                                get_constructs(apic_ip, refreshed_token, i)


                    except Exception as e:

                      # print(e)

                      pass


                if 'fvRsPathAtt' in i:

                    # print(i)

                    pass


def start(apic_ip, cookie, apic_url, uname, upwd):

    # listener for ACI Events (Threading)
    wss_listener = listener(apic_ip, cookie, uname, upwd)

    wss_listener.start()

    # using sleep to make sure that the websocket
    # listener was active before making the subscriptions
    time.sleep(5)

    subscription_ids = (build_subscription(apic_url, cookie))

    # worker to refresh the subscription IDs every 45 seconds (60 default expire)
    subworker = worker(apic_ip, subscription_ids,cookie)

    subworker.start()

    time.sleep(60)


refreshed_token = ''

