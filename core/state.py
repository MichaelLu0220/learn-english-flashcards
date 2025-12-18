"""應用程式狀態管理"""
import random
from typing import Optional, List
from core.models import WordEntry


class AppState:
    """集中管理應用程式狀態"""
    
    def __init__(self):
        # 播放狀態
        self.current_index: int = 0
        self.is_paused: bool = False
        self.is_random_mode: bool = False
        
        # UI 狀態
        self.is_editing: bool = False
        self.is_mouse_in: bool = False
        
        # 資料
        self.word_entries: List[WordEntry] = []
    
    # === 播放控制 ===
    
    def toggle_pause(self) -> bool:
        """切換暫停狀態，回傳新狀態"""
        self.is_paused = not self.is_paused
        return self.is_paused
    
    # === 導航 ===
    
    def next_index(self) -> int:
        """移動到下一個索引"""
        if not self.word_entries:
            return 0
        
        if self.is_random_mode:
            self.current_index = random.randint(0, len(self.word_entries) - 1)
        else:
            self.current_index = (self.current_index + 1) % len(self.word_entries)
        
        return self.current_index
    
    def prev_index(self) -> Optional[int]:
        """移動到上一個索引（隨機模式回傳 None）"""
        if not self.word_entries:
            return None
        
        if self.is_random_mode:
            return None
        
        self.current_index = (self.current_index - 1) % len(self.word_entries)
        return self.current_index
    
    def reset_index(self):
        """重置索引"""
        self.current_index = 0
    
    # === 模式 ===
    
    def toggle_random_mode(self) -> bool:
        """切換隨機模式，回傳新狀態"""
        self.is_random_mode = not self.is_random_mode
        return self.is_random_mode
    
    # === 資料 ===
    
    def set_entries(self, entries: List[WordEntry]):
        """設定單字列表"""
        self.word_entries = entries
        self.current_index = 0
    
    def get_current_entry(self) -> Optional[WordEntry]:
        """取得當前單字"""
        if not self.word_entries:
            return None
        if self.current_index >= len(self.word_entries):
            self.current_index = 0
        return self.word_entries[self.current_index]
    
    @property
    def total_entries(self) -> int:
        """總單字數"""
        return len(self.word_entries)
