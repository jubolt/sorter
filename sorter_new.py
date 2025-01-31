import sys
import os
import shutil
import json
import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QFileDialog, QScrollArea
)

SETTINGS_FILE = "settings.json"
NUM_FIELDS = 20  # ← Измени это число, чтобы задать количество полей
LOG_FOLDER = "logs"  # Папка для хранения логов

class FileMoverApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File Mover & Copier")
        self.setGeometry(200, 200, 900, 600)

        self.main_layout = QVBoxLayout()

        # Добавляем область прокрутки
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.scroll_widget = QWidget()
        self.layout = QVBoxLayout(self.scroll_widget)

        self.entries = []

        self.load_settings()  # Загружаем сохраненные настройки

        # Если полей меньше, чем нужно — добавляем пустые
        while len(self.entries) < NUM_FIELDS:
            self.add_entry()

        self.scroll_area.setWidget(self.scroll_widget)
        self.main_layout.addWidget(self.scroll_area)

        self.setLayout(self.main_layout)

        # Создаем папку для логов, если ее нет
        if not os.path.exists(LOG_FOLDER):
            os.makedirs(LOG_FOLDER)

    def add_entry(self, src_text="", dest_text=""):
        """Добавляет строку с путями, кнопками и загружает сохраненные данные"""
        hbox = QHBoxLayout()

        src_input = QLineEdit(self)
        src_input.setText(src_text)

        dest_input = QLineEdit(self)
        dest_input.setText(dest_text)

        btn_browse_src = QPushButton("...")
        btn_browse_src.clicked.connect(lambda: self.browse_folder(src_input))  # Выбор папки

        btn_browse_dest = QPushButton("...")
        btn_browse_dest.clicked.connect(lambda: self.browse_folder(dest_input))  # Выбор папки

        btn_copy = QPushButton("Копiювати")
        btn_copy.clicked.connect(lambda: self.copy_files(src_input.text(), dest_input.text()))

        btn_move = QPushButton("Перемiстити")
        btn_move.clicked.connect(lambda: self.move_files(src_input.text(), dest_input.text()))

        hbox.addWidget(QLabel("Звiдки:"))
        hbox.addWidget(src_input)
        hbox.addWidget(btn_browse_src)
        hbox.addWidget(QLabel("Куди:"))
        hbox.addWidget(dest_input)
        hbox.addWidget(btn_browse_dest)
        hbox.addWidget(btn_copy)
        hbox.addWidget(btn_move)

        self.entries.append((src_input, dest_input))
        self.layout.addLayout(hbox)

    def browse_folder(self, line_edit):
        """Диалог выбора папки"""
        folder_path = QFileDialog.getExistingDirectory(self, "Оберiть папку")
        if folder_path:
            line_edit.setText(folder_path)
            self.save_settings()

    def copy_files(self, src, dest):
        """
        Копирует файлы из src в dest по алгоритму с ключевыми словами.
        Сохраняет результаты в лог-файл.
        """
        if os.path.isdir(src) and os.path.isdir(dest):
            move_count = {}
            # Проходим по всем файлам в папке src
            for filename in os.listdir(src):
                file_path = os.path.join(src, filename)

                if os.path.isfile(file_path):
                    # Проходим по всем папкам в dest
                    for folder_name in os.listdir(dest):
                        folder_path = os.path.join(dest, folder_name)

                        if os.path.isdir(folder_path):
                            # Извлекаем часть после "_", если она есть
                            folder_parts = folder_name.split('_', 1)
                            keyword = folder_parts[1] if len(folder_parts) > 1 else folder_parts[0]

                            # Проверяем, содержится ли keyword в названии файла
                            if keyword in filename:
                                dest_file_path = os.path.join(folder_path, filename)
                                shutil.copy(file_path, dest_file_path)
                                move_count[keyword] = move_count.get(keyword, 0) + 1

            # Логируем результаты
            self.log_results(move_count, "копiювання")

    def move_files(self, src, dest):
        """
        Перемещает файлы из src в dest по алгоритму с ключевыми словами.
        Сохраняет результаты в лог-файл.
        """
        if os.path.isdir(src) and os.path.isdir(dest):
            move_count = {}
            # Проходим по всем файлам в папке src
            for filename in os.listdir(src):
                file_path = os.path.join(src, filename)

                if os.path.isfile(file_path):
                    # Проходим по всем папкам в dest
                    for folder_name in os.listdir(dest):
                        folder_path = os.path.join(dest, folder_name)

                        if os.path.isdir(folder_path):
                            # Извлекаем часть после "_", если она есть
                            folder_parts = folder_name.split('_', 1)
                            keyword = folder_parts[1] if len(folder_parts) > 1 else folder_parts[0]

                            # Проверяем, содержится ли keyword в названии файла
                            if keyword in filename:
                                dest_file_path = os.path.join(folder_path, filename)
                                shutil.copy2(file_path, dest_file_path)
                                os.remove(file_path)
                                move_count[keyword] = move_count.get(keyword, 0) + 1

            # Логируем результаты
            self.log_results(move_count, "перемiщення")

    def log_results(self, move_count, operation):
        """
        Сохраняет результаты операции (копирования или перемещения) в лог-файл.
        """
        date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_file_path = os.path.join(LOG_FOLDER, f'log_{date}.txt')

        with open(log_file_path, 'w', encoding='utf8') as log_file:
            for folder_name, count in move_count.items():
                log_file.write(f'В папку "{folder_name}" {operation} {count} файлов\n')

    def save_settings(self):
        """Сохраняет пути в settings.json"""
        data = [{"src": src.text(), "dest": dest.text()} for src, dest in self.entries]
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def load_settings(self):
        """Загружает пути из settings.json, если файл существует"""
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for entry in data:
                    self.add_entry(entry["src"], entry["dest"])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileMoverApp()
    window.show()
    sys.exit(app.exec())