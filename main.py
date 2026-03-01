import flet as ft
from ui.app import EnglishFlashcardApp


def main():
    """程式入口"""
    app = EnglishFlashcardApp()
    
    ft.app(
        target=app.main,
        assets_dir="assets",  # 可選：放圖片等資源
    )


if __name__ == "__main__":
    main()