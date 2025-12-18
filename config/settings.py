import json
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).parent.parent

class ConfigManager:
    """設定管理器"""
    
    DEFAULT_CONFIG = {
        # 顯示設定
        "display_time": 3000,        # 顯示時間（毫秒）
        "is_random_mode": False,     # 隨機模式
        
        # 視窗設定
        "window_width": 380,
        "window_height": 118,  # 基礎高度（不含控制面板）
        "always_on_top": True,
        
        # 檔案設定
        "excel_file": "list.xlsx",
        "sheet_name": "",            # 空字串表示使用第一個工作表
        
        # 主題
        "theme": "dark",             # dark / light
    }
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = ROOT_DIR / config_file
        self.config = self._load()
    
    def _load(self) -> dict:
        """載入設定"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # 合併預設值
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(loaded)
                    return config
            except Exception as e:
                print(f"載入設定失敗: {e}")
        
        return self.DEFAULT_CONFIG.copy()
    
    def save(self):
        """儲存設定"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"儲存設定失敗: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """取得設定值"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any, auto_save: bool = True):
        """設定值"""
        self.config[key] = value
        if auto_save:
            self.save()