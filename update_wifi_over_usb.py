import os
import json
from time import sleep

from jinja2 import FileSystemLoader, Environment


def get_wifi_config(mount_point):
    if mount_point:
        with open(f'{mount_point}/wifi.config', 'r') as f:
            lines = f.readlines()
            ssid, password = tuple(lines[0].strip().split(','))

            template_loader = FileSystemLoader(searchpath="./templates")
            template_env = Environment(loader=template_loader)

            # building docker-compose.yml
            template_file = "template.wpa_supplicant.conf"
            template = template_env.get_template(template_file)
            output_stream = template.stream(ssid=ssid, psk=password)
            output_stream.dump("wpa_supplicant.conf")


def routine():
    os.system('lsblk --fs -J > previous.json')

    while 1:
        os.system('lsblk --fs -J > current.json')

        previous, current = {}, {}
        previous_devices, current_devices = [], []
        with open('previous.json', 'r') as pf:
            previous_devices = json.load(pf).get('blockdevices', [])
            pf.close()
        with open('current.json', 'r') as cf:
            current_devices = json.load(cf).get('blockdevices', [])
            cf.close()

        devices = [device for device in current_devices if device not in previous_devices]
        new_device = None
        if len(devices) == 1:
            new_device = devices[0]

        if new_device:
            mount_point = new_device.get('mountpoint')
            if not mount_point:
                mount_point = f'/mnt/{new_device["uuid"]}'
                os.system(f'sudo mkdir -p {mount_point}')
                os.system(f'sudo mount /dev/{new_device["name"]} {mount_point}')

            get_wifi_config(mount_point)

        os.system('lsblk --fs -J > previous.json')

        print(new_device)
        sleep(5)


if __name__ == "__main__":
    routine()
