import sys
import os
import uuid
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QTextEdit, QLabel, QFileDialog)
from PyQt5.QtCore import Qt

class EblanPluginCompiler(QMainWindow):
    def __init__(self):
        super().__init__()
        self.console = None  # Инициализация console как None
        print("[INFO] Инициализация интерфейса...")  # Логирование в терминал до создания console

        try:
            self.setWindowTitle("EblanPlug Community - Компилятор .eblp плагинов")
            self.setGeometry(100, 100, 600, 400)

            # Основной виджет и layout
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            main_layout = QVBoxLayout(central_widget)
            print("[INFO] Основной layout создан")

            # Метка статуса
            self.status_label = QLabel("Статус: Ожидание выбора файла")
            self.status_label.setStyleSheet("font-size: 16px;")
            main_layout.addWidget(self.status_label)
            print("[INFO] Метка статуса создана")

            # Кнопка открытия файла
            self.open_button = QPushButton("Открыть .txt файл")
            self.open_button.clicked.connect(self.open_txt)
            main_layout.addWidget(self.open_button)
            print("[INFO] Кнопка открытия файла создана")

            # Кнопка компиляции
            self.compile_button = QPushButton("Компилировать в .eblp")
            self.compile_button.clicked.connect(self.compile_eblp)
            self.compile_button.setEnabled(False)  # Отключена до выбора файла
            main_layout.addWidget(self.compile_button)
            print("[INFO] Кнопка компиляции создана")

            # Консоль отладки
            self.console = QTextEdit()
            self.console.setReadOnly(True)
            main_layout.addWidget(self.console)
            self.log("Привет! Ты попал в компилятор плагинов подробнее: https://twgood.serv00.net/browser/S/docs", "SUCCESS")

            # Текущий файл
            self.current_file = None
            self.current_plugin = None

        except Exception as e:
            self.log(f"Ошибка инициализации интерфейса: {str(e)}", "ERROR")
            self.status_label.setText("❌ Ошибка инициализации интерфейса")
            self.status_label.setStyleSheet("color: red; font-size: 16px;")

    def log(self, message, level="INFO"):
        color = {"INFO": "black", "ERROR": "red", "SUCCESS": "green"}.get(level, "black")
        if self.console:  # Проверка наличия console
            self.console.append(f'<span style="color:{color};">[{level}] {message}</span>')
        print(f"[{level}] {message}")  # Логи в терминал

    def open_txt(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите .txt файл", "", "Text Files (*.txt)")
        if file_path:
            self.current_file = file_path
            self.compile_button.setEnabled(True)
            self.log(f"Открыт файл: {file_path}", "SUCCESS")
            self.status_label.setText("Статус: Замечаний ненайдено. Файл готов")
            self.status_label.setStyleSheet("color: black; font-size: 16px;")
            self.parse_txt(file_path)

    def parse_txt(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            plugin = {}
            # Парсинг полей .eblp
            name_match = re.search(r'name=\[(.*?)\]', content, re.DOTALL)
            ver_match = re.search(r'ver=\[(.*?)\]', content, re.DOTALL)
            description_match = re.search(r'description=\[(.*?)\]', content, re.DOTALL)
            author_match = re.search(r'author=\[(.*?)\]', content, re.DOTALL)
            id_match = re.search(r'id=\[(.*?)\]', content, re.DOTALL)
            js_match = re.search(r'js=\[(.*?)\]', content, re.DOTALL)

            # Проверка обязательных полей
            errors = []
            if not name_match or not name_match.group(1).strip():
                errors.append("Название не указано или пустое")
            if not ver_match or not re.match(r"^\d+\.\d+$", ver_match.group(1).strip()):
                errors.append("Версия не указана или не в формате 0.0")
            if not description_match or not description_match.group(1).strip():
                errors.append("Описание не указано или пустое")
            if not author_match or not author_match.group(1).strip():
                errors.append("Автор не указан или пустой")
            if not js_match or not js_match.group(1).strip():
                errors.append("JavaScript код не указан или пустой")

            if errors:
                self.status_label.setText("❌ Ошибка: " + "; ".join(errors))
                self.status_label.setStyleSheet("color: red; font-size: 16px;")
                for error in errors:
                    self.log(error, "ERROR")
                self.compile_button.setEnabled(False)
                self.current_plugin = None
                return

            plugin['name'] = name_match.group(1).strip()
            plugin['ver'] = ver_match.group(1).strip()
            plugin['description'] = description_match.group(1).strip()
            plugin['author'] = author_match.group(1).strip()
            plugin['id'] = id_match.group(1).strip() if id_match and re.match(r"^eblan\.[a-zA-Z0-9-]+$", id_match.group(1).strip()) else f"eblan.{str(uuid.uuid4())[:8]}"
            plugin['js'] = js_match.group(1).strip()

            self.current_plugin = plugin
            self.log(f"Файл распарсен: {plugin['name']} (ID: {plugin['id']})", "SUCCESS")
            self.status_label.setText("✅ Файл готов к компиляции")
            self.status_label.setStyleSheet("color: green; font-size: 16px;")

        except Exception as e:
            self.status_label.setText("❌ Ошибка чтения файла")
            self.status_label.setStyleSheet("color: red; font-size: 16px;")
            self.log(f"Ошибка чтения файла: {str(e)}", "ERROR")
            self.compile_button.setEnabled(False)
            self.current_plugin = None

    def compile_eblp(self):
        if not self.current_plugin:
            self.status_label.setText("❌ Нет данных для компиляции")
            self.status_label.setStyleSheet("color: red; font-size: 16px;")
            self.log("Ошибка: Нет данных для компиляции", "ERROR")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить .eblp файл", "", "EBLAN Plugin Files (*.eblp)")
        if file_path:
            try:
                if not file_path.endswith('.eblp'):
                    file_path += '.eblp'
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"name=[{self.current_plugin['name']}]\n")
                    f.write(f"ver=[{self.current_plugin['ver']}]\n")
                    f.write(f"description=[{self.current_plugin['description']}]\n")
                    f.write(f"author=[{self.current_plugin['author']}]\n")
                    f.write(f"id=[{self.current_plugin['id']}]\n")
                    f.write(f"js=[\n{self.current_plugin['js']}\n]")

                self.status_label.setText("✅ Готово")
                self.status_label.setStyleSheet("color: green; font-size: 16px;")
                self.log(f"Плагин скомпилирован: {file_path}", "SUCCESS")
                self.compile_button.setEnabled(False)
                self.current_plugin = None

            except Exception as e:
                self.status_label.setText("❌ Ошибка сохранения файла")
                self.status_label.setStyleSheet("color: red; font-size: 16px;")
                self.log(f"Ошибка сохранения: {str(e)}", "ERROR")

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        window = EblanPluginCompiler()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"[FATAL] Ошибка запуска приложения: {str(e)}")
