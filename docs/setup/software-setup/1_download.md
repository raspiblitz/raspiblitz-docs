---
sidebar_position: 1
---

# Download / Flash

## Downloading the Software

In this section you find the latest ready-to-use RaspiBlitz SDcard images. Basically you just download, write/flash the image file to an sd card and start your Raspberry Pi with it - its the same for first install or updating to a newer version. You can choose from two ready-made sd card images below.

### FATPACK SD Card Image (Beginners - WebUI)

This is the sd card image you should choose if your at the beginning of your RaspiBlitz journey or you are a casual node runner wanna download the next update/upgrade - with WebUI & fast installing bonus apps.

- **FATPACK SD CARD IMAGE ⮕ [raspiblitz-fat-v1.11.4-2024-12-24.img.gz](https://raspiblitz.fulmo.org/images/raspiblitz-fat-v1.11.4-2024-12-24.img.gz)**
- SHA-256: 31877d0085c20f34bf2bedeeec6bd4abc108595a4b0985d273ddaba2b0fbe654
- GPG 64-bit (main): 1C73 060C 7C17 6461 & (sub): AA9D D1B5 CC56 47DA
- Signature-File: [raspiblitz-fat-v1.11.4-2024-12-24.img.gz.sig](https://raspiblitz.fulmo.org/images/raspiblitz-fat-v1.11.4-2024-12-24.img.gz.sig)
- Torrent: [raspiblitz-fat-v1.11.4-2024-12-24.img.gz.torrent](https://github.com/raspiblitz/raspiblitz/raw/dev/home.admin/assets/raspiblitz-fat-v1.11.4-2024-12-24.img.gz.torrent)
- [How to verify the SD card image after download?](../../faq/faq.md#how-to-verify-the-sd-card-image-after-download)


### MINIMAL SD Card Image (Experienced Users - SSH)

This is the sd card image for RaspiBlitz users that are already more experienced and want to use just a limited set of features of the RaspiBlitz. This image has just the bare minimum of features pre-installed - LCD & HDMI output is off by default. Setup, Update or Recovery needs to be done thru SSH login - API & WebUI are later available but are not pre-installed/activated by default. The RaspiBlitz will download & compile just the tools that are in your ´raspiblitz.conf´ - this will take longer but as a trade-off this RaspiBlitz then just runs with a reduced set of dependencies and so a minimized attack vector and better performance. Its for the serious & experienced node runners.

- **MINIMAL SD CARD IMAGE ⮕ [raspiblitz-min-v1.11.4-2024-12-24.img.gz](https://raspiblitz.fulmo.org/images/raspiblitz-min-v1.11.4-2024-12-24.img.gz)**
- SHA-256: 3d874e8e2518bb9db79df196d1dd7e6d567a0608a3df568cadef87a77b4d3841
- GPG 64-bit (main): 1C73 060C 7C17 6461 & (sub): AA9D D1B5 CC56 47DA
- Signature-File: [raspiblitz-min-v1.11.4-2024-12-24.img.gz.sig](https://raspiblitz.fulmo.org/images/raspiblitz-min-v1.11.4-2024-12-24.img.gz.sig)
- Torrent: [raspiblitz-min-v1.11.4-2024-12-24.img.gz.torrent](https://github.com/raspiblitz/raspiblitz/raw/dev/home.admin/assets/raspiblitz-min-v1.11.4-2024-12-24.img.gz.torrent)
- [How to verify the SD card image after download?](../../faq/faq.md#how-to-verify-the-sd-card-image-after-download)

- [What has changed from version to version?](https://github.com/raspiblitz/raspiblitz/blob/dev/CHANGES.md)

## Write the SD-Card image to your SD Card

You need to write the downloaded SD card image (the img.gz-file) to your SD card (32GB minimum) - you can use the very easy tool [Balena Etcher](https://www.balena.io/etcher/) for this. It's available for Win, Mac & Linux.

## Boot your RaspiBlitz

Insert the SD card and connect the power plug.

- Make sure to connect the raspberry with a LAN cable to the internet at this point.
- Make sure that your laptop and the raspberry are on the same local network.

**Troubleshoot:**

- [I don't have a LAN port on my Laptop - how to connect to my RaspiBlitz?](../../faq/faq.md#i-dont-have-a-lan-port-on-my-laptop---how-do-i-connect-to-my-raspiblitz)
- [Is it possible to connect the Blitz over Wifi instead of using a LAN cable?](../../faq/faq.md#is-it-possible-to-connect-the-blitz-over-wifi-instead-of-using-a-lan-cable)
- [Can I directly connect the RaspiBlitz with my laptop?](../../faq/faq.md#can-i-directly-connect-the-raspiblitz-to-my-laptop)
- [I connected my HDD, but it still says 'Connect HDD' on the display?](../../faq/faq.md#i-connected-my-hdd-but-it-still-says-connect-hdd-on-the-display)

When everything boots up correctly (one reboot is normal), you should finally see the local IP address of your RaspiBlitz on the LCD panel.

- [How do I find the IP address when running without a display?](../../faq/faq.md#how-do-i-find-the-ip-address-when-running-without-a-display)

![LCD0](../../../static/img/lcd0-welcome.png)

Now open up a terminal ([OSX](https://www.youtube.com/watch?v=5XgBd6rjuDQ)/[Win10](https://www.howtogeek.com/336775/how-to-enable-and-use-windows-10s-built-in-ssh-commands/)) and connect through SSH with the command displayed by the RaspiBlitz:

`ssh admin@[YOURIP]` → use password: `raspiblitz`
 
- [I cannot connect by SSH to my RaspiBlitz. What to do?](../../faq/faq.md#i-cannot-connect-via-ssh-to-my-raspiblitz-what-do-i-do)

To follow the setup dialogue in your terminal you can continue with chapter [Basic Setup](2_basic.md).
