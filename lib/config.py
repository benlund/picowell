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

endpoint = {
    'url': 'http://rp4.local:8080/picowell',
    'retries': 2,
    'retry_timeout': 10
}
