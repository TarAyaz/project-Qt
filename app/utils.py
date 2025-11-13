from pathlib import Path
from PyQt6 import uic


# // === Подгрузка ui файлов ===
def load_ui(ui_file_name):
    ui_path = Path(__file__).parent.parent / "ui" / ui_file_name
    if not ui_path.exists():
        raise FileNotFoundError(f"UI файл не найден: {ui_path}")

    return uic.loadUi(str(ui_path))
