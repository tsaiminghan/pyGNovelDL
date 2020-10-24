from ctypes import windll
import ctypes
from shutil import copyfile
import os
import string

# reference
# https://programtalk.com/vs2/python/13515/Cura/plugins/RemovableDriveOutputDevice/WindowsRemovableDrivePlugin.py/
# https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getvolumeinformationa

DRIVE_UNKNOWN = 0  # The drive type cannot be determined.
DRIVE_NO_ROOT_DIR = 1  # The root path is invalid; for example, there is no volume mounted at the specified path.
DRIVE_REMOVABLE = 2  # The drive has removable media; for example, a floppy drive, thumb drive, or flash card reader.
DRIVE_FIXED = 3  # The drive has fixed media; for example, a hard disk drive or flash drive.
DRIVE_REMOTE = 4  # The drive is a remote (network) drive.
DRIVE_CDROM = 5  # The drive is a CD-ROM drive.
DRIVE_RAMDISK = 6  # The drive is a RAM disk.


class WinDevice(object):

    def __init__(self):
        self.volume_info = []
        for drive, drive_type in self.get_drives():
            volume_name = self.get_volume_name(drive)
            self.volume_info.append((volume_name, drive, drive_type))

    def search(self, volume_name, drive_type):
        for _volume_name, drive, _drive_type in self.volume_info:
            if volume_name == _volume_name and drive_type == _drive_type:
                return drive

    @staticmethod
    def get_drives():
        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drive = letter + ':\\'
                drive_type = windll.kernel32.GetDriveTypeA(drive.encode("ascii"))
                drives.append((drive, drive_type))
            bitmask >>= 1
        return drives

    @staticmethod
    def get_volume_name(drive):
        kernel32 = ctypes.windll.kernel32
        volumeNameBuffer = ctypes.create_unicode_buffer(1024)
        fileSystemNameBuffer = ctypes.create_unicode_buffer(1024)
        serial_number = None
        max_component_length = None
        file_system_flags = None

        rc = kernel32.GetVolumeInformationW(
            ctypes.c_wchar_p(drive),
            volumeNameBuffer,
            ctypes.sizeof(volumeNameBuffer),
            serial_number,
            max_component_length,
            file_system_flags,
            fileSystemNameBuffer,
            ctypes.sizeof(fileSystemNameBuffer)
        )
        return volumeNameBuffer.value if rc else ''


class Kindle(WinDevice):

    def __init__(self):
        super().__init__()
        self.drive = self.search('Kindle', DRIVE_REMOVABLE)

    def exist(self):
        return self.drive is not None

    def push(self, src):
        if self.drive:
            filename = os.path.basename(src)
            target = os.path.join(self.drive, 'documents', filename)
            return copyfile(src, target)
