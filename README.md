# Update WiFi config over USB (wpa_supplicant)
Overwrite `wpa_supplicant.conf` on host system, when specific wifi configuration file is mount to the host via USB device.

## Features
* Periodically check for usb mount (5 secs)
* Generate new `wpa_supplcant.conf`

## Getting Started

### Prerequisites
* Raspberry Pi 4 (or linux)
* Python 3.7.3
* pipenv
* lsblk

### Setup environment
```
pipenv install
```

### Setup for USB
For usb device, put your wifi ssid and password inside a file called `wifi.config`.

wifi.config
```
test,12345678
```

File format: one-line document with ssid and password separated by a comma without ant extra white-spaces


### Setup for host device
For device to update the wifi over usb
`pipenv run python update_wifi_over_usb.py`

### Future work
* migrate to golang

### Contributors
* Chai-Shi, Chang
