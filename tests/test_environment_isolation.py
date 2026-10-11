"""Offline regressions must not inherit the operator's live Talk configuration."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("inherited_mode", ["live", "not-a-voice-mode"])
def test_provider_policy_tests_ignore_inherited_live_configuration(tmp_path, inherited_mode):
    # Run the exact registration and connect-cancellation regressions in a
    # fresh pytest process. Setting a target also catches accidental canonical
    # routing independently of the voice-mode knob. No actual host is loaded.
    root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    env.update(
        TALK_VOICE_MODE=inherited_mode,
        TALK_TASK_TARGET="inherited-target-must-not-be-selected",
        HERMES_HOME=str(tmp_path / "hermes-home"),
        PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
        PYTHONDONTWRITEBYTECODE="1",
    )
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest", "-p", "pytest_timeout", "-o", "addopts=", "-q",
            "--timeout=5", "--timeout-method=thread",
            "tests/test_register.py::test_slash_command_takes_the_discord_room_inside_an_event_loop",
            "tests/test_register.py::test_join_captures_and_forwards_the_exact_host_execution_attachment",
            "tests/test_register.py::test_join_on_an_older_host_keeps_the_explicitly_limited_fallback",
            "tests/test_fake_provider_session.py::test_cancellation_during_connect_closes_every_session_owned_resource",
        ],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "4 passed" in result.stdout
