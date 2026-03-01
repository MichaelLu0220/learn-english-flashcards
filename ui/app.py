"""英文單字卡應用程式"""
import flet as ft
import threading
from typing import Optional

from config.settings import ConfigManager
from core.excel import ExcelReader
from core.state import AppState
from core.timer import TimerManager
from ui.flashcard import Flashcard
from ui.controls import Controls


class EnglishFlashcardApp:
    """英文單字卡應用程式"""
    
    # 控制面板高度
    CONTROLS_HEIGHT = 45
    
    def __init__(self):
        # 核心模組
        self.config = ConfigManager()
        self.state = AppState()
        self.timers = TimerManager()
        self.excel_reader: Optional[ExcelReader] = None
        
        # UI 元件
        self.page: Optional[ft.Page] = None
        self.flashcard: Optional[Flashcard] = None
        self.controls: Optional[Controls] = None
        self.controls_container: Optional[ft.Container] = None
        self.message_text: Optional[ft.Text] = None
        self.message_container: Optional[ft.Container] = None
        
        # 訊息計時器
        self._message_timer: Optional[threading.Timer] = None
        
        # 從 config 初始化狀態
        self.state.is_random_mode = self.config.get("is_random_mode", False)
    
    def main(self, page: ft.Page):
        """應用程式入口"""
        self.page = page
        
        self._setup_window()
        self._build_ui()
        self._load_data()
        self._start_display()
        self._ensure_base_height()
    
    # ==================== 視窗設定 ====================
    
    def _setup_window(self):
        """設定視窗"""
        self.page.title = "English Flashcard"
        self.page.window.width = self.config.get("window_width", 500)
        self.page.window.height = self.config.get("window_height", 140)
        self.page.window.min_width = 400
        self.page.window.min_height = 80
        self.page.window.always_on_top = self.config.get("always_on_top", True)
        self.page.window.resizable = True
        
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#1a1a2e"
        self.page.padding = 0
        self.page.spacing = 0
        
        self.page.on_keyboard_event = self._on_keyboard
        self.page.window.on_event = self._on_window_event
    
    # ==================== UI 建立 ====================
    
    def _build_ui(self):
        """建立 UI"""
        # 單字卡片
        self.flashcard = Flashcard(on_click=self._on_card_click)
        self.flashcard.set_loading()
        
        # 控制面板
        self.controls = Controls(
            is_paused=self.state.is_paused,
            is_random=self.state.is_random_mode,
            speed=self.config.get("display_time", 3000) / 1000,
            on_play_pause=self._toggle_pause,
            on_prev=self._prev_word,
            on_next=self._next_word,
            on_mode_toggle=self._toggle_mode,
            on_speed_change=self._on_speed_change,
            on_reload=self._reload_data,
            on_speed_focus=self._on_speed_focus,
            on_speed_blur=self._on_speed_blur,
        )
        
        # 訊息文字（整合在控制面板上方）
        self.message_text = ft.Text(
            value="",
            size=11,
            color=ft.colors.WHITE70,
            text_align=ft.TextAlign.CENTER,
        )
        
        self.message_container = ft.Container(
            content=self.message_text,
            alignment=ft.alignment.center,
            opacity=0,
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        )
        
        # 控制面板容器（含訊息 + 按鈕）
        controls_content = ft.Column(
            controls=[
                self.message_container,
                self.controls,
            ],
            spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )
        
        # 控制面板容器（無動畫，避免閃爍）
        self.controls_container = ft.Container(
            content=controls_content,
            height=0,
            opacity=0,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )
        
        # 主容器
        main_container = ft.Container(
            content=ft.Column(
                controls=[self.flashcard, self.controls_container],
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            bgcolor="#1a1a2e",
            padding=12,
            expand=True,
            on_hover=self._on_hover,
        )
        
        self.page.add(main_container)
    
    # ==================== 資料載入 ====================
    
    def _load_data(self):
        """載入資料"""
        excel_file = self.config.get("excel_file", "list.xlsx")
        sheet_name = self.config.get("sheet_name", "")
        
        self.excel_reader = ExcelReader(excel_file, sheet_name)
        success, message = self.excel_reader.load()
        
        if success:
            self.state.set_entries(self.excel_reader.word_entries)
            self._show_message(message)
        else:
            self._show_message(message)
            self.flashcard.set_empty(message)
    
    def _reload_data(self):
        """重新載入資料"""
        if self.excel_reader:
            success, message = self.excel_reader.reload()
            self._show_message(message)
            
            if success:
                self.state.set_entries(self.excel_reader.word_entries)
                self._display_current()
    
    # ==================== 播放控制 ====================
    
    def _start_display(self):
        """開始顯示"""
        if self.state.word_entries:
            self._display_current()
            self._schedule_next()
    
    def _display_current(self):
        """顯示當前單字"""
        entry = self.state.get_current_entry()
        if entry:
            self.flashcard.update_content(entry)
            self.controls.update_progress(
                self.state.current_index + 1,
                self.state.total_entries
            )
    
    def _schedule_next(self):
        """安排下一次自動切換"""
        if not self.state.is_paused:
            delay = self.config.get("display_time", 3000) / 1000
            self.timers.start_auto_timer(delay, self._auto_next)
    
    def _auto_next(self):
        """自動切換"""
        self.state.next_index()
        if self.page:
            self.page.run_thread(self._display_and_schedule)
    
    def _display_and_schedule(self):
        """顯示並安排下一次"""
        self._display_current()
        self._schedule_next()
    
    def _toggle_pause(self):
        """切換播放/暫停"""
        is_paused = self.state.toggle_pause()
        self.controls.update_play_state(is_paused)
        
        if is_paused:
            self.timers.cancel_auto_timer()
            self._show_message("已暫停")
        else:
            self._schedule_next()
            self._show_message("播放中")
    
    def _prev_word(self):
        """上一個單字"""
        result = self.state.prev_index()
        if result is None:
            self._show_message("隨機模式無法回到上一個")
            return
        
        self._display_current()
        if not self.state.is_paused:
            self._schedule_next()
    
    def _next_word(self):
        """下一個單字"""
        self.state.next_index()
        self._display_current()
        
        if not self.state.is_paused:
            self._schedule_next()
    
    def _toggle_mode(self):
        """切換模式"""
        is_random = self.state.toggle_random_mode()
        self.config.set("is_random_mode", is_random)
        self.controls.update_mode(is_random)
        
        mode_text = "隨機" if is_random else "順序"
        self._show_message(f"切換到{mode_text}模式")
    
    def _on_speed_change(self, speed: float):
        """速度變更"""
        self.config.set("display_time", int(speed * 1000))
        self._show_message(f"速度：{speed} 秒")
        
        if not self.state.is_paused:
            self._schedule_next()
    
    def _on_card_click(self, e):
        """點擊卡片"""
        self._next_word()
    
    # ==================== 控制面板顯示/隱藏 ====================
    
    def _on_hover(self, e: ft.ControlEvent):
        """滑鼠 hover 事件"""
        if e.data == "true":
            self.state.is_mouse_in = True
            self.timers.cancel_hide_timer()
            self._show_controls()
        else:
            self.state.is_mouse_in = False
            
            if self.state.is_editing:
                return
            
            self.timers.start_hide_timer(1.0, self._do_hide_controls)
    
    def _show_controls(self):
        """瞬間展開控制面板"""
        if self.controls_container.height > 0:
            return
        
        base_height = self.config.get("window_height", 140)
        target_height = base_height + self.CONTROLS_HEIGHT + 20
        
        # 所有狀態一次性設定，只呼叫一次 page.update()
        self.controls_container.height = self.CONTROLS_HEIGHT + 20
        self.controls_container.opacity = 1
        self.page.window.height = target_height
        self.page.update()
    
    def _hide_controls(self):
        """瞬間收起控制面板"""
        if self.controls_container.height == 0:
            return
        
        self.timers.cancel_hide_timer()
        
        base_height = self.config.get("window_height", 140)
        
        # 所有狀態一次性設定（含訊息隱藏），只呼叫一次 page.update()
        self.controls_container.height = 0
        self.controls_container.opacity = 0
        self.message_container.opacity = 0
        self.page.window.height = base_height
        self.page.update()
    
    def _do_hide_controls(self):
        """延遲隱藏的回調（由計時器觸發）"""
        if self.state.is_mouse_in or self.state.is_editing:
            return
        
        if self.page:
            self.page.run_thread(self._hide_controls)
    
    def _on_speed_focus(self, e):
        """速度輸入框獲得焦點"""
        self.state.is_editing = True
        self.timers.cancel_hide_timer()
    
    def _on_speed_blur(self, e):
        """速度輸入框失去焦點"""
        self.state.is_editing = False
        if not self.state.is_mouse_in:
            self.timers.start_hide_timer(1.0, self._do_hide_controls)

    def _ensure_base_height(self):
        """確保視窗為基礎高度"""
        if self.controls_container and self.controls_container.height == 0:
            base_height = self.config.get("window_height", 140)
            self.page.window.height = base_height
            self.page.update()
    
    # ==================== 事件處理 ====================
    
    def _on_keyboard(self, e: ft.KeyboardEvent):
        """鍵盤事件"""
        key_actions = {
            " ": self._toggle_pause,
            "Arrow Left": self._prev_word,
            "Arrow Right": self._next_word,
        }
        
        if e.key in key_actions:
            key_actions[e.key]()
        elif e.key.lower() == "m":
            self._toggle_mode()
        elif e.key.lower() == "r":
            self._reload_data()
    
    def _on_window_event(self, e):
        """視窗事件"""
        if e.data == "close":
            self.timers.cancel_all()
            if self._message_timer:
                self._message_timer.cancel()
            self.config.save()
    
    # ==================== 訊息提示 ====================
    
    def _show_message(self, message: str):
        """顯示訊息（在控制面板內）"""
        if self._message_timer:
            self._message_timer.cancel()
        
        self.message_text.value = message
        self.message_container.opacity = 1
        
        if self.page:
            self.message_container.update()
        
        self._message_timer = threading.Timer(2.0, self._fade_out_message)
        self._message_timer.daemon = True
        self._message_timer.start()
    
    def _fade_out_message(self):
        """淡出訊息"""
        if self.page:
            self.page.run_thread(self._hide_message)
    
    def _hide_message(self):
        """隱藏訊息"""
        self.message_container.opacity = 0
        if self.page:
            self.message_container.update()