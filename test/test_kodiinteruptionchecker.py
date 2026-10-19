import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from checkers.kodiinterruptionchecker import KodiInterruptionChecker
from utils.period import Period


class TestKodiInteruptionChecker(unittest.TestCase):

    def test_kodiinteruptionchecker(self):

        setting = {
            "enable": True,
            "host": "192.168.178.30",
            "port": 9080,
            "user": "kodi",
            "password": "kodi",
            "post_active_time": 10
        }

        dt_now = datetime.today()

        period = Period(timedelta(), timedelta(days=8))
        kodiinteruptionchecker = KodiInterruptionChecker(
            setting=setting)

        with patch.object(kodiinteruptionchecker._kodiJsonRpcClient,
                          "get_active_players", return_value=[]):
            kodiinteruptionchecker.get_occupation(dt_now)
            kodiinteruptionchecker.get_upcoming_event(dt_now)

        self.assertTrue(True)

    def test_runtime_error_means_kodi_is_not_occupied(self):

        setting = {
            "host": "192.168.178.30",
            "port": 9080,
            "user": "kodi",
            "password": "kodi",
            "stay_awake": 10
        }
        checker = KodiInterruptionChecker(setting=setting)

        with patch.object(
                checker._kodiJsonRpcClient,
                "get_active_players",
                side_effect=RuntimeError("Kodi is unavailable")), \
                self.assertLogs(level="WARNING") as logs:
            occupation = checker.get_occupation(datetime.now())

        self.assertIsNone(occupation)
        self.assertIn("Kodi is not occupied", logs.output[0])
        self.assertIn("Kodi is unavailable", logs.output[0])

    def test_stop_player_failure_is_logged_and_other_players_are_stopped(self):

        checker = KodiInterruptionChecker({
            "host": "192.168.178.30",
            "port": 9080,
            "user": "kodi",
            "password": "kodi",
        })
        active_players = [
            {"type": "audio", "playerid": 1},
            {"type": "video", "playerid": 2},
        ]

        with patch.object(
                checker._kodiJsonRpcClient,
                "get_active_players",
                return_value=active_players), \
                patch.object(
                    checker._kodiJsonRpcClient,
                    "stop_player",
                    side_effect=[RuntimeError("Kodi is unavailable"), None]
                ) as stop_player, \
                self.assertLogs(level="WARNING") as logs:
            checker.perform_pre_action(datetime.now())

        self.assertEqual(stop_player.call_count, 2)
        self.assertEqual(
            stop_player.call_args_list[1].args,
            (2,))
        self.assertIn("Failed to stop Kodi audio player 1", logs.output[0])
        self.assertIn("Kodi is unavailable", logs.output[0])
