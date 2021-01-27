"""
  @date 2021/1/22 下午10:47
"""
__author__ = 'ilmostro'

from machine import Pin


class Relay():

    def __init__(self, pin):
        self.relaypin = Pin(pin, Pin.OUT)
        self.last_status = "ON"

    def set_state(self, state):
        if state == "ON":
            self.relaypin.value(0)
        else:
            self.relaypin.value(1)
        self.last_status = state
