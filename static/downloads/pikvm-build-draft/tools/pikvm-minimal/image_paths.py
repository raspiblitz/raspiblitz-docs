"""Operate on expected file types inside a cold, exclusively mounted guest image."""

from contextlib import contextmanager
import os
from pathlib import Path
import stat


@contextmanager
def _parent(root, relative):
    path = Path(relative)
    if path.is_absolute() or not path.parts or '..' in path.parts:
        raise ValueError(f'Expected an image-relative file path: {relative}')
    flags = os.O_DIRECTORY | os.O_NOFOLLOW | os.O_RDONLY
    directory = os.open(root, flags)
    try:
        device = os.fstat(directory).st_dev
        for name in path.parts[:-1]:
            child = os.open(name, flags, dir_fd=directory)
            os.close(directory)
            directory = child
            if os.fstat(directory).st_dev != device:
                raise ValueError(f'Unexpected mount beneath image root: {relative}')
        yield directory, path.name, device
    finally:
        os.close(directory)


def _check_entry(info, device, relative, symlink=False):
    expected = stat.S_ISLNK if symlink else stat.S_ISREG
    if info.st_dev != device or info.st_nlink != 1 or not expected(info.st_mode):
        raise ValueError(f'Unexpected file type, link count or device: {relative}')


@contextmanager
def _regular(root, relative, mode):
    with _parent(root, relative) as (directory, name, device):
        # Linux O_PATH pins the inode without opening a potential device or FIFO.
        inode = os.open(name, os.O_PATH | os.O_NOFOLLOW, dir_fd=directory)
        try:
            _check_entry(os.fstat(inode), device, relative)
            # Reopen the checked inode itself through the controller's procfs.
            # No component of the guest-supplied path is looked up a second time.
            with open(f'/proc/self/fd/{inode}', mode) as stream:
                yield stream
        finally:
            os.close(inode)


def regular_file_read(root, relative, max_bytes) -> bytes:
    """Read a regular file in full or fail before accepting an oversized file."""
    if max_bytes < 0:
        raise ValueError('Expected a nonnegative size limit')
    with _regular(root, relative, 'rb') as source:
        if os.fstat(source.fileno()).st_size > max_bytes:
            raise ValueError(f'Image file exceeds {max_bytes} bytes: {relative}')
        data = source.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise ValueError(f'Image file exceeds {max_bytes} bytes: {relative}')
        return data


def unlink_regular(root, relative, *, symlink=False):
    """Unlink the expected entry. symlink=True requires a symlink and never follows it."""
    with _parent(root, relative) as (directory, name, device):
        info = os.stat(name, dir_fd=directory, follow_symlinks=False)
        _check_entry(info, device, relative, symlink=symlink)
        os.unlink(name, dir_fd=directory)


def overwrite_existing(root, relative, data: bytes):
    """Replace the contents of an existing single-link regular file."""
    with _regular(root, relative, 'r+b') as dest:
        dest.write(data)
        dest.truncate()


def create_regular(root, relative, data: bytes, mode=0o600):
    """Create a new file with the given mode subject to umask, or preserve an existing entry."""
    if not 0 <= mode <= 0o777:
        raise ValueError('Expected permission bits without special mode bits')
    with _parent(root, relative) as (directory, name, device):
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW
        handle = os.open(name, flags, mode, dir_fd=directory)
        try:
            with os.fdopen(handle, 'wb') as dest:
                _check_entry(os.fstat(handle), device, relative)
                dest.write(data)
        except BaseException:
            os.unlink(name, dir_fd=directory)
            raise


def create_link(root, relative, target):
    """Install a controller-owned enablement symlink beneath the cold mount."""
    with _parent(root, relative) as (directory, name, _):
        os.symlink(target, name, dir_fd=directory)
