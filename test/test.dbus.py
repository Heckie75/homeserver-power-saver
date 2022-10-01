import io
import os
import threading
import time

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib


class DbusPrepareForSleepHandler():

    def __init__(self) -> None:

        self._fd: io.TextIOWrapper = None
        DBusGMainLoop(set_as_default=True)
        self._bus = dbus.SystemBus()

    def aquireLock(self) -> None:

        obj = self._bus.get_object(
            "org.freedesktop.login1", "/org/freedesktop/login1")
        inhibit = obj.get_dbus_method(
            "Inhibit", "org.freedesktop.login1.Manager")
        fd = inhibit(dbus.String("sleep"), dbus.String("who"),
                     dbus.String("why"), dbus.String("delay"))
        self._fd = os.fdopen(fd.take())

    def releaseLock(self) -> None:

        try:
            if self._fd:
                self._fd.close()

        except:
            pass

    def handleSleep(self):

        def _prepareForSleep(prepareForSleep: 'dbus.Boolean') -> None:

            if bool(prepareForSleep):
                # check occupation
                # if occupied
                #   - don't release lock
                # else if not occupied
                #   - calculate when to wake up and set rtc
                #   - perform pre-actions
                #   - release lock
                print("prepare for sleep 1")
                time.sleep(10)
                self.releaseLock()
                print("prepare for sleep 2")

            else:
                print("prepare after sleep 1")
                self.aquireLock()
                # perform wakeup actions
                time.sleep(10)
                print("prepare after sleep 2")

        self._bus.add_signal_receiver(
            _prepareForSleep,
            'PrepareForSleep',
            'org.freedesktop.login1.Manager',
            'org.freedesktop.login1'
        )

        loop = GLib.MainLoop()
        t = threading.Thread(target=loop.run)
        t.start()

if __name__ == "__main__":

    handler = DbusPrepareForSleepHandler()
    handler.handleSleep()
    # handler.aquireLock()
    pass