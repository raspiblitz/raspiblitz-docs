---
sidebar_position: 2
---

# Hardware

RaspiBlitz runs on RaspberryPi 4&5 - but if you go buy new hardware anyway, we recommend getting a RaspberryPi 5 with 8GB RAM. The LCD screen is optional but also recommended for easier setup and monitoring once running.

:::info
For the RaspberryPi 5 you can already use an NVMe (over the new PCIexpress) instead of an external SSD via USB3. But we dont have settled on a final hardware recommendation for NVMe yet - so for RaspBlitz v1.11 we still recommend using an external SSD. If you want to play it safe with an NVMe upgrade, wait until we offer a hardware recommendation and a migration path with a later version release of RaspiBlitz.
:::

# Shopping Lists

:::caution
Please try to use the exact hardware models that are recommended in the shopping lists.
We have had multiple reports where, for example, other SSD or SSD cases/controllers lead to problems.
The idea of the shopping lists is to provide you the best tested hardware components that work together - improvement recommendations are always welcome.
:::

### RaspberryPi 5 Setup (recommended)

- RaspberryPi 5 8GB [pimoroni shop](https://shop.pimoroni.com/products/raspberry-pi-5?variant=41044580171859)
- RaspberryPi 5 Active Cooler [pimoroni shop](https://shop.pimoroni.com/products/raspberry-pi-5-active-cooler)
- RaspberryPi 5 Official Power Supply 27W [pimoroni shop](https://shop.pimoroni.com/products/raspberry-pi-27w-usb-c-power-supply)
- 1TB SSD - SanDisk SSD Plus 1TB 2.5" : [amazon referral link](https://geni.us/raspiblitz-1000gb-san) _other 1TB SSD models might cause power issues_
- SSD-case - UGREEN 2.5" External USB 3.0 Hard Disk Case with UASP support : [amazon referral link](https://geni.us/raspiblitz-ssd-case)
- LCD - 3.5" RPi Display, GPIO connection, XPT2046 Touch Controller: [amazon referral link](https://geni.us/raspiblitz-touchscreen)
- MicroSDCard 32GB - Samsung PRO Endurance 32 GB microSDHC UHS-I U1: [amazon referral link](https://geni.us/raspiblitz-sc-card)

### RaspberryPi 4 Setup (legacy)

- Raspberry Pi 4 4GB (or 8GB) [amazon referral link](https://geni.us/raspiblitz-4gb-new)
- Heatsink Case for RPi4 : [amazon referral link](https://geni.us/heatsink-raspi4)
- Power Supply - USB-C, 5V, >=3A [amazon referral link](https://geni.us/raspiblitz-ps)
- 1TB SSD - SanDisk SSD Plus 1TB 2.5" : [amazon referral link](https://geni.us/raspiblitz-1000gb-san) _other 1TB SSD models might cause power issues_
- SSD-case - UGREEN 2.5" External USB 3.0 Hard Disk Case with UASP support : [amazon referral link](https://geni.us/raspiblitz-ssd-case)
- LCD - 3.5" RPi Display, GPIO connection, XPT2046 Touch Controller: [amazon referral link](https://geni.us/raspiblitz-touchscreen)
- MicroSDCard 32GB - Samsung PRO Endurance 32 GB microSDHC UHS-I U1: [amazon referral link](https://geni.us/raspiblitz-sc-card)

### Alternative Parts

_If the above mentioned LCD screen is sold out you can also use these different vendors for the screen on Amazon:_

- Quimat 3,5'' Zoll Inch Touch
- ELEGOO Display 3.5" Zoll TFT LCD
- kuman 3.5 Inch Touch Screen TFT Monitor
- Waveshare 3.5inch Display for Raspberry Pi

With all LCD screen models don't use the ones that have an HDMI port/connector - what you need is a 3.5 inch LCD screen model (resolution of 480×320) that connects only thru the GPIO ports (SPI) and has an XPT2046 touch controller.

If you want to get an NVMe instead of a external SSD you can try these parts (release 1.12 needed):


- Pimoroni NVMe Base [pimoroni shop](https://shop.pimoroni.com/products/nvme-base?variant=41219587178579)
- NVMe Crucial P3 Plus 2TB Gen4 CT2000P3PSSD8 [amazon link](https://www.amazon.com/dp/B0B25ML2FH)

- Geekworm X1004 V1.1 NVME PIP shield [Geekworm official] (https://geekworm.com/products/x1004)
- NVMe Verbatim VI3000 2TB (49376) drive 

If you are testing or searching alternative SSD/NVMe models - check out this repository:
[https://github.com/chGoodchild/raspi5_ssd_compattibility](https://github.com/chGoodchild/raspi5_ssd_compattibility)

## Assemble your RaspiBlitz

When you have all parts you need to:

- Assemble the Heatsink-Case (when RaspberryPi4) or click-on the Active Cooler Fan (when RaspberryPi 5).
- Put the SSD into the Case and connect it per USB to the Raspberry Pi (blue ports).
- Add the display on top with the pins ending at the edge.
- Plug in the network cable.

In the end your RaspiBlitz should look like this (when RaspberryPi 5):

![HardwareSetup](../../static/img/hardwaresetup.jpeg)

You now have the hardware ready for your RaspiBlitz - whats missing is the software to run. This is normally done by downloading an image file and then writing it (flashing it) to the sd card. This is a bigger file (multiple GigaBytes) so make sure to have the available storage space on your laptop.

To continue setup go to next chapter [Software Download](./software-setup/1_download.md).

:::info
If you are a very advanced user who is able to read/verify code or you like to run a self-modified/forked version of RaspiBlitz you can also build the sd card image yourself - see the [Build your own sd card image](../faq/dev.md#what-is-the-process-of-creating-a-new-sd-card-image-release)
:::
