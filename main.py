# TODO: order imports
import wifimgr
import network
from usyslog import UDPClient, SyslogClient

#For oled
from machine import Pin, I2C
import ssd1306
from time import sleep

#for RFID reading
from wiegand import Wiegand


#For querying API
import urequests as requests
import utime as time

#The AD group the member must be part of for access to be granted

AD_Group="3D Printer Basics"
syslog_server = '54.161.59.61' #'logs.evanlott.com'
syslog_port = 514

#oled init
i2c = I2C(-1, scl=Pin(5), sda=Pin(4))
reset_pin = 16
oled_width = 128
oled_height = 32
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c,)
oled.invert(1)
oled.show()
oled.text(str('Connecting...'), 0, 0)
oled.show()

# configure the wifis
wlan = wifimgr.get_connection()
if wlan is None:
    print("Could not initialize the network connection.")
    oled.fill(0)
    oled.show()
    oled.text(str("Can't connect to wifi!"), 0, 0)
    oled.show()
    while True:
        pass  
else:    
    nic = network.WLAN(network.STA_IF)
    print("ESP OK")
    oled.fill(0)
    oled.show()
    oled.text(str('AP:' + nic.config('essid')), 0, 0)
    oled.text(str(nic.ifconfig()[0]), 0, 10)
    oled.text('Ready', 0, 20)
    oled.show()
    sleep(2)



logger = UDPClient(ip=syslog_server, port=syslog_port)
    
logger.log(5,"3DFabCab: Cabinet lock online at: " + nic.ifconfig()[0])
logger.log(5,"3DFabCab: Cabinet lock access group: " + AD_Group)

print(AD_Group)

def has_access(rfid,AD_Group):
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
    pin = Pin(15, machine.Pin.OUT)
    pin.on()
    sleep(2)
    pin.off()


def wiegand26_decode(facility_code, card):
    #wiegand library returns separate facility code and card number in decimal format.  To get the number printed on the card, we need to convert both to binary, concatenate, then convert back to decimal.
    facility_code_bin="{0:b}".format(facility_code)                                                                                                                            
    card_bin="{0:b}".format(card)                                                                                                                                                                                                                                                  
    return int(facility_code_bin+card_bin,2)  

def on_card(card_number, facility_code, cards_read):
    decoded_rfid = str(wiegand26_decode(facility_code, card_number))
    print('facility code: ' + str(facility_code) + '|' + 'card read:' + str(card_number) + '|' + str(cards_read) )
    print("Decoded: " + decoded_rfid)
    logger.log(5,'3DFabCab: rfid scanned: ' + decoded_rfid)
    oled.fill(0)
    oled.show()
    oled.text(decoded_rfid,0,20)
    oled.show()
    sleep(1)

    print("Checking access API...")
    oled.fill(0)
    oled.show()
    oled.text("Checking Access API...",0,20)
    oled.show()
    try:
        if has_access(decoded_rfid, AD_Group):
            print("Access Granted to " + AD_Group)
            oled.fill(0)
            oled.show()
            oled.text("Access Granted!",0,20)
            oled.show()
            logger.log(5,"3DFabCab: Access Granted")
            open_lock()
            sleep(3)
            oled.fill(0)
            oled.show()
            oled.text('Scan!', 0, 20)
            oled.show()

        else:
            print("Access Denied to " + AD_Group)
            oled.fill(0)
            oled.show()
            oled.text('Access Denied!', 0, 20)
            oled.show()
            logger.log(5,"3DFabCab: Access Denied")
            sleep(5)
            oled.fill(0)
            oled.show()
            oled.text('Scan!', 0, 20)
            oled.show()

    except Exception as E:
        print(str(E))
        oled.fill(0)
        oled.show()
        oled.text("API issue",0,20)
        oled.show()
        f = open('error.txt', 'w')
        f.write(str(E))
        f.close()
        sleep(10)
        oled.fill(0)
        oled.show()
        oled.text('Scan!', 0, 20)
        oled.show()


def main():
    #Make sure the pin driving the solenoid's transistor is off:
    pin = Pin(15, machine.Pin.OUT)
    pin.off()

    #the Wiegand class will wait for IRQ interrupt on the specified pins, then execute the on_card callback function
    WIEGAND_ZERO = 12  # D0 Pin number here
    WIEGAND_ONE = 13   # D1 Pin number here

    Wiegand(WIEGAND_ZERO, WIEGAND_ONE, on_card)

    oled.fill(0)
    oled.show()
    oled.text('Scan!', 0, 20)
    oled.show()
    

main()

