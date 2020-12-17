"""script for update wifi over usb"""

import os
import json
from time import sleep

from loguru import logger
from jinja2 import FileSystemLoader, Environment


# pylint: disable=bare-except
def generate_wifi_config(mount_point):
    """Generate wpa_supplicant file from usb storage's `wifi.config` file"""

    if mount_point:
        # wifi.config is text file with only one line of information: `ssid,password`
        try:
            with open(f"{mount_point}/wifi.config", "r") as config_file:
                # parsing wifi.config from usb mount point
                try:
                    lines = config_file.readlines()
                    ssid, password = tuple(lines[0].strip().split(","))
                    logger.info(f"[wifi.config] ssid: {ssid}, password: {password}")

                    # generate new wpa_supplicant for device
                    try:
                        template_loader = FileSystemLoader(searchpath="./templates")
                        template_env = Environment(loader=template_loader)

                        # building wpa_supplicant.conf
                        template_file = "template.wpa_supplicant.conf"
                        template = template_env.get_template(template_file)
                        output_stream = template.stream(ssid=ssid, psk=password)
                        output_stream.dump("wpa_supplicant.conf")
                    except:
                        logger.error(
                            "[template] error rendering new wpa_supplicant.conf"
                        )

                    # TODO: add wpa_supplicant.conf replacement
                    # e.g `sudo cp wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf`
                except:
                    logger.error("[wifi.config] content format is wrong")
        except:
            logger.error("[wifi.config] file not found in mount point")
    else:
        logger.warning("[mount point] no mount point")


# pylint: enable=bare-except


def routine():
    """
    Run lsblk command periodically to detect new usb device
    When new device is connected, execute the generate wifi script
    """

    # generate initial lsblk info
    os.system("lsblk --fs -J > previous.json")

    # loop
    while 1:
        # generate current lsblk info
        os.system("lsblk --fs -J > current.json")

        # get devices for both previous and current info
        previous_devices, current_devices = [], []
        with open("previous.json", "r") as previous_file:
            previous_devices = json.load(previous_file).get("blockdevices", [])
            previous_file.close()
        with open("current.json", "r") as current_file:
            current_devices = json.load(current_file).get("blockdevices", [])
            current_file.close()

        # diff the devices
        devices = [
            device for device in current_devices if device not in previous_devices
        ]
        new_device = None

        # new device can be found if there is one device more in current devices
        if len(devices) == 1:
            new_device = devices[0]

        # generate wifi configuration script if and only if new usb device is present
        if new_device:
            logger.info(f"[USB] new device detected!\n device info: {new_device}")

            # existing mount point if usb is auto-mounted
            mount_point = new_device.get("mountpoint")

            # manually mounting the mount point for usb if auto-mounting is not set for the device
            # manual mount point is in /mnt/{UUID}
            if not mount_point:
                mount_point = f'/mnt/{new_device["uuid"]}'
                os.system(f"sudo mkdir -p {mount_point}")
                os.system(f'sudo mount /dev/{new_device["name"]} {mount_point}')

            # wifi config script
            generate_wifi_config(mount_point)

        # the `current` lsblk info is now `previous`
        os.system("lsblk --fs -J > previous.json")

        sleep(5)


if __name__ == "__main__":
    routine()
