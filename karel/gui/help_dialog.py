from pathlib import Path
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PySide6.QtGui import QFont, QIcon

from karel.gui.help_content import LEVEL_HELP


_ASSETS_DIR = Path(__file__).parent / "assets"

class HelpDialog(QDialog):
    def __init__(self, level, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Podsetnik")
        self.setWindowIcon(QIcon(str(_ASSETS_DIR / "lefrog.png")))


        content = LEVEL_HELP[level]

        outer_layout = QVBoxLayout(self)

        title_label = QLabel(content["title"])
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        outer_layout.addWidget(title_label)

        for section in content["sections"]:
            heading_label = QLabel(section["heading"])
            heading_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
            outer_layout.addWidget(heading_label)

            for command, description in section["items"]:
                item_label = QLabel(f"<b>{command}</b> - {description}")
                outer_layout.addWidget(item_label)

        example_heading = QLabel("Primer:")
        example_heading.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        outer_layout.addWidget(example_heading)

        example_label = QLabel(content["example"])
        example_font = QFont("Consolas", 10)
        example_font.setStyleHint(QFont.Monospace)
        example_label.setFont(example_font)
        example_label.setStyleSheet("background-color: #2b2b2b; padding: 8px; border-radius: 4px;")
        outer_layout.addWidget(example_label)

        self.adjustSize()