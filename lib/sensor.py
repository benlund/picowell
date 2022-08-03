import machine
import time

FeetPerPsi = const(2.31)
MaxAdc = const(65535)
MaxVolts = const(3.3)
MaxPSI = const(21.0) # This is not measured, but calculated as the value at 3.3V based on sensor specification

class Sensor:

    def __init__(self, adc_gpio_pin_num, zero_adc_reading):
        print('Sensor#init')
        print('  adc_gpio_pin_num = ', adc_gpio_pin_num)
        print('  zero_adc_reading = ', zero_adc_reading)

        self.pin = machine.ADC(adc_gpio_pin_num)
        self.zero_psi_volts = self.calc_volts(zero_adc_reading)


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
        psi = self.calc_psi(volts)
        feet = self.calc_feet(psi)

        return {
            'adc': ave_adc,
            'num': num_readings_to_take,
            'wait': reading_wait_s,
            'volts': volts,
            'psi': psi,
            'feet': feet
        }


    def do_reading(self):
        return self.pin.read_u16()


    def calc_volts(self, adc):
        return adc * MaxVolts / MaxAdc


    def calc_psi(self, volts):
        return (volts - self.zero_psi_volts) * MaxPSI / (MaxVolts - self.zero_psi_volts)


    def calc_feet(self, psi):
        return FeetPerPsi * psi
