import wifimgr
import network
import poll_uart
import has_access

#oled
from machine import Pin, I2C
import ssd1306
from time import sleep


# configure the wifis
wlan = wifimgr.get_connection()
if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        pass  # you shall not pass :D


# Main Code goes here, wlan is a working network.WLAN(STA_IF) instance.
print("ESP OK")

nic = network.WLAN(network.STA_IF)


#oled demo
# ESP8266 Pin assignment
i2c = I2C(-1, scl=Pin(5), sda=Pin(4))
reset_pin = 16

oled_width = 128
oled_height = 32
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c,)

oled.
oled.text(str('AP:' + nic.config('essid')), 0, 0)
oled.text(str(nic.ifconfig()[0]), 0, 10)
oled.text('Ready', 0, 20)
oled.show()

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



poll_uart.start()
