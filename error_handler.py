from typing import Callable, List, Tuple

class ErrorHandler:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ErrorHandler, cls).__new__(cls)
            cls._instance._subscribers: List[Callable[[str, str], None]] = []
            cls._instance._history: List[Tuple[str, str]] = []
        return cls._instance

    def subscribe(self, callback: Callable[[str, str], None]):
        if callback not in self._subscribers:
            self._subscribers.append(callback)
            for level, msg in self._history:
                callback(level, msg)

    def unsubscribe(self, callback: Callable[[str, str], None]):
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def _notify(self, level: str, message: str):
        self._history.append((level, message))
        for callback in self._subscribers:
            callback(level, message)
        print(f"[{level}] {message}")

    def print_error(self, m: str): self._notify("ERROR", m)
    def print_warning(self, m: str): self._notify("WARNING", m)
    def print_info(self, m: str): self._notify("INFO", m)
