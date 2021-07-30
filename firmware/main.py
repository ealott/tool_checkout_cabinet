# TODO: PEP8 cleanup
import wifimgr
import network
from utime import sleep
from usyslog import UDPClient, SyslogClient
from machine import Pin, Timer

#for RFID reading
from wiegand import Wiegand


#For querying API
import urequests as requests

# TODO: Implement the watchdog timer
# TODO: move these settings to a config file


#The AD group the member must be part of for access to be granted

AD_Group="3D Printer Basics"
syslog_server = '54.161.59.61' #'logs.evanlott.com'
syslog_port = 514


# configure the wifis
# TODO: add extended configurations to temporary Setup wifi page
wlan = wifimgr.get_connection()
if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        pass  
else:    
    nic = network.WLAN(network.STA_IF)
    print("ESP OK")

# TODO: Create variable for cabinet name, move to config file

logger = UDPClient(ip=syslog_server, port=syslog_port)
    
logger.log(5,"3DFabCab: Cabinet lock online at: " + nic.ifconfig()[0])
logger.log(5,"3DFabCab: Cabinet lock access group: " + AD_Group)

print(AD_Group)

def has_access(rfid,AD_Group):
    # TODO: Move lookup API URL to config file
    url="http://192.168.200.32:8080/api/v1/lookupByRfid"
    headers = {'cache-control':"no-cache",'content-type': "application/x-www-form-urlencoded",}
    payload = 'rfid=' + str(rfid) 
    response = requests.request("POST", url, data=payload, headers=headers)
    if AD_Group in response.text:
        #print("Access Granted; opening.").
        return True
    else:
        #print("Access Denied")
        return False

def open_lock():
    # TODO: move pin # to config file
    pin = Pin(4, Pin.OUT)
    
    #Start a 2 second timer to shutoff the lock.  Engaging the lock for more than a few minutes will melt it.
    tim0 = Timer(0)
    tim0.init(period=5000, mode=Timer.ONE_SHOT, callback=lambda t:pin.off())

    pin.on()

def get_lock_status():
    #returns 1 when lock is unlatched, 0 when latched
    pin = Pin(32, Pin.IN, Pin.PULL_UP)
    status = pin.value()
    if(status==1):
        return str(status) + ' unlatched'
    else:
        return str(status) + ' latched'
    
#Should produce 11094651804
def wiegand26_decode(facility_code, card):
    #wiegand library returns separate facility code and card number in decimal format.  
    #To get the number printed on the card, we need to convert both to binary, concatenate, then convert back to decimal.
    facility_code_bin="{0:b}".format(facility_code)                                                                                                                            
    card_bin="{0:b}".format(card)                                                                                                                                                                                                                                                  
    return int(facility_code_bin+card_bin,2)  

def on_card(card_number, facility_code, cards_read):
    decoded_rfid = str(wiegand26_decode(facility_code, card_number))
    print('facility code: ' + str(facility_code) + '|' + 'card read:' + str(card_number) + '|' + str(cards_read) )
    print("Decoded: " + decoded_rfid)
    logger.log(5,'3DFabCab: rfid scanned: ' + decoded_rfid)

    print("Checking access API...")
    try:
        if has_access(decoded_rfid, AD_Group):
            print("Lock status: " + get_lock_status())            
            print("Access Granted to " + AD_Group)
            logger.log(5,"3DFabCab: Access Granted")
            open_lock()
            tim0 = Timer(3)
            tim0.init(period=5000, mode=Timer.ONE_SHOT, callback=lambda t:print("Lock status: " + get_lock_status()))
            


        else:
            print("Access Denied to " + AD_Group)
            logger.log(5,"3DFabCab: Access Denied")

    except Exception as E:
        print(str(E))
        f = open('error.txt', 'w')
        f.write(str(E))
        f.close()


def main():
    #Make sure the pin driving the solenoid's transistor is off
    #the solenoid will melt if left on for more than a minute or two:
    pin = Pin(4, Pin.OUT)
    pin.off()

    #the Wiegand class will wait for IRQ interrupt on the specified pins, then execute the on_card callback function
    WIEGAND_ZERO = 34  # D0 Pin number here
    WIEGAND_ONE = 35  # D1 Pin number here

    Wiegand(WIEGAND_ZERO, WIEGAND_ONE, on_card)

    
main()


