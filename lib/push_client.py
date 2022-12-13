import gc
import machine
import time
import urequests
import json

import config
from wifi import WiFi
from sensor import Sensor


def dots(n, on_s=0.1, off_s=0.1):
    led = machine.Pin('LED', machine.Pin.OUT)
    while n > 0:
        led.on()
        time.sleep(on_s)
        led.off()
        time.sleep(off_s)
        n -= 1

def dashes(n):
    dots(n, 0.3, 0.1)


def vsys_reading():
    reading = None

    ## TODO short-circuit if wifi is active

    try:
        # GPIO 25 set to high to enable vsys read on GPIO 29
        machine.Pin(25, mode=machine.Pin.OUT, pull=machine.Pin.PULL_DOWN).high()

        # GPIO 29 set to IN to initialize ADC 3 for VSYS
        machine.Pin(29, machine.Pin.IN)

        # ADC 3 reads VSYS after a 1/3 voltage divider
        vsys_adc = machine.ADC(3).read_u16()
        reading =  {'adc': vsys_adc, 'volts': vsys_adc * 3 * 3.3 / 65535}

    finally:
        # Reset GPIO 29 for wifi usage
        print('reset')
        machine.Pin(29, machine.Pin.ALT, pull=machine.Pin.PULL_DOWN, alt=7)

    return reading


def set_clock_freq():
    try:
        if config.app['clock_frequency']:
            print('Change clock freq:', config.app['clock_frequency'])
            machine.freq(config.app['clock_frequency'])
    except:
        print('Error changing clock freq')


print('Start Client')
print('  source = ', config.app['source'])


sensor = Sensor(config.sensor['on_gpio_pin_num'],
                config.sensor['adc_gpio_pin_num'],
                config.app['low_adc_anchor'],
                config.app['high_adc_anchor'])
wifi = WiFi(config.wifi['ssid'], config.wifi['password'],
            config.wifi['max_wait_s'], config.wifi['retries'], config.wifi['retry_timeout_s'])


import debug_file

iteration = 0
start_time = time.time()

while True:
    set_clock_freq()

    vsys_reading_done = False
    wifi_done = False
    reading_done = False
    http_done = False
    response_code = None
    exception = None

    try:
        dots(1)

        print('VSYS reading')
        vsr = vsys_reading()
        vsys_reading_done = True
        print('  vsr = ', vsr)

        print('Sensor reading')
        reading = sensor.reading(config.sensor['num_readings_to_take'],
                                 config.sensor['reading_wait_s'],
                                 config.sensor['num_bits_to_ignore'])
        reading_done = True
        print('  reading = ', reading)

        ip_address = wifi.connect()

        if ip_address == None:
            dashes(2)
            print('!! no wifi connection, cannot proceed')

        else:
            wifi_done = True
            dots(2)

            print('Submit')
            retry_count = 0
            while retry_count <= config.endpoint['retries']:
                if retry_count > 0:
                    print('  retrying (', retry_count, ')')
                    time.sleep(config.endpoint['retry_timeout_s'])

                response = None

                try:
                    url = config.endpoint['url']
                    data = {
                        'source': config.app['source'],
                        'sensor': reading,
                        'vsys': vsr,
                        'meta': {
                            'iteration': iteration,
                            'uptime_s': time.time() - start_time
                        }
                    }
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
