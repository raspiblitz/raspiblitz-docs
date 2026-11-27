"""Package a detached Pi image and restore its archive onto a sparse test medium."""

from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import os
from pathlib import Path
import re
import secrets
import shutil
import stat
import subprocess


CHUNK = 1024 * 1024
SPARSE_BLOCK = 64 * 1024
ZERO_BLOCK = bytes(SPARSE_BLOCK)
GADGETS = Path('/sys/kernel/config/usb_gadget')


def _detached(image):
    loops = subprocess.check_output(['losetup', '-j', str(image)], text=True)
    if loops.strip():
        raise RuntimeError(f'A loop device is using {image}')
    for lun in GADGETS.glob('*/functions/mass_storage.*/lun.*/file'):
        attached = lun.read_text().strip()
        if attached and image.samefile(attached):
            raise RuntimeError(f'A USB drive is using {image}')


def _feed_raw(raw, sink):
    digest = hashlib.sha256()
    with sink:
        while block := raw.read(CHUNK):
            sink.write(block)
            digest.update(block)
    return digest.hexdigest()


def _compress(image, archive, check_space):
    pigz = shutil.which('pigz')
    command = [pigz, '-p', '2'] if pigz else ['gzip']
    with image.open('rb') as raw, archive.open('xb') as packed:
        before = os.fstat(raw.fileno())
        # Ignore local compressor defaults so name, timestamp, and options are fixed.
        env = os.environ.copy()
        for name in ('GZIP', 'PIGZ'):
            env.pop(name, None)
        with (subprocess.Popen([*command, '-n', '-6', '-c'], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, env=env) as compressor,
              ThreadPoolExecutor(max_workers=1) as worker):
            try:
                feeder = worker.submit(_feed_raw, raw, compressor.stdin)
                while block := compressor.stdout.read(CHUNK):
                    check_space(len(block))
                    packed.write(block)
                code = compressor.wait()
                if code:
                    raise RuntimeError(f'Image compression failed with exit status {code}')
                digest = feeder.result()
            finally:
                # Release any blocked pipe writer before joining the input worker.
                if compressor.poll() is None:
                    compressor.kill()
        packed.flush()
        os.fsync(packed.fileno())
        after = os.fstat(raw.fileno())
        if (not os.path.samestat(after, image.stat(follow_symlinks=False)) or before.st_size != after.st_size
                or before.st_mtime_ns != after.st_mtime_ns or before.st_ctime_ns != after.st_ctime_ns):
            raise RuntimeError('The cold RAW image changed while it was being packaged')
        return digest


class _ArchiveReader:
    """Hash exactly the compressed bytes read during the verification pass."""

    def __init__(self, source):
        self.source = source
        self.digest = hashlib.sha256()

    def read(self, size=-1):
        block = self.source.read(size)
        self.digest.update(block)
        return block


def _unpack(archive, data, raw_bytes, expected, target_bytes, check_space):
    digest = hashlib.sha256()
    total = 0
    with archive.open('rb') as source:
        reader = _ArchiveReader(source)
        with gzip.GzipFile(fileobj=reader, mode='rb') as packed:
            while block := packed.read(CHUNK):
                total += len(block)
                if total > raw_bytes:
                    raise RuntimeError('Archive expands beyond the original RAW size')
                digest.update(block)
                if ZERO_BLOCK not in block:
                    check_space(len(block))
                    data.write(block)
                    continue
                # Keep zero-filled regions as holes, including inside mixed chunks.
                for offset in range(0, len(block), SPARSE_BLOCK):
                    part = block[offset:offset + SPARSE_BLOCK]
                    if part == ZERO_BLOCK[:len(part)]:
                        data.seek(len(part), os.SEEK_CUR)
                    else:
                        check_space(len(part))
                        data.write(part)
    if total != raw_bytes or digest.hexdigest() != expected:
        raise RuntimeError('Restored archive does not match the frozen RAW image')
    data.truncate(target_bytes)
    data.flush()
    os.fsync(data.fileno())
    return reader.digest.hexdigest()


def package_and_unpack(image: Path, pending: Path, test_image: Path,
                       target_bytes: int, reserve_bytes: int, observe_free=None) -> tuple[int, str, str]:
    """Consume the cold RAW, producing a verified package and a target-sized test copy."""
    if (not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9._-]*\.img', image.name)
            or not stat.S_ISREG(image.lstat().st_mode)):
        raise ValueError('Expected a regular .img input')
    if (image.parent != pending.parent or image.parent != test_image.parent
            or len({image, pending, test_image}) != 3
            or os.path.lexists(pending) or os.path.lexists(test_image)):
        raise ValueError('Use distinct new package and test paths in the run directory')
    raw_bytes = image.stat().st_size
    if not 0 < raw_bytes <= target_bytes or reserve_bytes < 0:
        raise ValueError('Invalid RAW size, target capacity, or space reserve')

    def check_space(additional=0):
        free = shutil.disk_usage(image.parent).free
        if observe_free is not None:
            observe_free(free)
        if free < reserve_bytes + additional:
            raise RuntimeError(f'Packaging needs {additional} bytes plus {reserve_bytes} bytes '
                               f'of free reserve. Available: {free} bytes')

    _detached(image)
    check_space()
    stage = pending.parent / ('.rb-pack.' + secrets.token_hex(4))
    stage.mkdir(mode=0o700)
    archive = stage / (image.name + '.gz')
    test_owned = False
    try:
        raw_hash = _compress(image, archive, check_space)
        check_space()
        _detached(image)
        image.unlink()
        with test_image.open('xb') as data:
            test_owned = True
            archive_hash = _unpack(archive, data, raw_bytes, raw_hash, target_bytes, check_space)
        check_space(8192)
        for name, digest in ((image.name, raw_hash), (archive.name, archive_hash)):
            with (stage / (name + '.sha256')).open('x', encoding='ascii') as sidecar:
                sidecar.write(f'{digest}  {name}\n')
                sidecar.flush()
                os.fsync(sidecar.fileno())
        stage.rename(pending)
        return raw_bytes, raw_hash, archive_hash
    except BaseException:
        if test_owned:
            test_image.unlink(missing_ok=True)
        shutil.rmtree(stage)
        raise
