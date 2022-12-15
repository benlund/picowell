import machine
import time
import math

MaxAdc = const(2 ** 16)
MaxVolts = const(3.3)

class Sensor:

    def __init__(self, on_gpio_pin_num, adc_gpio_pin_num, low_adc_anchor, high_adc_anchor):
        print('Sensor#init')
        print('  on_gpio_pin_num = ', on_gpio_pin_num)
        print('  adc_gpio_pin_num = ', adc_gpio_pin_num)
        print('  low_adc_anchor = ', low_adc_anchor)
        print('  high_adc_anchor = ', high_adc_anchor)

        self.on_pin = None
        if on_gpio_pin_num is not None:
            self.on_pin = machine.Pin(on_gpio_pin_num, machine.Pin.OUT)
            self.on_pin.off()
        self.adc_pin = machine.ADC(adc_gpio_pin_num)
        self.low_adc = low_adc_anchor['adc']
        self.low_inches = low_adc_anchor['inches']
        self.inches_per_adc = (high_adc_anchor['inches'] - low_adc_anchor['inches']) / (high_adc_anchor['adc'] - low_adc_anchor['adc'])


    def reading(self, num_readings_to_take=8, reading_wait_s=1, num_bits_to_ignore=0, on_wait=0.2):
        if self.on_pin:
            self.on_pin.on()
            time.sleep(on_wait)

        readings_taken = 0
        readings_total = 0.0
        while readings_taken < num_readings_to_take:
            if readings_taken > 0:
                time.sleep(reading_wait_s)

            readings_total += (self.do_reading() >> num_bits_to_ignore << num_bits_to_ignore)
            readings_taken += 1

        if self.on_pin:
            self.on_pin.off()

        ave_adc = int(readings_total / num_readings_to_take) >> num_bits_to_ignore << num_bits_to_ignore
        volts = self.calc_volts(ave_adc)
        inches = self.calc_inches(ave_adc)
        feet = inches / 12

        ##@@ TODO calc rounding factor based on bits_to_ignore, max range, sensitivity
        volts = round(volts, 3)
        inches = round(inches, 1)
        feet = round(feet, 2)

        return {
            'adc': ave_adc,
            'num': num_readings_to_take,
            'wait': reading_wait_s,
            'bits_ignored': num_bits_to_ignore,
            'volts': volts,
            'inches': inches,
            'feet': feet,
            'ftin': self.calc_ftin(inches)
        }


    def do_reading(self):
        return self.adc_pin.read_u16()


    def calc_volts(self, adc):
        return adc * MaxVolts / MaxAdc


    def calc_inches(self, adc):
        return self.low_inches + ( (adc - self.low_adc) * self.inches_per_adc )


    def calc_ftin(self, inches):
        if inches >= 0:
            sign = ''
        else:
            sign = '-'

        whole_feet = math.floor(abs(inches) / 12)
        whole_inches = math.floor(abs(inches) % 12)
        fractional_inches = [round((abs(inches) % 1) * 8), 8] ## todo chose demoninator based on rounding

        if fractional_inches[0] == fractional_inches[1]:
            whole_inches += 1
            fractional_inches[0] = 0

        if whole_inches == 12:
            whole_inches = 0
            whole_feet += 1

        return "{}{}' {} {}/{}\"".format(sign, whole_feet, whole_inches,
                                         fractional_inches[0], fractional_inches[1])
