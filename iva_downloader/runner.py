from PySide6.QtCore import QObject, QProcess, QTimer, Signal


class DownloadRunner(QObject):
    output = Signal(str)
    state_changed = Signal(str)
    finished = Signal(int)

    def __init__(self, parent=None, kill_timeout_ms: int = 3000):
        super().__init__(parent)
        self.kill_timeout_ms = kill_timeout_ms
        self.is_running = False
        self._process = QProcess(self)
        self._kill_timer = QTimer(self)
        self._kill_timer.setSingleShot(True)
        self._kill_timer.timeout.connect(self._kill_if_running)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._read_output)
        self._process.finished.connect(self._on_finished)
        self._process.errorOccurred.connect(self._on_process_error)

    def start(self, command: list[str]) -> None:
        if self.is_running or not command:
            return
        self._kill_timer.stop()
        self.is_running = True
        self.state_changed.emit("running")
        self._process.start(command[0], command[1:])

    def stop(self) -> None:
        if not self.is_running:
            return
        self.state_changed.emit("stopping")
        self._process.terminate()
        self._kill_timer.start(self.kill_timeout_ms)

    def _read_output(self) -> None:
        data = bytes(self._process.readAllStandardOutput()).decode("utf-8", errors="replace")
        if data:
            self.output.emit(data)

    def _kill_if_running(self) -> None:
        if self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.kill()

    def _on_finished(self, exit_code: int, _exit_status: QProcess.ExitStatus) -> None:
        self._read_output()
        self._finish(exit_code)

    def _on_process_error(self, error: QProcess.ProcessError) -> None:
        if error == QProcess.ProcessError.FailedToStart and self.is_running:
            self.output.emit(f"Could not start process: {self._process.errorString()}\n")
            self._finish(-1)

    def _finish(self, exit_code: int) -> None:
        if not self.is_running:
            return
        self._kill_timer.stop()
        self.is_running = False
        self.state_changed.emit("idle")
        self.finished.emit(exit_code)
