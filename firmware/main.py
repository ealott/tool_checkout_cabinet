import wifimgr
import network
#import poll_uart
#import has_access

#For oled
from machine import Pin, I2C
import ssd1306
from time import sleep

#For UART polling
import uasyncio as asyncio
from machine import UART
import uos

#For querying API
import urequests as requests
import utime as time

#The AD group the member must be part of for access to be granted
AD_Group="Digital Media Locker"


#oled demo
# ESP8266 Pin assignment
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
    oled.text(str("Can't connect"), 0, 0)
    oled.show()
    while True:
        pass  # you shall not pass :D


# Main Code goes here, wlan is a working network.WLAN(STA_IF) instance.
print("ESP OK")

nic = network.WLAN(network.STA_IF)

oled.fill(0)
oled.show()
oled.text(str('AP:' + nic.config('essid')), 0, 0)
oled.text(str(nic.ifconfig()[0]), 0, 10)
oled.text('Ready', 0, 20)
oled.show()

#init UART
uos.dupterm(None, 1) # disable REPL on UART(0) so we can receive from the RFID reader
uart = UART(0, 9600)
uart.init()

sleep(2)

# # start simple webserver
# import machine
# pins = [machine.Pin(i, machine.Pin.IN) for i in (0, 2, 4, 5, 12, 13, 14, 15)]

# html = """<!DOCTYPE html>
# <html>
#     <head> <title>ESP8266 Pins</title> </head>
#     <body> <h1>ESP8266 Pins</h1>
#         <table border="1"> <tr><th>Pin</th><th>Value</th></tr> %s </table>
#     </body>
# </html>
# """

# import socket
# addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

# s = socket.socket()
# s.bind(addr)
# s.listen(1)

# print('listening on', addr)

# while True:
#     cl, addr = s.accept()
#     print('client connected from', addr)
#     cl_file = cl.makefile('rwb', 0)
#     while True:
#         line = cl_file.readline()
#         if not line or line == b'\r\n':
#             break
#     rows = ['<tr><td>%s</td><td>%d</td></tr>' % (str(p), p.value()) for p in pins]
#     response = html % '\n'.join(rows)
#     cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
#     cl.send(response)
#     cl.close()


# uos.dupterm(None, 1) # disable REPL on UART(0)
# from machine import UART

# uart = UART(0, 9600)                         # init with given baudrate
# uart.init(9600)

# while True:
#     rfid=uart.read()      # read all available characters
#     if rfid:
#         url="http://192.168.200.32:8080/api/v1/lookupByRfid"
#         headers = {'cache-control':"no-cache",'content-type': "application/x-www-form-urlencoded",}
#         payload = 'rfid=' + str(rfid) 
#         response = urequests.request("POST", url, data=payload, headers=headers)

#         if AD_Group in response.text:
#             print("Access Granted")
#             oled.text('Access Granted', 0, 20)
#             oled.show()
#         else:
#             print("Access Denied")
#             oled.text('Access Denied', 0, 20)
#             oled.show()
def has_access(rfid,AD_Group):
    url="http://192.168.200.32:8080/api/v1/lookupByRfid"
    headers = {'cache-control':"no-cache",'content-type': "application/x-www-form-urlencoded",}
    payload = 'rfid=' + str(rfid) 
    response = requests.request("POST", url, data=payload, headers=headers)
    if AD_Group in response.text:
        #print("Access Granted, opening.")
        return True
    else:
        #print("Access Denied")
        return False

#this is broked
def open_lock():
    pin = Pin(15, machine.Pin.OUT)
    pin.on()
    sleep(2)
    pin.off()

# async def receiver():
#     sreader = asyncio.StreamReader(uart)
#     while True:
#         res = await sreader.readline()
#         print('Recieved', res)
#         #has_access(int(res),AD_Group)

async def start():
    #loop = asyncio.get_event_loop()
    #loop.create_task(receiver())
    #loop.run_forever()
    pass

def main():
    has_rfid = False
    while not has_rfid:
        while uart.any() < 1:
            sleep(0.5)
            oled.fill(0)
            oled.show()
            oled.text('Scan!', 0, 20)
            oled.show()
        res = uart.read()
        print('Recieved', res)
        oled.fill(0)
        oled.show()
        oled.text(res,0,20)
        oled.show()
        sleep(1)
        try:
            rfid=res.decode().strip() #might fail here if bad RFID sequence is read
            print(rfid)
            has_rfid = True
        except:
            print("Oh no!")
            oled.fill(0)
            oled.show()
            oled.text("Oh no.  Poop.",0,00)
            oled.text("Bad Read.",0,10)
            oled.text("Try read again!",0,20)
            oled.show()
            sleep(2)


    
    try:
        #rfid=res.decode().strip() #might fail here if bad RFID sequence is read
        #print(rfid)
        oled.fill(0)
        oled.show()
        print("RFID OK")
        oled.text('RFID OK',0,20)
        oled.show()
        sleep(1)

        if len(rfid) == 10:
            try:
                print("Checking access API...")
                oled.fill(0)
                oled.show()
                oled.text("Checking Access API...",0,20)
                oled.show()
                if has_access(rfid, AD_Group):
                    print("Access Granted!")
                    oled.fill(0)
                    oled.show()
                    oled.text("Granted!",0,20)
                    oled.show()
                    open_lock()
                    sleep(3)
                else:
                    print("Access Denied!")
                    oled.fill(0)
                    oled.show()
                    oled.text('Access Denied!', 0, 20)
                    oled.show()
                    sleep(5)
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

    except:
        print("Bad read; try again.")
        oled.fill(0)
        oled.show()
        oled.text("Try read again.")
        oled.show()
        sleep(2)


while True: 
    main()
    sleep(1)

