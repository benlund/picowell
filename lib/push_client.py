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

def dots(n, on_s=0.1, off_s=0.1):
    while n > 0:
        led.on()
        time.sleep(on_s)
        led.off()
        time.sleep(off_s)
        n -= 1

def dashes(n):
    dots(n, 0.3, 0.1)


def vsys_reading():
    # GPIO 29 set to IN to initialize ADC 3 for VSYS
    machine.Pin(29, machine.Pin.IN)
    # ADC 3 reads VSYS after a 1/3 voltage divider
    adc = machine.ADC(3).read_u16()
    # MUST set GPIO 29 back to OUT to avoid breaking wifi (for some reason TBD)
    # - Nope, this still breaks wifi! Disabled
    machine.Pin(29, machine.Pin.OUT)
    return {'adc': adc, 'volts': adc * 3.3 * 3 / 65535}


sensor = Sensor(config.sensor['adc_gpio_pin_num'], config.app['low_adc_anchor'], config.app['high_adc_anchor'])
wifi = WiFi(config.wifi['ssid'], config.wifi['password'],
            config.wifi['max_wait_s'], config.wifi['retries'], config.wifi['retry_timeout_s'])


import debug_file

iteration = 0

while True:
    vsys_reading_done = False
    wifi_done = False
    reading_done = False
    http_done = False
    response_code = None
    exception = None

    try:
        dots(1)

        print('VSYS reading')
        print('  disabled')
        vsr = None #vsys_reading()
        vsys_reading_done = True
        print('  vsr = ', vsr)

        ip_address = wifi.connect()

        if ip_address == None:
            dashes(2)
            print('!! no wifi connection, cannot proceed')

        else:
            wifi_done = True
            dots(2)

            print('Sensor reading')
            reading = sensor.reading(config.sensor['num_readings_to_take'],
                                     config.sensor['reading_wait_s'],
                                     config.sensor['num_bits_to_ignore'])
            reading_done = True
            print('  reading = ', reading)

            print('Submit')
            retry_count = 0
            while retry_count <= config.endpoint['retries']:
                if retry_count > 0:
                    print('  retrying (', retry_count, ')')
                    time.sleep(config.endpoint['retry_timeout_s'])

                response = None

                try:
                    url = config.endpoint['url']
                    data = {'source': config.app['source'], 'sensor': reading, 'vsys' : vsr}
                    print('  send to: ', url)
                    print('   data: ', data)
                    response = urequests.post(url, json=data)

                    http_done = True
                    response_code = response.status_code
                    exception = None
                    dots(3)
                    print('    response: ', response.status_code)
                    break

                except Exception as e:
                    exception = e
                    dashes(3)
                    print('    error: ', e)
                    import sys
                    sys.print_exception(e)

                finally:
                    # Make sure to close response to avoidn ENOMEM errors
                    if response != None:
                        response.close()

                retry_count += 1

            wifi.disconnect()
            gc.collect()


    except Exception as e:
        exception = e
        dashes(3)
        print('error: ', e)

    debug_file.write_json({'iteration': iteration,
                           'wifi_done': wifi_done,
                           'reading_done': reading_done,
                           'vsys_reading_done': vsys_reading_done,
                           'http_done': http_done,
                           'response_code': response_code,
                           'exception': exception})
    if exception != None:
        debug_file.append_exception(exception)

    iteration += 1

    if config.client['loop']:
        if 'light' == config.client['sleep_mode']:
            machine.lightsleep(config.client['sleep_ms'])
        elif 'deep' == config.client['sleep_mode']:
            # Don't use this, not implemented in micropython
            machine.deepsleep(config.client['sleep_ms'])
        else:
            time.sleep(config.client['sleep_ms'] / 1000)
    else:
        break
