# TODO: PEP8 cleanup
import wifimgr
import network
from utime import sleep
from usyslog import UDPClient, SyslogClient
from machine import Pin, Timer

#for RFID reading
from wiegand import Wiegand


#For querying API
import prequests as requests

# TODO: Implement the watchdog timer
# TODO: move these settings to a config file


#The AD group the member must be part of for access to be granted

AD_Group="3D Printer Basics"
syslog_server = '54.161.59.61' #'logs.evanlott.com'
syslog_port = 514

member_cache = []


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

def update_member_cache(*args):
    global member_cache
    print('attempting update of member cache')
    try:
        url = "http://pqzr4p9asl.execute-api.us-east-1.amazonaws.com/prod/api/v1/groups/3D%20Printer%20Basics"
        headers = {'x-api-key':"5bTUqyW6yJ7XbxEzAed0V3cOlROW0Sn39rbGpmUk"}
        response = requests.request("GET", url, headers=headers)
    except:
        print('failed to retrieve new member list for cache')
        
    try:
        member_cache.append(response.text)
        print('cache updated')
        if len(member_cache) > 1:
            member_cache.pop(0)
    except:
        print('failed to update cache object')



try:
    update_member_cache()
    print(member_cache)

except Exception as e:
    print('failed initial update of member cache: ' + str(e))
    

# Setup member cache refresh timer
#tim1 = Timer(1)
#tim1.init(period=10000, mode=Timer.PERIODIC, callback=update_member_cache)
#print('started member cache refresh timer')



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

def has_access_cached(rfid):
    global member_cache
    #print(rfid)
    #print(type(rfid))
    if int(rfid) > 16777215:
        print('40-bit ID detected')
        h=hex(int(rfid))
        h_trunc=h[4:]
        rfid=int(h_trunc,16)
        print('40-bit ID converted to: ' + str(rfid))
    # TODO: Pass ADGroup into URL parameter
    # TODO: Move base URL and headers to config file

    if str(rfid) in member_cache[0]:
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
    tim0.init(period=2000, mode=Timer.ONE_SHOT, callback=lambda t:pin.off())

    pin.on()

def get_lock_status():
    #returns 1 when lock is unlatched, 0 when latched
    pin = Pin(32, Pin.IN, Pin.PULL_UP)
    status = pin.value()
    if(status==1):
        return str(status) + ' unlatched'
    else:
        return str(status) + ' latched'
    
#def wiegand26_decode(facility_code, card):
    #wiegand library returns separate facility code and card number in decimal format.  
    #To get the number printed on the card, we need to convert both to binary, concatenate, then convert back to decimal.
    #facility_code_bin="{0:b}".format(facility_code)                                                                                                                            
    #card_bin="{0:b}".format(card)                                                                                                                                                                                                                                                  
    #return int(facility_code_bin+card_bin,2)
    
def decode_raw_rfid_to_10D(raw_rfid):
    mask = 0b00111111111111111111111110
    decoded_rfid = raw_rfid & mask
    return decoded_rfid

def on_card(card_number, facility_code, cards_read):
    #print('raw card number: ' + str(card_number))
    decoded_rfid = str(decode_raw_rfid_to_10D(card_number))
    #print('facility code: ' + str(facility_code) + '|' + 'card read:' + str(card_number) + '|' + str(cards_read) )
    print("Decoded: " + decoded_rfid)
    logger.log(5,'3DFabCab: rfid scanned: ' + decoded_rfid)

    print("Checking access API...")
    try:
        if has_access_cached(decoded_rfid):
            #print("Lock status: " + get_lock_status())            
            print("Access Granted to " + AD_Group)
            logger.log(5,"3DFabCab: Access Granted")
            open_lock()
            #tim0 = Timer(3)
            #tim0.init(period=2000, mode=Timer.ONE_SHOT, callback=lambda t:print("Lock status: " + get_lock_status()))

        else:
            print("Access Denied to " + AD_Group)
            logger.log(5,"3DFabCab: Access Denied")

    except Exception as E:
        print(str(E))
        f = open('error.txt', 'w')
        f.write(str(E))
        f.close()
    
    


# TODO: get interrupt working for latch switch
#def _on_pin(newstate):  
    #print('Door latch state changed: ' + str(newstate))
    
#def _on_pin32(newstate): _on_pin( newstate)


    
def main():
    #Make sure the pin driving the solenoid's transistor is off
    #the solenoid will melt if left on for more than a minute or two:
    pin = Pin(4, Pin.OUT)
    pin.off()

    #the Wiegand class will wait for IRQ interrupt on the specified pins, then execute the on_card callback function
    WIEGAND_ZERO = 34  # D0 Pin number here 
    WIEGAND_ONE = 35  # D1 Pin number here
    
    Wiegand(WIEGAND_ZERO, WIEGAND_ONE, on_card)
    
    # TODO: get interrupt working to detect latch switch and transistor gate pin state changes in near-realtime
    #pin32 = Pin(32, Pin.IN)
    #pin32.irq(trigger=Pin.IRQ_FALLING, handler=_on_pin32)

main()


