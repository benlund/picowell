import machine
import time
import math

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
        self.low_inches = low_adc_anchor['inches']
        self.inches_per_adc = (high_adc_anchor['inches'] - low_adc_anchor['inches']) / (high_adc_anchor['adc'] - low_adc_anchor['adc'])


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
        inches = self.calc_inches(ave_adc)
        feet = inches / 12

        ##@@ TODO calc rounding factor based on bits_to_ignore, max range, sensitivity
        volts = round(volts, 3)
        inches = round(inches, 1)
        feet = round(feet, 2)

        whole_feet = math.floor(feet)
        whole_inches = math.floor(inches % 12)
        fractional_inches = [round((inches % 1) * 8), 8] ## todo chose demoninator based on rounding
        if fractional_inches[0] == fractional_inches[1]:
            whole_inches += 1
            fractional_inches[0] = 0

        ftin = "{}' {} {}/{}\"".format(whole_feet, whole_inches, fractional_inches[0], fractional_inches[1])

        return {
            'adc': ave_adc,
            'num': num_readings_to_take,
            'wait': reading_wait_s,
            'bits_ignored': num_bits_to_ignore,
            'volts': volts,
            'inches': inches,
            'feet': feet,
            'ftin': ftin
        }


    def do_reading(self):
        return self.pin.read_u16()


    def calc_volts(self, adc):
        return adc * MaxVolts / MaxAdc


    def calc_inches(self, adc):
        return self.low_inches + ( (adc - self.low_adc) * self.inches_per_adc )
