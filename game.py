import sys
import random
import sqlite3
import hashlib
import json
import os
from PyQt5.QtWidgets import QMessageBox
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QDialog, QHBoxLayout, QRadioButton, 
    QButtonGroup, QTableWidget, QTableWidgetItem, 
    QHeaderView, QStackedWidget, QGroupBox, QSlider
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
import pygame
sqlite3.register_adapter(datetime, lambda dt: dt.isoformat())
sqlite3.register_converter("datetime", lambda val: datetime.fromisoformat(val.decode()))

class MainMenu(QWidget):
    def __init__(self, stacked_widget, game_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.game_widget = game_widget
        self.load_last_user()
        self.load_settings()
        self.init_ui()
        self.update_login_button()

    def load_settings(self):
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    self.settings = json.load(f)
            else:
                self.settings = {'volume': 50, 'music_volume': 50}
        except Exception:
            self.settings = {'volume': 50, 'music_volume': 50}

    def save_settings(self):
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f)

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)

        # Заголовок
        self.title_label = QLabel('''
            <span style="color: white;">Dr.Ist</span> 
            <span style="color: #4CAF50;">Game</span>
        ''')
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet('font-size: 40px; font-weight: bold; background-color: #1e1e1e; margin-bottom: 60px;')

        # Основные кнопки
        button_style = '''
            QPushButton {
                font-size: 30px; 
                padding: 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                min-width: 250px;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #3d8b40; }
        '''

        self.play_button = QPushButton('ИГРАТЬ')
        self.play_button.setStyleSheet(button_style)
        self.play_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))  # Изменяем индекс на экран выбора игры

        self.rating_button = QPushButton('РЕЙТИНГ')
        self.rating_button.setStyleSheet(button_style)
        self.rating_button.clicked.connect(self.show_rating)

        self.settings_button = QPushButton('НАСТРОЙКИ')
        self.settings_button.setStyleSheet(button_style)
        self.settings_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))

        self.exit_button = QPushButton('ВЫХОД')
        self.exit_button.setStyleSheet(button_style)
        self.exit_button.clicked.connect(QApplication.instance().quit)

        # Кнопка входа
        self.login_button = QPushButton('Войти в аккаунт')
        self.login_button.setStyleSheet('''
            QPushButton {
                font-size: 14px;
                color: #4CAF50;
                background: transparent;
                border: 1px solid #4CAF50;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover { background: rgba(76, 175, 80, 0.1); }
        ''')
        self.login_button.clicked.connect(self.show_login)

        # Организация макетов
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.play_button, 0, Qt.AlignHCenter)
        button_layout.addWidget(self.rating_button, 0, Qt.AlignHCenter)
        button_layout.addWidget(self.settings_button, 0, Qt.AlignHCenter)
        button_layout.addWidget(self.exit_button, 0, Qt.AlignHCenter)
        button_layout.setSpacing(20)

        # Нижняя панель для кнопки входа
        bottom_panel = QHBoxLayout()
        bottom_panel.addStretch()
        bottom_panel.addWidget(self.login_button)

        main_layout.addStretch()
        main_layout.addWidget(self.title_label)
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        main_layout.addLayout(bottom_panel)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #1a1a1a;")

    def start_game(self):
        self.game_widget.new_game()
        self.stacked_widget.setCurrentIndex(1)

    def show_login(self):
        login_dialog = QDialog(self)
        login_dialog.setWindowTitle("Вход / Регистрация")
        login_dialog.setStyleSheet(self.styleSheet())
        login_dialog.setFixedSize(400, 400)

        login_layout = QVBoxLayout()
        login_layout.setContentsMargins(20, 20, 20, 20)
        login_layout.setSpacing(15)

        self.auth_mode = QButtonGroup(login_dialog)
        login_rb = QRadioButton("Вход")
        reg_rb = QRadioButton("Регистрация")
        login_rb.setChecked(True)
        self.auth_mode.addButton(login_rb, 0)
        self.auth_mode.addButton(reg_rb, 1)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(login_rb)
        mode_layout.addWidget(reg_rb)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Имя пользователя")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Подтвердите пароль")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email (необязательно)")

        self.action_button = QPushButton("Войти")
        self.action_button.setStyleSheet('''
            QPushButton {
                font-size: 16px; padding: 10px;
                background: #4CAF50; color: white;
                border-radius: 5px; border: none;
            }
            QPushButton:hover { background: #45a049; }
        ''')

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-size: 14px;")
        self.error_label.setVisible(False)

        input_style = '''
            QLineEdit {
                font-size: 16px; padding: 8px;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                background: #333; color: white;
            }
        ''' if self.game_widget.is_dark_theme else '''
            QLineEdit {
                font-size: 16px; padding: 8px;
                border: 2px solid #2196F3;
                border-radius: 5px;
                background: white; color: black;
            }
        '''
        self.username_input.setStyleSheet(input_style)
        self.password_input.setStyleSheet(input_style)
        self.confirm_password_input.setStyleSheet(input_style)
        self.email_input.setStyleSheet(input_style)

        def update_ui():
            is_registration = reg_rb.isChecked()
            self.confirm_password_input.setVisible(is_registration)
            self.email_input.setVisible(is_registration)
            self.action_button.setText("Зарегистрироваться" if is_registration else "Войти")

        self.auth_mode.buttonClicked.connect(update_ui)
        self.action_button.clicked.connect(lambda: self.handle_auth(login_dialog))
        update_ui()

        login_layout.addLayout(mode_layout)
        login_layout.addWidget(self.username_input)
        login_layout.addWidget(self.password_input)
        login_layout.addWidget(self.confirm_password_input)
        login_layout.addWidget(self.email_input)
        login_layout.addWidget(self.action_button)
        login_layout.addWidget(self.error_label)

        login_dialog.setLayout(login_layout)
        login_dialog.exec_()

    def handle_auth(self, dialog):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        is_registration = self.auth_mode.checkedId() == 1

        if not username or not password:
            self.error_label.setText("Заполните все обязательные поля!")
            self.error_label.setVisible(True)
            return

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        if is_registration:
            confirm_password = self.confirm_password_input.text().strip()
            email = self.email_input.text().strip()

            if password != confirm_password:
                self.error_label.setText("Пароли не совпадают!")
                self.error_label.setVisible(True)
                return

            try:
                self.game_widget.cursor.execute(
                    "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                    (username, password_hash, email if email else None)
                )
                self.game_widget.conn.commit()
                QMessageBox.information(self, "Успех", "Регистрация прошла успешно!")
                dialog.accept()
            except sqlite3.IntegrityError:
                self.error_label.setText("Имя пользователя уже занято!")
                self.error_label.setVisible(True)
            return

        self.handle_login(username, password, dialog)

    def update_login_button(self):
        if self.game_widget.current_user:
            self.login_button.setText(f"Выйти ({self.game_widget.current_user[1]})")
            self.login_button.clicked.disconnect()
            self.login_button.clicked.connect(self.handle_logout)
        else:
            self.login_button.setText("Войти в аккаунт")
            self.login_button.clicked.disconnect()
            self.login_button.clicked.connect(self.show_login)

    def handle_login(self, username, password, dialog):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.game_widget.cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password_hash = ?", 
            (username, password_hash)
        )
        user = self.game_widget.cursor.fetchone()

        if user:
            self.game_widget.current_user = user
            with open('last_user.json', 'w') as f:
                json.dump({
                    'username': username,
                    'password_hash': password_hash
                }, f)
            QMessageBox.information(self, "Успех", f"Добро пожаловать, {username}!")
            self.update_login_button()
            dialog.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверное имя пользователя или пароль.")

    def handle_logout(self):
        self.game_widget.current_user = None
        if os.path.exists('last_user.json'):
            os.remove('last_user.json')
        QMessageBox.information(self, "Выход", "Вы успешно вышли из аккаунта.")
        self.update_login_button()

    def load_last_user(self):
        try:
            if os.path.exists('last_user.json'):
                with open('last_user.json', 'r') as f:
                    data = json.load(f)
                    if data.get('username') and data.get('password_hash'):
                        self.game_widget.cursor.execute(
                            "SELECT * FROM users WHERE username = ? AND password_hash = ?",
                            (data['username'], data['password_hash'])
                        )
                        user = self.game_widget.cursor.fetchone()
                        if user:
                            self.game_widget.current_user = user
                            return True
        except Exception as e:
            print(f"Ошибка загрузки последнего пользователя: {e}")
        return False

    def show_settings(self):
        self.stacked_widget.setCurrentIndex(2)

    def show_rating(self):
        self.game_widget.last_screen = 0  # Сохраняем индекс главного меню
        self.stacked_widget.setCurrentIndex(3)

class SettingsScreen(QWidget):
    def __init__(self, stacked_widget, game_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.game_widget = game_widget
        self.settings = game_widget.settings
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        title = QLabel("⚙️ НАСТРОЙКИ")
        title.setStyleSheet('font-size: 40px; font-weight: bold; background-color: #1e1e1e; margin-bottom: 60px;')
        title.setAlignment(Qt.AlignCenter)

        # Группа настроек звуковых эффектов
        effects_group = QGroupBox("ЗВУКОВЫЕ ЭФФЕКТЫ")
        effects_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                padding: 20px;
                margin-top: 15px;
            }
            QGroupBox::title {
                color: #4CAF50;
                padding: 0 10px;
            }
        """)
        effects_layout = QVBoxLayout()

        self.volume_label = QLabel(f"Громкость эффектов: {self.settings['volume']}%")
        self.volume_label.setStyleSheet("font-size: 16px; margin-bottom: 10px;")
        self.volume_label.setAlignment(Qt.AlignCenter)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(self.settings['volume'])
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 12px;
                background: #333333;
                margin: 2px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal {
                background-color: #4CAF50;
                border: none;
                width: 24px;
                margin: -8px 0;
                border-radius: 12px;
            }
        """)
        self.volume_slider.valueChanged.connect(self.update_volume)

        effects_layout.addWidget(self.volume_label)
        effects_layout.addWidget(self.volume_slider)
        effects_group.setLayout(effects_layout)

        # Группа настроек громкости музыки
        music_group = QGroupBox("ГРОМКОСТЬ МУЗЫКИ")
        music_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                padding: 20px;
                margin-top: 15px;
            }
            QGroupBox::title {
                color: #4CAF50;
                padding: 0 10px;
            }
        """)
        music_layout = QVBoxLayout()

        self.music_volume_label = QLabel(f"Громкость музыки: {self.settings.get('music_volume', 50)}%")
        self.music_volume_label.setStyleSheet("font-size: 16px; margin-bottom: 10px;")
        self.music_volume_label.setAlignment(Qt.AlignCenter)

        self.music_volume_slider = QSlider(Qt.Horizontal)
        self.music_volume_slider.setMinimum(0)
        self.music_volume_slider.setMaximum(100)
        self.music_volume_slider.setValue(self.settings.get('music_volume', 50))
        self.music_volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 12px;
                background: #333333;
                margin: 2px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal {
                background-color: #4CAF50;
                border: none;
                width: 24px;
                margin: -8px 0;
                border-radius: 12px;
            }
        """)
        self.music_volume_slider.valueChanged.connect(self.update_music_volume)

        music_layout.addWidget(self.music_volume_label)
        music_layout.addWidget(self.music_volume_slider)
        music_group.setLayout(music_layout)

        back_button = QPushButton("ВЕРНУТЬСЯ В МЕНЮ")
        back_button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                padding: 15px 30px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                min-width: 200px;
            }
            QPushButton:hover {
                background: #45a049;
            }
        """)
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        main_layout.addWidget(title)
        main_layout.addWidget(effects_group)
        main_layout.addWidget(music_group)  # Добавляем группу громкости музыки
        main_layout.addStretch()
        main_layout.addWidget(back_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #1a1a1a; color: white;")

    def update_volume(self, value):
        self.settings['volume'] = value
        self.volume_label.setText(f"Громкость эффектов: {value}%")
        volume = value / 100.0
        self.game_widget.win_sound.set_volume(volume)
        self.game_widget.lose_sound.set_volume(volume)
        self.game_widget.record_sound.set_volume(volume)
        self.save_settings()

    def update_music_volume(self, value):
        self.settings['music_volume'] = value
        self.music_volume_label.setText(f"Громкость музыки: {value}%")
        music_volume = value / 100.0
        pygame.mixer.music.set_volume(music_volume)
        self.save_settings()

    def save_settings(self):
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f)

class RatingScreen(QWidget):
    def __init__(self, stacked_widget, game_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.game_widget = game_widget
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        title = QLabel("🏆 ТАБЛИЦА РЕКОРДОВ 🏆")
        title.setStyleSheet('font-size: 40px; font-weight: bold; background-color: #1e1e1e; margin-bottom: 20px;')
        title.setAlignment(Qt.AlignCenter)

        # Добавляем переключатель игр
        self.games_group = QButtonGroup(self)
        games_layout = QHBoxLayout()
        games_layout.setContentsMargins(0, 0, 0, 10)  # Уменьшаем отступ снизу
        
        guess_number_rb = QRadioButton("УГАДАЙ ЧИСЛО")
        bulls_cows_rb = QRadioButton("БЫКИ И КОРОВЫ")
        
        radio_style = """
            QRadioButton {
                font-size: 16px;
                color: white;
                padding: 8px;
            }
            QRadioButton::indicator {
                width: 20px;
                height: 20px;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #4CAF50;
                border-radius: 10px;
            }
            QRadioButton::indicator:checked {
                background-color: #4CAF50;
                border: 2px solid #4CAF50;
                border-radius: 10px;
            }
        """
        
        guess_number_rb.setStyleSheet(radio_style)
        bulls_cows_rb.setStyleSheet(radio_style)
        
        guess_number_rb.setChecked(True)
        self.games_group.addButton(guess_number_rb, 0)
        self.games_group.addButton(bulls_cows_rb, 1)
        
        games_layout.addWidget(guess_number_rb)
        games_layout.addWidget(bulls_cows_rb)
        games_layout.setAlignment(Qt.AlignCenter)
        
        # Добавляем обработчик переключения
        self.games_group.buttonClicked.connect(self.switch_table)
        
        self.table = QTableWidget()
        self.table.setSelectionMode(QTableWidget.NoSelection)  # Отключаем выделение
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.verticalHeader().setDefaultSectionSize(35)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2D2D2D;
                color: white;
                gridline-color: #3D3D3D;
                border: none;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 3px 8px;
                border-bottom: 1px solid #3D3D3D;
            }
            QTableWidget::item:selected {
                background-color: transparent;
            }
            QTableWidget::item:alternate {
                background-color: #2D2D2D;
            }
            QTableWidget::item:!alternate {
                background-color: #333333;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                font-weight: bold;
                font-size: 15px;
                border: none;
            }
        """)

        self.update_table()

        back_button = QPushButton('НАЗАД')  # Меняем текст кнопки
        back_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 12px 24px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: #45a049;
            }
        """)
        back_button.clicked.connect(self.go_back)

        main_layout.addWidget(title)
        main_layout.addLayout(games_layout)  # Добавляем переключатель после заголовка
        main_layout.addWidget(self.table)
        main_layout.addWidget(back_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #1a1a1a; color: white;")

    def update_table(self):
        if hasattr(self, 'games_group') and self.games_group.checkedId() == 1:
            # Таблица для Быков и Коров
            try:
                self.game_widget.cursor.execute('''
                    SELECT player_name, attempts, COALESCE(score, 0) as score, record_date 
                    FROM bulls_cows_records 
                    ORDER BY score DESC, attempts, record_date DESC
                ''')
                results = self.game_widget.cursor.fetchall()
            except sqlite3.OperationalError:
                # Если возникла ошибка, используем запрос без score
                self.game_widget.cursor.execute('''
                    SELECT player_name, attempts, record_date 
                    FROM bulls_cows_records 
                    ORDER BY attempts, record_date DESC
                ''')
                # Преобразуем результаты, добавляя нулевые очки
                results = [(name, attempts, 0, date) for name, attempts, date in self.game_widget.cursor.fetchall()]
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(['ИГРОК', 'ХОДОВ', 'ОЧКИ', 'ДАТА'])
        else:
            # Таблица для Угадай число
            self.game_widget.cursor.execute('''
                SELECT player_name, level, attempts, record_date 
                FROM records 
                ORDER BY level, attempts, record_date DESC
            ''')
            results = self.game_widget.cursor.fetchall()
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(['ИГРОК', 'УРОВЕНЬ', 'ПОПЫТКИ', 'ДАТА'])
        
        self.table.setRowCount(len(results))
        
        if hasattr(self, 'games_group') and self.games_group.checkedId() == 1:
            # Заполнение для Быков и Коров
            for row, (name, attempts, score, date) in enumerate(results):
                player_item = QTableWidgetItem(name)
                if "Anonymous" not in name:
                    player_item.setForeground(QColor('#4CAF50'))
                else:
                    player_item.setForeground(QColor('#BBBBBB'))
                
                attempts_item = QTableWidgetItem(str(attempts))
                score_item = QTableWidgetItem(str(score))
                score_item.setForeground(QColor('#FFD700'))  # Золотой цвет для очков
                date_item = QTableWidgetItem(date.strftime("%d.%m.%Y %H:%M"))

                self.table.setItem(row, 0, player_item)
                self.table.setItem(row, 1, attempts_item)
                self.table.setItem(row, 2, score_item)
                self.table.setItem(row, 3, date_item)
        else:
            # Заполнение для Угадай число
            level_names = {
                1: '🟢 Легкий',
                2: '🟡 Средний',
                3: '🟠 Сложный',
                4: '🔴 PRO'
            }
            
            for row, (name, level, attempts, date) in enumerate(results):
                player_item = QTableWidgetItem(name)
                if "Anonymous" not in name:
                    player_item.setForeground(QColor('#4CAF50'))
                else:
                    player_item.setForeground(QColor('#BBBBBB'))
                
                level_item = QTableWidgetItem(level_names.get(level, 'Неизвестно'))
                level_item.setForeground(QColor('white'))
                
                attempts_item = QTableWidgetItem(str(attempts))
                attempts_item.setForeground(QColor('white'))
                
                date_item = QTableWidgetItem(date.strftime("%d.%m.%Y %H:%M"))
                date_item.setForeground(QColor('white'))

                self.table.setItem(row, 0, player_item)
                self.table.setItem(row, 1, level_item)
                self.table.setItem(row, 2, attempts_item)
                self.table.setItem(row, 3, date_item)

    def switch_table(self):
        self.update_table()

    def showEvent(self, event):
        super().showEvent(event)
        self.update_table()

    def go_back(self):
        self.stacked_widget.setCurrentIndex(self.game_widget.last_screen)

class NumberGuessingGamePRO(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.current_level = 1
        self.max_number = 10
        self.attempts = 0
        self.max_attempts = 5
        self.secret_number = 0
        self.is_dark_theme = True
        self.current_user = None
        self.load_settings()
        self.init_db()
        self.init_sound()
        self.init_ui()
        self.new_game()

    def load_settings(self):
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    self.settings = json.load(f)
            else:
                self.settings = {'volume': 50, 'music_volume': 50}
        except Exception:
            self.settings = {'volume': 50, 'music_volume': 50}

    def init_sound(self):
        pygame.mixer.init()
        try:
            self.win_sound = pygame.mixer.Sound("mixkit-completion-of-a-level-2063.wav")
            self.lose_sound = pygame.mixer.Sound("mixkit-player-losing-or-failing-2042.wav")
            self.record_sound = pygame.mixer.Sound("mixkit-unlock-game-notification-253.wav")
            
            # Инициализация фоновой музыки
            pygame.mixer.music.load("Qumu - Sweden.mp3")
            pygame.mixer.music.play(-1)  # -1 означает бесконечное воспроизведение
            
            volume = self.settings.get('volume', 50) / 100.0
            music_volume = self.settings.get('music_volume', 50) / 100.0
            
            self.win_sound.set_volume(volume)
            self.lose_sound.set_volume(volume)
            self.record_sound.set_volume(volume)
            pygame.mixer.music.set_volume(music_volume)
            
        except Exception as e:
            print(f"Ошибка инициализации звука: {e}")
            self.settings = {'volume': 50, 'music_volume': 50}

    def init_db(self):
        self.conn = sqlite3.connect(
        'users.db',
        detect_types=sqlite3.PARSE_DECLTYPES
        )
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                player_name TEXT NOT NULL,
                level INTEGER NOT NULL,
                attempts INTEGER NOT NULL,
                record_date DATETIME NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bulls_cows_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                player_name TEXT NOT NULL,
                attempts INTEGER NOT NULL,
                score INTEGER NOT NULL DEFAULT 0,
                record_date DATETIME NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        self.conn.commit()

    def init_ui(self):
        self.setWindowTitle('Dr.Ist Game')
        self.set_theme()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(20)

        top_panel = QHBoxLayout()
        self.theme_button = QPushButton('Светлая тема' if self.is_dark_theme else 'Темная тема')
        self.theme_button.clicked.connect(self.toggle_theme)
        self.rating_button = QPushButton('ПОЛНЫЙ РЕЙТИНГ')
        self.rating_button.clicked.connect(self.show_full_rating)
        top_panel.addWidget(self.theme_button)
        top_panel.addStretch()
        top_panel.addWidget(self.rating_button)

        self.level_label = QLabel(f'УРОВЕНЬ: {self.current_level}')
        self.level_label.setProperty('class', 'header')
        
        self.record_label = QLabel('РЕКОРД: -')
        self.record_label.setProperty('class', 'subheader')
        
        self.attempts_label = QLabel('ПОПЫТКИ: 0')
        self.attempts_label.setProperty('class', 'attempts')
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText('Введите число...')
        self.input_field.returnPressed.connect(self.check_guess)
        
        self.guess_button = QPushButton('ПРОВЕРИТЬ')
        self.guess_button.clicked.connect(self.check_guess)
        
        self.menu_button = QPushButton('ВЕРНУТЬСЯ В МЕНЮ')
        self.menu_button.setStyleSheet('''
            QPushButton {
                font-size: 16px;
                padding: 12px 24px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: #45a049;
            }
        ''')
        self.menu_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        
        self.hint_label = QLabel('')
        self.hint_label.setProperty('class', 'hint')
        
        self.notification_box = QGroupBox()
        self.notification_box.setMaximumHeight(200)
        self.notification_box.setVisible(False)
        notification_layout = QVBoxLayout()
        
        self.notification_title = QLabel()
        self.notification_title.setProperty('class', 'notification-title')
        
        self.notification_text = QLabel()
        self.notification_text.setWordWrap(True)
        
        self.buttons_layout = QHBoxLayout()
        self.play_again_button = QPushButton('Сыграть еще')
        self.exit_button = QPushButton('Выход')
        
        self.buttons_layout.addWidget(self.play_again_button)
        self.buttons_layout.addWidget(self.exit_button)
        
        notification_layout.addWidget(self.notification_title)
        notification_layout.addWidget(self.notification_text)
        notification_layout.addLayout(self.buttons_layout)
        self.notification_box.setLayout(notification_layout)

        level_group = QGroupBox("ВЫБЕРИТЕ УРОВЕНЬ СЛОЖНОСТИ")
        level_layout = QHBoxLayout()
        self.level_group = QButtonGroup(self)
        levels = [
            ('ЛЕГКИЙ (1-10)', 10, 5),
            ('СРЕДНИЙ (1-100)', 100, 10),
            ('СЛОЖНЫЙ (1-1000)', 1000, 100),
            ('PRO (1-1,000,000)', 1000000, 1000)
        ]
        for i, (text, value, max_attempts) in enumerate(levels):
            rb = QRadioButton(text)
            rb.setProperty('level', value)
            rb.setProperty('max_attempts', max_attempts)
            self.level_group.addButton(rb, i)
            level_layout.addWidget(rb)
        self.level_group.button(0).setChecked(True)
        self.level_group.buttonClicked.connect(self.change_level)
        level_group.setLayout(level_layout)

        main_layout.addLayout(top_panel)
        main_layout.addWidget(self.level_label)
        main_layout.addWidget(self.record_label)
        main_layout.addWidget(level_group)
        main_layout.addWidget(self.attempts_label)
        main_layout.addWidget(self.input_field)
        main_layout.addWidget(self.guess_button)
        main_layout.addWidget(self.hint_label)
        main_layout.addWidget(self.notification_box)
        main_layout.addStretch()
        
        bottom_panel = QHBoxLayout()
        bottom_panel.addStretch()
        bottom_panel.addWidget(self.menu_button)
        main_layout.addLayout(bottom_panel)

        self.setLayout(main_layout)

    def set_theme(self):
        if self.is_dark_theme:
            self.setStyleSheet("""
                QWidget {
                    background-color: #1a1a1a;
                    color: #ffffff;
                }
                QLabel[class="header"] {
                    font-size: 28px;
                    color: #4CAF50;
                    font-weight: bold;
                }
                QLabel[class="subheader"] {
                    font-size: 18px;
                    color: #888;
                }
                QLabel[class="attempts"] {
                    font-size: 20px;
                    color: #FF9800;
                }
                QLabel[class="hint"] {
                    font-size: 18px;
                    color: #FF9800;
                }
                QLineEdit {
                    font-size: 20px;
                    padding: 10px;
                    border: 2px solid #4CAF50;
                    border-radius: 5px;
                    background: #333;
                }
                QPushButton {
                    font-size: 16px;
                    padding: 12px 24px;
                    background: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background: #45a049;
                }
                QGroupBox {
                    border: 2px solid #4CAF50;
                    border-radius: 5px;
                }
                QLabel[class="notification-title"] {
                    font-size: 24px;
                    color: #4CAF50;
                    font-weight: bold;
                }
                QLabel[class="error"] {
                    color: #ff4444;
                    font-size: 14px;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #f0f0f0;
                    color: #333333;
                }
                QLabel[class="header"] {
                    font-size: 28px;
                    color: #2196F3;
                    font-weight: bold;
                }
                QLabel[class="subheader"] {
                    font-size: 18px;
                    color: #666;
                }
                QLabel[class="attempts"] {
                    font-size: 20px;
                    color: #FF5722;
                }
                QLabel[class="hint"] {
                    font-size: 18px;
                    color: #FF5722;
                }
                QLineEdit {
                    font-size: 20px;
                    padding: 10px;
                    border: 2px solid #2196F3;
                    border-radius: 5px;
                    background: white;
                }
                QPushButton {
                    font-size: 16px;
                    padding: 12px 24px;
                    background: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background: #1976D2;
                }
                QGroupBox {
                    border: 2px solid #2196F3;
                    border-radius: 5px;
                }
                QLabel[class="notification-title"] {
                    font-size: 24px;
                    color: #2196F3;
                    font-weight: bold;
                }
                QLabel[class="error"] {
                    color: #ff0000;
                    font-size: 14px;
                }
            """)
        palette = QPalette()
        if self.is_dark_theme:
            palette.setColor(QPalette.Window, QColor(30, 30, 30))
            palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
        else:
            palette.setColor(QPalette.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.WindowText, QColor(50, 50, 50))
        QApplication.instance().setPalette(palette)

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.theme_button.setText('Темная тема' if self.is_dark_theme else 'Светлая тема')
        self.set_theme()

    def change_level(self):
        level_map = {
            0: (10, 5),
            1: (100, 10),
            2: (1000, 100),
            3: (1000000, 1000)
        }
        selected = self.level_group.checkedId()
        self.max_number, self.max_attempts = level_map[selected]
        self.current_level = selected + 1
        self.level_label.setText(f'УРОВЕНЬ: {["ЛЕГКИЙ", "СРЕДНИЙ", "СЛОЖНЫЙ", "PRO"][selected]}') 
        self.new_game()

    def new_game(self): 
        self.secret_number = random.randint(1, self.max_number)
        print(f"\n[DEBUG] Правильный ответ: {self.secret_number}")
        self.attempts = 0
        self.update_attempts()
        self.input_field.setEnabled(True)
        self.guess_button.setEnabled(True)
        self.menu_button.setVisible(True)
        self.hint_label.clear()
        self.input_field.clear()
        self.notification_box.setVisible(False)
        self.update_record_label()

    def update_attempts(self):
        self.attempts_label.setText(f'ПОПЫТКИ: {self.attempts}/{self.max_attempts}')

    def update_record_label(self):
        self.cursor.execute('''
            SELECT MIN(attempts), player_name 
            FROM records 
            WHERE level = ?
        ''', (self.current_level,))
        result = self.cursor.fetchone()
        if result and result[0]:
            self.record_label.setText(f'РЕКОРД: {result[0]} ({result[1]})')
        else:
            self.record_label.setText('РЕКОРД: -')

    def check_guess(self):
        try:
            guess = int(self.input_field.text())
            if guess < 1 or guess > self.max_number:
                raise ValueError
                
            self.attempts += 1
            self.update_attempts()

            if guess == self.secret_number:
                self.win_sound.play()
                self.show_win()
                return

            difference = abs(self.secret_number - guess)
            percentage_diff = (difference / self.max_number) * 100

            hints = []
            direction = "больше" if guess < self.secret_number else "меньше"
            hints.append(f"Загаданное число {direction} {guess}")

            if self.max_number == 10:
                if difference == 1:
                    hints.append("Вы в одном шаге от победы!")
                hints.append(f"Осталось {self.max_attempts - self.attempts} попыток")
            elif self.max_number == 100:
                if difference <= 5:
                    hints.append(f"Очень близко! Разница меньше 5")
                else:
                    range_size = max(20 - self.attempts * 2, 5)
                    lower = max(1, guess - range_size)
                    upper = min(self.max_number, guess + range_size)
                    hints.append(f"Число находится между {lower} и {upper}")
            elif self.max_number == 1000:
                if difference <= 10:
                    hints.append("Горячо! Разница меньше 10")
                elif difference <= 50:
                    hints.append("Тепло! Разница меньше 50")
            elif self.max_number == 1000000:
                if percentage_diff < 1:
                    hints.append("Вы невероятно близко (ошибка < 1%)!")
                elif percentage_diff < 5:
                    hints.append("Очень близко (ошибка < 5%)!")
                elif percentage_diff < 10:
                    hints.append("Близко (ошибка < 10%)!")

                digit_sum = sum(int(d) for d in str(self.secret_number))
                hints.append(f"Сумма цифр числа: {digit_sum}")

                divisors = []
                for d in [2, 3, 5, 10]:
                    if self.secret_number % d == 0:
                        divisors.append(d)
                if divisors:
                    hints.append(f"Число делится на: {', '.join(map(str, divisors))}")

                digits = len(str(self.secret_number))
                hints.append(f"Это {digits}-значное число")

                if self.attempts >= 3:
                    hints.append(f"Первая цифра: {str(self.secret_number)[0]}")

            if len(hints) > 2:
                selected_hints = random.sample(hints, 2)
                hint = "\n".join(selected_hints)
            else:
                hint = "\n".join(hints)
            self.hint_label.setText(hint)

            if self.attempts >= self.max_attempts:
                self.lose_sound.play()
                self.show_game_over()
            
            self.input_field.clear()
        except ValueError:
            self.lose_sound.play()
            self.hint_label.setText(f'Ошибка! Введите число от 1 до {self.max_number:,}'.replace(',', ' '))
            self.input_field.clear()

    def show_win(self):
        self.input_field.setEnabled(False)
        self.guess_button.setEnabled(False)
        self.menu_button.setVisible(False)

        self.cursor.execute('''
            SELECT MIN(attempts) 
            FROM records 
            WHERE level = ?
        ''', (self.current_level,))
        result = self.cursor.fetchone()
        old_record = result[0] if result[0] else float('inf')
        is_new_record = self.attempts < old_record

        self.notification_title.setText('🎉 ПОБЕДА! 🎉')
        self.notification_text.setText(
            f'Вы угадали число за {self.attempts} попыток!\n'
            + ('🏆 НОВЫЙ РЕКОРД! 🏆' if is_new_record else '')
        )

        self.notification_box.setVisible(True)

        if is_new_record:
            self.record_sound.play()

        self.save_and_restart()  # Добавляем эту строку
        self.play_again_button_clicked()
        self.exit_button_clicked()

    def play_again_button_clicked(self):
        try:
            self.play_again_button.disconnect()
        except:
            pass
        self.play_again_button.clicked.connect(self.new_game)

    def exit_button_clicked(self):
        try:
            self.exit_button.disconnect()
        except:
            pass
        self.exit_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

    def save_record(self, player_name):
        try:
            # Определяем данные пользователя
            if self.current_user:
                player_name = self.current_user[1]
                user_id = self.current_user[0]
            else:
                user_id = None
                player_name = f"Anonymous_{random.randint(1000, 9999)}"

            # Ищем лучший результат для этого уровня
            self.cursor.execute('''
                SELECT MIN(attempts)
                FROM records 
                WHERE level = ?
            ''', (self.current_level,))
            best_result = self.cursor.fetchone()[0]

            # Если это новый рекорд или рекорда еще нет
            if not best_result or self.attempts < best_result:
                self.cursor.execute('''
                    INSERT INTO records (user_id, player_name, level, attempts, record_date)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, player_name, self.current_level, self.attempts, datetime.now()))
                self.conn.commit()
                
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка сохранения рекорда: {e}")

    def handle_exit(self):
        if self.attempts > 0:
            if self.current_user:
                player_name = self.current_user[1]
            else:
                player_name = f"Anonymous_{random.randint(1000, 9999)}"
            self.save_record(player_name)
        
        self.stacked_widget.setCurrentIndex(0)

    def save_and_restart(self):
        if self.current_user:
            player_name = self.current_user[1]
        else:
            player_name = f"Anonymous_{random.randint(1000, 9999)}"
        self.save_record(player_name)
        self.update_record_label()
        self.new_game()
        self.notification_box.setVisible(False)

    def show_game_over(self):
        self.input_field.setEnabled(False)
        self.guess_button.setEnabled(False)
        self.menu_button.setVisible(False)

        self.notification_title.setText('😞 ИГРА ОКОНЧЕНА 😞')
        self.notification_text.setText(
            f'Попытки закончились!\nЗагаданное число: {self.secret_number}'
        )
        self.notification_box.setVisible(True)

        self.play_again_button_clicked()
        self.exit_button_clicked()

    def show_full_rating(self):
        self.last_screen = 1  # Индекс текущего экрана
        self.stacked_widget.setCurrentIndex(3)

class GameSelectScreen(QWidget):
    def __init__(self, stacked_widget, game_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.game_widget = game_widget
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        # Заголовок
        title = QLabel("ВЫБЕРИТЕ ИГРУ")
        title.setStyleSheet('font-size: 40px; font-weight: bold; background-color: #1e1e1e; margin-bottom: 60px;')
        title.setAlignment(Qt.AlignCenter)

        # Кнопки выбора игры
        button_style = '''
            QPushButton {
                font-size: 30px; 
                padding: 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                min-width: 300px;
                min-height: 100px;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #3d8b40; }
        '''

        guess_number_btn = QPushButton('УГАДАЙ ЧИСЛО')
        guess_number_btn.setStyleSheet(button_style)
        guess_number_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        bulls_cows_btn = QPushButton('БЫКИ И КОРОВЫ')
        bulls_cows_btn.setStyleSheet(button_style)
        bulls_cows_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(5))  # Индекс для новой игры
        bulls_cows_btn.setEnabled(True)  # Включаем кнопку

        # Кнопка возврата
        back_button = QPushButton("НАЗАД")
        back_button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                padding: 15px 30px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                min-width: 200px;
            }
            QPushButton:hover { background: #45a049; }
        """)
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        # Компоновка
        button_layout = QVBoxLayout()
        button_layout.addWidget(guess_number_btn, alignment=Qt.AlignCenter)
        button_layout.addWidget(bulls_cows_btn, alignment=Qt.AlignCenter)
        button_layout.setSpacing(20)

        main_layout.addWidget(title)
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        main_layout.addWidget(back_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #1a1a1a; color: white;")

class BullsAndCowsGame(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.secret_number = self.generate_number()
        self.attempts = 0
        self.settings = {'volume': 50}  # Добавляем значение по умолчанию
        self.load_settings()
        self.init_sound()
        self.init_db()
        self.init_ui()
        
    def generate_number(self):
        digits = list(range(10))
        random.shuffle(digits)
        return ''.join(map(str, digits[:4]))
        
    def load_settings(self):
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    self.settings = json.load(f)
            else:
                self.settings = {'volume': 50}
        except Exception:
            self.settings = {'volume': 50}

    def init_sound(self):
        pygame.mixer.init()
        try:
            self.win_sound = pygame.mixer.Sound("mixkit-completion-of-a-level-2063.wav")
            
            volume = self.settings.get('volume', 50) / 100.0
            
            self.win_sound.set_volume(volume)
            
        except Exception as e:
            print(f"Ошибка инициализации звука: {e}")

    def init_db(self):
        self.conn = sqlite3.connect('users.db')
        self.cursor = self.conn.cursor()
        
        # Проверяем существование столбца score
        self.cursor.execute("PRAGMA table_info(bulls_cows_records)")
        columns = [column[1] for column in self.cursor.fetchall()]
        
        if "score" not in columns:
            # Если таблица существует, добавляем столбец score
            try:
                self.cursor.execute("ALTER TABLE bulls_cows_records ADD COLUMN score INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                # Если таблица не существует, создаем её с нужной структурой
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS bulls_cows_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        player_name TEXT NOT NULL,
                        attempts INTEGER NOT NULL,
                        score INTEGER NOT NULL DEFAULT 0,
                        record_date DATETIME NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )
                ''')
        
        self.conn.commit()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        # Заголовок
        title = QLabel("🐮 БЫКИ И КОРОВЫ 🐂")
        title.setStyleSheet('font-size: 40px; font-weight: bold; background-color: #1e1e1e; margin-bottom: 30px;')
        title.setAlignment(Qt.AlignCenter)

        # История игры
        self.history = QTableWidget()
        self.history.setColumnCount(3)
        self.history.setHorizontalHeaderLabels(['Число', 'Быки', 'Коровы'])
        self.history.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history.setStyleSheet("""
            QTableWidget {
                background-color: #2D2D2D;
                color: white;
                gridline-color: #3D3D3D;
                border: none;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
        """)

        # Поле ввода
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText('Введите 4-значное число...')
        self.input_field.setStyleSheet("""
            QLineEdit {
                font-size: 20px;
                padding: 10px;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                background: #333;
                color: white;
            }
        """)
        self.input_field.returnPressed.connect(self.make_guess)

        # Кнопка проверки
        self.guess_button = QPushButton('ПРОВЕРИТЬ')
        self.guess_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 12px 24px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover { background: #45a049; }
        """)
        self.guess_button.clicked.connect(self.make_guess)

        # Добавляем счетчик ходов
        self.attempts_label = QLabel('Ходов: 0')
        self.attempts_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #4CAF50;
                font-weight: bold;
            }
        """)

        # Добавляем метку для очков
        self.score_label = QLabel('Очки: 1000')
        self.score_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #FFD700;
                font-weight: bold;
            }
        """)

        # Добавляем кнопку рейтинга
        rating_button = QPushButton('РЕЙТИНГ')
        rating_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 12px 24px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover { background: #45a049; }
        """)
        rating_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(6))  # Новый индекс для рейтинга

        # Изменяем компоновку
        top_panel = QHBoxLayout()
        top_panel.addWidget(self.attempts_label)
        top_panel.addWidget(self.score_label)
        top_panel.addStretch()
        top_panel.addWidget(rating_button)

        main_layout.addWidget(title)
        main_layout.addLayout(top_panel)
        main_layout.addWidget(self.history)
        main_layout.addWidget(self.input_field)
        main_layout.addWidget(self.guess_button)

        # Кнопка возврата
        back_button = QPushButton('ВЕРНУТЬСЯ В МЕНЮ')
        back_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 12px 24px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                min-width: 200px;
            }
            QPushButton:hover { background: #45a049; }
        """)
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))

        # Нижняя панель для кнопки возврата
        bottom_panel = QHBoxLayout()
        bottom_panel.addStretch()
        bottom_panel.addWidget(back_button)
        
        main_layout.addStretch()
        main_layout.addLayout(bottom_panel)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #1a1a1a; color: white;")
        print(f"[DEBUG] Загаданное число: {self.secret_number}")  # Для отладки

    def calculate_score(self, bulls, cows):
        base_score = 1000
        attempt_penalty = 50 * (self.attempts - 1)
        bulls_bonus = bulls * 100
        cows_bonus = cows * 25
        score = max(0, base_score - attempt_penalty + bulls_bonus + cows_bonus)
        return score

    def make_guess(self):
        guess = self.input_field.text().strip()
        if not self.validate_input(guess):
            return

        self.attempts += 1
        self.attempts_label.setText(f'Ходов: {self.attempts}')
        
        bulls, cows = self.check_guess(guess)
        current_score = self.calculate_score(bulls, cows)
        self.score_label.setText(f'Очки: {current_score}')
        
        self.add_to_history(guess, bulls, cows)
        self.input_field.clear()

        if bulls == 4:
            self.save_record(current_score)
            self.show_win_message(current_score)

    def validate_input(self, guess):
        if not guess.isdigit() or len(guess) != 4 or len(set(guess)) != 4:
            QMessageBox.warning(self, "Ошибка", "Введите 4 разные цифры!")
            return False
        return True

    def check_guess(self, guess):
        bulls = cows = 0
        for i in range(4):
            if guess[i] == self.secret_number[i]:
                bulls += 1
            elif guess[i] in self.secret_number:
                cows += 1
        return bulls, cows

    def add_to_history(self, guess, bulls, cows):
        row = self.history.rowCount()
        self.history.insertRow(row)
        
        # Создаем элементы для каждой колонки
        guess_item = QTableWidgetItem(guess)
        bulls_item = QTableWidgetItem(str(bulls))
        cows_item = QTableWidgetItem(str(cows))
        
        # Устанавливаем стиль для элементов
        items = [guess_item, bulls_item, cows_item]
        for item in items:
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Делаем ячейки нередактируемыми
        
        # Если это правильный ответ, выделяем строку зеленым
        if bulls == 4:
            color = QColor('#4CAF50')
            for item in items:
                item.setBackground(color)
                item.setForeground(QColor('white'))
        
        # Устанавливаем элементы в таблицу
        self.history.setItem(row, 0, guess_item)
        self.history.setItem(row, 1, bulls_item)
        self.history.setItem(row, 2, cows_item)
        
        # Прокручиваем к последней строке
        self.history.scrollToBottom()

    def save_record(self, score):
        try:
            if hasattr(self, 'current_user') and self.current_user:
                player_name = self.current_user[1]
                user_id = self.current_user[0]
            else:
                player_name = f"Anonymous_{random.randint(1000, 9999)}"
                user_id = None

            self.cursor.execute('''
                INSERT INTO bulls_cows_records (user_id, player_name, attempts, score, record_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, player_name, self.attempts, score, datetime.now()))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка сохранения рекорда: {e}")

    def show_win_message(self, score):
        self.win_sound.play()  # Добавляем воспроизведение звука
        QMessageBox.information(self, "Победа!", 
            f"Поздравляем! Вы угадали число {self.secret_number}!\n"
            f"Количество ходов: {self.attempts}\n"
            f"Набрано очков: {score}")
        self.secret_number = self.generate_number()
        self.history.setRowCount(0)
        self.attempts = 0
        self.attempts_label.setText('Ходов: 0')
        self.score_label.setText('Очки: 1000')
        print(f"[DEBUG] Новое число: {self.secret_number}")

class BullsAndCowsRating(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        title = QLabel("🏆 РЕЙТИНГ БЫКИ И КОРОВЫ 🏆")
        title.setStyleSheet('font-size: 40px; font-weight: bold; background-color: #1e1e1e; margin-bottom: 30px;')
        title.setAlignment(Qt.AlignCenter)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ИГРОК', 'ХОДОВ', 'ОЧКИ', 'ДАТА'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2D2D2D;
                color: white;
                gridline-color: #3D3D3D;
                border: none;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
        """)

        back_button = QPushButton('НАЗАД')  # Изменили текст кнопки
        back_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 12px 24px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover { background: #45a049; }
        """)
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(5))  # 5 - индекс игры "Быки и Коровы"

        main_layout.addWidget(title)
        main_layout.addWidget(self.table)
        main_layout.addWidget(back_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #1a1a1a; color: white;")
        self.update_table()

    def update_table(self):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT player_name, attempts, score, record_date 
            FROM bulls_cows_records 
            ORDER BY score DESC, attempts, record_date DESC
        ''')
        results = cursor.fetchall()
        self.table.setRowCount(len(results))

        for row, (name, attempts, score, date) in enumerate(results):
            player_item = QTableWidgetItem(name)
            if "Anonymous" not in name:
                player_item.setForeground(QColor('#4CAF50'))
            else:
                player_item.setForeground(QColor('#BBBBBB'))
            
            attempts_item = QTableWidgetItem(str(attempts))
            score_item = QTableWidgetItem(str(score))
            score_item.setForeground(QColor('#FFD700'))  # Золотой цвет для очков
            date_item = QTableWidgetItem(datetime.fromisoformat(date).strftime("%d.%m.%Y %H:%M"))

            self.table.setItem(row, 0, player_item)
            self.table.setItem(row, 1, attempts_item)
            self.table.setItem(row, 2, score_item)
            self.table.setItem(row, 3, date_item)

        conn.close()

    def showEvent(self, event):
        super().showEvent(event)
        self.update_table()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    try:
        pygame.mixer.init()
    except Exception as e:
        print(f"Внимание: Не удалось инициализировать звук: {e}")
        
    stacked_widget = QStackedWidget()
    try:
        game = NumberGuessingGamePRO(stacked_widget)
        menu = MainMenu(stacked_widget, game)
        settings = SettingsScreen(stacked_widget, game)
        rating = RatingScreen(stacked_widget, game)
        game_select = GameSelectScreen(stacked_widget, game)
        bulls_and_cows = BullsAndCowsGame(stacked_widget)
        bulls_and_cows_rating = BullsAndCowsRating(stacked_widget)
        
        # Добавляем функцию для синхронизации current_user между виджетами
        def update_current_user(user):
            game.current_user = user
            bulls_and_cows.current_user = user
            menu.update_login_button()
        
        # Переопределяем методы авторизации в MainMenu
        original_handle_login = menu.handle_login
        def new_handle_login(username, password, dialog):
            result = original_handle_login(username, password, dialog)
            update_current_user(game.current_user)
            return result
        menu.handle_login = new_handle_login
        
        original_handle_logout = menu.handle_logout
        def new_handle_logout():
            original_handle_logout()
            update_current_user(None)
        menu.handle_logout = new_handle_logout

        widgets = [menu, game, settings, rating, game_select, bulls_and_cows, bulls_and_cows_rating]
        
        for widget in widgets:
            stacked_widget.addWidget(widget)
            
    except Exception as e:
        print(f"Ошибка при инициализации виджетов: {e}")
        sys.exit(1)

    stacked_widget.setWindowTitle('Dr.Ist Game')
    stacked_widget.setFixedSize(800, 650)
    stacked_widget.show()

    def handle_exit():
        try:
            if game.current_user:
                with open('last_user.json', 'w') as f:
                    json.dump({
                        'username': game.current_user[1],
                        'password_hash': game.current_user[2]
                    }, f)
        except Exception as e:
            print(f"Ошибка при сохранении данных пользователя: {e}")
        app.quit()

    app.aboutToQuit.connect(handle_exit)
    sys.exit(app.exec_())