import sys

from iva_downloader.runner import DownloadRunner


def test_runner_streams_output_and_reports_completion(qtbot):
    runner = DownloadRunner()
    output = []
    states = []
    runner.output.connect(output.append)
    runner.state_changed.connect(states.append)

    with qtbot.waitSignal(runner.finished, timeout=3000) as completed:
        runner.start([sys.executable, "-c", "print('streamed output', flush=True)"])

    assert completed.args == [0]
    assert "streamed output" in "".join(output)
    assert states == ["running", "idle"]
    assert runner.is_running is False


def test_runner_stop_terminates_a_running_process(qtbot):
    runner = DownloadRunner(kill_timeout_ms=50)
    states = []
    runner.state_changed.connect(states.append)

    runner.start([sys.executable, "-c", "import time; time.sleep(10)"])
    qtbot.waitUntil(lambda: runner.is_running, timeout=1000)

    with qtbot.waitSignal(runner.finished, timeout=3000) as completed:
        runner.stop()

    assert completed.args[0] != 0
    assert states == ["running", "stopping", "idle"]
    assert runner.is_running is False



def test_runner_recovers_when_executable_cannot_start(qtbot):
    runner = DownloadRunner()
    output = []
    states = []
    runner.output.connect(output.append)
    runner.state_changed.connect(states.append)

    with qtbot.waitSignal(runner.finished, timeout=3000) as completed:
        runner.start(["/definitely/missing/iva-downloader-command"])

    assert completed.args == [-1]
    assert "Could not start process" in "".join(output)
    assert states == ["running", "idle"]
    assert runner.is_running is False


def test_old_stop_timer_does_not_kill_replacement_process(qtbot):
    runner = DownloadRunner(kill_timeout_ms=75)

    with qtbot.waitSignal(runner.finished, timeout=3000):
        runner.start([sys.executable, "-c", "import time; time.sleep(10)"])
        qtbot.waitUntil(lambda: runner.is_running, timeout=1000)
        runner.stop()

    with qtbot.waitSignal(runner.finished, timeout=3000) as replacement:
        runner.start([sys.executable, "-c", "import time; time.sleep(0.2)"])

    assert replacement.args == [0]
