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
from ui.example_dialog import ExampleDialog


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
        self.example_dialog: Optional[ExampleDialog] = None
        
        # 訊息計時器
        self._message_timer: Optional[threading.Timer] = None
        
        # Dialog 開啟旗標（防止控制面板在 Dialog 顯示時被收起）
        self._is_dialog_open: bool = False
        
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
        # 單字卡片（短按換字、長按開例句）
        self.flashcard = Flashcard(
            on_short_click=self._on_card_short_click,
            on_long_press=self._on_card_long_press,
        )
        self.flashcard.set_loading()

        # 訊息 overlay（疊在卡片右上角）
        self.message_text = ft.Text(
            value="",
            size=11,
            color=ft.colors.WHITE,
        )
        self.message_container = ft.Container(
            content=self.message_text,
            bgcolor=ft.colors.with_opacity(0.55, ft.colors.BLACK),
            border_radius=6,
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            right=8,
            top=8,
            opacity=0,
            animate_opacity=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
        )

        # 卡片 + overlay 疊加
        self.card_stack = ft.Stack(
            controls=[self.flashcard, self.message_container],
            expand=True,
        )

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
        
        # 控制面板容器（無動畫，避免閃爍）
        self.controls_container = ft.Container(
            content=self.controls,
            height=0,
            opacity=0,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )
        
        # 主容器
        main_container = ft.Container(
            content=ft.Column(
                controls=[self.card_stack, self.controls_container],
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            bgcolor="#1a1a2e",
            padding=12,
            expand=True,
            on_hover=self._on_hover,
        )
        
        self.page.add(main_container)

        # 例句彈出視窗（page.add 之後才初始化）
        self.example_dialog = ExampleDialog(
            page=self.page,
            on_close=self._on_example_closed,
        )
    
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
    
    # ==================== 卡片點擊 ====================

    def _on_card_short_click(self, e):
        """短按卡片 → 換下一個單字"""
        self._next_word()

    def _on_card_long_press(self, e):
        """長按計時到達 → 暫停播放並顯示例句視窗"""
        entry = self.state.get_current_entry()
        if not entry:
            return

        # 標記 dialog 已開啟，防止控制面板被收起
        self._is_dialog_open = True

        # 暫停播放
        if not self.state.is_paused:
            self.state.is_paused = True
            self.timers.cancel_auto_timer()
            self.controls.update_play_state(True)

        # 記錄目前視窗高度，並放大以容納 Dialog 內容
        self._pre_dialog_height = self.page.window.height
        dialog_height = self.config.get("window_height", 140) + self.CONTROLS_HEIGHT + 8 + 200

        # 確保控制面板展開，視窗一次性放大
        self.controls_container.height = self.CONTROLS_HEIGHT + 8
        self.controls_container.opacity = 1
        self.page.window.height = dialog_height
        self.page.update()

        # 顯示例句彈出視窗
        self.example_dialog.show(entry)

    def _on_example_closed(self):
        """例句視窗關閉 → 還原視窗高度並恢復播放"""
        self._is_dialog_open = False

        # 還原視窗高度
        restore_height = getattr(self, "_pre_dialog_height", None)
        if restore_height:
            self.page.window.height = restore_height
            self.page.update()

        self.state.is_paused = False
        self.controls.update_play_state(False)
        self._schedule_next()
        self._show_message("繼續播放")

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
        target_height = base_height + self.CONTROLS_HEIGHT + 8
        
        self.controls_container.height = self.CONTROLS_HEIGHT + 8
        self.controls_container.opacity = 1
        self.page.window.height = target_height
        self.page.update()
    
    def _hide_controls(self):
        """瞬間收起控制面板"""
        if self.controls_container.height == 0:
            return
        
        self.timers.cancel_hide_timer()
        
        base_height = self.config.get("window_height", 140)
        
        self.controls_container.height = 0
        self.controls_container.opacity = 0
        self.message_container.opacity = 0
        self.page.window.height = base_height
        self.page.update()
    
    def _do_hide_controls(self):
        """延遲隱藏的回調（由計時器觸發）"""
        # Dialog 開啟中、滑鼠在內、或正在編輯時都不收起
        if self.state.is_mouse_in or self.state.is_editing or self._is_dialog_open:
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
        """在卡片右上角以 overlay 顯示訊息，2 秒後自動淡出"""
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