#!/usr/bin/python3
import argparse
import json
import logging
import os
import signal
import sys
import time
from datetime import datetime, timedelta

from utils.datetimeutils import format_datetime
from utils.logger import add_log_handler, init_logging
from powersaver.powersaver import PowerSaver

from utils.dbushandler import DbusSleepHandler

try:
    import daemon
    import daemon.pidfile
except ImportError:
    daemon = None

VERSION = "0.1.0 (2022-12-30)"

PID_FILE = "/tmp/homeserver-power-saver.pid"

LOGGER = logging.getLogger()


def start(settings):

    def _shutdown(signum, frame):

        LOGGER.info("Signal %i received. Going to shutdown homeserver-power-saver" % signum)
        sys.exit(0)

    signal_map = {
        signal.SIGTERM: _shutdown,
        signal.SIGTSTP: _shutdown
    }

    with daemon.DaemonContext(pidfile=daemon.pidfile.PIDLockFile(PID_FILE), signal_map=signal_map):

        if settings["logfile"]:
            add_log_handler(settings["logfile"], settings["log"])

        LOGGER.info("Start homeserver-power-saver as daemon with settings:\n%s" %
                    json.dumps(settings, indent=2))

        powersaver = PowerSaver(settings)
        if settings["dbus"]:
            DbusSleepHandler(powersaver)

        dt_now = datetime.today()
        stayup = settings["min_uptime"]
        LOGGER.info("Keep PC awake at least until %s" % format_datetime(dt_now + timedelta(minutes=stayup)))
        time.sleep(stayup * 60)

        powersaver.main()


def get_settings(args: argparse.Namespace) -> 'dict':

    if args.settings:
        with open(args.settings, "r") as f:
            s = "\n".join(f.readlines())
            f.close()

        settings = json.loads(s)

    else:
        settings = dict()

    if args.dry_run:
        settings["dryrun"] = args.dry_run
    elif "dryrun" not in settings:
        settings["dryrun"] = False

    if args.dbus:
        settings["dbus"] = args.dbus
    elif "dbus" not in settings:
        settings["dbus"] = False

    if args.mode:
        settings["mode"] = args.mode
    elif "mode" not in settings:
        settings["mode"] = "mem"

    if args.log:
        settings["log"] = args.log
    elif "log" not in settings:
        settings["log"] = "INFO"

    if args.logfile:
        settings["logfile"] = args.logfile
    elif "logfile" not in settings:
        settings["logfile"] = None

    return settings


def prepare_args(argv: 'list[str]') -> 'tuple[argparse.ArgumentParser,argparse.Namespace]':

    parser = argparse.ArgumentParser()
    parser.add_argument("--daemon", action="store_true",
                        help="start as daemon")
    parser.add_argument("--dbus", action="store_true",
                        help="handle events coming from d-bus for pre-/post actions")
    parser.add_argument("--stop", action="store_true",
                        help="stop running daemon")
    parser.add_argument("--status", action="store_true",
                        help="get status of daemon")
    parser.add_argument("--version", action="store_true",
                        help="print version")
    parser.add_argument("--dry-run", action="store_true",
                        help="simulate")
    parser.add_argument(
        "--mode", type=str, choices=["mem", "disk", "off", "shutdown"], help="mode")
    parser.add_argument("--settings", type=str, required=True,
                        help="(required) path to settings file in json format. Typically '../ext/settings.json'")
    parser.add_argument(
        "--log", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="(optional) log level. Default is INFO")
    parser.add_argument("--logfile", type=str,
                        help="path to log file if process is started as daemon.")

    return parser, parser.parse_args(argv[1:])


def print_help(parser: argparse.ArgumentParser) -> None:

    print_version()
    parser.print_help()


def print_version() -> None:

    print("A service that suspends your homeserver and wakes it up in time.\nVersion: %s\n" % VERSION)


def status() -> 'dict':

    def _status():
        if not os.path.isfile(PID_FILE):
            return False, -1

        current_pid = int(open(PID_FILE, 'r').readlines()[0])
        try:
            os.kill(current_pid, 0)
            return True, current_pid
        except PermissionError:
            return True, current_pid
        except:
            os.remove(PID_FILE)
            return False, -1

    _s, _pid = _status()
    return {"running": _s, "pid": _pid}


def stop(_pid: int) -> None:

    os.kill(_pid, signal.SIGTERM)


if __name__ == "__main__":

    # stop homeserver-power-saver daemon
    if "stop" in sys.argv or "--stop" in sys.argv:
        _status = status()
        if _status["running"]:
            stop(_status["pid"])
            exit(0)
        else:
            print("homeserver-power-saver is not running", file=sys.stderr)
            exit(1)

    # get status of homeserver-power-saver daemon
    elif "status" in sys.argv or "--status" in sys.argv:
        _status = status()
        print(json.dumps(_status, sort_keys=True), file=sys.stderr)
        exit(0 if _status["running"] else 1)

    elif "--version" in sys.argv:
        print_version()
        exit(0)

    try:
        parser, args = prepare_args(sys.argv)
        settings = get_settings(args)
    except Exception as ex:
        print("%s\n" % ex)
        print_help(parser)
        exit(1)

    init_logging("home-server-powersaver", settings["log"])

    # Start as daemon
    if args.daemon:
        _status = status()
        if not _status["running"]:
            start(settings=settings)
            exit(0)
        else:
            print("homeserver-power-saver is already running with process ID %i" %
                  _status["pid"], file=sys.stderr)
            exit(1)

    else:

        powersaver = PowerSaver(settings)
        if settings["dbus"]:
            DbusSleepHandler(powersaver)
        powersaver.main()
