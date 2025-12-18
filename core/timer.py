"""計時器管理"""
import threading
from typing import Optional, Callable


class TimerManager:
    """管理自動播放和延遲隱藏計時器"""
    
    def __init__(self):
        self._auto_timer: Optional[threading.Timer] = None
        self._hide_timer: Optional[threading.Timer] = None
    
    # === 自動播放計時器 ===
    
    def start_auto_timer(self, delay: float, callback: Callable):
        """啟動自動播放計時器"""
        self.cancel_auto_timer()
        
        self._auto_timer = threading.Timer(delay, callback)
        self._auto_timer.daemon = True
        self._auto_timer.start()
    
    def cancel_auto_timer(self):
        """取消自動播放計時器"""
        if self._auto_timer:
            self._auto_timer.cancel()
            self._auto_timer = None
    
    # === 隱藏控制面板計時器 ===
    
    def start_hide_timer(self, delay: float, callback: Callable):
        """啟動隱藏計時器"""
        self.cancel_hide_timer()
        
        self._hide_timer = threading.Timer(delay, callback)
        self._hide_timer.daemon = True
        self._hide_timer.start()
    
    def cancel_hide_timer(self):
        """取消隱藏計時器"""
        if self._hide_timer:
            self._hide_timer.cancel()
            self._hide_timer = None
    
    def is_hide_timer_running(self) -> bool:
        """檢查隱藏計時器是否在執行"""
        return self._hide_timer is not None and self._hide_timer.is_alive()
    
    # === 清理 ===
    
    def cancel_all(self):
        """取消所有計時器"""
        self.cancel_auto_timer()
        self.cancel_hide_timer()
