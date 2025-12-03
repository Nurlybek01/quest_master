from PyQt6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QListWidget, QLabel
from PyQt6.QtCore import Qt
from core.gamification import GamificationManager  # будем создавать при каждом вызове


class GamificationPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.update_display()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.title = QLabel("🏆 Геймификация")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.title)

        self.level_label = QLabel()
        self.level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.level_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)  # max XP = 100
        layout.addWidget(self.progress)

        self.achievements_label = QLabel("Достижения:")
        layout.addWidget(self.achievements_label)

        self.achievements_list = QListWidget()
        layout.addWidget(self.achievements_list)

        self.setLayout(layout)

    def update_display(self):
        gm = GamificationManager()
        level = gm.get_current_level()
        self.level_label.setText(f"Уровень: {level} ({gm.xp} XP)")
        self.progress.setValue(gm.xp)
        self.achievements_list.clear()
        for ach in sorted(gm.achievements):
            self.achievements_list.addItem(ach)

    def refresh(self):
        self.update_display()