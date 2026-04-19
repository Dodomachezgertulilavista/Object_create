# --- error_handler.py ---

from typing import Callable, List, Tuple

class ErrorHandler:
    """Глобальный обработчик ошибок (Singleton) + Publisher с историей."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ErrorHandler, cls).__new__(cls)
            cls._instance._subscribers: List[Callable[[str, str], None]] =[]
            # ДОБАВЛЯЕМ СПИСОК ИСТОРИИ:
            cls._instance._history: List[Tuple[str, str]] =[] 
        return cls._instance

    def subscribe(self, callback: Callable[[str, str], None]) -> None:
        """Подписка на события логгирования."""
        if callback not in self._subscribers:
            self._subscribers.append(callback)
            
            # КАК ТОЛЬКО КТО-ТО ПОДПИСАЛСЯ, СРАЗУ ОТПРАВЛЯЕМ ЕМУ ВСЮ ИСТОРИЮ
            for level, message in self._history:
                callback(level, message)

    def unsubscribe(self, callback: Callable[[str, str], None]) -> None:
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def _notify(self, level: str, message: str) -> None:
        """Рассылка сообщения всем подписчикам и сохранение в историю."""
        # СОХРАНЯЕМ В ИСТОРИЮ
        self._history.append((level, message))
        
        for callback in self._subscribers:
            callback(level, message)
        
        print(f"[{level}] {message}")

    def print_error(self, message: str) -> None:
        self._notify("ERROR", message)

    def print_warning(self, message: str) -> None:
        self._notify("WARNING", message)
        
    def print_info(self, message: str) -> None:
        self._notify("INFO", message)