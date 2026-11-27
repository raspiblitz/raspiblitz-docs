#!/usr/bin/env bash
# Inspect a cold native RaspiBlitz build. Only read the mounted image.
set -euo pipefail
export LC_ALL=C

fail() { printf '%s\n' "$*" >&2; exit 2; }

device_for() {
    local mount=$1 fs=$2 dev options
    [[ $mount != / ]] && mountpoint -q -- "$mount" || fail "Expected an image mount: $mount"
    [[ $(findmnt -rn -M "$mount" -o FSTYPE) == "$fs" ]] || fail "Expected $fs at $mount"
    options=$(findmnt -rn -M "$mount" -o OPTIONS)
    [[ ,$options, == *,ro,* ]] || fail "Expected a read-only mount: $mount"
    dev=$(findmnt -rn -M "$mount" -o SOURCE)
    [[ $(lsblk -dn -o RO -- "$dev") == 1 ]] || fail "Expected a read-only block device for $mount"
    lsblk -dn -o PKNAME -- "$dev"
}
shopt -s nullglob
if [[ ${1:-} == --isolated-content ]]; then
    [[ $# == 3 ]] || fail 'Isolated content check needs a commit and version.'
    root=/image-root
    boot=/image-boot
    commit=$2
    version=$3
else
    [[ $# == 4 ]] || fail 'Usage: check-native-release.sh ROOT_MOUNT BOOT_MOUNT EXPECTED_COMMIT EXPECTED_VERSION'
    root=$(realpath -e -- "$1")
    boot=$(realpath -e -- "$2")
    commit=$3
    version=$4
    root_disk=$(device_for "$root" ext4)
    boot_disk=$(device_for "$boot" vfat)
    [[ $root_disk =~ ^loop[0-9]+$ && $root_disk == "$boot_disk" ]] || fail 'Expected partitions of one read-only loop device.'
    backing=$(losetup -ln -O BACK-FILE "/dev/$root_disk")
    [[ -f $backing ]] || fail 'Loop backing file unavailable.'
    for lun in /sys/kernel/config/usb_gadget/*/functions/mass_storage.*/lun.*/file; do
        attached=$(cat -- "$lun")
        [[ ! $backing -ef $attached ]] || fail 'The image is still attached to a USB gadget.'
    done
fi
[[ $commit =~ ^[0-9a-f]{40}$ && $version =~ ^[0-9][a-zA-Z0-9.-]+$ ]] || fail 'Invalid commit or version.'

issues=0
finding() { printf 'HOLD: %s\n' "$1"; issues=$((issues + 1)); }
repo="$root/home/admin/raspiblitz"
info="$root/home/admin/_version.info"
if ! observed=$(git --no-optional-locks -c safe.directory="$repo" --git-dir="$repo/.git" rev-parse --verify 'HEAD^{commit}'); then
    finding 'Installed source revision unavailable'
elif [[ $observed != "$commit" ]]; then
    finding 'Installed source revision differs from the manifest'
fi
grep -Fxq -- "codeVersion=\"$version\"" "$info" || finding 'Version differs from the manifest'
grep -Fxq -- "codeRelease=\"${commit:0:4}\"" "$info" || finding 'Native release marker differs from the manifest'

for path in "$boot/stop" "$boot/network-config" "$boot/network-config.txt" "$boot/raspiblitz-image-shutdown" \
    "$root/etc/systemd/system/raspiblitz-image-bootstrap.service" \
    "$root/etc/systemd/system/multi-user.target.wants/raspiblitz-image-bootstrap.service" \
    "$root/usr/local/lib/raspiblitz-image-guest.sh" "$root/var/log/raspiblitz-image-bootstrap.log" \
    "$root/home/admin/stop" "$root/home/blitzapi/blitz_api/.env" \
    "$root/etc/ssh/rb_handbuch_host_ed25519" "$root/etc/ssh/sshd_config.d/00-rb-handbuch.conf" \
    "$root/etc/sudoers.d/010_rb_handbuch" "$root/var/lib/raspiblitz-agent" "$root"/var/lib/rb-handbuch-*; do
    if [[ -e $path || -L $path ]]; then finding "Retained build state (${path#"$root"/})"; fi
done
[[ -r $boot/cmdline.txt ]] || fail 'Boot command line unavailable.'
if grep -Eq '(^|[[:space:]])modprobe\.blacklist=[^[:space:]]*nvme' "$boot/cmdline.txt"; then
    finding 'Lab NVMe blacklist present in boot command line'
fi
hostkey=$(find "$root/etc/ssh" -maxdepth 1 -name 'ssh_host_*_key' -print -quit)
[[ -z $hostkey ]] || finding 'SSH host private key present'
access=$(find "$root/root" "$root/home" -xdev \( -type f -o -type l \) \
    -path '*/.ssh/authorized_keys*' -size +0c -print -quit)
[[ -z $access ]] || finding 'Preauthorized SSH login present'

if (( issues > 0 )); then
    printf '%d findings. Hold the image.\n' "$issues" >&2
    exit 1
fi
printf 'Native image checks passed for %s (%s).\n' "$version" "$commit"
