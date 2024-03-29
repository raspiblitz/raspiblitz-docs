---
sidebar_position: 1
---

# Download / Flash

## Downloading the Software

In this section you find the latest ready-to-use RaspiBlitz SDcard images. Basically you just download, write/flash the image file to an sd card and start your Raspberry Pi with it - its the same for first install or updating to a newer version. You can choose from two ready-made sd card images below:

### FATPACK SD Card Image (Beginners - WebUI)

This is the sd card image you should choose if your at the beginning of your RaspiBlitz journey or you are a casual node runner wanna download the next update/upgrade - with WebUI & fast installing bonus apps.

<!-- :::warning
THIS IS STILL A RELEASE CANDIDATE VERSION JUST USE FOR TESTING, HIGHER RISK OF LOSING FUNDS!
::: -->

- FATPACK SD CARD IMAGE ⮕ [raspiblitz-fat-v1.11.0-2024-03-28.img.gz](https://raspiblitz.fulmo.org/images/raspiblitz-fat-v1.11.0-2024-03-28.img.gz)
- SHA-256: 2c495a1890449149d0288c8b41b3791c3d0be62c7638c30998bc2f54ac0f5381
- GPG 64-bit (main): 1C73 060C 7C17 6461 & (sub): AA9D D1B5 CC56 47DA
- Signature-File: [raspiblitz-fat-v1.11.0-2024-03-28.img.gz.sig](https://raspiblitz.fulmo.org/images/raspiblitz-fat-v1.11.0-2024-03-28.img.gz.sig)
<!-- - Torrent: [raspiblitz-fat-v1.9.0-2022-12-21.img.gz.torrent](https://github.com/rootzoll/raspiblitz/raw/dev/home.admin/assets/raspiblitz-fat-v1.9.0-2023-05-22.img.gz.torrent) -->
- [How to verify the SD card image after download?](../../faq/faq.md#how-to-verify-the-sd-card-image-after-download)

### MINIMAL SD Card Image (Experienced Users - SSH)

This is the sd card image for RaspiBlitz users that are already more experienced and want to use just a limited set of features of the RaspiBlitz. This image has just the bare minimum of features pre-installed - LCD & HDMI output is off by default. Setup, Update or Recovery needs to be done thru SSH login - API & WebUI are later available but are not pre-installed/activated by default. The RaspiBlitz will download & compile just the tools that are in your ´raspiblitz.conf´ - this will take longer but as a trade-off this RaspiBlitz then just runs with a reduced set of dependencies and so a minimized attack vector and better performance. Its for the serious & experienced node runners.

<!-- :::warning
THIS IS STILL A RELEASE CANDIDATE VERSION JUST USE FOR TESTING, HIGHER RISK OF LOSING FUNDS!
::: -->

- **MINIMAL SD CARD IMAGE ⮕ [raspiblitz-min-v1.11.0-2024-03-28.img.gz](https://raspiblitz.fulmo.org/images/raspiblitz-min-v1.11.0-2024-03-28.img.gz)**
- SHA-256: 5d249ba20b408da0bf80d7902749a73e547957b2046bc0c13401e014d6f7e97c
- GPG 64-bit (main): 1C73 060C 7C17 6461 & (sub): AA9D D1B5 CC56 47DA
- Signature-File: [raspiblitz-min-v1.11.0-2024-03-28.img.gz.sig](https://raspiblitz.fulmo.org/images/raspiblitz-min-v1.11.0-2024-03-28.img.gz.sig)
<!-- - Torrent: [raspiblitz-min-v1.9.0-2022-12-21.img.gz.torrent](https://github.com/rootzoll/raspiblitz/raw/dev/home.admin/assets/raspiblitz-min-v1.9.0-2023-05-22.img.gz.torrent) -->
- [How to verify the SD card image after download?](../../faq/faq.md#how-to-verify-the-sd-card-image-after-download)

## Write the SD-Card image to your SD Card

You need to write the downloaded SD card image (the img.gz-file) to your SD card (32GB minimum) - you can use the very easy tool [Balena Etcher](https://www.balena.io/etcher/) for this. It's available for Win, Mac & Linux.
