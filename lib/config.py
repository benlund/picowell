app = {
    # name to associate with this sensor
    'source': 'well-sensor',

    # average of 5 readings taken outside water
    'zero_adc_reading': 19402.4
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
    #'sleep_ms': 1000 * 3600 # sleep for 1hr between readings when in client mode
    'sleep_ms': 1000 * 60 ##@@ TODO rm me
}

endpoint = {
    #'url': 'http://rp4.local:8080/picowell',
    'url': 'http://arrow.local:8080/picowell',
    'retries': 0,
    'retry_timeout_s': 10
}
