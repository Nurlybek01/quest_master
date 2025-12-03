from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget
from gui.quest_wizard import QuestWizard
from gui.map_editor import MapEditor
from gui.gamification_panel import GamificationPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quest Master — Гильдия пергаментов")
        self.resize(1000, 700)

        # Создаём виджеты
        self.quest_wizard = QuestWizard()
        self.quest_wizard.main_window_ref = self  # ← передаём ссылку
        self.map_editor = MapEditor()
        self.map_editor.main_window_ref = self
        self.gamification_panel = GamificationPanel()

        # Центральный виджет с вкладками
        central = QWidget()
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.addTab(self.quest_wizard, "🧙 Создать квест")
        self.tabs.addTab(self.map_editor, "🗺️ Редактор карт")
        self.tabs.addTab(self.gamification_panel, "🏆 Геймификация")
        layout.addWidget(self.tabs)
        central.setLayout(layout)
        self.setCentralWidget(central)

        # Подключаем обработчик переключения вкладок
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        if index == 1:
            quest_id = self.quest_wizard.current_quest_id
            if quest_id is not None:
                self.map_editor.set_quest_id(quest_id)
        elif index == 2:  # GamificationPanel
            self.gamification_panel.update_display()

    def notify_xp_earned(self):
        if hasattr(self, 'gamification_panel'):
            self.gamification_panel.refresh()