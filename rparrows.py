#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import os
from time import sleep

def write_file(path, text):
    f = open(path, 'w')
    f.write(text + "\n")
    f.close()

base_dir = '/sys/kernel/config/usb_gadget/rparrows'
os.mkdir(base_dir)

# Linux Foundation
write_file(os.path.join(base_dir, 'idVendor'), '0x1d6b')
# Multifunction Composite Gadget
write_file(os.path.join(base_dir, 'idProduct'), '0x0104')
# v1.0.0
write_file(os.path.join(base_dir, 'bcdDevice'), '0x0100')
# USB2
write_file(os.path.join(base_dir, 'bcdUSB'), '0x0200')

strings_dir = os.path.join(base_dir, 'strings/0x409')
os.makedirs(strings_dir)
write_file(os.path.join(strings_dir, 'serialnumber'), 'f88dc9a2f1c3524d')
write_file(os.path.join(strings_dir, 'manufacturer'), 'marcie001')
write_file(os.path.join(strings_dir, 'product'), 'rparrows')

configs_dir = os.path.join(base_dir, 'configs/c.1/strings/0x409')
os.makedirs(configs_dir)
write_file(os.path.join(configs_dir, 'configuration'), 'Config 1: ECM network')
write_file(os.path.join(base_dir, 'configs/c.1/MaxPower'), '250')

hid_dir = os.path.join(base_dir, 'functions/hid.usb0')
os.makedirs(hid_dir)
write_file(os.path.join(hid_dir, 'protocol'), '1')
write_file(os.path.join(hid_dir, 'subclass'), '1')
write_file(os.path.join(hid_dir, 'report_length'), '8')
desc = os.open(os.path.join(hid_dir, 'report_desc'), os.O_WRONLY)
os.write(desc, b'\x05\x01\x09\x06\xa1\x01\x05\x07\x19\xe0\x29\xe7\x15\x00\x25\x01\x75\x01\x95\x08\x81\x02\x95\x01\x75\x08\x81\x03\x95\x05\x75\x01\x05\x08\x19\x01\x29\x05\x91\x02\x95\x01\x75\x03\x91\x03\x95\x06\x75\x08\x15\x00\x25\x65\x05\x07\x19\x00\x29\x65\x81\x00\xc0')
os.close(desc)
os.symlink(hid_dir, os.path.join(base_dir, 'configs/c.1/hid.usb0'))

write_file(os.path.join(base_dir, 'UDC'), os.listdir('/sys/class/udc')[0])

class Keymap:
    def __init__(self, name, bcm, usage_id, index):
        self.name = name
        self.bcm = bcm
        self.usage_id = usage_id
        self.index = index

right = Keymap('RIGHT_ARROW', int(os.getenv('RIGHT_ARROW', '27')), 0x4f, 2)
left  = Keymap('LEFT_ARROW',  int(os.getenv('LEFT_ARROW',  '22')), 0x50, 3)
down  = Keymap('DOWN_ARROW',  int(os.getenv('DOWN_ARROW',  '23')), 0x51, 4)
up    = Keymap('UP_ARROW',    int(os.getenv('UP_ARROW',    '24')), 0x52, 5)

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup(right.bcm)
GPIO.cleanup(left.bcm)
GPIO.cleanup(down.bcm)
GPIO.cleanup(up.bcm)
GPIO.setup(right.bcm, GPIO.IN)
GPIO.setup(left.bcm, GPIO.IN)
GPIO.setup(down.bcm, GPIO.IN)
GPIO.setup(up.bcm, GPIO.IN)

dev = os.open('/dev/hidg0', os.O_WRONLY)

state = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')

def right_change(ch):
    global dev, state, right
    if GPIO.input(ch) == GPIO.LOW:
        state[right.index] = 0x00
    else:
        state[right.index] = right.usage_id
    os.write(dev, bytes(state))

def left_change(ch):
    global dev, state, left
    if GPIO.input(ch) == GPIO.LOW:
        state[left.index] = 0x00
    else:
        state[left.index] = left.usage_id
    os.write(dev, bytes(state))

def down_change(ch):
    global dev, state, down
    if GPIO.input(ch) == GPIO.LOW:
        state[down.index] = 0x00
    else:
        state[down.index] = down.usage_id
    os.write(dev, bytes(state))

def up_change(ch):
    global dev, state, up
    if GPIO.input(ch) == GPIO.LOW:
        state[up.index] = 0x00
    else:
        state[up.index] = up.usage_id
    os.write(dev, bytes(state))

GPIO.add_event_detect(right.bcm, GPIO.BOTH, callback = right_change, bouncetime = 50)
GPIO.add_event_detect(left.bcm,  GPIO.BOTH, callback = left_change,  bouncetime = 50)
GPIO.add_event_detect(down.bcm,  GPIO.BOTH, callback = down_change,  bouncetime = 50)
GPIO.add_event_detect(up.bcm,    GPIO.BOTH, callback = up_change,    bouncetime = 50)

try:
    while True:
        sleep(0.1)
finally:
    os.close(dev)
    GPIO.cleanup(right.bcm)
    GPIO.cleanup(left.bcm)
    GPIO.cleanup(down.bcm)
    GPIO.cleanup(up.bcm)
