import machine
import time

MaxAdc = const(2 ** 16)
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


    def reading(self, num_readings_to_take=8, reading_wait_s=1, num_bits_to_ignore=0):
        readings_taken = 0
        readings_total = 0.0
        while readings_taken < num_readings_to_take:
            if readings_taken > 0:
                time.sleep(reading_wait_s)
            readings_total += (self.do_reading() >> num_bits_to_ignore << num_bits_to_ignore)
            readings_taken += 1

        ave_adc = int(readings_total / num_readings_to_take) >> num_bits_to_ignore << num_bits_to_ignore
        volts = self.calc_volts(ave_adc)
        feet = self.calc_feet(ave_adc)
        if num_bits_to_ignore > 0:
            ##@@ TODO calc rounding factor based on bits_to_ignore
            volts = round(volts, 3)
            feet = round(feet, 3)

        return {
            'adc': ave_adc,
            'num': num_readings_to_take,
            'wait': reading_wait_s,
            'bits_ignored': num_bits_to_ignore,
            'volts': volts,
            'feet': feet
        }


    def do_reading(self):
        return self.pin.read_u16()


    def calc_volts(self, adc):
        return adc * MaxVolts / MaxAdc


    def calc_feet(self, adc):
        return self.low_feet + ( (adc - self.low_adc) * self.feet_per_adc )
