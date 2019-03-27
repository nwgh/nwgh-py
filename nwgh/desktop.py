import shutil
import subprocess
import sys


class MissingUtilityException(Exception):
    pass


def notify(msg, title='Notification', group='nwgh-py'):
    """Use the OS notification service to show a notification to the user.

    Args:
        msg: <string> message to put in notification
        title: <string, optional> title of notification
        group: <string, optional> where to group notification (OS X only)
    """
    if sys.platform.startswith('darwin'):
        notifier = shutil.which('terminal-notifier')
        if not notifier:
            raise MissingUtilityException(
                'Install terminal-notifier to get notifications')

        subprocess.call([notifier,
                         '-title', title,
                         '-group', group,
                         '-message', msg])
    elif sys.platform.startswith('win'):
        from ctypes import Structure, windll, POINTER, sizeof
        from ctypes.wintypes import DWORD, HANDLE, WINFUNCTYPE, BOOL, UINT
        class FLASHWINDOW(Structure):
            _fields_ = [("cbSize", UINT),
                        ("hwnd", HANDLE),
                        ("dwFlags", DWORD),
                        ("uCount", UINT),
                        ("dwTimeout", DWORD)]
        FlashWindowExProto = WINFUNCTYPE(BOOL, POINTER(FLASHWINDOW))
        FlashWindowEx = FlashWindowExProto(("FlashWindowEX", windll.user32))
        FLASHW_CAPTION = 0x01
        FLASHW_TRAY = 0x02
        FLASHW_TIMERNOFG = 0x0C
        console = windll.kernel32.GetConsoleWindow()
        if not console:
            raise MissingUtilityException('Could not find console window')

        params = FLASHWINDOW(sizeof(FLASHWINDOW),
                             console,
                             FLASHW_CAPTION | FLASHW_TRAY | FLASHW_TIMERNOFG,
                             3, 0)
        FlashWindowEx(params)
    else: # linux
        notifier = shutil.which('notify-send')
        if not notifier:
            raise MissingUtilityException(
                'Install notify-send to get notifications')

        subprocess.call([notifier, '--app-name=%s' % (title,), title, msg])
