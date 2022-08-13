import machine
import time

MaxAdc = const(65535)
MaxVolts = const(3.3)

class Sensor:

    def __init__(self, adc_gpio_pin_num, low_adc_anchor, high_adc_anchor):
        print('Sensor#init')
        print('  adc_gpio_pin_num = ', adc_gpio_pin_num)
        print('  low_adc_anchor = ', low_adc_anchor)
        print('  high_adc_anchor = ', high_adc_anchor)

        self.pin = machine.ADC(adc_gpio_pin_num)
        self.low_adc = low_adc_anchor['adc']
        self.low_feet = low_adc_anchor['feet']
        self.feet_per_adc = (high_adc_anchor['feet'] - low_adc_anchor['feet']) / (high_adc_anchor['adc'] - low_adc_anchor['adc'])


    def reading(self, num_readings_to_take=5, reading_wait_s=1):
        readings_taken = 0
        readings_total = 0.0
        while readings_taken < num_readings_to_take:
            if readings_taken > 0:
                time.sleep(reading_wait_s)
            readings_total += self.do_reading()
            readings_taken += 1

        ave_adc = readings_total / num_readings_to_take
        volts = self.calc_volts(ave_adc)
        feet = self.calc_feet(ave_adc)

        return {
            'adc': ave_adc,
            'num': num_readings_to_take,
            'wait': reading_wait_s,
            'volts': volts,
            'feet': feet
        }


    def do_reading(self):
        return self.pin.read_u16()


    def calc_volts(self, adc):
        return adc * MaxVolts / MaxAdc


    def calc_feet(self, adc):
        return self.low_feet + ( (adc - self.low_adc) * self.feet_per_adc )
