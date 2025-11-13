import csv
from PyQt6.QtWidgets import (
    QMainWindow,
    QTableWidgetItem,
    QListWidgetItem,
    QMessageBox,
    QFileDialog,
)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QColor, QTextCharFormat, QPalette
from .utils import load_ui
from .dialogs import TaskDialog, EventDialog
from database.db_manager import DatabaseManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = load_ui("main_window.ui")
        self.setCentralWidget(self.ui)

        self.ui.actionToggleTheme.triggered.connect(self.toggle_theme)
        self.ui.actionExportTasks.triggered.connect(lambda: self.export_data("tasks"))
        self.ui.actionExportEvents.triggered.connect(lambda: self.export_data("events"))
        self.ui.actionExportNotes.triggered.connect(lambda: self.export_data("notes"))

        self.ui.btnAddTask.clicked.connect(self.add_task)
        self.ui.tableTasks.cellClicked.connect(self.on_task_cell_clicked)
        self.ui.btnAddEvent.clicked.connect(self.add_event)
        self.ui.listNotes.itemSelectionChanged.connect(self.load_selected_note)
        self.ui.btnSaveNote.clicked.connect(self.save_note)
        self.ui.btnDeleteNote.clicked.connect(self.delete_note)
        self.ui.comboTaskFilter.currentTextChanged.connect(self.refresh_tasks_table)

        self.db = DatabaseManager()
        self.tasks = self.db.load_tasks()
        self.events = self.db.load_events()
        self.notes = self.db.load_notes()
        self.dark_mode = False

        self.refresh_tasks_table()
        self.refresh_events_calendar()
        self.refresh_notes_list()

    # // === Задачи ===
    def add_task(self):
        dialog = TaskDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if data["title"]:
                data["completed"] = False
                self.tasks.append(data)
                self.refresh_tasks_table()

    def on_task_cell_clicked(self, row, column):
        if column == 0:
            filter_mode = self.ui.comboTaskFilter.currentText()
            visible_index = 0
            real_index = None
            for i, task in enumerate(self.tasks):
                show = (
                    filter_mode == "Все"
                    or (filter_mode == "Активные" and not task["completed"])
                    or (filter_mode == "Выполненные" and task["completed"])
                )
                if show:
                    if visible_index == row:
                        real_index = i
                        break
                    visible_index += 1
            if real_index is not None:
                self.tasks[real_index]["completed"] = not self.tasks[real_index][
                    "completed"
                ]
                self.refresh_tasks_table()

    def refresh_tasks_table(self):
        filter_mode = self.ui.comboTaskFilter.currentText()
        filtered_tasks = []
        for task in self.tasks:
            if filter_mode == "Все":
                filtered_tasks.append(task)
            elif filter_mode == "Активные" and not task["completed"]:
                filtered_tasks.append(task)
            elif filter_mode == "Выполненные" and task["completed"]:
                filtered_tasks.append(task)

        table = self.ui.tableTasks
        table.setRowCount(len(filtered_tasks))
        for i, task in enumerate(filtered_tasks):
            item_done = QTableWidgetItem()
            item_done.setFlags(
                Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled
            )
            item_done.setCheckState(
                Qt.CheckState.Checked if task["completed"] else Qt.CheckState.Unchecked
            )
            table.setItem(i, 0, item_done)
            table.setItem(i, 1, QTableWidgetItem(task["title"]))
            table.setItem(
                i,
                2,
                QTableWidgetItem(
                    {1: "Низкий", 2: "Средний", 3: "Высокий"}.get(
                        task["priority"], "Средний"
                    )
                ),
            )
            table.setItem(i, 3, QTableWidgetItem(task["due_date"]))
            table.setItem(i, 4, QTableWidgetItem(task["category"]))

    # // === События ===
    def add_event(self):
        dialog = EventDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if data["title"]:
                self.events.append(data)
                self.refresh_events_calendar()

    def refresh_events_calendar(self):
        self.ui.calendarWidget.setDateTextFormat(QDate(), QTextCharFormat())
        for ev in self.events:
            date = QDate.fromString(ev["date"], "yyyy-MM-dd")
            fmt = self.ui.calendarWidget.dateTextFormat(date)
            fmt.setBackground(QColor(ev["color"]))
            self.ui.calendarWidget.setDateTextFormat(date, fmt)

        today = QDate.currentDate().toString("yyyy-MM-dd")
        today_events = [ev for ev in self.events if ev["date"] == today]
        self.ui.listEventsToday.clear()
        for ev in today_events:
            item = QListWidgetItem(f"{ev['time']} – {ev['title']}")
            item.setBackground(QColor(ev["color"]))
            item.setForeground(
                Qt.GlobalColor.white
                if QColor(ev["color"]).lightness() < 160
                else Qt.GlobalColor.black
            )
            self.ui.listEventsToday.addItem(item)

    # // === Заметки ===
    def refresh_notes_list(self):
        self.ui.listNotes.clear()
        for note in self.notes:
            self.ui.listNotes.addItem(note["title"])

    def load_selected_note(self):
        items = self.ui.listNotes.selectedItems()
        if not items:
            return
        title = items[0].text()
        note = next((n for n in self.notes if n["title"] == title), None)
        if note:
            self.ui.editNoteTitle.setText(note["title"])
            self.ui.textNoteContent.setPlainText(note["content"])

    def save_note(self):
        title = self.ui.editNoteTitle.text().strip()
        content = self.ui.textNoteContent.toPlainText().strip()
        if not title:
            QMessageBox.warning(self, "Ошибка", "Заголовок не может быть пустым.")
            return
        existing = next((n for n in self.notes if n["title"] == title), None)
        if existing:
            existing["content"] = content
        else:
            self.notes.append({"title": title, "content": content})
            self.refresh_notes_list()

    def delete_note(self):
        title = self.ui.editNoteTitle.text().strip()
        if not title:
            return
        self.notes = [n for n in self.notes if n["title"] != title]
        self.refresh_notes_list()
        self.ui.editNoteTitle.clear()
        self.ui.textNoteContent.clear()

    # // === Тема и экспорт ===
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            palette.setColor(QPalette.ColorRole.Highlight, QColor(142, 45, 197))
            palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        else:
            palette = self.style().standardPalette()
        self.setPalette(palette)
        self.ui.tabWidget.setPalette(palette)

    def export_data(self, data_type):
        filename, _ = QFileDialog.getSaveFileName(
            self, f"Экспорт {data_type}", "", "CSV Files (*.csv)"
        )
        if not filename:
            return

        try:
            if data_type == "tasks":
                with open(filename, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        [
                            "Выполнено",
                            "Заголовок",
                            "Приоритет",
                            "Дедлайн",
                            "Категория",
                            "Описание",
                        ]
                    )
                    for task in self.tasks:
                        writer.writerow(
                            [
                                "Да" if task["completed"] else "Нет",
                                task["title"],
                                {1: "Низкий", 2: "Средний", 3: "Высокий"}.get(
                                    task["priority"], "Средний"
                                ),
                                task["due_date"],
                                task["category"],
                                task["description"],
                            ]
                        )

            elif data_type == "events":
                with open(filename, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        ["Название", "Дата", "Время", "Цвет", "Повторяется", "Описание"]
                    )
                    for ev in self.events:
                        writer.writerow(
                            [
                                ev["title"],
                                ev["date"],
                                ev["time"],
                                ev["color"],
                                "Да" if ev["is_recurring"] else "Нет",
                                ev["description"],
                            ]
                        )

            elif data_type == "notes":
                with open(filename, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Заголовок", "Содержимое"])
                    for note in self.notes:
                        writer.writerow(
                            [note["title"], note["content"].replace("\n", "\\n")]
                        )

            QMessageBox.information(
                self,
                "Успех",
                f"{data_type.capitalize()} успешно экспортированы в:\n{filename}",
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось экспортировать:\n{str(e)}"
            )

    # // === Сохранение данных при закрытии ===
    def closeEvent(self, event):
        self.db.save_tasks(self.tasks)
        self.db.save_events(self.events)
        self.db.save_notes(self.notes)
        event.accept()
