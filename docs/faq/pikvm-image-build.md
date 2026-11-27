---
title: "RaspiBlitz PiKVM image build (Draft)"
sidebar_label: "PiKVM image build (Draft)"
description: "Wire a PiKVM to a Raspberry Pi 5, install the verified controller, build Minimal or Fatpack and collect the unsigned archive."
---

# RaspiBlitz PiKVM image build (Draft)

**Draft · first hardware trial, 27 November 2026.** One command on the PiKVM starts a native build on the connected Raspberry Pi 5. Choose **Minimal** for a headless system or **Fatpack** for the LCD configuration, WebUI and preinstalled applications. Each starts from a fresh copy of Raspberry Pi OS. The PiKVM brings the original system back online before making the unsigned `.img.gz` available for collection and manual signing.

Setting up a new bench starts with the wiring below. On a provisioned bench, go straight to [Start a build](#start-a-build) or [Collect the image on Windows](#collect-the-image-on-windows).

## Wire the PiKVM and Pi 5

The tested controller uses a Raspberry Pi 4 Model B, Geekworm KVM-A8 and X630 HDMI capture board. The target is a Pi 5 Model B with PowerBlock Rev. 3.0. Both have 8 GiB RAM. Disconnect both supplies before wiring. [Geekworm connection diagram](https://wiki.geekworm.com/KVM-A8#Connection_Diagram)

| Connection | How to wire it |
| --- | --- |
| Video | Connect the Pi 5 micro-HDMI port marked **HDMI0** to the X630 **HDMI IN**. The controller reads bootloader prompts from this picture. |
| USB data | Connect a USB-A host port on the Pi 5 to the Pi 4 USB-C OTG port with a data-capable cable. This single cable carries the writable system disk (drive 0) and the read-only build helper (drive 1). |
| Power | Give the KVM-A8 its own 5.1 V supply rated for at least 3 A at the X630-A8 USB-C power input. Mount the PowerBlock on the first 12 pins of the Pi 5 GPIO header and plug the official Pi 5 supply into the PowerBlock USB-C input. [PowerBlock setup](https://www.petrockblock.com/powerblock-getting-started/) |
| Buttons | Connect the KVM ATX **power** output to the PowerBlock **switch** input. Connect **reset** across the Pi 5 power-button contacts. Raspberry Pi provides the two J2 pads for this normally open momentary contact. The controller uses short pulses. [Pi 5 power button](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#add-your-own-power-button) |
| Network | Connect both Ethernet ports to the same LAN switch. Reserve the Pi 5 address by MAC in DHCP. The PiKVM reaches the Pi 5 on TCP 2222 (build SSH), 22 (boot checks) and 80 (Fatpack setup). The Pi 5 needs Internet access for source and packages. The operator’s computer reaches the PiKVM over SSH. |

Use a USB **power blocker** that isolates VBUS and passes data to prevent backfeeding. Its installation on the original bench remains unconfirmed. Check USB enumeration and detach with the assembled cable.

### Check the bench before the first build

1. Complete [the two-drive setup](#enable-the-two-usb-drives) below. Boot a disposable image from drive 0 with both drives configured. Verify that the Pi 5 boots over USB after power-up and reboot. A USB-first boot order such as `0xf614` tries USB, SD, then NVMe. The build needs neither a physical microSD in the target nor a data SSD/NVMe. An inserted bootable card or NVMe must not take priority over the USB system disk. [PiKVM multiple drives](https://docs.pikvm.org/msd/#multiple-drives) · [Raspberry Pi boot order](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#BOOT_ORDER)
2. Verify HDMI capture and SSH. The PowerBlock setup reported 3 A and sometimes requested a button press before USB boot. Confirm a short **reset** pulse acknowledges the prompt.
3. On the return system, verify that a short **power** pulse triggers an orderly shutdown through its PowerBlock driver. Confirm the guest shuts down and the USB gadget stays detached before changing media. The ATX LED alone cannot establish that shutdown completed.

## Download and install the controller

The download is pinned to a revision of the maintainer’s documentation fork. Install the complete archive on the PiKVM. It contains the controller, guest script, filesystem checks, packaging helpers and Windows pickup script. The individual links also let you inspect the entry points.

| File | SHA-256 of the download |
| --- | --- |
| [Complete PiKVM kit (.tar.gz)](https://raw.githubusercontent.com/geco91/raspiblitz-docs/945b1b392d99b45c6685f68194805ad6f06a9095/static/downloads/pikvm-build-draft/pikvm-build-draft.tar.gz) · [checksum file](https://raw.githubusercontent.com/geco91/raspiblitz-docs/945b1b392d99b45c6685f68194805ad6f06a9095/static/downloads/pikvm-build-draft/pikvm-build-draft.tar.gz.sha256) | `f4fd9619410616ddf787930f30b3d4b48ad202a862b1ca951c9e61b2d7d4d6a5` |
| [Controller entry point (build.py)](https://raw.githubusercontent.com/geco91/raspiblitz-docs/945b1b392d99b45c6685f68194805ad6f06a9095/static/downloads/pikvm-build-draft/tools/pikvm-minimal/build.py) | `790dda739261d2d3575728b6803c437f106901274738dfb5fd3edc9a71c387b1` |
| [Windows pickup (Get-Release.ps1)](https://raw.githubusercontent.com/geco91/raspiblitz-docs/945b1b392d99b45c6685f68194805ad6f06a9095/static/downloads/pikvm-build-draft/tools/pikvm-minimal/Get-Release.ps1) | `fe098710045442c38a39ee4787815cb5597edd0847cde1a70a23ec5697deaa49` |

For a first installation, run this block as root on the **PiKVM**. It checks the compressed bytes before extraction, verifies all eight installed files, then places the verified directory at the path the pickup script expects. The command stops if a controller already exists. On an existing bench you can compare the installed files with the [per-file checksums](https://raw.githubusercontent.com/geco91/raspiblitz-docs/945b1b392d99b45c6685f68194805ad6f06a9095/static/downloads/pikvm-build-draft/CONTENTS.sha256) before scheduling an update.

```bash
(
  set -eu
  umask 077
  state=/var/lib/kvmd/msd/raspiblitz-image-build
  mountpoint -q /var/lib/kvmd/msd
  kvmd-helper-otgmsd-remount rw
  install -d -m 700 "$state"
  test ! -e "$state/controller" && test ! -L "$state/controller" || {
    echo "A controller is already installed" >&2
    exit 1
  }
  stage=$(mktemp -d "$state/.controller-install.XXXXXXXX")
  trap 'rm -rf -- "$stage"' EXIT
  cd "$stage"
  url=https://raw.githubusercontent.com/geco91/raspiblitz-docs/945b1b392d99b45c6685f68194805ad6f06a9095/static/downloads/pikvm-build-draft
  curl -fSL "$url/pikvm-build-draft.tar.gz" -o kit.tar.gz
  printf '%s  %s\n' f4fd9619410616ddf787930f30b3d4b48ad202a862b1ca951c9e61b2d7d4d6a5 kit.tar.gz | sha256sum -c -
  mkdir controller
  tar --no-same-owner --no-same-permissions -xzf kit.tar.gz -C controller
  (cd controller && sha256sum -c CONTENTS.sha256)
  mv -T --no-clobber controller "$state/controller"
  test ! -d controller
)
```

## Prepare the PiKVM once

Use a root shell on a PiKVM with the KVMD USB gadget, ATX control and HDMI capture working. The tested controller ran on Arch Linux ARM with KVMD 4.58, Python 3.13 and systemd. It needs Python 3.11 or later with `aiohttp`, Git, OpenSSH, sshpass, curl, parted, util-linux, dosfstools, e2fsprogs, gzip and Tesseract with English data. Pigz speeds up compression. Preparing the inputs below also uses GnuPG and xz. Use the PiKVM package repositories for missing tools. The controller also uses the local KVMD and uStreamer sockets under `/run/kvmd/` and the systemd sandbox on Arch ARM64. The build store must support sparse files, Linux permissions and loop mounts. Check the mounted store and its free space with `findmnt -T /var/lib/kvmd/msd` and `df -h /var/lib/kvmd/msd`. [PiKVM OS maintenance](https://docs.pikvm.org/faq/)

### Enable the two USB drives

Record the current system image with `kvmd-otgmsd -i 0`. Shut down the Pi 5 cleanly and confirm `cat /sys/class/udc/*/state` reports `not attached` before reconfiguring the gadget. On the PiKVM run `rw`, save a copy of `/etc/kvmd/override.yaml`, and merge these keys into its existing YAML. Reboot the **PiKVM**. Verify both drives with `kvmd-otgmsd -i 0` and `kvmd-otgmsd -i 1`. Leave drive 1 empty. The controller supplies its own read-only helper there on each run. [PiKVM multiple drives](https://docs.pikvm.org/msd/#multiple-drives)

```yaml
otg:
    devices:
        drives:
            enabled: true
            count: 1
            default:
                cdrom: false
                rw: false
```

### Prepare the verified build inputs

The hardware test used the **64-bit Raspberry Pi OS Bookworm desktop** image dated 13 May 2025. The profile below names its decompressed RAW. Run the following Bash block on the PiKVM for a fresh installation. It stops on a failed check. It verifies the vendor signature against the full signing fingerprint, authenticates the archive, expands it and checks the RAW separately. PiShrink is also pinned by commit and file hash. [RaspiBlitz ARM build inputs](https://github.com/raspiblitz/raspiblitz/blob/9bece9d6852f0d6b951106c6cc8534666c925ef8/ci/arm64-rpi/build.arm64-rpi.pkr.hcl) · [Raspberry Pi OS download and signature](https://downloads.raspberrypi.org/raspios_arm64/images/raspios_arm64-2025-05-13/) · [Tested PiShrink source](https://github.com/Drewsif/PiShrink/blob/a5f9463c01607ab07402c7e75c9cfd4bb3a0e886/pishrink.sh)

```bash
(
  set -euo pipefail
  umask 077
  state=/var/lib/kvmd/msd/raspiblitz-image-build
  mountpoint -q /var/lib/kvmd/msd
  kvmd-helper-otgmsd-remount rw
  install -d -m 700 "$state" "$state/inputs"
  cd "$state/inputs"
  export GNUPGHOME="$PWD/gnupg"
  install -d -m 700 "$GNUPGHOME"
  raw=2025-05-13-raspios-bookworm-arm64.img
  [[ ! -e "$raw" && ! -L "$raw" ]]
  url=https://downloads.raspberrypi.org/raspios_arm64/images/raspios_arm64-2025-05-13
  curl -fSLO "$url/$raw.xz"
  curl -fSLO "$url/$raw.xz.sig"
  curl -fsSLo vendor.asc https://www.raspberrypi.org/raspberrypi_downloads.gpg.key
  gpg --batch --yes --dearmor -o vendor.gpg vendor.asc
  gpgv --keyring "$PWD/vendor.gpg" --status-fd 1 "$raw.xz.sig" "$raw.xz" > signature.status
  awk -v fp=54C3DD610D9D1B4AF82A37758738CD6B956F460C \
    '$2 == "VALIDSIG" && ($3 == fp || $NF == fp) {valid=1} END {exit !valid}' signature.status
  printf '%s  %s\n' 1162c2a47c2ebda34c7ebeafc4afb71910a05b368d0721ae3736928e60ba5047 "$raw.xz" | sha256sum -c -
  xz -d "$raw.xz"
  printf '%s  %s\n' 776274c0d76f1a05e1f07d31acee7765a5129f95d8f3a78e7453a52fe589325c "$raw" | sha256sum -c -
  curl -fsSLo pishrink.sh https://raw.githubusercontent.com/Drewsif/PiShrink/a5f9463c01607ab07402c7e75c9cfd4bb3a0e886/pishrink.sh
  printf '%s  %s\n' 71026f0c02ac099e588a3eb8f70760c1b680aa8ea3acde61a0141fbaeb68c777 pishrink.sh | sha256sum -c -
)
```

### Prepare the system to return to

Choose an existing, boot-tested USB system image under `/var/lib/kvmd/msd/`, outside `raspiblitz-image-build/`. It needs FAT partition 1 and ext4 partition 2, SSH on TCP 22 at the reserved Pi 5 Ethernet address, and its own persistent `/etc/ssh/ssh_host_ed25519_key.pub`. The controller reads this public key from the detached image and checks the identity of the restarted system before publishing the build.

On a new bench, one way to provision that system is to make a **separate** sparse copy of the verified Raspberry Pi OS RAW at `/var/lib/kvmd/msd/return.img`. With the Pi off, both slots empty and that filename unused, copy the RAW using `cp --sparse=always`, extend the copy with `truncate -s 16G /var/lib/kvmd/msd/return.img`, then present it with `kvmd-otgmsd -i 0 --set-cdrom=0 --set-rw=1 --set-image=/var/lib/kvmd/msd/return.img`. Boot it once, complete first-time setup through HDMI/HID, enable SSH, and confirm the Ed25519 host key and Ethernet address on the Pi. The trial used the PowerBlock service on the return system. Check `systemctl is-active powerblock.service` there and confirm its switch-off action requests an orderly OS shutdown. Test a short power pulse on this disposable system before using the running-system start mode. For a bench where that shutdown path has yet to be verified, shut down the return system from its OS, confirm USB detach, and use `start --pi-stopped`. The controller still needs a working return image in this mode. [PowerBlock driver at the tested revision](https://github.com/petrockblog/PowerBlock/commit/4832bd44c50e0d8ce4e4d16e8bfbdaebeb2b73fa)

### Configure access and the build profile

The two local credentials serve different machines. On the PiKVM, run `rw`, set `umask 077` and create `/root/.config/raspiblitz-agent/` with mode 0700. Using an editor as root, place exactly these two lines in `kvmd-curl.conf` in that directory, replacing the placeholders with the local KVMD web/API account. The account must be able to read ATX state, issue short ATX clicks and start the video stream. This draft uses fixed request headers. A KVM login that requires a freshly generated one-time code on each request needs a different authentication integration. [PiKVM API authentication](https://docs.pikvm.org/api/#authentication)

```text
header = "X-KVMD-User: YOUR_KVMD_USER"
header = "X-KVMD-Passwd: YOUR_KVMD_PASSWORD"
```

Create `/root/.config/raspiblitz-agent/factory-password` with one line containing the stock **RaspiBlitz admin** password set by the pinned installer. The boot probe uses this to authenticate on the disposable first-boot copy. Keep both files owned by root, mode 0600, then run `ro`. This read-only ATX query checks the credentials and the same local TLS trust path used by the controller. It should return `"ok": true`. The PiKVM web certificate at that path must be valid for `localhost`. [Installer at the tested revision](https://github.com/geco91/raspiblitz/blob/9bece9d6852f0d6b951106c6cc8534666c925ef8/build_sdcard.sh)

```bash
curl --config /root/.config/raspiblitz-agent/kvmd-curl.conf \
  --cacert /etc/kvmd/nginx/ssl/server.crt --noproxy localhost \
  --resolve localhost:443:127.0.0.1 --fail --silent --show-error https://localhost/api/atx
```

Create `/var/lib/kvmd/msd/raspiblitz-image-build/minimal-profile.json` as root, mode 0600. Both variants use this filename. Replace the example IPv4 address and lowercase MAC with the Pi 5's reserved LAN address and wired MAC. Set `return_image` to the exact image prepared above. The other values reproduce the inputs of the hardware trial while the named branch points to the recorded commit.

```json
{
  "address": "192.0.2.15",
  "mac": "02:00:00:00:00:15",
  "return_image": "/var/lib/kvmd/msd/return.img",
  "base": "/var/lib/kvmd/msd/raspiblitz-image-build/inputs/2025-05-13-raspios-bookworm-arm64.img",
  "base_sha256": "776274c0d76f1a05e1f07d31acee7765a5129f95d8f3a78e7453a52fe589325c",
  "pishrink": "/var/lib/kvmd/msd/raspiblitz-image-build/inputs/pishrink.sh",
  "pishrink_sha256": "71026f0c02ac099e588a3eb8f70760c1b680aa8ea3acde61a0141fbaeb68c777",
  "owner": "geco91",
  "branch": "dev",
  "commit": "9bece9d6852f0d6b951106c6cc8534666c925ef8",
  "blob": "4451947bf40920afd191aafe3191b571da1f19ed",
  "version": "1.12.1",
  "factory_password_file": "/root/.config/raspiblitz-agent/factory-password"
}
```

For a new candidate select an existing RaspiBlitz branch under `owner`. Confirm its head with `git ls-remote https://github.com/OWNER/raspiblitz.git refs/heads/BRANCH`. From a local checkout containing that commit, use `git rev-parse 'COMMIT:build_sdcard.sh'` for `blob` and read `codeVersion` using `git show 'COMMIT:home.admin/_version.info'` (substitute the actual commit in both commands). A moving branch or changed installer layout can stop the build. To rerun this development snapshot after its branch advances, point a branch of your RaspiBlitz fork at the recorded commit and update `owner` and `branch`.

Optional profile values are integers in bytes. `minimal_working_bytes` defaults to 25,769,803,776 (24 GiB), `fatpack_working_bytes` to 64,000,000,000 and `target_bytes` to 64,000,000,000. Use complete 512-byte sectors and set the target to the smallest actual card capacity you intend to support. The working image can be larger. `reserve_bytes` preserves free space on the PiKVM (default 8 GiB). `fatpack_root_free_bytes` reserves space usable by ordinary applications inside Fatpack, checked cold and after first boot (default 2 GiB).

## Start a build

As **root on the PiKVM**, run the command for one variant. Begin with Minimal when commissioning a bench. The normal starting state is the configured return image running on drive 0 with SSH available and drive 1 empty. The controller prints the run ID and starts a systemd service that survives closing the operator's terminal.

```bash
controller=/var/lib/kvmd/msd/raspiblitz-image-build/controller/tools/pikvm-minimal/build.py
python "$controller" start --variant minimal
```

For a separate Fatpack build, use `python "$controller" start --variant fatpack`. Run one job at a time. When starting from a confirmed powered-down Pi 5 with its USB gadget detached, append `--pi-stopped`. The controller still restores the configured return image after that run.

```bash
python "$controller" list
# Replace RUN_ID with the value printed at start.
journalctl -fu rb-release-RUN_ID
```

**Success is the status `exported`.** The guest finishes the installer and release cleanup, signals readiness and shuts down. The PiKVM waits for stable USB detach, audits the filesystems, shrinks and compresses the image, then verifies the RAW hash while expanding the archive into a disposable boot copy. That copy boots on the Pi 5 at the target capacity. Fatpack also has to serve its WebUI and setup API over the LAN and pass its application-space checks. The controller then restores drive 0 and checks the return system’s SSH identity. The unsigned files are under `/var/lib/kvmd/msd/raspiblitz-image-build/RUN_ID/export/` until collection.

### Capacity for a run

The published Raspberry Pi images target a **64 GB microSD**. Set `target_bytes` to the usable byte count of the smallest card you support, obtainable from a Linux card reader with `lsblk -b -d -o NAME,SIZE,MODEL`. This limit applies to the uncompressed image. The build disk can be larger. [RaspiBlitz Download / Flash](../setup/software-setup/1_download.md)

| Measured on the draft bench | Minimal | Fatpack |
| --- | ---: | ---: |
| Virtual build disk | 24 GiB | 64 GB |
| Finished RAW | 6.67 GB | 39.85 GB |
| Archive to collect | 1.89 GB | 10.60 GB |
| Build and Windows pickup | about 53 min | about 4 h 6 min |

The controller checks the larger of the input RAW size and a variant allowance (10 GiB Minimal, 32 GiB Fatpack), plus the configured reserve, before starting. This is an entry check. In the Fatpack trial the media store started with **76.41 GB** free and reached a sampled low of **30.22 GB**. Budget for the measured peak and future growth. The finished Fatpack left 24.15 GB below the 64 GB target and 2.40 GB available to ordinary applications immediately after its first boot. See `storage_min_sampled_free_bytes`, `target_spare_bytes` and the Fatpack free-space measurements in your own `build.json`.

## Collect the image on Windows

Windows needs PowerShell and the OpenSSH client (`ssh` and `sftp`). Add this entry to `$HOME\.ssh\config` for a root SSH key already authorized on the PiKVM. Replace the example hostname with your controller’s address.

```text
Host pikvm-release
    HostName pikvm.example.net
    User root
```

Read the host fingerprint on the PiKVM console with `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub`. On first connection from Windows, run `ssh -o HostKeyAlgorithms=ssh-ed25519 -o StrictHostKeyChecking=ask pikvm-release exit` and match the displayed fingerprint before accepting. Then run `ssh -o BatchMode=yes -o StrictHostKeyChecking=yes pikvm-release id -u` (expected output `0`). For another configured alias, pass `-PiKvm YOUR-ALIAS` to the pickup script.

Download the pickup script once in PowerShell. Verify it before running it. If PowerShell flags the downloaded file, `Unblock-File` below applies only to the file that passed the check.

```powershell
$uri = 'https://raw.githubusercontent.com/geco91/raspiblitz-docs/945b1b392d99b45c6685f68194805ad6f06a9095/static/downloads/pikvm-build-draft/tools/pikvm-minimal/Get-Release.ps1'
Invoke-WebRequest -Uri $uri -OutFile .\Get-Release.ps1 -UseBasicParsing
$expected = 'fe098710045442c38a39ee4787815cb5597edd0847cde1a70a23ec5697deaa49'
if ((Get-FileHash .\Get-Release.ps1 -Algorithm SHA256).Hash -ne $expected) {
    throw 'Pickup script checksum mismatch'
}
Unblock-File -LiteralPath .\Get-Release.ps1
```

To **collect a finished run**, execute `.\Get-Release.ps1` when exactly one export is waiting. To choose a run or destination, use the ID printed by the controller.

```powershell
.\Get-Release.ps1 -RunId RUN_ID -Destination 'D:\Releases'
```

To **start and collect with one command**, execute `.\Get-Release.ps1 -Build minimal` or `.\Get-Release.ps1 -Build fatpack`. The PiKVM owns the build. Windows waits, downloads and verifies the result.

By default, the archive is in **`$HOME\Downloads\RaspiBlitz\RUN_ID\`**. The script prints its full path. Keep the `.img.gz`, its `.img.gz.sha256`, the uncompressed `.img.sha256` and `build.json` together. The script checks the downloaded length and SHA-256 and checks both checksum files against the manifest. Only after that succeeds does it acknowledge the transfer, release the remote export space and set the run to `downloaded`. For release, take the verified **compressed file** to the maintainer’s signing machine. Recheck its hash there and sign those bytes. [Manual release and signing notes](dev.md#what-is-the-process-of-creating-a-new-raspberrypi-sd-card-image-release-manually)

## Recover an interrupted run

| What happened | What to do |
| --- | --- |
| Windows terminal or download disconnected | Look up the run with `list`. Once it shows `exported`, repeat `Get-Release.ps1 -RunId RUN_ID` with the same destination. SFTP resumes a partial file. The same command retries an interrupted acknowledgement from the verified local copy. |
| PiKVM lost the build SSH session to the Pi 5 | The run fails. A local timer stops the guest build and requests power-off. Check `journalctl -u rb-release-RUN_ID` and the run’s `guest.log`. After confirmed shutdown, stable USB detach and recovery of the return system, the operator can start a fresh run. |
| Shutdown or medium ownership is unclear | Leave the media in place. Check HDMI, gadget state and the journal. Resolve the target state before ejecting or clearing any image. A failed attempt with detached media can appear as `failed-detached`. |
| Insufficient free space | Check `df -h /var/lib/kvmd/msd` and `list`. Collect older `exported` runs. A new build cleans its recognized detached work files and preserves uncollected exports and diagnostic logs. |

To exercise the shutdown timer during commissioning, run `python "$controller" abort-probe` from the normal return-system state. It uses a disposable build copy and intentionally interrupts the guest SSH session. Check the journal, the restored return system and the final status `abort-tested` before relying on unattended operation.
