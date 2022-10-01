import io
import logging
import os
import threading

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from powersaver.powersaver import PowerSaver
from datetime import datetime

LOGGER = logging.getLogger()


class DbusSleepHandler():

    def __init__(self, powersaver: PowerSaver) -> None:

        self._fd: io.TextIOWrapper = None
        DBusGMainLoop(set_as_default=True)
        self._bus = dbus.SystemBus()

        def _prepareForSleep(prepareForSleep: 'dbus.Boolean') -> None:

            if bool(prepareForSleep):
                LOGGER.info("received prepareForSleep event -> prepare sleep")
                upcoming_event = powersaver.get_upcoming_event(
                    datetime.today())

                powersaver.reset_wakealarm()
                powersaver.set_wakealarm(upcoming_event)
                powersaver.perform_pre_actions(upcoming_event)
                self._releaseLock()

            else:
                LOGGER.info("received prepareForSleep event -> after wakeup")
                self._aquireLock()
                powersaver.perform_post_actions()

        self._bus.add_signal_receiver(
            _prepareForSleep,
            'PrepareForSleep',
            'org.freedesktop.login1.Manager',
            'org.freedesktop.login1'
        )

        loop = GLib.MainLoop()
        t = threading.Thread(target=loop.run)
        t.start()

        self._aquireLock()

        LOGGER.info("initialized")

    def _aquireLock(self) -> None:

        obj = self._bus.get_object(
            "org.freedesktop.login1", "/org/freedesktop/login1")
        inhibit = obj.get_dbus_method(
            "Inhibit", "org.freedesktop.login1.Manager")
        fd = inhibit(dbus.String("sleep"), dbus.String("homeserver-power-server"),
                     dbus.String("perform pre-actions"), dbus.String("delay"))
        self._fd = os.fdopen(fd.take())

        LOGGER.debug("lock aquired")

    def _releaseLock(self) -> None:

        try:
            if self._fd:
                self._fd.close()

            LOGGER.debug("lock released")

        except:
            pass
