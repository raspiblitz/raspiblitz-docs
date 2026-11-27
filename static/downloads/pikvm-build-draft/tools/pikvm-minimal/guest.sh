#!/usr/bin/env bash
# Runs only in the build guest. The PiKVM supplies the runtime files on a read-only disk.
set -Eeuo pipefail
umask 077
export HOME=/root USER=root LOGNAME=root LC_ALL=C
runtime=/run/raspiblitz-image-build
boot=/boot/firmware
timer=raspiblitz-image-lease.timer
job=raspiblitz-image-job.service

check_build_disk() {
    local root_device root_disk disks
    root_device=$(findmnt -nro SOURCE /) || return 1
    root_disk=$(lsblk -dnro PKNAME -- "$root_device") || return 1
    disks=$(lsblk -dnro NAME,TYPE) || return 1
    if [[ -z $root_disk ]] || ! grep -Fxq -- "$root_disk disk" <<< "$disks"; then
        echo 'Could not identify the root partition in the disk inventory.' >&2
        return 1
    fi
    if grep -Eq '^nvme' <<< "$disks"; then
        echo 'Physical NVMe visible on the build Pi.' >&2
        return 1
    fi
}

bootstrap() {
    local helper_uuid=$1 device attempt root_uuid
    trap 'rc=$?; printf "Bootstrap failed at line %s with exit %s\n" "$LINENO" "$rc" >&2; systemctl --no-block poweroff' ERR
    mountpoint -q "$boot"
    [[ $(findmnt -no FSTYPE /run) == tmpfs ]]
    [[ $(tr -d '\0' </proc/device-tree/model) == 'Raspberry Pi 5 '* ]]
    check_build_disk
    install -d -m 700 "$runtime" "$runtime/source"
    device="/dev/disk/by-uuid/$helper_uuid"
    for ((attempt=0; attempt<40; attempt++)); do
        [[ ! -b $device ]] || break
        sleep 1
    done
    [[ -b $device ]]
    mount -o ro,nosuid,nodev,noexec -- "$device" "$runtime/source"
    # Read only the nonsecret build profile until the root identity is checked
    # and swap is disabled. Key material must stay off the exported disk.
    # shellcheck source=/dev/null
    source "$runtime/source/profile"
    root_uuid=$(findmnt -no UUID /)
    [[ -n $root_uuid && $root_uuid == "$ROOT_UUID" ]]
    # Keep guest SSH keys off swap on the image, including while apt upgrades packages.
    systemctl mask --runtime --now dphys-swapfile.service
    swapoff --all
    # Keep scheduled APT jobs from starting during the build. An APT process
    # already running can finish while the native installer waits for its lock.
    systemctl mask --runtime --now apt-daily.timer apt-daily-upgrade.timer
    systemctl mask --runtime apt-daily.service apt-daily-upgrade.service
    for file in profile guest.sh hostkey authorized_keys build_sdcard.sh; do
        install -m 600 -- "$runtime/source/$file" "$runtime/$file"
    done
    umount -- "$runtime/source"
    # A cold Bookworm boot can reach Ethernet before NTP sets its clock.
    # The read-only helper carries the controller time for the first TLS requests.
    local guest_epoch
    guest_epoch=$(date +%s)
    if ((guest_epoch < CONTROLLER_EPOCH || guest_epoch > CONTROLLER_EPOCH + 900)); then
        printf 'Correcting first-boot clock from epoch %s using the PiKVM.\n' "$guest_epoch"
        date --utc --set "@$CONTROLLER_EPOCH"
    fi
    install -d -m 755 /run/sshd
    cat > "$runtime/sshd.conf" <<EOF
Port $SSH_PORT
HostKey $runtime/hostkey
AuthorizedKeysFile $runtime/authorized_keys
AllowUsers root
PermitRootLogin forced-commands-only
AuthenticationMethods publickey
PasswordAuthentication no
KbdInteractiveAuthentication no
DisableForwarding yes
PermitTTY no
UsePAM yes
PrintMotd no
PidFile $runtime/sshd.pid
EOF
    /usr/sbin/sshd -t -f "$runtime/sshd.conf"
    systemd-run --unit=raspiblitz-image-lease --on-active=4min --timer-property=AccuracySec=1s \
        /bin/bash "$runtime/guest.sh" expire
    systemd-run --unit=raspiblitz-image-ssh --service-type=exec \
        /usr/sbin/sshd -D -e -f "$runtime/sshd.conf"
}

signal() { printf 'RBBUILD %s %s\n' "$RUN_ID" "$*"; }

power_down() {
    local result=$1 failed=0
    # A controller disconnect can close stdout while the acknowledgement is
    # being sent. Finish the local poweroff even if printf gets EPIPE.
    trap '' PIPE
    if printf '%s %s\n' "$RUN_ID" "$result" > "$boot/raspiblitz-image-shutdown" &&
            sync -f / && sync -f "$boot"; then
        signal "POWEROFF $result" || failed=1
    else
        failed=1
        signal 'FAILED shutdown-record' || true
    fi
    if ! systemctl --no-block poweroff; then
        signal 'FAILED poweroff-request' || true
        return 1
    fi
    return "$failed"
}

session() {
    [[ ${SSH_ORIGINAL_COMMAND:-} == start ]]
    signal "READY $(findmnt -no UUID /) $(cat /proc/sys/kernel/random/boot_id)"
    local request job_timeout=3h
    if [[ $MODE == fatpack ]]; then job_timeout=12h; fi
    if ! IFS= read -r request || [[ $request != start ]]; then
        return 2
    fi
    mkdir "$runtime/started"
    # Cover the handover: the initial timer still protects the Pi if creating
    # the renewable lease fails.
    systemd-run --unit=raspiblitz-image-abort --on-active=40s --timer-property=AccuracySec=1s \
        /bin/bash "$runtime/guest.sh" expire
    systemctl stop "$timer"
    timer=raspiblitz-image-abort.timer
    touch "$runtime/build.log"
    systemd-run --unit="${job%.service}" --service-type=exec --property="RuntimeMaxSec=$job_timeout" \
        --property=TimeoutStopSec=30s --property=KillMode=control-group \
        --property="StandardOutput=append:$runtime/build.log" --property=StandardError=inherit \
        /bin/bash "$runtime/guest.sh" build
    tail -n +1 --pid="$$" -s 0.2 -f "$runtime/build.log" &
    trap 'kill "$!" 2>/dev/null || true' EXIT
    while IFS= read -r request; do
        if ! systemctl is-active --quiet "$job"; then
            signal 'FAILED inactive-build-job'
            return 1
        fi
        case $request in
            heartbeat) systemctl restart "$timer" ;;
            shutdown)
                [[ -e $runtime/release-ready ]]
                # Write directly to the SSH stream before requesting poweroff.
                # The controller requires this confirmation as well as the cold marker.
                power_down release
                return
                ;;
            *) return 2 ;;
        esac
    done
}

start_apt_tor() {
    # The installer disables its normal instance until DATA is set up. A
    # client in RAM lets release validate the configured onion APT source.
    local data=/run/raspiblitz-image-apt-tor attempt
    install -d -o debian-tor -g debian-tor -m 700 "$data"
    install -o debian-tor -g debian-tor -m 600 /dev/null "$data/torrc"
    systemd-run --unit=raspiblitz-image-apt-tor --service-type=exec --uid=debian-tor \
        --property="StandardOutput=append:$data/tor.log" --property=StandardError=inherit \
        "$(command -v tor)" --defaults-torrc "$data/torrc" -f "$data/torrc" --DataDirectory "$data" \
        --ClientOnly 1 --ExitRelay 0 --RunAsDaemon 0 --SocksPort 127.0.0.1:9050 --Log 'notice stdout'
    for ((attempt=0; attempt<90; attempt++)); do
        if grep -Fq 'Bootstrapped 100%' "$data/tor.log"; then
            echo 'Temporary Tor APT transport bootstrapped.'
            return 0
        fi
        systemctl is-active --quiet raspiblitz-image-apt-tor.service || break
        sleep 2
    done
    tail -n 25 "$data/tor.log" >&2
    return 1
}

prepare_pinned_installer() {
    local original="$runtime/build_sdcard.sh" clone line
    local -a matches
    [[ $COMMIT =~ ^[0-9a-f]{40}$ && $(git hash-object -- "$original") == "$BLOB" ]] || {
        echo 'Invalid pinned commit or installer blob.' >&2
        return 1
    }
    clone='sudo -u admin git clone -b "${branch}" https://github.com/${github_user}/raspiblitz.git || exit 1'
    mapfile -t matches < <(grep -Fnx -- "$clone" "$original")
    if [[ ${#matches[@]} != 1 ]]; then
        echo 'Expected exactly one recognized RaspiBlitz clone in the pinned native installer.' >&2
        return 1
    fi
    line=${matches[0]%%:*}
    {
        head -n "$((line - 1))" -- "$original"
        printf 'raspiblitz_build_commit=%s\n' "$COMMIT"
        # Match the fetched branch before checking out any files. Keep its
        # normal upstream tracking configuration for the shipped RaspiBlitz.
        cat <<'PINNED_CHECKOUT'
sudo -u admin git clone --no-checkout -b "${branch}" "https://github.com/${github_user}/raspiblitz.git" || exit 1
raspiblitz_fetched_commit=$(sudo -u admin git -C /home/admin/raspiblitz rev-parse --verify 'HEAD^{commit}') || exit 1
if [[ $raspiblitz_fetched_commit != "$raspiblitz_build_commit" ]]; then
    printf 'RaspiBlitz branch changed during build: expected %s, fetched %s\n' "$raspiblitz_build_commit" "$raspiblitz_fetched_commit" >&2
    exit 1
fi
sudo -u admin git -C /home/admin/raspiblitz reset --hard "$raspiblitz_build_commit" || exit 1
PINNED_CHECKOUT
        tail -n "+$((line + 1))" -- "$original"
    } > "$runtime/pinned-installer.sh"
}

clean_fatpack_compiler_caches() (
    cd -P -- /home
    [[ $PWD == /home ]]
    local app
    for app in mempool thunderhub; do
        # The account used to build the application also removes its own generated files.
        runuser -u "$app" -- bash -seu -- "$app" <<'CLEAN_COMPILER_CACHE'
set -o pipefail
[[ $EUID -ne 0 ]]
app=$1
# Never enter linked or foreign directories. Relative steps keep the selected working
# directory anchored; verify the physical path even if the entry changed during cd.
enter_owned() {
    local expected=$PWD/$1
    [[ -d $1 && ! -L $1 && -O $1 ]] && cd -P -- "$1" && [[ $PWD == "$expected" ]]
}
clean_cache() (
    local part unsafe before after
    for part in "$@"; do enter_owned "$part" || return 0; done
    unsafe=$(find -P . -xdev \( ! -uid "$EUID" -o -type l \) -print -quit)
    if [[ -n $unsafe ]]; then
        printf 'Skipping compiler cache with linked or foreign entries: %s\n' "$PWD"
        return 0
    fi
    before=$(du -sx -B1 -- .)
    find -P . -xdev -depth -mindepth 1 -uid "$EUID" -delete
    after=$(du -sx -B1 -- .)
    printf 'Fatpack compiler cache %s allocated bytes before=%s after=%s\n' \
        "$PWD" "${before%%[[:space:]]*}" "${after%%[[:space:]]*}"
)
# Skip mounted storage, including a same-filesystem bind mount in either cache tree.
mounts=$(findmnt -rn -o TARGET)
while IFS= read -r target; do
    case $target in "$PWD"|"$PWD/$app"|"$PWD/$app/"*) exit 0 ;; esac
done <<< "$mounts"
enter_owned "$app" || exit 0
case $app in
    mempool)
        for part in mempool frontend .angular cache; do enter_owned "$part" || exit 0; done
        for version in *; do
            [[ $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || continue
            clean_cache "$version" angular-webpack
        done ;;
    thunderhub) clean_cache thunderhub src client .next cache webpack ;;
esac
CLEAN_COMPILER_CACHE
    done
)

verify_fatpack() {
    local repo path branch revision expected_branch app file status
    lnd --version
    lightningd --version
    node --version
    /home/electrs/electrs/target/release/electrs --version
    /home/blitzapi/blitz_api/venv/bin/python -B -c 'import fastapi, grpc, uvicorn'
    grep -Fxq 'displayClass=lcd' /home/admin/raspiblitz.info
    for repo in blitz_api blitz_web; do
        path="/home/blitzapi/$repo"
        branch=$(git -c safe.directory="$path" -C "$path" branch --show-current)
        revision=$(git -c safe.directory="$path" -C "$path" rev-parse --verify 'HEAD^{commit}')
        [[ -n $branch && ${#revision} == 40 ]]
        printf 'FATPACK component %s %s %s\n' "$repo" "$branch" "$revision"
        if [[ $BRANCH == v[0-9]* && $BRANCH != *dev* ]]; then
            expected_branch="blitz-$BRANCH"
            if [[ $repo == blitz_web ]]; then expected_branch="release/$BRANCH"; fi
            if [[ $branch != "$expected_branch" ]]; then
                printf 'Release requires %s branch %s, got %s\n' "$repo" "$expected_branch" "$branch" >&2
                return 1
            fi
        fi
    done
    for app in albyhub lnbits jam btcpayserver rtl thunderhub btc-rpc-explorer mempool electrs; do
        status=$("/home/admin/config.scripts/bonus.$app.sh" status)
        if ! grep -Fxq 'fatpack=1' <<< "$status"; then
            printf 'Missing Fatpack installation for %s\n' "$app" >&2
            return 1
        fi
    done
    # Some installers create the app account before compiling and return
    # success even when their final build command failed. Inspect the payload.
    for file in /home/admin/assets/nginx/www_public/index.html \
        /home/albyhub/bin/albyhub /home/lnbits/lnbits/pyproject.toml \
        /home/jam/webui/build/index.html /home/btcpay/dotnet/dotnet \
        /home/btcpay/btcpayserver/BTCPayServer/bin/Release/*/BTCPayServer.dll \
        /home/btcpay/NBXplorer/NBXplorer/bin/Release/*/NBXplorer.dll \
        /home/rtl/RTL/rtl.js /home/rtl/RTL/node_modules/express/package.json \
        /home/thunderhub/thunderhub/src/client/.next/BUILD_ID \
        /home/btcrpcexplorer/btc-rpc-explorer/node_modules/express/package.json \
        /home/mempool/mempool/backend/dist/index.js; do
        if [[ ! -f $file || ! -s $file ]]; then
            printf 'Missing Fatpack payload: %s\n' "$file" >&2
            return 1
        fi
    done
    printf 'Fatpack installation and compiled payload checks passed.\n'
}

build() {
    # Package scripts need normal system file permissions. The parent /run
    # directory protects the job logs and keys independently.
    umask 022
    trap 'rc=$?; signal "FAILED $rc"; exit "$rc"' ERR
    if [[ $MODE == abort ]]; then
        printf '%s\n' "$RUN_ID" > "$boot/raspiblitz-image-probe"
        sync
        signal PROBE
        sleep infinity
        return
    fi

    local remote="https://github.com/$OWNER/raspiblitz.git" installed expected package
    local fatpack_flag=0 display=headless
    case $MODE in
        build) ;;
        fatpack)
            fatpack_flag=1
            display=lcd
            # Smaller root partitions cause the native Fatpack helper to
            # request an expansion and potentially reboot during the SSH job.
            local root_device root_bytes
            root_device=$(findmnt -n -o SOURCE /)
            root_bytes=$(blockdev --getsize64 "$root_device")
            if ((root_bytes < 58465668608)); then
                echo "Fatpack requires a root partition of at least 58465668608 bytes, got $root_bytes" >&2
                return 1
            fi
            ;;
        *) printf 'Unknown build mode: %s\n' "$MODE" >&2; return 2 ;;
    esac
    date --utc --iso-8601=seconds
    expected=$(git ls-remote --exit-code "$remote" "refs/heads/$BRANCH")
    [[ ${expected%%[[:space:]]*} == "$COMMIT" ]]
    prepare_pinned_installer
    printf 'DPkg::Lock::Timeout "180";\n' > "$runtime/apt-build.conf"
    APT_CONFIG="$runtime/apt-build.conf" bash "$runtime/pinned-installer.sh" --github-user "$OWNER" --branch "$BRANCH" \
        --interaction 0 --fatpack "$fatpack_flag" --display "$display" --tweak-boot-drive 0 --wifi-region off
    grep -Fxq '# BUILD DONE - see above' "$runtime/build.log"
    if grep -Eq '^E: (Could not get lock|Unable to acquire .*lock)' "$runtime/build.log"; then
        echo 'The native installer encountered an APT lock error.' >&2
        return 1
    fi
    installed=$(runuser -u admin -- git -C /home/admin/raspiblitz rev-parse HEAD)
    [[ $installed == "$COMMIT" ]]
    expected=$(git ls-remote --exit-code "$remote" "refs/heads/$BRANCH")
    [[ ${expected%%[[:space:]]*} == "$COMMIT" ]]
    grep -Fxq "codeVersion=\"$VERSION\"" /home/admin/_version.info
    command -v bitcoind tor
    bitcoind --version | sed -n '1p'
    tor --version | sed -n '1p'
    [[ -x /usr/bin/snowflake-proxy && -x /usr/bin/snowflake-client ]]
    [[ -z $(dpkg --audit) ]]

    # Use the installed release helper, handing its last poweroff to this job
    # so we can record completion after cleanup, with the temporary SSH still up.
    local release=/home/admin/config.scripts/blitz.release.sh
    [[ $(tail -n 1 -- "$release") == 'sudo shutdown now' ]]
    sed '$d' "$release" > "$runtime/release.sh"
    if [[ -s /etc/apt/sources.list.d/tor.list ]] && grep -q '^deb .*tor+' /etc/apt/sources.list.d/tor.list; then
        start_apt_tor
    fi
    runuser -u admin -- bash < "$runtime/release.sh"
    [[ -z $(dpkg --audit) ]]
    grep -Fxq "codeRelease=\"${COMMIT:0:4}\"" /home/admin/_version.info
    # APT can return zero while keeping stale indexes. Require a strict update
    # after Tor and other prerequisites have been installed and started.
    apt-get -o APT::Update::Error-Mode=any update
    for package in chromium firefox cups-daemon libreoffice-core; do
        if [[ $(dpkg-query -W -f='${db:Status-Status}' "$package" 2>/dev/null) == installed ]]; then
            printf 'Unexpected desktop package in release image: %s\n' "$package" >&2
            return 1
        fi
    done
    if [[ $MODE == fatpack ]]; then
        clean_fatpack_compiler_caches
        verify_fatpack
    fi
    apt-get clean
    # Flush bulk build writes while heartbeats are still flowing. The SSH
    # handler syncs both filesystems again after writing its final marker.
    sync -f /
    sync -f "$boot"
    touch "$runtime/release-ready"
    signal SHUTDOWN-READY
    # Keep the checked job active until the controller acknowledges readiness.
    # Loss of the connection lets the existing lease expire and powers off.
    exec sleep infinity
}

case ${1:-} in
    bootstrap) bootstrap "$2" ;;
    start|build|expire)
        # shellcheck source=/dev/null
        source "$runtime/profile"
        case $1 in
            start) session ;;
            build) build ;;
            expire)
                systemctl stop "$job" || true
                power_down aborted
                ;;
        esac
        ;;
    *) exit 2 ;;
esac
