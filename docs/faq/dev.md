## FAQ Development

These are FAQ and notes for developers only - if you are just operating a RaspiBlitz you can skip these. 

### Steps to create RaspberryPi images with Packer?

* Make sure you have:
  * Correct version-string in: `_version.info`
  * Correct version-branch as fallback in `build_sdcard.sh`
* Start [`Debian LIVE`](https://cdimage.debian.org/debian-cd/current-live/amd64/iso-hybrid/debian-live-12.4.0-amd64-cinnamon.iso) from USB stick
  * On USB boot be sure to start the "LIVE_SYSTEM" image
  * Set KeyboardLang, "Screensaver" & "Power Management"
  * Connect a additional 128GB USB with NFTS formatted 
* Using Filemanager open the 128GB-USBDrive and right-click "Open in Terminal"
* Make sure the packer script is in root of the 128GB-USBDrive
  * If it is not there download: 
  * `curl -O -L https://raw.githubusercontent.com/raspiblitz/raspiblitz/dev/ci/packer.sh`
* Security read/check script and compare checksum:
  * `shasum -a 256 ./ci/packer.sh` or
  * `shasum -a 256 packer.sh`
* Start build with:
* `sudo bash ./packer.sh` and enter:
  * `BRANCH` = the branch name on this repo of which the image should be build
  * `[arm|x86]` = The architecture the image is targeting (RaspberryPi = `arm`)
  * `[min|fat]` = lean or fatpack (fatpack prepackages lots of apps already with the image)
  * `LASTCOMMITHASH` (optional) = security check & copy the latest commit hash of the branch you want to build (substring is ok)
 
To directly write an image from the final `img.gz` file from the build laptop you need tu unzip the file first with `gunzip [imagefile.img.gz]` and then use the debian Image Writer.

### What is the process of creating a new RaspberryPi SD card image release manually?

Checklist before making a SD card image release:

* "Versioning" number is upfates in your RaspiBlitz Source Code (_version.info)
* Latest code is merged in release branch

Creating the base minimal sd card:

* Start [`Ubuntu LIVE`](http://releases.ubuntu.com/18.04.3/ubuntu-18.04.3-desktop-amd64.iso) from USB stick
* Under Settings: best to set correct keyboard language & power settings to prevent monitor turn off
* Connect to a secure WiFi (hardware switch on) or LAN
* Download the latest RaspiOS-64bit (zip/xz & sig file) namend in the build_sdcard.sh and note the SHA256 checksum
* From the browser `Show All Downloads` and from the context menu select `Open Containing Folder`
* On that file manager open context (right click) on the white-space and select `Open in Terminal`
* Compare the checksum with the one you just made note of, using `shasum -a 256 *.zip`
* Check signature: `wget https://www.raspberrypi.org/raspberrypi_downloads.gpg.key && gpg --import ./raspberrypi_downloads.gpg.key && gpg --verify *.sig`
* The result should say "correct signature" and the fingerprint should end with `8738 CD6B 956F 460C`
* Insert an NTFS formatted USB stick and use the file manager to move all files to the USB
* If image is an ZIP file use in file manager context on NTFS USB stick `extract here` to unzip
* Download script for later with `curl https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh > pishrink.sh`
* Connect SD card reader with a SD card (16GB recommended)
* In the file manager open context on the .img-file, select `Open With Disk Image Writer` and write the image to the SD card
* In the file manager open context on `boot` drive free space `open in terminal`
* Run the commands `touch ssh`
* Run the command: `echo "pi:\$6\$TE7HmruYY9EaNiKP\$Vz0inJ6gaoJgJvQrC5z/HMDRMTN2jKhiEnG83tc1Jsw7lli5MYdeA83g3NOVCsBaTVW4mUBiT/1ZRWYdofVQX0" > userconf` and `exit`
* Eject the `boot` and the `NTFS` volume
* Connect a RaspiBlitz (without HDD) to network, insert sd card and power up
* Find the IP of the RaspiBlitz (arp -a or check router)
* In terminal `ssh pi@[IP-OF-RASPIBLITZ]`
* Password is `raspberry`
* Run the following command BUT REPLACE `[BRANCH]` with the branch-string of your latest version
* To run the minimal pack: `wget --no-cache https://raw.githubusercontent.com/raspiblitz/raspiblitz/[BRANCH]/build_sdcard.sh && sudo bash build_sdcard.sh -u raspiblitz -b [BRANCH] -f 0 -d headless`
* Monitor/Check outputs for warnings/errors
* Login new with `ssh admin@[IP-OF-RASPIBLITZ]` (pw: raspiblitz) and run `release`
* Disconnect WiFi/LAN on build laptop (hardware switch off) and shutdown
* Remove `Ubuntu LIVE` USB stick and cut power from the RaspberryPi

Creating the image of sd card:

* Connect USB stick with latest `TAILS` (make it stay offline)
* Boot Tails with extra setting of Admin-Passwort and remember (use later for sudo)
* Menu > Systemtools > Settings > Energy -> best to set monitor to never turn off
* Connect USB stick with GPG signing keys - decrypt drive if needed
* Open Terminal and cd into directory of USB Stick under `/media/amnesia`
* Run `gpg --import ./sub.key`, check and `exit`
* Disconnect USB stick with GPG keys
* Take the SD card from the RaspberryPi and connect with an external SD card reader to the laptop
* Click on `boot` volume once in the file manger
* Connect the NTFS USB stick, open in file manager and delete old files
* To make a raw image from sd card - second way (UI with progress): 
  * Search "Laufwerke" or "Drives" on Tails Apps
  * Create image named `raspiblitz.img` to USB storage
* Open Terminal and cd into directory of NTFS USB stick under `/media/amnesia`
* `shasum -a 256 ./pishrink.sh` should be `760a7996fe8496e1d463e7a174d87ee92e41a8a1b195c02e98a27fcad2051dc6`
* `chmod +x ./pishrink.sh | sudo ./pishrink.sh ./raspiblitz.img`
* `gzip -c ./raspiblitz.img > ./raspiblitz-min/fat-vX.X.X-YEAR-MONTH-DAY.img.gz`
* `shasum -a 256 ./raspiblitz-min/fat-vX.X.X-YEAR-MONTH-DAY.img.gz > ./raspiblitz-min/fat-vX.X.X-YEAR-MONTH-DAY.img.gz.sha`
* make analog copy/note of checksum 
* Sign with `gpg --output raspiblitz-min/fat-vX.X.X-YEAR-MONTH-DAY.img.gz.sig --detach-sign raspiblitz-min/fat-vX.X.X-YEAR-MONTH-DAY.img.gz`

Prepare template for subversion update later:

* `mv ./raspiblitz.img ./raspiblitz-min-vX.X.X.img`
* `shasum -a 256 ./raspiblitz-min-vX.X.img > ./raspiblitz-min-vX.X.X.img.sha`
* make analog copy/note of checksum

Creating a fatpack sd card from the minimal image:

* Start TAILS live image
* On NTFS USB Stick (Open in Terminal) check hash of raspiblitz-min-vX.X.X.img wit analog note:
* `shasum -a 256 ./raspiblitz-min-vX.X.X.img`
* Right-Click the file and write to a min 32GB sd card
* On `bootfs` in FileManger (Open in Terminal):
* `touch stop` & `exit` terminal
* Shutdown TAILS & eject sd card
* Bootup UBUNTU LIVE
* Connect a RaspiBlitz (without HDD) to network, insert sd card and power up
* Find the IP of the RaspiBlitz (arp -a or check router)
* In terminal `ssh admin@[IP-OF-RASPIBLITZ]`
* Update to latest code with `patch code`
* the following only if its a `fatpack`:
  * run command `fatpack`
  * if it reboot, ssh in again & again run command `fatpack`
  * check that script ended without errors
* do the creation & signing of the image file like in chapter above

Publishing the images:

* Connect the NTFS USB stick to MacOS (it is just read-only)
* Run tests on the new image
* Upload the new image to the Download Server - put sig-file next to it
* Copy SHA256-String into GitHub README and update the download link
* Create Torrent file from image and place in in the `home.admin/assets` folder
  * upload images per FTP (Filezilla) to `yourseedbox.com` server under `torrent/rtorrent`
  * open QuickBox > ruTorrent and choose `create Torrent`
  * select image file, add trackers (see below) and start seeding
  * download the torrent-file into `home.admin/assets` folder & commit
  * get raw-link to torrent file from gitub
  * edit in `raspiblitz-docs` the `docs/software-setup/_download.md`

This is a recommended tracker list to be used with the torrent:
```
udp://tracker.coppersurfer.tk:6969/announce
http://tracker.yoshi210.com:6969/announce
http://open.acgtracker.com:1096/announce
http://tracker.skyts.net:6969/announce
udp://9.rarbg.me:2780/announce
http://tracker2.itzmx.com:6961/announce
udp://exodus.desync.com:6969/announce
http://pow7.com:80/announce
udp://tracker.leechers-paradise.org:6969
```

### Versioning

* Major Updates: 1.0.0, 2.0.0, 3.0.0, ... are epic updates signaling that the software reached a new era.
* Main Updates: 1.1.0, 1.2.0, 1.3.0, ... are release updates - the reflashing of the sd ard is mandatory.
* Minor Updates: 1.3.0, 1.3.1, 1.3.2, ... are patch updates - can be done by 'patching' the scripts & code, but new sd card reflash is still advised.

Every release has its own branch: `v1.9`, `v1.10`, `v1.11` .. this way hot patches can be merged into the release branch and people update with the `patch code` command

### How can I customize my RaspiBlitz or add other software?

The RaspiBlitz is your computer to experiment with. Feel free to add your own scripts, edit the system or install further software from the command line. Just keep in mind that after an update/recovery the RaspiBlitz starts with a fresh and clean operating system again. So all your editings and installs might be gone. To prevent this you should do the following:

- place your own scripts and data that should survive an update/recovery into the `/mnt/hdd/app-data` directory
- put all install commands & modification of the system into the script `/mnt/hdd/app-data/custom-installs.sh` which will be started automatically on a recovery/update.

### GitHub Workflow

- Development is done on the 'dev' branch, new features should be done on single feature branches and merged into 'dev' once ready.
- When a release of a new main-update (see above) comes closer, a new release branch gets created from 'dev' with the first release candidate - the RCs and the final release sd card will be build from this branch.
- All minor-releases will basically all work with the same 'build_sdcard.sh' script so that the code could be updated by just calling 'patch'. Emergency updates on lnd & bitcoin may break this guideline, but basic structure & packaging should stay mostly consistent over a main-update version.
- Once a release is ready, that release branch will be set as the "default" branch on GitHub (so its shown as main page)
- Hot fixes & new features for minor versions will be created as single branches from the release branch, and once ready will be merged back into that release branch as a Pull Request using 'Squash-Merge' AND then, this 'Squash-Merge' (one single commit) will get cherry-picked into the  'dev' branch ('git cherry-pick COMMITHASH' - may call 'git fetch' & 'git pull' before to make a clean cherry-pick into dev).

### Can I run RaspiBlitz on other computers than RaspberryPi?

Yes. The build script `build_sdcard.sh` (in the root of the raspiblitz repo) has the goal to be able to turn a fresh setup of the Linux distribution [Debian](https://cdimage.debian.org/cdimage/) (use latest release) into a RaspiBlitz system. Login as root and run:

`wget --no-cache https://raw.githubusercontent.com/raspiblitz/raspiblitz/dev/build_sdcard.sh && bash build_sdcard.sh -u raspiblitz -b dev -f 0 -d headless`

You can replace the first `raspiblitz` in the URL & after parameter `-u` with your github username and `dev` (replace 2 times) the the branch you want to build the system from. 

There is also an experimental section in the raspiblitz repo that tries to build for other SingleBoardComputers. Feel free to try it out and share your experience: [alternative.platforms/README.md](https://github.com/raspiblitz/raspiblitz/blob/dev/alternative.platforms/README.md)

### How can I build an SD card from another branch?

There might be new, but not released features in development that are not yet in the default version branch - but you want to try them out.

To build a SD card image from another branch than master, you can use the packer.sh script and just give it the name of the branch to build from - see top of this chapter.

### How can I build an SD card from my forked GitHub Repo?

If you fork the RaspiBlitz repo (much welcome) and you want to build an sd vcard you need to change one line in your code to the address of your repo and use that packer file to run: https://github.com/raspiblitz/raspiblitz/blob/655f5cb7b08d090fd5e5a54d5ee7f300bb975aab/ci/packer.sh#L9 

### How can I checkout a new branch from the RaspiBlitz repo to my forked repo?

You need to have your forked repo checked-out on your laptop. There your should see your forked repo as `origin` when you run `git remote -v`. If you don't see an additional `upstream` remote yet, then create it with the following command: `git remote add upstream https://github.com/raspiblitz/raspiblitz.git`.

So, first checkout the new branch named `BRANCH` from the original RaspBlitz repo to your local computer with: `git fetch upstream` and then `git checkout -b BRANCH upstream/BRANCH`.

Now push the new branch to your forked GitHub repo with `git push -u origin BRANCH`.

Once the branch is available and synced between the RaspiBlitz GitHub repo, your forked GitHub repo and your local computer git repo, you can start developing.

### How can I sync a branch of my forked GitHub with my local RaspiBlitz?

On the terminal use the command `github` and a menu shows up. Change the `REPO` to your forked Github repo. And then use `BRANCH` from that menu to set the branch your are working in.

You can the always use `PATCH` from that menu if you want to sync the scripts of your RaspiBlitz with the latest version of the scripts in your forked repo & branch. You can also use the terminal command `patch code` diretcly to trigger the sync.

So your workflow can go like this: You write code on your local computer. Commit to your local repo, push it to your forked repo and use the sync-script above to get the code to your RaspiBlitz.

### How can I manual provision an image with updated code?

For RaspberryPi: To boot an already build sd card image with your updated raspiblitz code base you can use the `stop` file flag. This will make the `_bootstrap.sh` script stop basically before making any setup or recovery changes to the system. You can SSH in an use the `github` command to update the raspiblitz code and then use `release` command. To set the `stop` file flag. Insert a fresh written sd card into your PC and on the root of `bootfs` drive with a file manager place a empty file simply called `stop` (with no file extension).

For VMs/Proxmox (since 1.11.3): If you wanna stop the bootstrap of a RaspiBlitz running in a VM you can add an "Audio Device" to it. If RaspiBlitz is running in a VM and an audio device it will stop for manual provision. So you just need to build your RaspiBlitz VM once, than have it as a template with an added audio device and just clone it, start it, SSH in to provision updated code (change to another branch or PR you want to test) and then use `release` to shutdown. Remove the audio device and your good to go. Under Proxmox on your VM under `Hardware` just add any of the three basic emulated audio devices available - just choose `driver=none`.

### How to add an app to the RaspiBlitz?

To add your app you can fork the raspiblitz repo, follow the `/home.admin/config.scripts/bonus.template.sh` script [see code](https://github.com/raspiblitz/raspiblitz/blob/dev/home.admin/config.scripts/bonus.template.sh), copy/adapt it, test it on your RaspiBlitz and make a PR back to the main repo.

### How contribute a feature/change from my forked branch back to the RaspiBlitz repo?

In the same way as described above, you can build a new feature or test a change. Once you have something ready that you want to contribute back, you make sure it's pushed to your forked GitHub repo, and then start a pull request from your forked repo to the RaspiBlitz repo.

See more info: https://yangsu.github.io/pull-request-tutorial/

### How can I help testing a Pull Request?

On the terminal use command 'github' (make sure your on the main raspiblitz repo). In the menu choose `PR` and enter the issue number of the pull request. Then your scripts will sync to the state of the PR and you can test it. If your done - use command `github` again and change `BRANCH` back to dev or the latest release.

### How can I push changes to an existing Pull Request?

See article: https://tech.sycamore.garden/add-commit-push-contributor-branch-git-github .. only works if your a contributor on raspiblitz repo.

### How to run the automatic amd64 build on a VM on OSX?

just notes so far:

https://brew.sh
brew install qemu
https://github.com/raspiblitz/raspiblitz/actions --> download amd64-lean image
double unzip until `qcow2` file 
convert `qcow2` to `vdi:
qemu-img convert -f qcow2 raspiblitz-amd64-debian-lean.qcow2 -O vdi raspiblitz-amd64-debian-lean.vdi
https://www.virtualbox.org/wiki/Downloads
