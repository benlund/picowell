app = {
    # name to associate with this sensor
    'source': 'dev-sensor',

    'low_adc_anchor': {
        'inches': 22,
        'adc': 17600
    },

    'high_adc_anchor': {
        'inches': 50,
        'adc': 27392
    },

    'clock_frequency' : 62500000
}

wifi = {
    'ssid': 'ssid',
    'password': 'password',
    'max_wait_s': 10,
    'retries': 2,
    'retry_timeout_s': 5
}

sensor = {
    'on_gpio_pin_num': 22,
    'adc_gpio_pin_num': 28,
    'num_readings_to_take': 8,
    'reading_wait_s': 1,
    'num_bits_to_ignore': 6
}

server = {
    'address': '0.0.0.0',
    'port': 80
}

client = {
    'loop': True,
    'sleep_mode': 'light',
    #'sleep_mode': 'deep', # don't use this, not implemented in micropython yet
    #'sleep_mode': 'test',
    #'sleep_ms': 1000 * 3600 # sleep for 1hr between readings when in client mode
    'sleep_ms': 1000 * 65
}

endpoint = {
    #'url': 'http://rp4.local:3637/picowell',
    'url': 'http://arrow.local:9292/picowell',
    'retries': 0,
    'retry_timeout_s': 10
}
