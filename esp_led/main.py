from LED import Led
from Relay import Relay

import time
import uasyncio
import network
import ujson
from umqtt.simple import MQTTClient
import esp

"""
Wi-Fi Gateway : SSID and Password
"""
WIFI_AP_SSID = "TP-LINK_11D4"
WIFI_AP_PSW = "13634130635"

"""
MQTT topic
"""
MQTT_SERVER = '192.168.1.104'
MQTT_PORT = 1883
MQTT_CLIENT_ID = 'drawing_light_1'
MQTT_USER_NAME = ""
MQTTT_PASSWORD = ""
#发布命令
MQTT_COMMAND_TOPIC = 'drawing/light/switch'
#接受状态
MQTT_STATE_TOPIC = 'drawing/light/state'

led = Led(5, 4, 0)
relay = Relay(16)

mqtt_client = None
color = 0  # enum 0=red, 1=green, 2=blue
name = ""  # light name. it is optional
light_changed = False


async def wifi_connect(ssid, pwd):
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    sta.connect(ssid, pwd)

    while not sta.isconnected():
        print("Wi-Fi Connecting...")
        time.sleep_ms(500)


def mqtt_callback(topic, msg):
    global led, relay
    global color, name, light_changed

    print((topic, msg))
    params = ujson.loads(msg)
    power_switch_tmp = params.get('state')
    if power_switch_tmp is not None:
        power_switch = power_switch_tmp
        relay.set_state(power_switch)

    brightness_tmp = params.get('brightness')
    if brightness_tmp is not None:
        led.brightness = brightness_tmp/255

    color_tmp = params.get('color_temp')
    if color_tmp is not None:
        color = color_tmp

    color = params.get('color')
    if color is not None:
        led.r = color.get('r')
        led.g = color.get('g')
        led.b = color.get('b')

    if brightness_tmp is not None or color_tmp is not None or color is not None:
        light_changed = True


async def mqtt_connect():

    global mqtt_client

    mqtt_client = MQTTClient(MQTT_CLIENT_ID, MQTT_SERVER, MQTT_PORT, MQTT_USER_NAME, MQTTT_PASSWORD, 60)
    mqtt_client.set_callback(mqtt_callback)
    mqtt_client.connect()


def mqtt_report(client):
    msg = {
        "brightness": led.brightness,
        "color": {
            "r": led.r,
            "g": led.g,
            "b": led.b,
        },
        "state": relay.last_status
    }

    client.publish(MQTT_STATE_TOPIC.encode(), ujson.dumps(msg).encode())


async def light_loop():
    global led, relay
    global name, light_changed

    time_cnt = 0

    led.rgb_light()

    mqtt_client.subscribe(MQTT_COMMAND_TOPIC.encode())
    while True:
        mqtt_client.check_msg()

        if light_changed:
            light_changed = False
            led.rgb_light()

        if time_cnt >= 20:
            mqtt_report(mqtt_client)
            time_cnt = 0
        time_cnt = time_cnt + 1
        uasyncio.sleep_ms(50)


async def main():
    global mqtt_client

    # Wi-Fi connection
    try:
        await uasyncio.wait_for(wifi_connect(WIFI_AP_SSID, WIFI_AP_PSW), 20)
        esp.sleep_type(2)
    except uasyncio.TimeoutError:
        print("wifi connected timeout!")
    # MQTT connection
    try:
        await uasyncio.wait_for(mqtt_connect(), 20)
    except uasyncio.TimeoutError:
        print("mqtt connected timeout!")

    await uasyncio.gather(light_loop())


uasyncio.run(main())