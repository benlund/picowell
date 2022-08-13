app = {
    # name to associate with this sensor
    'source': 'well-sensor',

    # average of 5 readings taken outside water
    'low_adc_anchor': {
        'feet': 0.0,
        'adc': 11352.4
    },

    # average of 5 readings taken at measured depth
    'high_adc_anchor': {
        'feet': 5.8,
        'adc': 18800.8
    }
}

wifi = {
    'ssid': 'ssid',
    'password': 'password',
    'max_wait_s': 10,
    'retries': 2,
    'retry_timeout_s': 5
}

sensor = {
    'adc_gpio_pin_num': 28,
    'num_readings_to_take': 5,
    'reading_wait_s': 1
}

server = {
    'address': '0.0.0.0',
    'port': 80
}

client = {
    'loop': True,
    #'sleep_mode': 'light',
    #'sleep_mode': 'deep', # don't use this, not implemented in micropython yet
    'sleep_mode': 'test',
    #'sleep_ms': 1000 * 3600 # sleep for 1hr between readings when in client mode
    'sleep_ms': 1000 * 90 ##@@ TODO rm me
}

endpoint = {
    #'url': 'http://rp4.local:3637/picowell',
    'url': 'http://arrow.local:9292/picowell',
    'retries': 0,
    'retry_timeout_s': 10
}
