import re
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QSpinBox, QTextEdit, QDateTimeEdit, QPushButton,
    QMessageBox, QCheckBox
)
from PyQt6.QtCore import QDateTime, Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from core.database import save_quest, DB_PATH
from core.gamification import GamificationManager
import sqlite3


class QuestWizard(QWidget):
    def __init__(self):
        super().__init__()
        self.current_quest_id = None
        self.setup_ui()
        self.setup_connections()
        self.setup_shortcuts()
        self.main_window_ref = None

    def setup_ui(self):
        layout = QVBoxLayout()

        # Название квеста
        self.title_edit = QLineEdit()
        self.title_edit.setMaxLength(50)
        layout.addWidget(QLabel("Название квеста (макс. 50 симв.):"))
        layout.addWidget(self.title_edit)

        # Сложность
        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["Лёгкий", "Средний", "Сложный", "Олимпийский"])
        layout.addWidget(QLabel("Сложность:"))
        layout.addWidget(self.diff_combo)

        # Наградา
        self.reward_spin = QSpinBox()
        self.reward_spin.setRange(10, 10000)
        layout.addWidget(QLabel("Награда (золотых):"))
        layout.addWidget(self.reward_spin)

        # Описание
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Введите описание (минимум 50 слов)...")
        layout.addWidget(QLabel("Описание:"))
        layout.addWidget(self.desc_edit)

        # Срок выполнения
        self.deadline_edit = QDateTimeEdit()
        self.deadline_edit.setDateTime(QDateTime.currentDateTime().addDays(7))
        self.deadline_edit.setDisplayFormat("dd.MM.yyyy HH:mm")
        layout.addWidget(QLabel("Срок выполнения:"))
        layout.addWidget(self.deadline_edit)

        # Кнопка создания
        self.create_btn = QPushButton("Создать квест")
        layout.addWidget(self.create_btn)

        # Выбор шаблона
        self.template_combo = QComboBox()
        self.template_combo.addItems([
            "royal_decree.html",
            "guild_contract.html",
            "ancient_scroll.html"
        ])
        layout.addWidget(QLabel("Шаблон документа:"))
        layout.addWidget(self.template_combo)

        # Кнопки экспорта
        export_layout = QHBoxLayout()
        self.pdf_btn = QPushButton("Экспорт в PDF")
        self.docx_btn = QPushButton("Экспорт в DOCX")
        export_layout.addWidget(self.pdf_btn)
        export_layout.addWidget(self.docx_btn)
        layout.addLayout(export_layout)

        # Чекбокс QR-кода
        self.qr_checkbox = QCheckBox("Добавить QR-код с URL квеста")
        layout.addWidget(self.qr_checkbox)

        self.setLayout(layout)

    def setup_connections(self):
        self.title_edit.textChanged.connect(self.auto_save)
        self.diff_combo.currentTextChanged.connect(self.auto_save)
        self.reward_spin.valueChanged.connect(self.auto_save)
        self.desc_edit.textChanged.connect(self.auto_save)
        self.deadline_edit.dateTimeChanged.connect(self.auto_save)

        self.create_btn.clicked.connect(self.create_quest)
        self.pdf_btn.clicked.connect(self.export_pdf)
        self.docx_btn.clicked.connect(self.export_docx)

    def setup_shortcuts(self):
        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut.activated.connect(self.create_quest)

    def auto_save(self):
        title = self.title_edit.text().strip()
        description = self.desc_edit.toPlainText().strip()
        if title and len(re.findall(r'\b\w+\b', description)) >= 50:
            deadline = self.deadline_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            self.current_quest_id = save_quest(
                title=title,
                difficulty=self.diff_combo.currentText(),
                reward=self.reward_spin.value(),
                description=description,
                deadline=deadline
            )

    def validate_fields(self):
        valid = True
        title = self.title_edit.text().strip()
        desc = self.desc_edit.toPlainText().strip()
        words = len(re.findall(r'\b\w+\b', desc))

        if not title:
            self.title_edit.setStyleSheet("border: 2px solid red; padding: 2px;")
            valid = False
        else:
            self.title_edit.setStyleSheet("")

        if words < 50:
            self.desc_edit.setStyleSheet("border: 2px solid red; padding: 2px;")
            valid = False
        else:
            self.desc_edit.setStyleSheet("")

        return valid

    def create_quest(self):
        if self.validate_fields():
            GamificationManager().add_xp(3, "Создан квест")
            if self.main_window_ref:
                self.main_window_ref.notify_xp_earned()
            QMessageBox.information(self, "Успех", "Квест успешно создан!")
        else:
            QMessageBox.warning(self, "Ошибка", "Заполните название и описание (минимум 50 слов).")

    def _get_quest_by_id(self, quest_id):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "SELECT id, title, difficulty, reward, description, deadline FROM quests WHERE id = ?",
            (quest_id,)
        )
        row = cur.fetchone()
        conn.close()
        if row:
            return {
                "id": row[0],
                "title": row[1],
                "difficulty": row[2],
                "reward": row[3],
                "description": row[4],
                "deadline": row[5]
            }
        return None

    def export_pdf(self):
        if not self.current_quest_id:
            QMessageBox.warning(self, "Ошибка", "Сначала создайте квест!")
            return
        try:
            from core.template_engine import export_to_pdf
            quest_data = self._get_quest_by_id(self.current_quest_id)
            path = export_to_pdf(
                quest_data,
                template=self.template_combo.currentText(),
                with_qr=self.qr_checkbox.isChecked()
            )
            GamificationManager().add_xp(2, "Экспорт в PDF")
            if self.main_window_ref:
                self.main_window_ref.notify_xp_earned()
            QMessageBox.information(self, "Успех", f"PDF сохранён:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать PDF:\n{str(e)}")

    def export_docx(self):
        if not self.current_quest_id:
            QMessageBox.warning(self, "Ошибка", "Сначала создайте квест!")
            return
        try:
            from core.template_engine import export_to_docx
            quest_data = self._get_quest_by_id(self.current_quest_id)
            path = export_to_docx(
                quest_data,
                template=self.template_combo.currentText(),
                with_qr=self.qr_checkbox.isChecked()
            )
            GamificationManager().add_xp(2, "Экспорт в DOCX")
            if self.main_window_ref:
                self.main_window_ref.notify_xp_earned()
            QMessageBox.information(self, "Успех", f"DOCX сохранён:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать DOCX:\n{str(e)}")