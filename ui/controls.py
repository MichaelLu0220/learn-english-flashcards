import flet as ft
from typing import Optional, Callable


class Controls(ft.Container):
    """控制面板元件"""
    
    def __init__(
        self,
        is_paused: bool = False,
        is_random: bool = False,
        speed: float = 3.0,
        progress_text: str = "0/0",
        on_play_pause: Optional[Callable] = None,
        on_prev: Optional[Callable] = None,
        on_next: Optional[Callable] = None,
        on_mode_toggle: Optional[Callable] = None,
        on_speed_change: Optional[Callable[[float], None]] = None,
        on_reload: Optional[Callable] = None,
        on_speed_focus: Optional[Callable] = None,
        on_speed_blur: Optional[Callable] = None,
    ):
        super().__init__()
        
        # 狀態
        self.is_paused = is_paused
        self.is_random = is_random
        self.speed = speed
        self.progress_text = progress_text
        
        # 回調函數
        self._on_play_pause = on_play_pause
        self._on_prev = on_prev
        self._on_next = on_next
        self._on_mode_toggle = on_mode_toggle
        self._on_speed_change = on_speed_change
        self._on_reload = on_reload
        self._on_speed_focus = on_speed_focus
        self._on_speed_blur = on_speed_blur
        
        # 建立 UI
        self._build()
    
    def _build(self):
        """建立 UI"""
        btn_size = 28
        icon_size = 16
        
        # 播放/暫停按鈕
        self.play_btn = ft.IconButton(
            icon=ft.Icons.PLAY_ARROW_ROUNDED if self.is_paused else ft.Icons.PAUSE_ROUNDED,
            icon_color=ft.Colors.WHITE,
            icon_size=icon_size,
            width=btn_size,
            height=btn_size,
            bgcolor=ft.Colors.BLUE_700,
            on_click=self._handle_play_pause,
            tooltip="播放/暫停 (Space)",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
                padding=0,
            ),
        )
        
        # 上一個按鈕
        self.prev_btn = ft.IconButton(
            icon=ft.Icons.SKIP_PREVIOUS_ROUNDED,
            icon_color=ft.Colors.WHITE,
            icon_size=icon_size,
            width=btn_size,
            height=btn_size,
            bgcolor=ft.Colors.BLUE_700,
            on_click=self._handle_prev,
            tooltip="上一個 (←)",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
                padding=0,
            ),
        )
        
        # 下一個按鈕
        self.next_btn = ft.IconButton(
            icon=ft.Icons.SKIP_NEXT_ROUNDED,
            icon_color=ft.Colors.WHITE,
            icon_size=icon_size,
            width=btn_size,
            height=btn_size,
            bgcolor=ft.Colors.BLUE_700,
            on_click=self._handle_next,
            tooltip="下一個 (→)",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
                padding=0,
            ),
        )
        
        # 模式切換按鈕
        self.mode_btn = ft.ElevatedButton(
            text="隨機" if self.is_random else "順序",
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.RED_700,
            on_click=self._handle_mode_toggle,
            tooltip="切換模式 (M)",
            height=btn_size,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
                padding=ft.padding.symmetric(horizontal=8),
                text_style=ft.TextStyle(size=11),
            ),
        )
        
        # 重新載入按鈕
        self.reload_btn = ft.IconButton(
            icon=ft.Icons.REFRESH_ROUNDED,
            icon_color=ft.Colors.WHITE,
            icon_size=icon_size,
            width=btn_size,
            height=btn_size,
            bgcolor=ft.Colors.GREEN_700,
            on_click=self._handle_reload,
            tooltip="重新載入 (R)",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
                padding=0,
            ),
        )
        
        # 速度輸入
        self.speed_field = ft.TextField(
            value=str(self.speed),
            width=40,
            height=btn_size,
            text_size=11,
            content_padding=ft.padding.symmetric(horizontal=4, vertical=0),
            text_align=ft.TextAlign.CENTER,
            bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE),
            border_color=ft.Colors.TRANSPARENT,
            color=ft.Colors.WHITE,
            on_submit=self._handle_speed_change,
            on_focus=self._handle_speed_focus,
            on_blur=self._handle_speed_blur,
        )
        
        # 進度標籤
        self.progress_label = ft.Text(
            value=self.progress_text,
            size=11,
            color=ft.Colors.WHITE70,
        )
        
        # 左側按鈕群
        left_controls = ft.Row(
            controls=[
                self.play_btn,
                self.prev_btn,
                self.next_btn,
                self.mode_btn,
                self.reload_btn,
            ],
            spacing=4,
        )
        
        # 右側速度 + 進度
        right_controls = ft.Row(
            controls=[
                ft.Text("速度", size=10, color=ft.Colors.WHITE54),
                self.speed_field,
                ft.Text("秒", size=10, color=ft.Colors.WHITE54),
                ft.Container(width=8),
                self.progress_label,
            ],
            spacing=4,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        # 整體佈局
        self.content = ft.Row(
            controls=[
                left_controls,
                ft.Container(expand=True),
                right_controls,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        # 容器設定
        self.bgcolor = ft.Colors.with_opacity(0.15, ft.Colors.WHITE)
        self.border_radius = 8
        self.padding = ft.padding.symmetric(horizontal=10, vertical=6)
    
    def _handle_play_pause(self, e):
        if self._on_play_pause:
            self._on_play_pause()
    
    def _handle_prev(self, e):
        if self._on_prev:
            self._on_prev()
    
    def _handle_next(self, e):
        if self._on_next:
            self._on_next()
    
    def _handle_mode_toggle(self, e):
        if self._on_mode_toggle:
            self._on_mode_toggle()
    
    def _handle_reload(self, e):
        if self._on_reload:
            self._on_reload()
    
    def _handle_speed_focus(self, e):
        """速度輸入框獲得焦點"""
        if self._on_speed_focus:
            self._on_speed_focus(e)
    
    def _handle_speed_blur(self, e):
        """速度輸入框失去焦點"""
        # 先處理速度變更
        self._handle_speed_change(e)
        # 再通知外部
        if self._on_speed_blur:
            self._on_speed_blur(e)
    
    def _handle_speed_change(self, e):
        try:
            new_speed = float(self.speed_field.value)
            new_speed = max(0.5, min(60, new_speed))  # 限制範圍
            self.speed = new_speed
            self.speed_field.value = str(new_speed)
            
            if self._on_speed_change:
                self._on_speed_change(new_speed)
        except ValueError:
            # 輸入無效，還原
            self.speed_field.value = str(self.speed)
        
        if self.page:
            self.update()
    
    def update_play_state(self, is_paused: bool):
        """更新播放狀態"""
        self.is_paused = is_paused
        self.play_btn.icon = ft.Icons.PLAY_ARROW_ROUNDED if is_paused else ft.Icons.PAUSE_ROUNDED
        
        if self.page:
            self.play_btn.update()
    
    def update_mode(self, is_random: bool):
        """更新模式"""
        self.is_random = is_random
        self.mode_btn.text = "隨機" if is_random else "順序"
        
        if self.page:
            self.mode_btn.update()
    
    def update_progress(self, current: int, total: int):
        """更新進度"""
        self.progress_text = f"{current}/{total}"
        self.progress_label.value = self.progress_text
        
        if self.page:
            self.progress_label.update()
    
    def update_speed(self, speed: float):
        """更新速度顯示"""
        self.speed = speed
        self.speed_field.value = str(speed)
        
        if self.page:
            self.speed_field.update()