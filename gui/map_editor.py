import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QComboBox, QLineEdit, QFileDialog, QLabel
)
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QFontDatabase, QPixmap, QImage
)
from PyQt6.QtCore import Qt, QPoint, QRectF
from pathlib import Path
from core.gamification import GamificationManager


class MapScene:
    """Хранит все объекты карты."""
    def __init__(self):
        self.objects = []
        self.background = None

    def add_object(self, obj):
        self.objects.append(obj)

    def undo(self):
        if self.objects:
            return self.objects.pop()
        return None

    def clear(self):
        self.objects.clear()

    def save_to_image(self, width=800, height=600, path="map.png"):
        image = QImage(width, height, QImage.Format.Format_RGB32)
        image.fill(QColor("#f4e4bc"))

        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.background:
            scaled = self.background.scaled(
                width, height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(0, 0, scaled)

        # Отрисовка всех объектов
        for obj in self.objects:
            if obj["type"] == "path":
                pen = QPen(QColor("#8B4513"), 3)
                painter.setPen(pen)
                painter.drawPolyline(obj["points"])
            elif obj["type"] == "marker":
                brush = QBrush(QColor(obj["color"]))
                painter.setBrush(brush)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(obj["pos"].x() - 8, obj["pos"].y() - 8, 16, 16)
            elif obj["type"] == "text":
                font = QFont("Uncial Antiqua", 10)
                painter.setFont(font)
                painter.setPen(QColor("black"))
                painter.drawText(obj["pos"], obj["text"])

        painter.end()
        image.save(path)


class MapEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.scene = MapScene()
        self.current_quest_id = None
        self.drawing = False
        self.last_point = QPoint()
        self.current_path = []

        # Загрузка шрифта, если есть
        font_path = Path(__file__).parent.parent / "assets" / "fonts" / "UncialAntiqua-Regular.ttf"
        if font_path.exists():
            QFontDatabase.addApplicationFont(str(font_path))

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # Панель инструментов
        tools_layout = QHBoxLayout()

        self.tool_combo = QComboBox()
        self.tool_combo.addItems(["Рисовать путь", "Город", "Подземелье", "Таверна", "Текст"])
        tools_layout.addWidget(QLabel("Инструмент:"))
        tools_layout.addWidget(self.tool_combo)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Текст для метки")
        self.text_input.setVisible(False)
        tools_layout.addWidget(self.text_input)

        self.tool_combo.currentTextChanged.connect(self.on_tool_changed)

        self.load_bg_btn = QPushButton("Загрузить фон")
        self.load_bg_btn.clicked.connect(self.load_background)
        tools_layout.addWidget(self.load_bg_btn)

        self.save_btn = QPushButton("Сохранить карту")
        self.save_btn.clicked.connect(self.save_map)
        tools_layout.addWidget(self.save_btn)

        self.undo_btn = QPushButton("Отмена")
        self.undo_btn.clicked.connect(self.undo)
        tools_layout.addWidget(self.undo_btn)

        main_layout.addLayout(tools_layout)

        self.canvas = MapCanvas(self)
        main_layout.addWidget(self.canvas)

        self.setLayout(main_layout)

    def on_tool_changed(self, tool):
        self.text_input.setVisible(tool == "Текст")

    def set_quest_id(self, quest_id):
        """Вызывается извне, когда выбран квест."""
        self.current_quest_id = quest_id

    def load_background(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение фона", "", "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.scene.background = QPixmap(file_path)
            self.canvas.update()

    def save_map(self):
        if not self.current_quest_id:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", "Сначала создайте или выберите квест!")
            return

        timestamp = self.canvas.get_timestamp()
        filename = f"map_{self.current_quest_id}_{timestamp}.png"
        path = Path("./parchments") / filename
        path.parent.mkdir(exist_ok=True)

        self.scene.save_to_image(800, 600, str(path))
        GamificationManager().add_xp(5, "Карта сохранена")
        # Начисление XP (можно вызвать извне)
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Успех", f"Карта сохранена:\n{path}")


    def undo(self):
        removed = self.scene.undo()
        if removed:
            self.canvas.update()

    def start_drawing(self, pos):
        tool = self.tool_combo.currentText()
        if tool == "Рисовать путь":
            self.drawing = True
            self.current_path = [pos]
        elif tool in ["Город", "Подземелье", "Таверна"]:
            color_map = {
                "Город": "#2E8B57",       # Зелёный
                "Подземелье": "#DC143C",  # Красный
                "Таверна": "#FFD700"      # Жёлтый
            }
            self.scene.add_object({
                "type": "marker",
                "pos": pos,
                "color": color_map[tool]
            })
            self.canvas.update()
        elif tool == "Текст":
            text = self.text_input.text().strip()
            if text:
                self.scene.add_object({
                    "type": "text",
                    "pos": pos,
                    "text": text
                })
                self.text_input.clear()
                self.canvas.update()

    def continue_drawing(self, pos):
        if self.drawing:
            self.current_path.append(pos)
            self.canvas.update()

    def finish_drawing(self):
        if self.drawing and len(self.current_path) > 1:
            self.scene.add_object({
                "type": "path",
                "points": self.current_path.copy()
            })
        self.drawing = False
        self.current_path.clear()


class MapCanvas(QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setFixedSize(800, 600)
        self.setStyleSheet("background-color: #f4e4bc;")

    def get_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Фоновое изображение
        if self.editor.scene.background:
            scaled = self.editor.scene.background.scaled(
                self.width(), self.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(0, 0, scaled)
        else:
            painter.fillRect(self.rect(), QColor("#f4e4bc"))

        # Объекты сцены
        for obj in self.editor.scene.objects:
            if obj["type"] == "path":
                pen = QPen(QColor("#8B4513"), 3)
                painter.setPen(pen)
                if len(obj["points"]) > 1:
                    painter.drawPolyline(obj["points"])
            elif obj["type"] == "marker":
                brush = QBrush(QColor(obj["color"]))
                painter.setBrush(brush)
                painter.setPen(Qt.PenStyle.NoPen)
                pt = obj["pos"]
                painter.drawEllipse(pt.x() - 8, pt.y() - 8, 16, 16)
            elif obj["type"] == "text":
                font = QFont("Uncial Antiqua", 10)
                painter.setFont(font)
                painter.setPen(QColor("black"))
                painter.drawText(obj["pos"], obj["text"])

        if self.editor.drawing and len(self.editor.current_path) > 1:
            pen = QPen(QColor("#8B4513"), 3, Qt.PenStyle.DotLine)
            painter.setPen(pen)
            painter.drawPolyline(self.editor.current_path)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.editor.start_drawing(event.pos())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.editor.continue_drawing(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.editor.finish_drawing()