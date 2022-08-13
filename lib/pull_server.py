import config
from wifi import WiFi
from sensor import Sensor

print('Start Server')
print('  source = ', config.app['source'])

sensor = Sensor(config.sensor['adc_gpio_pin_num'], config.app['zero_adc_reading'])
wifi = WiFi(config.wifi['ssid'], config.wifi['password'],
            config.wifi['max_wait_s'], config.wifi['retries'], config.wifi['retry_timeout_s'])

ip_address = wifi.connect()

if ip_address == None:
  print('!! no wifi connection, exiting')
  import sys
  sys.exit()


import socket
import json

print('Creating server socket')
addr = socket.getaddrinfo(config.server['address'], config.server['port'])[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print('  listening: addr = ', addr)

while True:
  try:
    cl, addr = s.accept()
    print('    connection from', addr)
    reading = sensor.reading(config.sensor['num_readings_to_take'], config.sensor['reading_wait_s'])
    print('    reading = ', reading)

    cl.send(json.dumps({'source': config.app['source'], 'reading': reading}) + "\n")
    cl.close()

  except OSError as e:
    cl.close()
    print('    connection closed')


wifi.disconnect()