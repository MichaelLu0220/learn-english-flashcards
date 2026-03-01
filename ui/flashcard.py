import flet as ft
from typing import Optional
from core.models import WordEntry


class Flashcard(ft.Container):
    """單字卡片元件"""
    
    def __init__(
        self,
        word_entry: Optional[WordEntry] = None,
        on_click: Optional[callable] = None,
    ):
        super().__init__()
        
        self.word_entry = word_entry
        self._on_click = on_click
        
        # 建立 UI 元件
        self._build()
    
    def _build(self):
        """建立 UI"""
        # 單字標籤
        self.word_text = ft.Text(
            value="",
            size=22,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.WHITE,
            text_align=ft.TextAlign.CENTER,
        )
        
        # 意思標籤
        self.meaning_text = ft.Text(
            value="",
            size=14,
            color=ft.colors.WHITE70,
            text_align=ft.TextAlign.CENTER,
        )
        
        # 例句標籤
        self.example_text = ft.Text(
            value="",
            size=12,
            italic=True,
            color=ft.colors.WHITE54,
            text_align=ft.TextAlign.CENTER,
        )
        
        # 卡片內容：英文在上、中文在下、例句最下
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
        
        # 設定容器屬性
        self.content = self.card_content
        self.bgcolor = ft.colors.with_opacity(0.15, ft.colors.WHITE)
        self.border_radius = 10
        self.padding = ft.padding.symmetric(horizontal=16, vertical=12)
        self.alignment = ft.alignment.center
        self.on_click = self._handle_click
        
        # 初始顯示
        if self.word_entry:
            self.update_content(self.word_entry)
    
    def _handle_click(self, e):
        """處理點擊事件"""
        if self._on_click:
            self._on_click(e)
    
    def update_content(self, entry: WordEntry):
        """更新顯示內容"""
        self.word_entry = entry
        self.word_text.value = entry.word
        self.meaning_text.value = entry.meaning
        self.example_text.value = entry.example if entry.example else ""
        
        # 如果沒有例句，隱藏例句區域
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