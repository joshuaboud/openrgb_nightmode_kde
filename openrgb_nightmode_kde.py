#!/usr/bin/env python3

import dbus
from openrgb import OpenRGBClient
from openrgb.orgb import Device, LED
from openrgb.utils import RGBColor
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from typing import List, Tuple, Dict
import signal
import sys

class DeviceWrapper:
  def __init__(self, device: Device):
    self.device = device
    self.colors_orig = device.colors

  def set_color_temp(self, lut: Tuple[int, int, int]) -> None:
    rf, gf, bf = lut
    self.device.set_colors([RGBColor(c.red * rf // 255, c.green * gf // 255, c.blue * bf // 255) for c in self.colors_orig], fast=True)

  def reset(self) -> None:
    self.device.set_colors(self.colors_orig)

DEVICES: List[DeviceWrapper] = None

KELVIN_TABLE: Dict[int, Tuple[int,int,int]] = {
  1000: (255,56,0),
  1500: (255,109,0),
  2000: (255,137,18),
  2500: (255,161,72),
  3000: (255,180,107),
  3500: (255,196,137),
  4000: (255,209,163),
  4500: (255,219,186),
  5000: (255,228,206),
  5500: (255,236,224),
  6000: (255,243,239),
  6500: (255,249,253),
  7000: (245,243,255),
  7500: (235,238,255),
  8000: (227,233,255),
  8500: (220,229,255),
  9000: (214,225,255),
  9500: (208,222,255),
  10000: (204,219,255),
}

def interp_color_temps(color_temp: int, x_bounds: Tuple[int, int]) -> Tuple[int,int,int]:
  y_bounds = (KELVIN_TABLE[x_bounds[0]], KELVIN_TABLE[x_bounds[1]])
  temp_factor = (color_temp - x_bounds[0]) / (x_bounds[1] - x_bounds[0])
  result = list(y_bounds[0])
  for component in range(3):
    result[component] += int(temp_factor * (float(y_bounds[1][component]) - float(y_bounds[0][component])))
  return result


def get_color_temp_matrix(color_temp: int) -> Tuple[int, int, int]:
  lut_temps = sorted(KELVIN_TABLE.keys())
  if color_temp <= lut_temps[0]:
    return KELVIN_TABLE[lut_temps[0]]
  if color_temp >= lut_temps[-1]:
    return KELVIN_TABLE[lut_temps[-1]]
  for index in range(len(lut_temps)):
    if lut_temps[index] == color_temp:
      return KELVIN_TABLE[lut_temps[index]]
    if lut_temps[index] > color_temp:
      return interp_color_temps(color_temp, (lut_temps[index-1], lut_temps[index]))
  raise Exception(f'ERROR: Could not interpolte color temperature: {color_temp}K')


def set_color_temp(devices: List[DeviceWrapper], color_temp: int) -> None:
  print(f'setting color temp to {color_temp}K')
  lut = get_color_temp_matrix(color_temp)
  for device in devices:
    device.set_color_temp(lut)


def on_properties_changed(sender: str, properties: dbus.Dictionary, args: dbus.Array):
  if 'currentTemperature' in properties:
    set_color_temp(DEVICES, int(properties['currentTemperature']))


def siginthandler(signum, frame):
  print(f'Exiting ({signal.Signals(signum).name}), resetting device colors...')
  for device in DEVICES:
    device.reset()
  print('Done. Exiting.')
  sys.exit(0)


def main():
  DBusGMainLoop(set_as_default=True)

  global DEVICES
  rgb = OpenRGBClient(protocol_version=3)
  DEVICES = [DeviceWrapper(device) for device in rgb.devices]

  signal.signal(signal.SIGINT, siginthandler)

  bus = dbus.SessionBus()
  color_correct_proxy = bus.get_object('org.kde.KWin', '/ColorCorrect')
  color_correct_iface = dbus.Interface(color_correct_proxy, 'org.freedesktop.DBus.Properties')

  color_temp = color_correct_iface.Get('org.kde.kwin.ColorCorrect', 'currentTemperature')
  set_color_temp(DEVICES, color_temp)

  color_correct_iface.connect_to_signal('PropertiesChanged', on_properties_changed)

  loop = GLib.MainLoop()
  loop.run()


if __name__ == '__main__':
  main()
