#!/usr/bin/env python3
"""Build and boot-test a native RaspiBlitz Minimal or Fatpack image on an attached Pi 5."""

import argparse
from contextlib import contextmanager, ExitStack
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import selectors
import shlex
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import time
import uuid

from package_image import package_and_unpack
from image_paths import create_link, create_regular, overwrite_existing, regular_file_read, unlink_regular
from audit_mounts import audit_mounts

TOOLS = Path(__file__).resolve().parent.parent
MSD = Path('/var/lib/kvmd/msd')
STATE = MSD / 'raspiblitz-image-build'
LUNS = Path('/sys/kernel/config/usb_gadget/kvmd/functions')
API_CONFIG = '/root/.config/raspiblitz-agent/kvmd-curl.conf'
BOOTSTRAP = 'etc/systemd/system/raspiblitz-image-bootstrap.service'
BOOTSTRAP_LINK = 'etc/systemd/system/multi-user.target.wants/raspiblitz-image-bootstrap.service'
GUEST = 'usr/local/lib/raspiblitz-image-guest.sh'
BOOTSTRAP_LOG = 'var/log/raspiblitz-image-bootstrap.log'
SHUTDOWN = 'raspiblitz-image-shutdown'
ISOLATION = b'\n[all]\n# PiKVM build isolation\ndtparam=pciex1=off\n'
NVME_GUARD = b' module_blacklist=nvme'
ID_PATTERN = r'[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}'
PORT = 2222
GIB = 1024**3
DEFAULT_PROFILE = STATE / 'minimal-profile.json'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def output(*args):
    return run(*args, text=True, stdout=subprocess.PIPE).stdout.strip()


def sha256(path):
    with path.open('rb') as data:
        return hashlib.file_digest(data, 'sha256').hexdigest()


def udc_state():
    paths = list(Path('/sys/class/udc').glob('*/state'))
    require(len(paths) == 1, 'Expected one PiKVM USB device controller')
    return paths[0].read_text().strip().replace(' ', '-')


def wait_off(timeout=150):
    end = time.monotonic() + timeout
    detached_since = None
    while time.monotonic() < end:
        now = time.monotonic()
        if udc_state() == 'not-attached':
            if detached_since is not None and now - detached_since >= 5:
                return
            detached_since = now if detached_since is None else detached_since
        else:
            detached_since = None
        time.sleep(1)
    raise RuntimeError('USB detach was not confirmed. The media remain reserved.')


def slot(index):
    return LUNS / f'mass_storage.usb{index}/lun.0'


def media(index):
    return (slot(index) / 'file').read_text().strip()


def insert(index, image, writable):
    require(not media(index), f'USB drive {index} is occupied')
    run('kvmd-otgmsd', '-i', str(index), '--set-cdrom=0',
        f'--set-rw={int(writable)}', f'--set-image={image}')
    require(media(index) == str(image) and
            (slot(index) / 'ro').read_text().strip() == str(int(not writable)),
            f'USB drive {index} did not select the expected image and mode')


def eject(index, expected):
    require(udc_state() == 'not-attached', 'USB host is still attached')
    mounted = media(index)
    if mounted:
        require(mounted == str(expected), f'Unrecognized medium in drive {index}')
        run('kvmd-otgmsd', '-i', str(index), '--eject')
        require(not media(index), f'Drive {index} did not eject')


def api(route, method='GET'):
    result = json.loads(output('curl', '--config', API_CONFIG, '--cacert',
                               '/etc/kvmd/nginx/ssl/server.crt', '--noproxy', 'localhost',
                               '--resolve', 'localhost:443:127.0.0.1', '--max-time', '10',
                               '--fail', '--silent', '--show-error', '--request', method,
                               f'https://localhost/api/{route}'))
    require(result['ok'], f'PiKVM API failed: {route}')
    return result['result']


def click(button):
    api(f'atx/click?button={button}&wait=1', method='POST')


def listening(address, port):
    try:
        with socket.create_connection((address, port), timeout=1):
            return True
    except OSError:
        return False


def firmware_prompt(work):
    picture = work / 'boot-screen.jpg'
    picture.unlink(missing_ok=True)
    run('python', TOOLS / 'pikvm-snapshot.py', picture, timeout=40)
    words = output('timeout', '25', 'env', 'OMP_THREAD_LIMIT=1',
                   'tesseract', picture, 'stdout', '--psm', '6').lower()
    return bool(re.search(r'press\s+(?:the\s+)?power\s+button', words) and
                ('usb' in words or 'supply' in words))


def boot(address, port, work):
    require(udc_state() == 'not-attached', 'Expected the Pi to be stopped before boot')
    # The reset relay is wired to the Pi 5 power button. The PowerBlock relay
    # is needed only if the power supply was switched off.
    click('reset')
    start = time.monotonic()
    power_clicked = False
    prompt_confirmed = False
    snapshot_at = start + 16
    while time.monotonic() - start < 240:
        state = udc_state()
        if state == 'configured' and listening(address, port):
            return
        if time.monotonic() >= snapshot_at and not prompt_confirmed:
            if firmware_prompt(work):
                click('reset')
                prompt_confirmed = True
            snapshot_at = time.monotonic() + 15
        if (time.monotonic() - start >= 28 and not power_clicked and not prompt_confirmed
                and state == 'not-attached' and not api('atx')['leds']['power']):
            click('power')
            power_clicked = True
        time.sleep(2)
    raise RuntimeError(f'Pi did not boot to SSH port {port}')


@contextmanager
def partitions(image, readonly):
    for path in LUNS.glob('mass_storage.*/lun.*/file'):
        attached = path.read_text().strip()
        require(not attached or not image.samefile(attached), 'An attached image cannot be mounted')
    require(not output('losetup', '-j', image), 'Another loop device already owns the image')
    options = ['--read-only'] if readonly else []
    loop = output('losetup', '--find', '--show', '--partscan', *options, image)
    try:
        run('udevadm', 'settle')
        boot_part, root_part = (Path(f'{loop}p{i}') for i in (1, 2))
        require(boot_part.is_block_device() and root_part.is_block_device(),
                'Expected a FAT boot partition and an ext4 root partition')
        require(output('blkid', '-s', 'TYPE', '-o', 'value', boot_part) == 'vfat' and
                output('blkid', '-s', 'TYPE', '-o', 'value', root_part) == 'ext4',
                'Unexpected image filesystem types')
        yield boot_part, root_part
    finally:
        run('losetup', '--detach', loop)


@contextmanager
def mount(device, target, options):
    target.mkdir(mode=0o700, exist_ok=True)
    run('mount', '-o', options, device, target)
    try:
        yield target
    finally:
        run('umount', target)


def ensure_fatpack_root_space(image, work, target_bytes, minimum_bytes):
    """Grow only the final ext4 partition of the detached, shrunk image."""
    require(0 < minimum_bytes < target_bytes and image.stat().st_size <= target_bytes,
            'Invalid Fatpack root reserve or target capacity')
    with partitions(image, readonly=False) as (boot_part, root_part):
        require(re.fullmatch(r'loop[0-9]+p2', root_part.name), 'Unexpected root loop partition')
        loop = root_part.with_name(root_part.name[:-2])
        table = json.loads(output('sfdisk', '--json', loop))['partitiontable']
        parts = table['partitions']
        require(table['label'] in ('dos', 'gpt') and table['unit'] == 'sectors'
                and [p['node'] for p in parts] == [str(boot_part), str(root_part)]
                and parts[0]['start'] + parts[0]['size'] <= parts[1]['start'],
                'Fatpack needs FAT partition 1 followed by the final ext4 partition 2')
        mib = 1024**2
        # The first boot writes logs and runtime data before measuring again.
        # Leave some working room above the required post-boot free space.
        desired = minimum_bytes + min(minimum_bytes // 4, 512 * mib)
        tried_at_capacity = False
        while True:
            with mount(root_part, work / 'root', 'ro,noload,nodev,nosuid,noexec') as root:
                fs = os.statvfs(root)
                available = fs.f_bavail * fs.f_frsize
            if available >= desired or (tried_at_capacity and available >= minimum_bytes):
                return available
            require(not tried_at_capacity,
                    f'Fatpack root has {available} bytes for apps at target capacity {target_bytes}; '
                    f'{minimum_bytes} bytes required')
            # Allow for new ext4 metadata, reserved blocks and first-boot writes.
            # f_bavail can be zero even while the reserved-block pool is depleted.
            growth = (desired - available) * 11 // 10 + 128 * mib
            old_size = image.stat().st_size
            size = min(target_bytes, ((old_size + growth + mib - 1) // mib) * mib)
            tried_at_capacity = size == target_bytes
            checked = subprocess.run(['e2fsck', '-fp', root_part], check=False)
            require(checked.returncode in (0, 1), 'Fatpack root filesystem check failed before resize')
            if size > old_size:
                with image.open('r+b') as raw:
                    raw.truncate(size)
                run('losetup', '--set-capacity', loop)
            run('parted', '--script', '--fix', loop, 'resizepart', '2', '100%')
            run('partx', '--update', '--nr', '2', loop)
            run('udevadm', 'settle')
            after = json.loads(output('sfdisk', '--json', loop))['partitiontable']['partitions']
            require(len(after) == 2 and after[0] == parts[0] and after[1]['start'] == parts[1]['start']
                    and after[1]['node'] == str(root_part) and after[1]['size'] >= parts[1]['size'],
                    'Unexpected change to the Fatpack partition layout')
            run('resize2fs', root_part)


def add_isolation(boot_dir):
    data = regular_file_read(boot_dir, 'config.txt', 1024**2)
    require(ISOLATION not in data, 'Unexpected PiKVM PCIe override in the base image')
    overwrite_existing(boot_dir, 'config.txt', data + ISOLATION)
    line = regular_file_read(boot_dir, 'cmdline.txt', 65536)
    require(len(line.splitlines()) == 1 and b'module_blacklist=' not in line,
            'Unexpected kernel command line for the PiKVM boot copy')
    command = line.rstrip(b'\r\n') + NVME_GUARD + line[len(line.rstrip(b'\r\n')):]
    overwrite_existing(boot_dir, 'cmdline.txt', command)
    require(regular_file_read(boot_dir, 'cmdline.txt', 65536) == command and
            regular_file_read(boot_dir, 'config.txt', 1024**2) == data + ISOLATION,
            'Could not confirm the boot-time NVMe isolation settings')


def copy_verified_base(source, image, expected, working_bytes):
    # Read the vendor RAW only once and authenticate exactly the bytes used for this job.
    digest = hashlib.sha256()
    zeros = bytes(256 * 1024)
    with source.open('rb') as original, image.open('xb') as clone:
        while block := original.read(len(zeros)):
            digest.update(block)
            if block == zeros:
                clone.seek(len(block), os.SEEK_CUR)
            else:
                clone.write(block)
        require(digest.hexdigest() == expected, 'Raspberry Pi OS RAW checksum mismatch')
        require(clone.tell() <= working_bytes, 'Working medium is smaller than the source')
        clone.truncate(working_bytes)


def prepare(image, work, profile, helper_uuid):
    copy_verified_base(profile['base'], image, profile['base_sha256'], profile['working_bytes'])
    run('parted', '-s', image, 'resizepart', '2', '100%')
    with partitions(image, readonly=False) as (boot_part, root_part):
        if profile['variant'] == 'fatpack':
            require(int(output('blockdev', '--getsize64', root_part)) >= 58465668608,
                    'Prepared root partition is too small for the native Fatpack installer')
        checked = subprocess.run(['e2fsck', '-pf', root_part], check=False)
        require(checked.returncode in (0, 1), 'Base root filesystem check failed')
        run('resize2fs', root_part)
        with mount(root_part, work / 'root', 'rw,nodev,nosuid,noexec') as root:
            guest = root / GUEST
            guest.parent.mkdir(parents=True, exist_ok=True)
            require(not guest.exists(), 'Unexpected bootstrap helper in base image')
            shutil.copyfile(TOOLS / 'pikvm-minimal/guest.sh', guest)
            (root / BOOTSTRAP).write_text(
                '[Unit]\nDescription=Temporary PiKVM image bootstrap\nAfter=local-fs.target\n'
                '[Service]\nType=oneshot\nTimeoutStartSec=90\n'
                f'StandardOutput=append:/{BOOTSTRAP_LOG}\nStandardError=inherit\n'
                f'ExecStart=/bin/bash /{GUEST} bootstrap {helper_uuid}\n'
                '[Install]\nWantedBy=multi-user.target\n')
            (root / BOOTSTRAP_LINK).symlink_to('/' + BOOTSTRAP)
        with mount(boot_part, work / 'boot', 'rw,nodev,nosuid,noexec') as boot_dir:
            add_isolation(boot_dir)
            (boot_dir / 'stop').touch()
        return output('blkid', '-s', 'UUID', '-o', 'value', root_part)


def make_helper(secure, profile, run_id, root_uuid, helper_uuid, mode):
    files = secure / 'files'
    files.mkdir(mode=0o700)
    run('ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-f', secure / 'client')
    run('ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-f', files / 'hostkey')
    host_public = (files / 'hostkey.pub').read_text().split()[:2]
    (secure / 'known_hosts').write_text(f'{run_id} {" ".join(host_public)}\n')
    public = (secure / 'client.pub').read_text().strip()
    command = '/bin/bash /run/raspiblitz-image-build/guest.sh start'
    (files / 'authorized_keys').write_text(f'restrict,command="{command}" {public}\n')
    shutil.copyfile(TOOLS / 'pikvm-minimal/guest.sh', files / 'guest.sh')
    owner, commit = profile['owner'], profile['commit']
    script = files / 'build_sdcard.sh'
    run('curl', '--fail', '--silent', '--show-error', '--location', '--proto', '=https',
        '--max-time', '90', '--output', script,
        f'https://raw.githubusercontent.com/{owner}/raspiblitz/{commit}/build_sdcard.sh')
    require(output('git', 'hash-object', script) == profile['blob'], 'Installer blob mismatch')
    values = {name.upper(): profile[name] for name in ('owner', 'branch', 'commit', 'blob', 'version')}
    values.update(RUN_ID=run_id, ROOT_UUID=root_uuid, MODE=mode, SSH_PORT=str(PORT),
                  CONTROLLER_EPOCH=str(int(time.time())))
    (files / 'profile').write_text(''.join(f'{key}={shlex.quote(value)}\n' for key, value in values.items()))
    helper = secure / 'helper.img'
    with helper.open('xb') as data:
        data.truncate(16 * 1024**2)
    run('mkfs.ext2', '-q', '-F', '-U', helper_uuid, '-d', files, helper)
    return helper


def ssh_options(known):
    return ['-o', 'StrictHostKeyChecking=yes', '-o', f'UserKnownHostsFile={known}',
            '-o', 'GlobalKnownHostsFile=/dev/null', '-o', 'ConnectTimeout=5',
            '-o', 'IdentitiesOnly=yes', '-o', 'ServerAliveInterval=5', '-o', 'ServerAliveCountMax=3']


def monitor(profile, secure, run_id, root_uuid, work, mode, space):
    args = ['ssh', '-T', *ssh_options(secure / 'known_hosts'), '-o', 'BatchMode=yes',
            '-o', f'HostKeyAlias={run_id}', '-p', str(PORT), '-i', str(secure / 'client'),
            'root@' + profile['address'], 'start']
    prefix = f'RBBUILD {run_id} '.encode()
    stages = {
        b'*** UPDATE Debian***': 'Updating the base operating system',
        b'*** PREPARING BITCOIN ***': 'Installing Bitcoin Core',
        b'* FATPACK activated': 'Installing Fatpack',
        b'# BUILD DONE - see above': 'Checking the native installation and preparing release',
    }
    with (work / 'guest.log').open('wb', buffering=0) as log, selectors.DefaultSelector() as selector:
        job = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, bufsize=0)
        try:
            selector.register(job.stdout, selectors.EVENT_READ)
            ready = planned = confirmed = False
            buffered = b''
            deadline = time.monotonic() + (12 if mode == 'fatpack' else 3) * 3600 + 120
            ready_deadline = time.monotonic() + 20
            next_heartbeat = 0
            while time.monotonic() < deadline:
                if selector.select(timeout=1):
                    block = os.read(job.stdout.fileno(), 65536)
                    if not block:
                        require(confirmed, 'Unexpected loss of SSH before the guest confirmed clean shutdown')
                        return 'release'
                    log.write(block)
                    buffered += block
                    while b'\n' in buffered:
                        line, buffered = buffered.split(b'\n', 1)
                        if not line.startswith(prefix):
                            message = stages.get(line.rstrip())
                            app = re.fullmatch(rb'\* Adding Code&Compile for WEBUI-APP: ([A-Z0-9 -]{1,32})', line.rstrip())
                            if message or app:
                                print(message or 'Installing Fatpack app ' + app[1].decode(), flush=True)
                            continue
                        event = line[len(prefix):].decode('ascii')
                        if event.startswith('READY '):
                            _, observed_root, boot_id = event.split()
                            require(not ready and observed_root == root_uuid and uuid.UUID(boot_id),
                                    'Unexpected Pi boot identity')
                            (work / 'boot-id').write_text(boot_id + '\n')
                            job.stdin.write(b'start\n')
                            ready = True
                        elif event == 'PROBE' and mode == 'abort':
                            return 'aborted'
                        elif event == 'SHUTDOWN-READY':
                            require(ready and not planned and mode != 'abort', 'Unexpected shutdown request')
                            deadline = min(deadline, time.monotonic() + 120)
                            job.stdin.write(b'shutdown\n')
                            planned = True
                        elif event == 'POWEROFF release':
                            require(planned and not confirmed, 'Unexpected shutdown confirmation')
                            confirmed = True
                        elif event.startswith('FAILED '):
                            raise RuntimeError(f'Build on the Pi failed: {event}')
                require(ready or time.monotonic() < ready_deadline, 'No authenticated guest readiness signal')
                if ready and not planned and time.monotonic() >= next_heartbeat:
                    space.check('guest')
                    job.stdin.write(b'heartbeat\n')
                    next_heartbeat = time.monotonic() + 5
            raise RuntimeError('Build or planned shutdown timed out')
        finally:
            job.stdin.close()
            if job.poll() is None:
                job.terminate()
                job.wait(timeout=10)


def confirm_and_clean(image, work, run_id, result):
    reclaimed = 0
    with partitions(image, readonly=True) as (boot_part, root_part):
        run('fsck.vfat', '-n', boot_part)
        run('e2fsck', '-fn', root_part)
        with mount(boot_part, work / 'boot', 'ro,nodev,nosuid,noexec') as boot_dir:
            require(regular_file_read(boot_dir, SHUTDOWN, 256).decode().strip() == f'{run_id} {result}',
                    'No matching guest shutdown record')
        retain_bootstrap_log(root_part, work)
    if result == 'release':
        with partitions(image, readonly=False) as (boot_part, root_part):
            with mount(root_part, work / 'root', 'rw,nodev,nosuid,noexec') as root:
                require(not os.path.lexists(root / 'PiShrink_zero_file'), 'Unexpected PiShrink scratch entry')
                unlink_regular(root, BOOTSTRAP_LINK, symlink=True)
                for name in (BOOTSTRAP, GUEST, BOOTSTRAP_LOG):
                    unlink_regular(root, name)
                # Deleted compiler outputs still occupy blocks in the USB backing
                # file. Trim only the cold guest root on its verified loop partition.
                require(output('findmnt', '-n', '-M', root, '-o', 'SOURCE') == str(root_part),
                        'Unexpected mount source before trimming the work image')
                if int(output('lsblk', '-bdno', 'DISC-MAX', root_part)) and shutil.which('fstrim'):
                    run('sync', '-f', root)
                    before = image.stat().st_blocks
                    run('fstrim', root)
                    reclaimed = max(0, before - image.stat().st_blocks) * 512
                    print(f'Reclaimed {reclaimed} bytes of free guest blocks on the PiKVM.', flush=True)
            with mount(boot_part, work / 'boot', 'rw,nodev,nosuid,noexec') as boot_dir:
                unlink_regular(boot_dir, SHUTDOWN)
                contents = regular_file_read(boot_dir, 'config.txt', 1024**2)
                require(contents.count(ISOLATION) == 1, 'Unexpected PCIe isolation override')
                overwrite_existing(boot_dir, 'config.txt', contents.replace(ISOLATION, b'', 1))
                command = regular_file_read(boot_dir, 'cmdline.txt', 65536)
                require(command.count(NVME_GUARD) == 1, 'Unexpected kernel NVMe module guard')
                overwrite_existing(boot_dir, 'cmdline.txt', command.replace(NVME_GUARD, b'', 1))
    return reclaimed


def retain_bootstrap_log(root_part, work):
    with mount(root_part, work / 'root', 'ro,noload,nodev,nosuid,noexec') as root:
        try:
            log = regular_file_read(root, BOOTSTRAP_LOG, 4 * 1024**2)
        except FileNotFoundError:
            return
        (work / 'bootstrap.log').write_bytes(log)


def audit(image, work, profile):
    with partitions(image, readonly=True) as (boot_part, root_part):
        run('fsck.vfat', '-n', boot_part)
        run('e2fsck', '-fn', root_part)
        with ExitStack() as mounts:
            root = mounts.enter_context(mount(root_part, work / 'root', 'ro,noload,nodev,nosuid,noexec'))
            boot_dir = mounts.enter_context(mount(boot_part, work / 'boot', 'ro,nodev,nosuid,noexec'))
            audit_mounts(TOOLS / 'check-native-release.sh', root, boot_dir, profile['commit'], profile['version'])
            config = regular_file_read(boot_dir, 'config.txt', 1024**2)
            require(b'# PiKVM build isolation' not in config, 'Retained PiKVM PCIe override')
            if profile['variant'] == 'fatpack':
                overlay = regular_file_read(boot_dir, 'overlays/waveshare35a.dtbo', 1024**2)
                require(re.search(rb'(?m)^dtoverlay=waveshare35a[:,\r\n]', config) and
                        overlay.startswith(bytes.fromhex('d00dfeed')), 'Expected Fatpack LCD overlay on bootfs')
            require(NVME_GUARD not in regular_file_read(boot_dir, 'cmdline.txt', 65536),
                    'Retained PiKVM kernel module guard')
            # Capture the final package versions from the frozen bytes for the signer.
            records = regular_file_read(root, 'var/lib/dpkg/status', 32 * 1024**2).split(b'\n\n')
            packages = {}
            for record in records:
                fields = dict(re.findall(rb'^(Package|Version|Architecture|Status): (.+)$', record, re.M))
                if fields.get(b'Status', b'').split()[1:] == [b'ok', b'installed']:
                    name = fields[b'Package'] + b':' + fields[b'Architecture']
                    packages[name.decode('ascii')] = fields[b'Version'].decode('ascii')
            require(packages, 'Frozen image has no installed package inventory')
            return packages


def validate_profile(path, variant):
    data = json.loads(path.read_text())
    for key, pattern in (
            ('owner', r'[A-Za-z0-9][A-Za-z0-9-]*'), ('branch', r'[A-Za-z0-9][A-Za-z0-9._/-]*'),
            ('commit', r'[0-9a-f]{40}'), ('blob', r'[0-9a-f]{40}'), ('version', r'[0-9][A-Za-z0-9.-]+'),
            ('base_sha256', r'[0-9a-f]{64}'), ('pishrink_sha256', r'[0-9a-f]{64}'),
            ('mac', r'([0-9a-f]{2}:){5}[0-9a-f]{2}')):
        require(re.fullmatch(pattern, data[key]), f'Invalid profile field: {key}')
    run('git', 'check-ref-format', f'refs/heads/{data["branch"]}')
    data['address'] = str(ipaddress.IPv4Address(data['address']))
    for key in ('base', 'return_image', 'pishrink', 'factory_password_file'):
        data[key] = Path(data[key]).resolve(strict=True)
    require(data['return_image'].is_relative_to(MSD) and not data['return_image'].is_relative_to(STATE),
            'Return image must be an existing medium outside the build directory')
    password_stat = data['factory_password_file'].stat()
    require(stat.S_ISREG(password_stat.st_mode) and password_stat.st_uid == 0 and
            password_stat.st_mode & 0o077 == 0, 'Factory test-password file must be root-only')
    data['target_bytes'] = int(data.get('target_bytes', 64_000_000_000))
    require(data['target_bytes'] >= 32_000_000_000 and data['target_bytes'] % 512 == 0,
            'Expected a target capacity of at least 32 GB in complete 512-byte sectors')
    data['variant'] = variant
    if variant == 'fatpack':
        data['fatpack_root_free_bytes'] = int(data.get('fatpack_root_free_bytes', 2 * GIB))
        require(0 < data['fatpack_root_free_bytes'] < data['target_bytes'],
                'Fatpack root free space must be positive and smaller than the target medium')
    default_size = 64_000_000_000 if variant == 'fatpack' else 24 * GIB
    data['working_bytes'] = int(data.get(variant + '_working_bytes', default_size))
    minimum = 60_000_000_000 if variant == 'fatpack' else data['base'].stat().st_size
    require(data['working_bytes'] >= max(minimum, data['base'].stat().st_size) and data['working_bytes'] % 512 == 0,
            'Working medium is too small for the selected variant')
    data['reserve_bytes'] = int(data.get('reserve_bytes', 8 * GIB))
    require(data['reserve_bytes'] > 0, 'reserve_bytes must be positive')
    return data


class Storage:
    def __init__(self, reserve):
        self.reserve = reserve
        self.trimmed = 0
        self.start = self.minimum = shutil.disk_usage(STATE).free

    def observe(self, free):
        self.minimum = min(self.minimum, free)

    def check(self, phase, needed=0):
        free = shutil.disk_usage(STATE).free
        self.observe(free)
        require(free >= self.reserve + needed,
                f'Insufficient space during {phase}: {free} bytes free, '
                f'{needed} needed plus {self.reserve} reserve. Check uncollected exports with list.')
        return free


def stock_ssh(profile, known, command):
    algorithm = known.read_text().split()[1]
    require(algorithm in ('ecdsa-sha2-nistp256', 'ssh-ed25519'), 'Unexpected pinned SSH key type')
    return output('timeout', '35', 'sshpass', '-f', profile['factory_password_file'], 'ssh', '-T',
                  *ssh_options(known), '-o', 'PreferredAuthentications=password',
                  '-o', 'HostKeyAlgorithms=' + algorithm, '-o', 'NumberOfPasswordPrompts=1',
                  'admin@' + profile['address'], command)


def boot_test(image, work, profile, secure, root_uuid, build_boot):
    # Seed only the ECDSA host key on this disposable copy. This authenticates
    # the factory login while RaspiBlitz creates its normal Ed25519 key on first boot.
    anchor = secure / 'stock-probe-ecdsa'
    run('ssh-keygen', '-q', '-t', 'ecdsa', '-b', '256', '-N', '', '-f', anchor)
    anchor_key = (secure / 'stock-probe-ecdsa.pub').read_text().split()[:2]
    known = secure / 'stock_anchor_hosts'
    known.write_text(f'{profile["address"]} {" ".join(anchor_key)}\n')
    timer = 'raspiblitz-test-poweroff.timer'
    with partitions(image, readonly=False) as (boot_part, root_part):
        with mount(root_part, work / 'root', 'rw,nodev,nosuid,noexec') as root:
            config = regular_file_read(root, 'etc/ssh/sshd_config', 1024**2)
            require(re.search(rb'(?mi)^\s*Include\s+/etc/ssh/sshd_config\.d/\*\.conf\s*$', config),
                    'Stock sshd configuration does not include its drop-in directory')
            # The native checkrepair helper clears ssh_host_* while regenerating
            # the stock keys. Keep the probe key outside that name pattern.
            create_regular(root, 'etc/ssh/raspiblitz-test-ecdsa', anchor.read_bytes())
            create_regular(root, 'etc/ssh/sshd_config.d/00-raspiblitz-test.conf',
                           b'HostKey /etc/ssh/raspiblitz-test-ecdsa\n'
                           b'HostKey /etc/ssh/ssh_host_ed25519_key\nHostKey /etc/ssh/ssh_host_rsa_key\n')
            create_regular(root, 'etc/systemd/system/' + timer,
                           b'[Unit]\nDescription=End the unattended first boot probe\n'
                           b'[Timer]\nOnBootSec=10min\nAccuracySec=1s\nUnit=poweroff.target\n')
            create_link(root, 'etc/systemd/system/timers.target.wants/' + timer, '../' + timer)
        with mount(boot_part, work / 'boot', 'rw,nodev,nosuid,noexec') as boot_dir:
            add_isolation(boot_dir)
    insert(0, image, writable=True)
    boot(profile['address'], 22, work)
    try:
        probe = verify_test(work, profile, secure, root_uuid, build_boot, known)
    finally:
        stock_ssh(profile, known, 'sudo -n systemctl poweroff')
    wait_off()
    eject(0, image)
    with partitions(image, readonly=True) as (boot_part, root_part):
        run('fsck.vfat', '-n', boot_part)
        run('e2fsck', '-fn', root_part)
        with mount(root_part, work / 'root', 'ro,noload,nodev,nosuid,noexec') as root:
            pub = regular_file_read(root, 'etc/ssh/ssh_host_ed25519_key.pub', 4096).decode().split()[:2]
            require(pub == (secure / 'stock_known_hosts').read_text().split()[1:],
                    'SSH host key did not match the key on the booted image')
    return probe


def fetch_http(address, path, max_bytes):
    request = subprocess.run(['curl', '--fail', '--silent', '--noproxy', '*', '--proto', '=http',
                              '--max-time', '5', '--max-filesize', str(max_bytes), f'http://{address}{path}'],
                             capture_output=True)
    return request.stdout if request.returncode == 0 else b''


def check_web_setup(profile, known):
    checksum = stock_ssh(profile, known, 'sha256sum /home/admin/assets/nginx/www_public/index.html').split()
    require(checksum and re.fullmatch(r'[0-9a-f]{64}', checksum[0]), 'No built WebUI index on the stock Fatpack')
    expected = checksum[0]
    # Native drive discovery either waits for DATA or offers setup on the USB disk itself.
    allowed = (('noHDD', 'boot', '>=1TB'), ('waitsetup', 'setup', 'Please start Setup'))
    # A cold nginx/API can take several attempts. SSH transport errors still end the probe.
    guest_status = ("curl -q --fail --silent --noproxy '*' --proto '=http' --max-time 5 "
                    "--max-filesize 65536 http://127.0.0.1/api/setup/status || true")
    end = time.monotonic() + 360
    while time.monotonic() < end:
        page = fetch_http(profile['address'], '/', 4 * 1024**2)
        if page and hashlib.sha256(page).hexdigest() == expected:
            try:
                lan = json.loads(fetch_http(profile['address'], '/api/setup/status', 65536))
                if isinstance(lan, dict) and (lan.get('state'), lan.get('setupPhase'), lan.get('message')) in allowed:
                    local = json.loads(stock_ssh(profile, known, guest_status))
                    if local == lan:
                        return {'index_sha256': expected, 'setup_state': lan['state'],
                                'setup_phase': lan['setupPhase'], 'setup_message': lan['message']}
            except (UnicodeError, ValueError):
                pass
        time.sleep(4)
    raise RuntimeError('Fatpack first boot requires the bundled WebUI and a matching noHDD/boot '
                       'or waitsetup/setup response through the LAN and the authenticated Pi')


def check_stock_disks(profile, known):
    # --all includes empty slots that lsblk normally omits from /sys/block.
    observed = stock_ssh(profile, known, 'set -e; dev=$(findmnt -nro SOURCE /); '
                         'lsblk -dnro PKNAME "$dev"; lsblk --all --nodeps --bytes --json -o KNAME,SIZE,RM,TRAN')
    root_disk, devices_json = observed.split('\n', 1)
    devices = json.loads(devices_json)['blockdevices']
    roots = [disk for disk in devices if disk['kname'] == root_disk]
    require(len(roots) == 1 and roots[0]['tran'] == 'usb' and int(roots[0]['size']) == profile['target_bytes'],
            'Stock boot root must be the USB disk of the declared target size')
    empty_slots = 0
    for disk in devices:
        name = disk['kname']
        if name == root_disk or re.fullmatch(r'(?:loop|ram|zram)\d+', name):
            continue
        # The ejected second gadget can still appear as an empty USB removable slot.
        require(disk['tran'] == 'usb' and disk['rm'] in (True, '1') and int(disk['size']) == 0,
                f'Unexpected stock-boot disk: {name}')
        empty_slots += 1
    require(empty_slots <= 1, 'Unexpected extra empty USB slots in stock boot')
    return f'{root_disk}, {profile["target_bytes"]} bytes. Block devices: {", ".join(d["kname"] for d in devices)}'


def verify_test(work, profile, secure, root_uuid, build_boot, anchor_hosts):
    address = profile['address']
    neighbors = json.loads(output('ip', '-j', 'neigh', 'show', 'to', address))
    require(any(n.get('lladdr') == profile['mac'] for n in neighbors), 'Pi MAC mismatch at stock boot')
    ed25519 = stock_ssh(profile, anchor_hosts,
                        'for i in $(seq 1 20); do sudo -n test -s /etc/ssh/ssh_host_ed25519_key.pub && break; '
                        'sleep 1; done; sudo -n cat /etc/ssh/ssh_host_ed25519_key.pub')
    host_key = ed25519.split()[:2]
    require(len(host_key) == 2 and host_key[0] == 'ssh-ed25519',
            'Unexpected stock SSH host key')
    require(host_key[1] not in (secure / 'known_hosts').read_text(), 'Stock image reused build host key')
    known = secure / 'stock_known_hosts'
    known.write_text(f'{address} {" ".join(host_key)}\n')
    denied = subprocess.run(['ssh', '-T', *ssh_options(known), '-o', 'BatchMode=yes',
                             '-o', 'PreferredAuthentications=publickey', '-i', str(secure / 'client'),
                             'root@' + address, 'true'], capture_output=True, text=True, timeout=20)
    require(denied.returncode == 255 and 'Permission denied' in denied.stderr,
            'Stock image did not reject the build key as expected')
    require(not listening(address, PORT), 'Temporary SSH port is still listening')
    observed = stock_ssh(profile, known, 'set -e; findmnt -no UUID /; cat /proc/sys/kernel/random/boot_id; '
                         'grep -m 1 "^codeVersion=" /home/admin/_version.info')
    values = observed.splitlines()
    require(len(values) == 3 and values[0] == root_uuid and uuid.UUID(values[1]) and values[1] != build_boot,
            'Stock boot started from the wrong root device or boot ID')
    require(f'codeVersion="{profile["version"]}"' in values, 'Stock boot reported the wrong version')
    require(not media(1), 'Build helper is still inserted during stock boot')
    disks = check_stock_disks(profile, known)
    web = check_web_setup(profile, known) if profile['variant'] == 'fatpack' else None
    boot_free = None
    if web:
        blocks, block_size = stock_ssh(profile, known, "stat -f -c '%a %S' /").split()
        boot_free = int(blocks) * int(block_size)
        require(boot_free >= profile['fatpack_root_free_bytes'],
                f'Booted Fatpack root has {boot_free} bytes for apps; '
                f'{profile["fatpack_root_free_bytes"]} bytes required')
    (work / 'test-boot.log').write_text(observed + f'\nBoot disk: {disks}\n'
                                        + (f'WebUI and API: {json.dumps(web)}\n'
                                           f'Root available to apps: {boot_free} bytes\n' if web else '')
                                        + 'Probe SSH key rejected and temporary port closed.\n')
    return web, boot_free


def status(directory, value):
    staged = directory / '.status.tmp'
    staged.write_text(value + '\n')
    staged.replace(directory / 'status')


def purge_finished(directory):
    value = (directory / 'status').read_text().strip()
    if value not in ('preparing', 'media-reserved', 'failed-detached', 'abort-tested', 'exported', 'downloaded'):
        return
    for path in LUNS.glob('mass_storage.*/lun.*/file'):
        attached = path.read_text().strip()
        require(not attached or not Path(attached).is_relative_to(directory), 'Run is still attached')
    images = list(directory.glob('*.img'))
    for image in images:
        require(not output('losetup', '-j', image), f'Loop device still owns {image.name}')
    for image in images:
        image.unlink()
    for stage in directory.glob('.rb-pack.*'):
        if re.fullmatch(r'\.rb-pack\.[A-Za-z0-9]{8}', stage.name):
            require(stage.is_dir() and not stage.is_symlink(), 'Unexpected packaging directory')
            shutil.rmtree(stage)
    for folder in ('root', 'boot'):
        path = directory / folder
        if path.exists():
            path.rmdir()
    if value in ('preparing', 'media-reserved', 'failed-detached') and (directory / 'export').is_dir():
        # rename(export) is the publication point. A crash can precede the status write.
        report = json.loads((directory / 'export/build.json').read_text())
        name = report['archive']
        require(report['run'] == directory.name and re.fullmatch(r'raspiblitz-(?:min|fat)-[\w.-]+\.img\.gz', name)
                and sha256(directory / 'export' / name) == report['archive_sha256'],
                'Interrupted export publication needs inspection')
        status(directory, 'exported')
        return
    if value in ('preparing', 'media-reserved', 'failed-detached'):
        if (directory / 'pending').is_dir():
            shutil.rmtree(directory / 'pending')
        status(directory, 'failed-detached')
    if value == 'downloaded' and (directory / 'export').is_dir():
        for item in (directory / 'export').iterdir():
            require(item.is_file() and not item.is_symlink(), 'Unexpected item in export directory')
            item.unlink()
        (directory / 'export').rmdir()


def work_dirs():
    return sorted(path for path in STATE.iterdir() if re.fullmatch(ID_PATTERN, path.name)
                  and path.is_dir() and not path.is_symlink() and (path / 'status').is_file())


def restore(profile, work):
    require(not media(0) and not media(1), 'Cannot restore the Pi with a build medium still inserted')
    host_key = []
    try:
        with partitions(profile['return_image'], readonly=True) as (_, root_part):
            with mount(root_part, work / 'root', 'ro,noload,nodev,nosuid,noexec') as root:
                host_key = regular_file_read(root, 'etc/ssh/ssh_host_ed25519_key.pub', 4096).decode().split()[:2]
    except (RuntimeError, ValueError, subprocess.SubprocessError, OSError) as exc:
        print(f'Return-system host key could not be read: {exc}', flush=True)
    require(not output('losetup', '-j', profile['return_image']), 'Return medium is still mounted on the PiKVM')
    insert(0, profile['return_image'], writable=True)
    boot(profile['address'], 22, work)
    require(len(host_key) == 2 and host_key[0] == 'ssh-ed25519',
            'Original medium restarted, but its SSH identity could not be confirmed')
    with tempfile.TemporaryDirectory(dir='/run') as temp:
        known = Path(temp) / 'known_hosts'
        known.write_text(f'{profile["address"]} {" ".join(host_key)}\n')
        probe = subprocess.run(['ssh', '-T', *ssh_options(known), '-o', 'BatchMode=yes',
                                '-o', 'HostKeyAlgorithms=ssh-ed25519', '-o', 'PreferredAuthentications=none',
                                'admin@' + profile['address'], 'true'],
                               stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=20)
        require((probe.returncode == 255 and 'Permission denied' in probe.stderr) or probe.returncode == 0,
                'Could not authenticate the return-system SSH host')
    print('Previous system medium booted and its SSH host identity was verified.', flush=True)


def export_release(work, profile, archive, raw_bytes, raw_hash, archive_hash, space, packages, web,
                   cold_free, boot_free):
    run_id = work.name
    report = dict(run=run_id, commit=profile['commit'], blob=profile['blob'],
                  owner=profile['owner'], branch=profile['branch'], version=profile['version'],
                  base_sha256=profile['base_sha256'], pishrink_sha256=profile['pishrink_sha256'],
                  target_bytes=profile['target_bytes'], raw_bytes=raw_bytes, raw_sha256=raw_hash,
                  archive=archive.name, archive_bytes=archive.stat().st_size,
                  archive_sha256=archive_hash, test_boot_nvme_isolated=True, variant=profile['variant'],
                  working_bytes=profile['working_bytes'], target_spare_bytes=profile['target_bytes'] - raw_bytes,
                  storage_start_free_bytes=space.start, storage_min_sampled_free_bytes=space.minimum,
                  storage_reserve_bytes=space.reserve, storage_trim_reclaimed_bytes=space.trimmed,
                  debian_packages=packages)
    if profile['variant'] == 'fatpack':
        require(web, 'Fatpack LAN setup probe is missing')
        report.update(fatpack_root_free_bytes=profile['fatpack_root_free_bytes'],
                      fatpack_root_cold_available_bytes=cold_free, fatpack_root_boot_available_bytes=boot_free)
        report['fatpack_web_probe'] = web
        components = {}
        with (work / 'guest.log').open('rb') as log:
            for line in log:
                match = re.fullmatch(rb'FATPACK component (blitz_api|blitz_web) (\S+) ([a-f0-9]{40})\s*', line)
                if match:
                    name, branch, commit = (part.decode('ascii') for part in match.groups())
                    components[name] = {'branch': branch, 'commit': commit}
        require(set(components) == {'blitz_api', 'blitz_web'}, 'Missing Fatpack source revisions')
        report['fatpack_components'] = components
    pending = archive.parent
    (pending / 'build.json').write_text(json.dumps(report, indent=2) + '\n')
    restore(profile, work)
    pending.rename(work / 'export')
    status(work, 'exported')
    purge_finished(work)
    print(f'{archive.name} SHA-256 {archive_hash} ({raw_bytes} bytes uncompressed)', flush=True)
    print(f'Export ready: {work / "export"}', flush=True)
    print(f'Windows: ./tools/pikvm-minimal/Get-Release.ps1 -RunId {run_id}', flush=True)


def controller(profile, mode, start_stopped, requested_id):
    require(slot(1).is_dir() and not media(1), 'Enable and empty the second PiKVM USB drive first')
    for path in work_dirs():
        purge_finished(path)
    space = Storage(profile['reserve_bytes'])
    print(f'PiKVM storage at start: {space.start} bytes free, {space.reserve} reserved.', flush=True)
    space.check('preparation', max(profile['base'].stat().st_size, (32 if mode == 'fatpack' else 10) * GIB))
    current = media(0)
    require(current in ('', str(profile['return_image'])), 'Unrecognized existing system medium')
    if not start_stopped:
        require(current and udc_state() == 'configured' and listening(profile['address'], 22),
                'Expected the known running system, or start with --pi-stopped')
    else:
        require(udc_state() == 'not-attached', '--pi-stopped requires a detached USB host')

    started = datetime.now(timezone.utc)
    run_id = requested_id or started.strftime('%Y%m%dT%H%M%SZ-') + uuid.uuid4().hex[:8]
    require(re.fullmatch(ID_PATTERN, run_id), 'Invalid run ID')
    work = STATE / run_id
    work.mkdir(mode=0o700)
    status(work, 'preparing')
    print(f'Build run {run_id} at {work}', flush=True)
    slug = 'fat' if profile['variant'] == 'fatpack' else 'min'
    image = work / f'raspiblitz-{slug}-v{profile["version"]}-{started:%Y-%m-%d}.img'
    helper_uuid = str(uuid.uuid4())
    with tempfile.TemporaryDirectory(prefix='raspiblitz-image-', dir='/run') as temp:
        secure = Path(temp)
        helper = None
        lab_live = False
        try:
            shrinker = secure / 'pishrink.sh'
            shutil.copyfile(profile['pishrink'], shrinker)
            require(sha256(shrinker) == profile['pishrink_sha256'], 'Unexpected PiShrink revision')
            root_uuid = prepare(image, work, profile, helper_uuid)
            helper = make_helper(secure, profile, run_id, root_uuid, helper_uuid, mode)
            if not start_stopped:
                click('power')
            wait_off()
            eject(0, profile['return_image'])
            status(work, 'media-reserved')
            lab_live = True
            insert(0, image, writable=True)
            insert(1, helper, writable=False)
            print('Starting Pi 5 with build image and read-only helper.', flush=True)
            boot(profile['address'], PORT, work)
            result = monitor(profile, secure, run_id, root_uuid, work, mode, space)
            wait_off()
            eject(1, helper)
            eject(0, image)
            lab_live = False
            space.trimmed = confirm_and_clean(image, work, run_id, result)
            if result == 'aborted':
                status(work, 'abort-tested')
                purge_finished(work)
                restore(profile, work)
                print('Abort probe passed: local timer powered off the guest and the cold media checked clean.', flush=True)
                return

            print(f'Packaging the clean and detached {profile["variant"]} image.', flush=True)
            space.check('shrink')
            run('bash', shrinker, '-n', '-s', image)
            require(image.stat().st_size <= profile['target_bytes'], 'RAW exceeds the target capacity')
            cold_free = None
            if profile['variant'] == 'fatpack':
                cold_free = ensure_fatpack_root_space(image, work, profile['target_bytes'],
                                                      profile['fatpack_root_free_bytes'])
                print(f'Cold Fatpack root available to apps: {cold_free} bytes', flush=True)
            packages = audit(image, work, profile)
            pending = work / 'pending'
            test_image = work / 'test-boot.img'
            raw_bytes, raw_hash, archive_hash = package_and_unpack(
                image, pending, test_image, profile['target_bytes'], space.reserve, space.observe)
            space.check('test boot')
            lab_live = True
            web, boot_free = boot_test(test_image, work, profile, secure, root_uuid,
                                       (work / 'boot-id').read_text().strip())
            lab_live = False
            export_release(work, profile, pending / (image.name + '.gz'), raw_bytes, raw_hash, archive_hash,
                           space, packages, web, cold_free, boot_free)
        except BaseException:
            print(f'Lowest observed free space: {space.minimum} bytes (reserve {space.reserve}).', flush=True)
            if lab_live:
                # The guest's local timer handles an unexpected SSH exit.
                # Wait for the independent USB signal before touching either drive.
                try:
                    wait_off(timeout=720 if media(0) == str(work / 'test-boot.img') else 115)
                    if helper is not None:
                        eject(1, helper)
                    active = media(0)
                    for candidate in (image, work / 'test-boot.img'):
                        if active == str(candidate):
                            eject(0, candidate)
                    require(not media(0), 'Unexpected medium during failure cleanup')
                    lab_live = False
                    if active == str(image):
                        try:
                            with partitions(image, readonly=True) as (_, root_part):
                                retain_bootstrap_log(root_part, work)
                        except (RuntimeError, ValueError, subprocess.SubprocessError, OSError) as exc:
                            print(f'Guest diagnostic log unavailable: {exc}', flush=True)
                except (RuntimeError, ValueError, subprocess.SubprocessError, OSError) as exc:
                    print(f'Media recovery needs attention: {exc}', flush=True)
                    # Preserve the temporary image while its USB drive is still configured.
                    if helper is not None and media(1) == str(helper):
                        secure.rename(Path('/run') / f'raspiblitz-held-{run_id}')
            if not lab_live:
                if not media(0) and not media(1):
                    try:
                        restore(profile, work)
                    except (RuntimeError, ValueError, subprocess.SubprocessError, OSError) as exc:
                        print(f'Previous system could not be restarted: {exc}', flush=True)
                if (work / 'status').read_text().strip() != 'exported':
                    status(work, 'failed-detached')
                    purge_finished(work)
            raise


def receipt(run_id, digest):
    require(re.fullmatch(ID_PATTERN, run_id) and re.fullmatch(r'[0-9a-f]{64}', digest), 'Invalid receipt')
    directory = STATE / run_id
    require(directory.is_dir() and not directory.is_symlink(), 'Unknown run')
    previous = (directory / 'status').read_text().strip()
    require(previous in ('exported', 'downloaded'), 'Run has no verified export')
    checksum = directory / 'downloaded.sha256'
    if previous == 'downloaded':
        require(checksum.read_text().strip() == digest, 'Receipt does not match')
    else:
        report = json.loads((directory / 'export/build.json').read_text())
        require(report['archive_sha256'] == digest, 'Receipt digest does not match the archived build')
        checksum.write_text(digest + '\n')
        status(directory, 'downloaded')
    purge_finished(directory)
    print(f'Confirmed and cleaned {run_id}. Free bytes: {shutil.disk_usage(STATE).free}', flush=True)


def start_unit(args):
    run_id = args.run_id or datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-') + uuid.uuid4().hex[:8]
    require(re.fullmatch(ID_PATTERN, run_id), 'Invalid run ID')
    unit = 'rb-release-' + run_id
    print(f'Run {run_id}. Follow with: journalctl -fu {unit}', flush=True)
    print(f'Windows pickup: ./tools/pikvm-minimal/Get-Release.ps1 -RunId {run_id}', flush=True)
    run('systemd-run', '--collect', '--service-type=exec', '--unit=' + unit,
        *(['--wait'] if args.wait else []), sys.executable, '-u', Path(__file__).resolve(),
        'build', args.profile.resolve(), '--variant', args.variant, '--run-id', run_id,
        *(['--pi-stopped'] if args.pi_stopped else []))


def main():
    import fcntl

    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('start', 'build', 'abort-probe'):
        job = commands.add_parser(name)
        job.add_argument('profile', type=Path, nargs='?', default=DEFAULT_PROFILE)
        if name in ('start', 'build'):
            job.add_argument('--variant', choices=('minimal', 'fatpack'), default='minimal')
        if name == 'start':
            job.add_argument('--wait', action='store_true')
        job.add_argument('--run-id')
        job.add_argument('--pi-stopped', action='store_true')
    commands.add_parser('list')
    ack = commands.add_parser('ack')
    ack.add_argument('run_id')
    ack.add_argument('sha256')
    args = parser.parse_args()
    require(os.geteuid() == 0 and os.path.ismount(MSD), 'Run as root on the PiKVM with its media store mounted')
    os.umask(0o077)
    if args.command == 'start':
        start_unit(args)
        return
    run('kvmd-helper-otgmsd-remount', 'rw')
    STATE.mkdir(mode=0o700, exist_ok=True)
    require(not STATE.is_symlink() and STATE.stat().st_uid == 0 and
            STATE.stat().st_mode & 0o077 == 0, 'Build directory must be root-only')
    with (STATE / '.lock').open('a') as lock:
        if args.command == 'list':
            for path in work_dirs():
                print(path.name, (path / 'status').read_text().strip())
        else:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                parser.exit(1, 'Another PiKVM build or collection is running.\n')
            if args.command == 'ack':
                receipt(args.run_id, args.sha256)
            else:
                variant = getattr(args, 'variant', 'minimal')
                mode = 'abort' if args.command == 'abort-probe' else ('fatpack' if variant == 'fatpack' else 'build')
                controller(validate_profile(args.profile, variant), mode, args.pi_stopped, args.run_id)


if __name__ == '__main__':
    main()
