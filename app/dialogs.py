from PyQt6.QtWidgets import QDialog, QVBoxLayout, QColorDialog
from PyQt6.QtCore import QDate, QTime
from PyQt6.QtGui import QColor
from .utils import load_ui


class TaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = load_ui("task_dialog.ui")
        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)
        self.setWindowTitle("Новая задача")

        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.ui.dateDeadline.setDate(QDate.currentDate())

    def get_data(self):
        priority_map = {"Низкий": 1, "Средний": 2, "Высокий": 3}
        return {
            "title": self.ui.editTitle.text().strip(),
            "description": self.ui.editDescription.toPlainText().strip(),
            "priority": priority_map.get(self.ui.comboPriority.currentText(), 2),
            "due_date": self.ui.dateDeadline.date().toString("yyyy-MM-dd"),
            "category": self.ui.editCategory.text().strip(),
        }

    def set_data(self, data):
        self.ui.editTitle.setText(data.get("title", ""))
        self.ui.editDescription.setPlainText(data.get("description", ""))
        priority_text = {1: "Низкий", 2: "Средний", 3: "Высокий"}.get(
            data.get("priority", 2), "Средний"
        )
        idx = self.ui.comboPriority.findText(priority_text)
        if idx != -1:
            self.ui.comboPriority.setCurrentIndex(idx)
        if data.get("due_date"):
            self.ui.dateDeadline.setDate(
                QDate.fromString(data["due_date"], "yyyy-MM-dd")
            )
        self.ui.editCategory.setText(data.get("category", ""))


class EventDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = load_ui("event_dialog.ui")
        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)
        self.setWindowTitle("Новое событие")

        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.ui.dateEvent.setDate(QDate.currentDate())
        self.ui.timeEvent.setTime(QTime.currentTime())

        self.selected_color = "#4A90E2"
        self.ui.btnPickColor.clicked.connect(self.pick_color)
        self.update_color_button()

    def pick_color(self):
        color = QColorDialog.getColor(
            QColor(self.selected_color), self, "Выберите цвет"
        )
        if color.isValid():
            self.selected_color = color.name()
            self.update_color_button()

    def update_color_button(self):
        self.ui.btnPickColor.setStyleSheet(
            f"background-color: {self.selected_color}; color: white;"
        )

    def get_data(self):
        return {
            "title": self.ui.editTitle.text().strip(),
            "description": self.ui.editDescription.toPlainText().strip(),
            "date": self.ui.dateEvent.date().toString("yyyy-MM-dd"),
            "time": self.ui.timeEvent.time().toString("HH:mm"),
            "color": self.selected_color,
            "is_recurring": self.ui.checkRecurring.isChecked(),
        }

    def set_data(self, data):
        self.ui.editTitle.setText(data.get("title", ""))
        self.ui.editDescription.setPlainText(data.get("description", ""))
        if data.get("date"):
            self.ui.dateEvent.setDate(QDate.fromString(data["date"], "yyyy-MM-dd"))
        if data.get("time"):
            self.ui.timeEvent.setTime(QTime.fromString(data["time"], "HH:mm"))
        self.selected_color = data.get("color", "#4A90E2")
        self.update_color_button()
        self.ui.checkRecurring.setChecked(data.get("is_recurring", False))
