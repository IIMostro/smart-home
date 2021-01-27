"""
  @date 2021/1/22 下午10:46
"""
__author__ = 'ilmostro'

from machine import PWM
from machine import Pin


class Led():
    """
    创建LED类
    """

    def __init__(self, rpin, gpin, bpin, freq=1000):
        """
        构造函数
        :param pin: 接LED的管脚，必须支持PWM
        :param freq: PWM的默认频率是1000
        """
        self.pin_red = Pin(rpin)
        self.pin_green = Pin(gpin)
        self.pin_blue = Pin(bpin)

        self.led_red = PWM(self.pin_red, freq=freq)
        self.led_green = PWM(self.pin_green, freq=freq)
        self.led_blue = PWM(self.pin_blue, freq=freq)

        self.r = 0
        self.g = 0
        self.b = 255

        self.brightness = 1

    def rgb_light(self):
        if self.r in range(256) and \
                self.g in range(256) and \
                self.b in range(256) and \
                0.0 <= self.brightness <= 1.0:
            self.led_red.duty(int(self.r / 255 * self.brightness * 1023))
            self.led_green.duty(int(self.g / 255 * self.brightness * 1023))
            self.led_blue.duty(int(self.b / 255 * self.brightness * 1023))
        else:
            print("red green blue must between 0 and 255, and brightness from 0.0 to 1.0")

    def rgb(self):
        return self.r, self.g, self.b

    def deinit(self):
        """
        析构函数
        """
        self.led_red.deinit()
        self.led_green.deinit()
        self.led_blue.deinit()
