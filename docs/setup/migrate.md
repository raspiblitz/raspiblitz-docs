# Migrate

:::info
If you want to update from an older version of the RaspiBlitz software, you should follow [these instructions](./software-setup/2_basic.md)
:::

Follow this guide only if you migrate from another node software like Umbrel or MyNode. If you run one of these, you basically have all the hardware needed and just need to change software. You don't need the LCD from the shopping list - RaspiBlitz can also run without an LCD.

### Before you start migration

- if you have on-chain funds on your old node - make sure to have the backup seed words
- if you have lightning channels open on your old node - make sure to have downloaded the latest Static Channel Backup file to your laptop

Also be aware that at the moment RaspiBlitz can only transfer your blockchain and LND wallet data (including channels) over to RaspiBlitz. Any data/pairing of additional apps cannot be transferred and may get lost.

## Instructions for Migration

### Step by step instructions

- shutdown your old node
- remove the SD card
- download the latest RaspiBlitz sd card image & flash it to your sd card
- if you want to use a HDMI monitor for status & progress, create a empty file called hdmi (without any ending) on the SD card while connected to your laptop
- insert sd card, boot up & login by SSH

Now RaspiBlitz should show you that old data from your node was detected and offer to do the migration for you.

- If you choose to continue it will prepare the data & reboot.
- The RaspiBlitz recover/update mode is starting - that will take a while and finally reboot.
- Login by SSH as before and reset the passwords (FINAL RECOVERY LOGIN on LCD). Then a final reboot will happen.
- Login by SSH with your new password A & unlock LND wallet with password C. Now blockchain needs to catch up and then your RaspiBlitz should be ready and show you (under INFO) your on-chain & channel balance.

### Troubleshooting without a connected display

If you don't have an LCD or HDMI monitor connected it might be a bit difficult to see what state your RaspiBlitz is in. Just (re-)try to login by SSH again after the reboots. It can take some time after a reboot before the operating system and SSH service is started, so just keep trying at intervals until successful.
