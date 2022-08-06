import gc
import machine
import time
import urequests
import json

import config
from wifi import WiFi
from sensor import Sensor

print('Start Client')
print('  source = ', config.app['source'])

led = machine.Pin('LED', machine.Pin.OUT)
led.off()

def dots(n):
    while n > 0:
        led.on()
        time.sleep(0.1)
        led.off()
        time.sleep(0.1)
        n -= 1

sensor = Sensor(config.sensor['adc_gpio_pin_num'], config.app['zero_adc_reading'])
wifi = WiFi(config.wifi['ssid'], config.wifi['password'],
            config.wifi['max_wait_s'], config.wifi['retries'], config.wifi['retry_timeout_s'])


while True:
    try:
        dots(1)

        ip_address = wifi.connect()

        if ip_address == None:
            print('!! no wifi connection, cannot proceed')

        else:
            dots(2)

            print('Report reading')
            reading = sensor.reading(config.sensor['num_readings_to_take'], config.sensor['reading_wait_s'])
            print('  reading = ', reading)

            retry_count = 0
            while retry_count <= config.endpoint['retries']:
                if retry_count > 0:
                    print('  retrying (', retry_count, ')')
                    time.sleep(config.endpoint['retry_timeout_s'])

                try:
                    print('  send to: ', config.endpoint['url'])
                    response = urequests.post(config.endpoint['url'],
                                              json={'source': config.app['source'], 'reading': reading})
                    print('    response: ', response.status_code)
                    break

                except Exception as e:
                    print('    error: ', e)

                finally:
                    # Make sure to close response to avoidn ENOMEM errors
                    if response:
                        response.close()

                retry_count += 1

            dots(3)
            wifi.disconnect()
            gc.collect()

    except Exception as e:
        dots(4)
        print('error: ', e)

    dots(5)
    machine.deepsleep(config.client['sleep_ms'])
    #machine.lightsleep(config.client['sleep_ms'])
    #time.sleep(config.client['sleep_ms'] / 1000)
