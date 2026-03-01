import flet as ft
from typing import Optional, Callable
from core.models import WordEntry


class ExampleDialog:
    """例句彈出視窗（AlertDialog 模態）"""

    def __init__(self, page: ft.Page, on_close: Optional[Callable] = None):
        self.page = page
        self._on_close = on_close
        self._dialog: Optional[ft.AlertDialog] = None

    def show(self, entry: WordEntry):
        """顯示例句視窗"""
        example_content = entry.example if entry.example else "（此單字沒有例句）"

        self._dialog = ft.AlertDialog(
            modal=True,
            bgcolor="#1a1a2e",
            shape=ft.RoundedRectangleBorder(radius=12),
            title=ft.Text(
                value="例句",
                size=13,
                color=ft.colors.WHITE38,
                text_align=ft.TextAlign.CENTER,
            ),
            content=ft.Container(
                content=ft.Text(
                    value=example_content,
                    size=14,
                    italic=True,
                    color=ft.colors.WHITE70,
                    text_align=ft.TextAlign.CENTER,
                ),
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
            ),
            actions=[
                ft.ElevatedButton(
                    text="關閉",
                    on_click=self._handle_close,
                    bgcolor=ft.colors.BLUE_700,
                    color=ft.colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        self.page.dialog = self._dialog
        self._dialog.open = True
        self.page.update()

    def _handle_close(self, e):
        """關閉視窗"""
        if self._dialog:
            self._dialog.open = False
            self.page.update()

        if self._on_close:
            self._on_close()

    def close(self):
        """強制關閉"""
        if self._dialog:
            self._dialog.open = False
            self.page.update()