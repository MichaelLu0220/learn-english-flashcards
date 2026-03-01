import flet as ft
import time
import threading
from typing import Optional, Callable
from core.models import WordEntry

LONG_PRESS_THRESHOLD = 0.4  # 長按判定秒數（0.4 秒）


class Flashcard(ft.Container):
    """單字卡片元件"""
    
    def __init__(
        self,
        word_entry: Optional[WordEntry] = None,
        on_short_click: Optional[Callable] = None,  # 短按：換單字
        on_long_press: Optional[Callable] = None,   # 長按：開例句
    ):
        super().__init__()
        
        self.word_entry = word_entry
        self._on_short_click = on_short_click
        self._on_long_press = on_long_press
        
        self._press_time: Optional[float] = None
        self._long_press_timer: Optional[threading.Timer] = None
        self._long_press_triggered: bool = False  # 是否已觸發長按
        
        self._build()
    
    def _build(self):
        """建立 UI"""
        self.word_text = ft.Text(
            value="",
            size=22,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.WHITE,
            text_align=ft.TextAlign.CENTER,
        )
        
        self.meaning_text = ft.Text(
            value="",
            size=14,
            color=ft.colors.WHITE70,
            text_align=ft.TextAlign.CENTER,
        )
        
        # 例句固定單行，超出截斷，避免換行撐高版面
        self.example_text = ft.Text(
            value="",
            size=12,
            italic=True,
            color=ft.colors.WHITE54,
            text_align=ft.TextAlign.CENTER,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        
        self.card_content = ft.Column(
            controls=[
                self.word_text,
                self.meaning_text,
                self.example_text,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
        )
        
        self.content = self.card_content
        self.bgcolor = ft.colors.with_opacity(0.15, ft.colors.WHITE)
        self.border_radius = 10
        self.padding = ft.padding.symmetric(horizontal=16, vertical=12)
        self.alignment = ft.alignment.center

        # 按下：啟動長按計時器
        # 放開：若長按未觸發則視為短按
        self.on_tap_down = self._handle_tap_down
        self.on_click = self._handle_click
        
        if self.word_entry:
            self.update_content(self.word_entry)
    
    def _handle_tap_down(self, e):
        """按下 → 啟動長按計時器"""
        self._press_time = time.time()
        self._long_press_triggered = False

        # 時間到直接觸發，不等放開
        self._long_press_timer = threading.Timer(
            LONG_PRESS_THRESHOLD, self._trigger_long_press
        )
        self._long_press_timer.daemon = True
        self._long_press_timer.start()

    def _trigger_long_press(self):
        """計時到達 → 直接觸發長按（按著狀態下）"""
        self._long_press_triggered = True
        if self._on_long_press:
            self._on_long_press(None)

    def _handle_click(self, e):
        """放開 → 若長按未觸發則視為短按"""
        # 取消還未觸發的長按計時器
        if self._long_press_timer:
            self._long_press_timer.cancel()
            self._long_press_timer = None

        if not self._long_press_triggered:
            if self._on_short_click:
                self._on_short_click(e)

        # 重置狀態
        self._press_time = None
        self._long_press_triggered = False
    
    def update_content(self, entry: WordEntry):
        """更新顯示內容"""
        self.word_entry = entry
        self.word_text.value = entry.word
        self.meaning_text.value = entry.meaning
        self.example_text.value = entry.example if entry.example else ""
        self.example_text.visible = bool(entry.example)
        
        if self.page:
            self.update()
    
    def set_loading(self):
        """顯示載入中狀態"""
        self.word_text.value = "載入中..."
        self.meaning_text.value = ""
        self.example_text.value = ""
        self.example_text.visible = False
        
        if self.page:
            self.update()
    
    def set_empty(self, message: str = "沒有單字資料"):
        """顯示空狀態"""
        self.word_text.value = message
        self.meaning_text.value = ""
        self.example_text.value = ""
        self.example_text.visible = False
        
        if self.page:
            self.update()