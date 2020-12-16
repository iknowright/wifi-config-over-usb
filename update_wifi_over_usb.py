import os
import json
from time import sleep

from jinja2 import FileSystemLoader, Environment


# lsblk --fs >/tmp/nousb.txt
def get_wifi_config(diff_file):
    mount_point = None
    with open(diff_file, 'r') as f:
        lines = f.readlines()
        if len(lines) < 2:
            return
        tokens = lines[1].strip().split(' ')
        direction = tokens[0]
        if direction == '<':
            mount_point = tokens[-1]

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
    while 1:
        # lsblk --fs >/tmp/nousb.txt
        os.system('lsblk --fs > current.txt')
        os.system('diff current.txt previous.txt > diff.txt')
        get_wifi_config('diff.txt')
        os.system('cp current.txt previous.txt')
        sleep(5)


if __name__ == "__main__":
    os.system('lsblk --fs > previous.txt')
    routine()
