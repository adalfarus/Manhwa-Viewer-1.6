from logging import raiseExceptions
from traceback import print_tb
from PySide6.QtWidgets import (QApplication, QLabel, QVBoxLayout, QScrollArea,
                             QWidget, QMainWindow, QCheckBox, QHBoxLayout,
                             QSpinBox, QPushButton, QGraphicsOpacityEffect,
                             QFrame, QComboBox, QFormLayout, QSlider, QLineEdit,
                             QRadioButton, QDialog, QGroupBox, QToolButton, 
                             QDialogButtonBox, QMessageBox, QFileDialog, 
                             QProgressDialog)
from PySide6.QtGui import QPixmap, QPalette, QColor, QIcon, QDoubleValidator
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QThread, Signal, Slot
from extensions.ManhwaFilePlugin import ManhwaFilePlugin
from extensions.AutoProviderPlugin import AutoProviderPlugin
from extensions.extra_autoprovider_plugins import *
from pathlib import Path
import importlib.util
import threading # Implement, needed if website is very slow
import base64
import ctypes # Implement, needed if website is very slow
import json
import time
import sys
import os

# Get the directory where the script (or frozen exe) is located
if getattr(sys, 'frozen', False):
    # If the script is running as a bundled executable created by PyInstaller
    script_dir = os.path.dirname(sys.executable)
else:
    # If the script is running as a normal Python script
    script_dir = os.path.dirname(os.path.realpath(__file__))

# Change the current working directory to the script directory
os.chdir(script_dir)

class Logger(object):
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self, message):
        timestamp = f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}] "
        message_with_timestamp = timestamp + message if message != '\n' else message
        if self.terminal is not None:
            try:
                self.terminal.write(message_with_timestamp)
            except Exception as e:
                pass
        self.log.write(message_with_timestamp)
        self.log.flush()

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass
        
def monitor_stdout(log_file):
    sys.stdout = Logger(log_file)
        
class Database:
    def __init__(self, path):
        import sqlite3
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name: str, columns: list):
        # Construct the CREATE TABLE query using the provided table name and columns
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        self.cursor.execute(query)
        self.conn.commit()

    def update_info(self, info: list, table: str, columns: list):
        # Check if the length of info matches the number of columns
        if len(info) != len(columns):
            raise ValueError("Length of info must match the number of columns.")

        # Construct the INSERT INTO query
        col_names = ", ".join(columns)
        placeholders = ", ".join("?" for _ in info)
        query = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
        
        self.cursor.execute(query, info)
        self.conn.commit()

    def get_info(self, table: str, columns: list) -> list:
        col_names = ", ".join(columns)
        query = f"SELECT {col_names} FROM {table}"
        self.cursor.execute(query)
        
        return self.cursor.fetchall()
        
    def close(self):
        self.conn.commit()
        self.conn.close()
        
class AutoProviderManager:
    def __init__(self, path):
        self.path = path
        self.providers = self._load_providers()

    def _load_providers(self):
        providers = {}
        for file in os.listdir(self.path):
            if file.endswith('.py') and file != '__init__.py':
                module_name = file[:-3]
                module_path = os.path.join(self.path, file)
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)
                    if isinstance(attribute, type) and issubclass(attribute, AutoProviderPlugin) and attribute is not AutoProviderPlugin:
                        providers[attribute_name] = attribute
        return providers

    def get_providers(self):
        return self.providers
        
class Settings:
    def __init__(self, new, db):
        self.new = new
        self.db = db
        self.settings = [["provider", "auto"], 
                         ["autoprovider", "ManhwaClan"], ["file_path", ""], 
                         ["title", ""], ["chapter", "1"],
                         ["downscaling", "True"], ["upscaling", "False"],
                         ["manual_width", "640"], ["borderless", "False"],
                         ["invisible_background", "False"], ["hide_scrollbar", "False"],
                         ["stay_on_top", "False"], ["geometry", "100, 100, 640, 480"], 
                         ["blacklisted_websites", "247manga.com, ww6.mangakakalot.tv, jimanga.com, mangapure.net, mangareader.mobi, onepiece.fandom.com"], 
                         ["export_settings", ""], ["auto_export", "False"]]
        if self.new == True: self.setup_database(self.settings)
        self.fetch_data()
        self.convert_settings()
        
    def convert_settings(self):
        if isinstance(self.settings, list):
            temp_dict = {}
            for i in self.settings:
                key, value = i[0], i[1]
                temp_dict = temp_dict | {key: value}
            self.settings = temp_dict
        elif isinstance(self.settings, dict):
            temp_list = []
            for key, value in zip(self.settings.keys(), self.settings.values()):
                temp_list.append([key, value])
            self.settings = temp_list
        
    def boolean(self, to_boolean):
        if to_boolean == "True":
            return True
        elif to_boolean == "False":
            return False
        
    def get_provider(self):
        return self.settings["provider"]
        
    def set_provider(self, new_provider):
        self.settings["provider"] = new_provider
        self.update_data()
        
    def get_autoprovider(self):
        return self.settings["autoprovider"]
        
    def set_autoprovider(self, new_autoprovider):
        self.settings["autoprovider"] = new_autoprovider
        self.update_data()
        
    def get_file_path(self):
        return self.settings["file_path"]
        
    def set_file_path(self, new_file_path):
        self.settings["file_path"] = new_file_path
        self.update_data()
        
    def get_title(self):
        return self.settings["title"]
        
    def set_title(self, new_title):
        self.settings["title"] = new_title
        self.update_data()
        
    def get_chapter(self):
        return int(self.settings["chapter"]) if float(self.settings["chapter"]).is_integer() else float(self.settings["chapter"])
        
    def set_chapter(self, new_chapter):
        self.settings["chapter"] = str(int(new_chapter) if float(new_chapter).is_integer() else new_chapter)
        self.update_data()
        
    def get_downscaling(self):
        return self.boolean(self.settings["downscaling"])
        
    def set_downscaling(self, new_downscaling):
        self.settings["downscaling"] = str(new_downscaling)
        self.update_data()
        
    def get_upscaling(self):
        return self.boolean(self.settings["upscaling"])
        
    def set_upscaling(self, new_upscaling):
        self.settings["upscaling"] = str(new_upscaling)
        self.update_data()
        
    def get_manual_width(self):
        return int(self.settings["manual_width"])
        
    def set_manual_width(self, new_manual_width):
        self.settings["manual_width"] = str(new_manual_width)
        self.update_data()
        
    def get_borderless(self):
        return self.boolean(self.settings["borderless"])
        
    def set_borderless(self, new_borderless):
        self.settings["borderless"] = str(new_borderless)
        self.update_data()
        
    def get_invisible_background(self):
        return self.boolean(self.settings["invisible_background"])
        
    def set_invisible_background(self, new_invisible_background):
        self.settings["invisible_background"] = str(new_invisible_background)
        self.update_data()
        
    def get_hide_scrollbar(self):
        return self.boolean(self.settings["hide_scrollbar"])
        
    def set_hide_scrollbar(self, new_hide_scrollbar):
        self.settings["hide_scrollbar"] = str(new_hide_scrollbar)
        self.update_data()
        
    def get_stay_on_top(self):
        return self.boolean(self.settings["stay_on_top"])
        
    def set_stay_on_top(self, new_stay_on_top):
        self.settings["stay_on_top"] = str(new_stay_on_top)
        self.update_data()
        
    def get_geometry(self):
        return [int(x) for x in self.settings["geometry"].split(", ")]
        
    def set_geometry(self, new_geometry):
        self.settings["geometry"] = ', '.join([str(x) for x in new_geometry])
        self.update_data()
        
    def get_blacklisted_websites(self):
        return [x for x in self.settings["blacklisted_websites"].split(", ")]
        
    def set_blacklisted_websites(self, new_blacklisted_websites):
        self.settings["blacklisted_websites"] = ', '.join([x for x in new_blacklisted_websites])
        self.update_data()
        
    def get_export_settings(self):
        return [x for x in self.settings["export_settings"].split(", ")]
        
    def set_export_settings(self, new_export_settings):
        self.settings["export_settings"] = ', '.join([str(x) for x in new_export_settings])
        self.update_data()
        
    def get_auto_export(self):
        return self.boolean(self.settings["auto_export"])
        
    def set_auto_export(self, new_auto_export):
        self.settings["auto_export"] = str(new_auto_export)
        
    def setup_database(self, settings):
        # Define tables and their columns
        tables = {
            "settings": ["key TEXT", "value TEXT"]
        }
        # Code to set up the database, initialize password hashes, etc.
        for table_name, columns in tables.items():
            self.db.create_table(table_name, columns)
        for i in self.settings:
            self.db.update_info(i, "settings", ["key", "value"])
        
    def fetch_data(self):
        self.settings = self.db.get_info("settings", ["key", "value"])
        
    def update_data(self):
        self.convert_settings()
        for i in self.settings:
            self.db.update_info(i, "settings", ["key", "value"])
        self.convert_settings()
        
class ExportDialog(QDialog):
    def __init__(self, parent=None, export_settings=["", "", False, "", False, 0, 0]):
        self.title = export_settings[0]
        self.chapter_name = export_settings[1]
        self.count_up = True if export_settings[2] == "True" else False
        self.file_path = export_settings[3]
        self.urls = True if export_settings[4] == "True" else False
        self.file = int(export_settings[5])
        self.chapter = int(export_settings[6])
        
        super().__init__(parent, Qt.WindowCloseButtonHint | Qt.WindowTitleHint)
        self.setWindowTitle("Dialog")
        self.resize(400, 100)
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        self.stackLayout = QHBoxLayout()

        # Name Group
        self.nameGroupBox = QGroupBox("Name", self)
        self.nameLayout = QFormLayout(self.nameGroupBox)

        self.titleLineEdit = QLineEdit(self.nameGroupBox)
        self.nameLayout.addRow("Title", self.titleLineEdit)

        self.chapterLayout = QHBoxLayout()
        self.chapterLineEdit = QLineEdit(self.nameGroupBox)
        self.chapterLayout.addWidget(QLabel("Save as Chapter"))
        self.chapterLayout.addWidget(self.chapterLineEdit)
        self.chapterCountUp = QCheckBox("Count Up")
        self.chapterLayout.addWidget(self.chapterCountUp)
        self.nameLayout.addRow(self.chapterLayout)

        self.fileLocationLineEdit = QLineEdit(self.nameGroupBox)
        self.fileLocationToolButton = QToolButton(self.nameGroupBox)
        self.fileLocationToolButton.setText("...")
        self.fileLocationLayout = QHBoxLayout()
        self.fileLocationLayout.addWidget(self.fileLocationLineEdit)
        self.fileLocationLayout.addWidget(self.fileLocationToolButton)
        self.nameLayout.addRow("File Location", self.fileLocationLayout)

        self.saveAsUrlsCheckBox = QCheckBox("Save as URLs", self.nameGroupBox)
        self.saveAsUrlsCheckBox.setEnabled(False)
        self.nameLayout.addRow(self.saveAsUrlsCheckBox)

        self.stackLayout.addWidget(self.nameGroupBox)

        self.rightLayout = QVBoxLayout()

        # File Group
        self.fileGroupBox = QGroupBox("File", self)
        self.fileLayout = QVBoxLayout(self.fileGroupBox)

        self.overwriteFileRadioButton = QRadioButton("Overwrite file", self.fileGroupBox)
        self.fileLayout.addWidget(self.overwriteFileRadioButton)

        self.addToFileRadioButton = QRadioButton("Add to file", self.fileGroupBox)
        self.fileLayout.addWidget(self.addToFileRadioButton)

        self.rightLayout.addWidget(self.fileGroupBox)

        # Chapter Group
        self.chapterGroupBox = QGroupBox("Chapter", self)
        self.chapterLayout = QVBoxLayout(self.chapterGroupBox)

        self.addChapterRadioButton = QRadioButton("Add Chapter", self.chapterGroupBox)
        self.chapterLayout.addWidget(self.addChapterRadioButton)

        self.overwriteChapterRadioButton = QRadioButton("Overwrite Chapter", self.chapterGroupBox)
        self.chapterLayout.addWidget(self.overwriteChapterRadioButton)

        self.appendChapterRadioButton = QRadioButton("Append Chapter", self.chapterGroupBox)
        self.chapterLayout.addWidget(self.appendChapterRadioButton)

        self.rightLayout.addWidget(self.chapterGroupBox)
        
        self.stackLayout.addLayout(self.rightLayout)

        self.mainLayout.addLayout(self.stackLayout)

        # Button Box
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.mainLayout.addWidget(self.buttonBox)
        
        self.titleLineEdit.setText(self.title)
        self.chapterLineEdit.setText(self.chapter_name)
        self.chapterCountUp.setChecked(self.count_up)
        self.count_up_method()
        self.fileLocationLineEdit.setText(self.file_path)
        self.saveAsUrlsCheckBox.setChecked(self.urls)
        if self.file == 0:
            self.overwriteFileRadioButton.setChecked(True)
        elif self.file == 1:
            self.addToFileRadioButton.setChecked(True)
        self.file_toggled()
        if self.chapter == 0:
            self.addChapterRadioButton.setChecked(True)
        elif self.chapter == 1:
            self.overwriteChapterRadioButton.setChecked(True)
        elif self.chapter == 2:
            self.appendChapterRadioButton.setChecked(True)
        self.chapter_toggled()
            
        self.fileLocationToolButton.clicked.connect(self.save_file)
        self.chapterCountUp.toggled.connect(self.count_up_method)
        self.overwriteFileRadioButton.toggled.connect(self.file_toggled)
        self.appendChapterRadioButton.toggled.connect(self.chapter_toggled)
            
    def chapter_toggled(self):
        if self.appendChapterRadioButton.isChecked() and not self.overwriteFileRadioButton.isChecked():
            self.chapterLineEdit.setEnabled(False)
            self.chapterCountUp.setEnabled(False)
        else:
            self.chapterLineEdit.setEnabled(True)
            self.chapterCountUp.setEnabled(True)
            
    def file_toggled(self):
        if self.overwriteFileRadioButton.isChecked():
            self.chapterGroupBox.setEnabled(False)
        else:
            self.chapterGroupBox.setEnabled(True)
        self.chapter_toggled()
            
    def count_up_method(self):
        if self.chapterCountUp.isChecked():
            self.chapterLineEdit.setEnabled(False)
        else:
            self.chapterLineEdit.setEnabled(True)
            
    def save_file(self):
        value = QFileDialog.getSaveFileName(self, 'Save File', '', 'Manhwa Viewer Files (*.mwa *.mwa1 *.mvf);;Images (*.png *.xpm *.jpg *.webp)', 'Manhwa Viewer Files')
        print(value)
        self.fileLocationLineEdit.setText(value[0])
            
    def accept(self):
        self.count_up = self.chapterCountUp.isChecked()
        if self.overwriteFileRadioButton.isChecked():
            self.file = 0
        elif self.addToFileRadioButton.isChecked():
            self.file = 1
        if self.addChapterRadioButton.isChecked():
            self.chapter = 0
        elif self.overwriteChapterRadioButton.isChecked():
            self.chapter = 1
        elif self.appendChapterRadioButton.isChecked():
            self.chapter = 2
        self.resultValue = [self.titleLineEdit.text(), 
                            self.chapterLineEdit.text(), self.count_up, 
                            self.fileLocationLineEdit.text(), 
                            self.saveAsUrlsCheckBox.isChecked(), 
                            self.file, self.chapter]
        super().accept()
        
class TaskRunner(QThread):
    task_completed = Signal(bool, object)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.is_running = True
        self.worker_thread = None
        self.result = None
        self.success = False

    class TaskCanceledException(Exception):
        """Exception to be raised when the task is canceled"""
        def __init__(self, message="A intended error occured"):
            self.message = message
            super().__init__(self.message)

    def run(self):
        if not self.is_running:
            return

        try:
            self.worker_thread = threading.Thread(target=self.worker_func)
            self.worker_thread.start()
            self.worker_thread.join()
            self.task_completed.emit(self.success, self.result)
            
        except Exception as e:
            self.task_completed.emit(False, None)
            print(e)

    def worker_func(self):
        try:
            self.result = self.func(*self.args, **self.kwargs)
            self.success = True
        except SystemExit:
            self.success = False
            self.result = None
            print("Task was forcefully stopped.")
        except Exception as e:
            self.success = False
            self.result = None
            print(e)

    def stop(self):
        print("Task is stopping.")
        self.is_running = False
        if not self.isFinished():
            self.raise_exception()
            self.wait()

    def get_thread_id(self):
        if self.worker_thread:
            return self.worker_thread.ident

    def raise_exception(self):
        thread_id = self.get_thread_id()
        if thread_id:
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), ctypes.py_object(SystemExit))
            if res > 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
                print("Exception raise failure")

class CustomProgressDialog(QProgressDialog):

    def __init__(self, windowTitle, windowIcon, windowLable="Doing a task...", buttonText="Cancel", func=lambda: None, *args, **kwargs):
        super().__init__(windowLable, buttonText, 0, 100)
        self.setWindowTitle(windowTitle)
        self.setWindowIcon(QIcon(windowIcon))

        self.taskRunner = TaskRunner(func, *args, **kwargs)
        self.taskRunner.task_completed.connect(self.onTaskCompleted)
        self.task_successful = False

        self.setAutoClose(False)
        self.setAutoReset(False)
        self.setWindowModality(Qt.ApplicationModal)
        self.canceled.connect(self.cancelTask)
        self.show()

        self.taskRunner.start()

        while self.value() < 99 and not self.wasCanceled() and self.taskRunner.isRunning():
            self.setValue(self.value() + 1)
            time.sleep(0.1)
            QApplication.processEvents()

    @Slot(bool, object)
    def onTaskCompleted(self, success, result):
        self.taskRunner.quit()
        self.taskRunner.wait()

        if not self.wasCanceled():
            if success:
                self.task_successful = True
                self.setValue(100)
                print("Task completed successfully! Result:" + str(result))  # Adjust as needed
                QTimer.singleShot(1000, self.accept)  # Close after 1 second if successful
            else:
                palette = QPalette(self.palette())
                palette.setColor(QPalette.Highlight, QColor(Qt.red))
                self.setPalette(palette)
                self.setLabelText("Task failed!")
                self.setCancelButtonText("Close")

    def cancelTask(self):
        self.taskRunner.stop()
        self.taskRunner.wait()
        self.setValue(0)
        self.setLabelText("Task cancelled")
        self.close()

    def closeEvent(self, event):
        if self.taskRunner.isRunning():
            self.cancelTask()
        event.accept()

def absolute_path(relative_path):
    ab = os.path.dirname(__file__)
    return os.path.join(ab, relative_path)

class ManhwaViewer(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.data_folder = absolute_path('data\\')
        self.cache_folder = absolute_path('cache\\')
        
        monitor_stdout(f"{self.data_folder}logs.txt")
        
        self.setupUi()
        
        self.setWindowTitle('Manhwa Viewer 1.2')
        self.setWindowIcon(QIcon(f'{self.data_folder}logo2.png'))
        
        db_path = Path(f"{self.data_folder}data.db")
        self.new = not db_path.is_file()
        self.db = Database(db_path)
        
        self.settings = Settings(self.new, self.db)
        
        g = self.settings.get_geometry()
        self.setGeometry(g[0], g[1], g[2], g[3])
        
        self.manager = AutoProviderManager(absolute_path('.\extensions\\'))
        self.providers = self.manager.get_providers()
        if len(sys.argv) >= 2:
            self.settings.set_file_path(sys.argv[1])
            self.settings.set_provider("file")
        if self.settings.get_provider() == "file":
            self.prov = ManhwaFilePlugin(self.settings.get_title(), self.settings.get_chapter(), self.settings.get_file_path(), self.data_folder, self.cache_folder)
            self.logo_path = f"{self.data_folder}empty.png"
        elif self.settings.get_provider() == "auto":
            self.prov = self.providers[f"AutoProviderPlugin{self.settings.get_autoprovider()}"](self.settings.get_title(), self.settings.get_chapter(), self.data_folder, self.cache_folder, 'direct')
            self.logo_path = self.prov.get_logo_path()
            self.prov.set_blacklisted_websites(self.settings.get_blacklisted_websites())
        print(self.prov)
        self.setWindowTitle(f'MV 1.2 | {self.prov.get_title().title()}, Chapter {self.prov.get_chapter()}')
        
        self.current_width = 0
        self.manual_width = self.settings.get_manual_width()
        self.window_width = 0
        self.current_image_width = 0
        self.prev_downscale_state = self.settings.get_downscaling()
        self.prev_upscale_state = self.settings.get_upscaling()
        self.image_paths = self.get_image_paths()
        self.task_successful = False
        self.threading = False
        
        # Image Labels
        self.image_labels = []
        for image_path in self.image_paths:
            image_label = QLabel()
            image_label.setAlignment(Qt.AlignCenter)
            self.content_layout.addWidget(image_label)
            self.image_labels.append(image_label)
        self.content_layout.addWidget(self.buttons_widget)
        
        if self.settings.get_provider() == "file":
            self.plugin_radio_button_file.setChecked(True)
        if self.settings.get_provider() == "auto":
            self.plugin_radio_button_auto.setChecked(True)
            
        for i in self.providers.keys():
            prov = self.providers[i]("", 1, self.data_folder, self.cache_folder, "direct")
            icon_path = prov.get_logo_path()
            prov = None
            i = i.replace("AutoProviderPlugin", "")
            self.provider_dropdown.addItem(QIcon(icon_path), i)
        self.provider_dropdown.setCurrentText(self.settings.get_autoprovider())
        #self.central_widget.setStyleSheet("background: transparent;")
        
        self.file_lineEdit.setText(self.settings.get_file_path())
        self.title_selector.setText(self.prov.get_title())
        self.chapter_selector.setText(str(self.prov.get_chapter()))
        self.downscale_checkbox.setChecked(self.settings.get_downscaling())
        self.upscale_checkbox.setChecked(self.settings.get_upscaling())
        self.width_spinbox.setValue(self.settings.get_manual_width())
        self.borderless_checkbox.setChecked(self.settings.get_borderless())
        self.invisible_background_checkbox.setChecked(self.settings.get_invisible_background())
        self.hide_scrollbar_checkbox.setChecked(self.settings.get_hide_scrollbar())
        self.stay_on_top_checkbox.setChecked(self.settings.get_stay_on_top())
        self.auto_export_checkbox.setChecked(self.settings.get_auto_export())
        
        self.connectSignals()
        if self.settings.get_provider() == "file": self.reload_chapter()
        self.onRadioBtnToggled()
        self.update_provider_logo()
        self.update_images()
        
    def setupUi(self):
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.verticalScrollBar().setSingleStep(30)
        self.main_layout.addWidget(self.scroll_area)
        
        # Content Widget
        self.content_widget = QWidget()
        self.scroll_area.setWidget(self.content_widget)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(0)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add buttons at the end of the images, side by side
        self.buttons_widget = QWidget()
        self.buttons_layout = QHBoxLayout(self.buttons_widget)
        self.prev_button = QPushButton('Previous')
        self.buttons_layout.addWidget(self.prev_button)
        self.next_button = QPushButton('Next')
        self.buttons_layout.addWidget(self.next_button)
        
        # Add a transparent image on the top left
        self.transparent_image = QLabel(self)
        self.transparent_image.setPixmap(QPixmap(f"{self.cache_folder}empty.png"))
        self.transparent_image.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        opacity = QGraphicsOpacityEffect(self.transparent_image)
        opacity.setOpacity(0.5)  # Adjust the opacity level
        self.transparent_image.setGraphicsEffect(opacity)
        self.transparent_image.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        # Timer to regularly check for resizing needs
        self.timer = QTimer(self)
        self.timer.start(500)
        
        # Side Menu
        self.side_menu = QFrame(self)
        self.side_menu.setFrameShape(QFrame.StyledPanel)
        self.side_menu.setAutoFillBackground(True)
        palette = self.side_menu.palette()
        palette.setColor(self.side_menu.backgroundRole(), QColor('#cccccc'))
        self.side_menu.setPalette(palette)
        self.side_menu.move(800, 0)
        
        # Animation for Side Menu
        self.animation = QPropertyAnimation(self.side_menu, b"geometry")
        self.animation.setDuration(500)
        
        # Side Menu Layout
        self.side_menu_layout = QFormLayout(self.side_menu)
        self.side_menu.setLayout(self.side_menu_layout)
        
        self.plugin_radio_button_file = QRadioButton('Manhwa File', self)
        self.plugin_radio_button_auto = QRadioButton('Auto Provider', self)
        self.side_menu_layout.addRow(self.plugin_radio_button_file, self.plugin_radio_button_auto)
        
        self.file_layout = QHBoxLayout()
        self.file_label = QLabel('File Location:', self)
        self.file_layout.addWidget(self.file_label)
        self.file_lineEdit = QLineEdit()
        self.file_layout.addWidget(self.file_lineEdit)
        self.fileLocationToolButton = QToolButton()
        self.fileLocationToolButton.setText("...")
        self.file_layout.addWidget(self.fileLocationToolButton)
        
        self.side_menu_layout.addRow(self.file_layout)
        
        self.provider_dropdown = QComboBox()#itemIcon(
        
        self.provider_layout = QHBoxLayout()
        self.provider_label = QLabel("Provider:")
        self.provider_layout.addWidget(self.provider_label)
        self.provider_layout.addWidget(self.provider_dropdown)
        self.side_menu_layout.addRow(self.provider_layout)
        
        self.blacklist_button = QPushButton("Blacklist Current URL")
        self.side_menu_layout.addRow(self.blacklist_button)
        
        [self.side_menu_layout.addRow(QWidget()) for _ in range(3)]
        
        self.title_layout = QHBoxLayout()
        self.title_layout.addWidget(QLabel("Title:"))
        self.title_selector = QLineEdit()
        self.title_selector.setMinimumWidth(120)
        self.title_layout.addWidget(self.title_selector)
        self.side_menu_layout.addRow(self.title_layout)
        
        self.chapter_selector = QLineEdit()
        self.side_menu_layout.addRow(QLabel("Chapter:"), self.chapter_selector)
        self.float_validator = QDoubleValidator(0.5, 999.5, 1)
        self.chapter_selector.setValidator(self.float_validator) #setInputMask("000.000.000.000")
        
        self.prev_chapter_button = QPushButton("Previous")
        self.next_chapter_button = QPushButton("Next")
        self.reload_chapter_button = QPushButton(QIcon(f"{self.data_folder}reload_icon.png"), "")
        
        # Create a new horizontal box layout
        self.buttons_layout = QHBoxLayout()
        
        # Add buttons to the horizontal box layout
        self.buttons_layout.addWidget(self.prev_chapter_button)
        self.buttons_layout.addWidget(self.next_chapter_button)
        self.buttons_layout.addWidget(self.reload_chapter_button)
        
        # Add the horizontal box layout containing the buttons to the form layout
        self.side_menu_layout.addRow(self.buttons_layout)
        
        [self.side_menu_layout.addRow(QWidget()) for _ in range(3)]
        
        # Checkboxes
        self.downscale_checkbox = QCheckBox('Downscale if larger than window')
        self.side_menu_layout.addRow(self.downscale_checkbox)
        
        self.upscale_checkbox = QCheckBox('Upscale if smaller than window')
        self.side_menu_layout.addRow(self.upscale_checkbox)
        
        # SpinBox for manual width input and Apply Button
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(10, 2000)
        self.side_menu_layout.addRow(self.width_spinbox)
        
        self.apply_button = QPushButton('Apply Width')
        self.side_menu_layout.addRow(self.apply_button)
        
        [self.side_menu_layout.addRow(QWidget()) for _ in range(3)]
        
        # Checkboxes
        self.borderless_checkbox = QCheckBox('Borderless')
        self.invisible_background_checkbox = QCheckBox('Invisible W.I.P')
        self.side_menu_layout.addRow(self.borderless_checkbox, self.invisible_background_checkbox)
        self.hide_scrollbar_checkbox = QCheckBox('Hide Scrollbar')
        self.stay_on_top_checkbox = QCheckBox('Stay on top')
        self.side_menu_layout.addRow(self.hide_scrollbar_checkbox, self.stay_on_top_checkbox)
        
        [self.side_menu_layout.addRow(QWidget()) for _ in range(3)]
        
        self.auto_export_checkbox = QCheckBox('Auto Export')
        self.side_menu_layout.addRow(self.auto_export_checkbox)
        self.export_button = QPushButton("Export Chapter")
        self.export_settings_button = QPushButton("Export Settings")
        self.side_menu_layout.addRow(self.export_button, self.export_settings_button)
        
        # Menu Button
        self.menu_button = QPushButton(QIcon(f"{self.data_folder}menu_icon.png"), "", self.central_widget)
        self.menu_button.setFixedSize(40, 40)
        
    def connectSignals(self):
        # Connect signals
        self.downscale_checkbox.toggled.connect(self.downscale_checkbox_toggled)
        self.upscale_checkbox.toggled.connect(self.upscale_checkbox_toggled)
        self.borderless_checkbox.toggled.connect(self.toggle_borderless)
        self.invisible_background_checkbox.toggled.connect(self.toggle_invisible_background)
        self.hide_scrollbar_checkbox.toggled.connect(self.toggle_scrollbar)
        self.stay_on_top_checkbox.toggled.connect(self.toggle_stay_on_top)
        self.auto_export_checkbox.toggled.connect(self.toggle_auto_export)
        
        self.file_lineEdit.textChanged.connect(self.set_file_path)
        self.title_selector.textChanged.connect(self.set_title)
        self.chapter_selector.textChanged.connect(self.set_chapter)
        
        self.menu_button.clicked.connect(self.toggle_menu) # Menu
        self.apply_button.clicked.connect(self.apply_manual_width) # Menu
        self.prev_chapter_button.clicked.connect(self.previous_chapter) # Menu
        self.next_chapter_button.clicked.connect(self.next_chapter) # Menu
        self.reload_chapter_button.clicked.connect(self.reload_chapter) # Menu
        self.prev_button.clicked.connect(self.previous_chapter)
        self.next_button.clicked.connect(self.next_chapter)
        self.export_settings_button.clicked.connect(self.export_settings) # Menu
        self.export_button.clicked.connect(self.export_chapter) # Menu
        self.blacklist_button.clicked.connect(self.blacklist_current_url) # Menu
        self.fileLocationToolButton.clicked.connect(self.open_file) # Menu
        
        #self.plugin_radio_button_file.toggled.connect(self.onRadioBtnToggled) # Menu
        self.plugin_radio_button_auto.toggled.connect(self.onRadioBtnToggled) # Menu
        
        self.provider_dropdown.currentIndexChanged.connect(self.change_provider) # Menu
        self.animation.valueChanged.connect(self.update_button_position) # Menu
        self.timer.timeout.connect(self.timer_tick)
        
    def toggle_auto_export(self):
        self.settings.set_auto_export(self.auto_export_checkbox.isChecked())
        
    def open_file(self):
        value = QFileDialog.getOpenFileName(self, 'Open File', '', 'Manhwa Viewer Files (*.mwa *.mwa1 *.mvf);;Images (*.png *.xpm *.jpg *.webp)', 'Manhwa Viewer Files')
        print(value)
        self.file_lineEdit.setText(value[0])
        
    def blacklist_current_url(self):
        search_machines_lst = ["Google", "DuckDuckGo", "Bing"]
        if self.settings.get_provider() == "auto" and (self.provider_dropdown.currentText() in search_machines_lst or self.prov.get_provider() in search_machines_lst):
            blk_urls = self.prov.get_blacklisted_websites()
            blk_urls.append(self.prov.get_current_url().split("/")[2])
            self.prov.set_blacklisted_websites(blk_urls)
            self.settings.set_blacklisted_websites(self.prov.get_blacklisted_websites())
            QMessageBox.information(self, "Info", 
                                      f"Blacklisted Website {blk_urls[-1]}.\nThis won't affect normal Auto-Providers (All that aren't Search Engines).'",
                                      QMessageBox.StandardButtons(QMessageBox.Ok),
                                      QMessageBox.Ok)
        else:
            QMessageBox.information(self, "Info", "You can't blacklist that website.")
        
    def export_chapter(self):
        export_settings = self.settings.get_export_settings()
        title = export_settings[0]
        chapter_number = export_settings[1] if export_settings[2] != "True" else str(self.prov.get_chapter())
        file_path = export_settings[3]
        file_mode = int(export_settings[5])
        chapter_mode = int(export_settings[6])

        if not chapter_number and chapter_mode == 2:
            with open(file_path, 'r') as file:
                data = json.load(file)
                if data['chapters']:
                    sorted_chapters = sorted(data['chapters'], key=lambda x: x['chapterNumber'])
                    last_chapter_number = sorted_chapters[-1]['chapterNumber']
                    chapter_number = last_chapter_number + 1

        # Convert images to base64
        base64_encoded_images = []
        for image_path in self.image_paths:
            with open(image_path, 'rb') as image_file:
                base64_encoded = base64.b64encode(image_file.read()).decode()
                base64_encoded_images.append({"type": "base64", "data": base64_encoded})

        new_chapter_data = {
            "chapterNumber": int(float(chapter_number)),
            "title": f"Chapter {chapter_number}",
            "pages": base64_encoded_images
        }

        if os.path.exists(file_path) and file_mode == 0:  # If file exists and file mode is overwrite
            data = {
                "metadata": {
                    "title": title  # Add other metadata as needed
                },
                "chapters": [new_chapter_data]  # This will overwrite the existing data
            }

            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)

        elif os.path.exists(file_path) and file_mode == 1:  # If file exists and file mode is add
            with open(file_path, 'r+') as file:
                data = json.load(file)

                # Implement your chapter mode logic here
                # For example:
                if chapter_mode == 0:  # If chapter mode is add if not exists
                    existing_chapter = next((c for c in data['chapters'] if c['chapterNumber'] == int(float(chapter_number))), None)
                    if not existing_chapter:
                        data['chapters'].append(new_chapter_data)

                # Implement other chapter mode conditions

                file.seek(0)
                file.truncate()
                json.dump(data, file, indent=4)

        else:  # If file doesn't exist, create new
            data = {
                "metadata": {
                    "title": title  # Add other metadata as needed
                },
                "chapters": [new_chapter_data]
            }

            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
                    
    def export_settings(self):
        settings = self.settings.get_export_settings()
        if settings != [""]:
            dialog = ExportDialog(self, settings)
        else:
            dialog = ExportDialog(self)
        result = dialog.exec_()

        if result == QDialog.Accepted:
            value = dialog.resultValue
            self.settings.set_export_settings(value)
            #QMessageBox.information(self, "Saved", f"Saved Settings: {value}") # Debug
        
    def set_file_path(self):
        self.prov.set_file_path(self.title_selector.text())
        self.settings.set_file_path(self.title_selector.text())
        
    def closeEvent(self, event):
        can_exit = True
        if can_exit:
            print("Exiting ...")
            if self.settings.get_provider() == "auto":
                self.settings.set_autoprovider(self.provider_dropdown.currentText())
            elif self.settings.get_provider() == "file":
                self.settings.set_file_path(self.file_lineEdit.text())
            self.settings.set_title(self.prov.get_title())
            self.settings.set_chapter(self.prov.get_chapter())
            self.settings.set_downscaling(self.downscale_checkbox.isChecked())
            self.settings.set_upscaling(self.upscale_checkbox.isChecked())
            self.settings.set_manual_width(self.width_spinbox.value())
            self.settings.set_borderless(self.borderless_checkbox.isChecked())
            self.settings.set_invisible_background(self.invisible_background_checkbox.isChecked())
            self.settings.set_hide_scrollbar(self.hide_scrollbar_checkbox.isChecked())
            self.settings.set_stay_on_top(self.stay_on_top_checkbox.isChecked())
            self.settings.set_geometry([100, 100, self.width(), self.height()])
            self.settings.set_blacklisted_websites(self.prov.get_blacklisted_websites())
            self.settings.set_auto_export(self.auto_export_checkbox.isChecked()) # Export settings can't get saved here
            self.prov.redo_prep()
            event.accept() # let the window close
        else:
            print("Couldn't exit.")
            event.ignore()
        
    def onRadioBtnToggled(self):
        if self.plugin_radio_button_file.isChecked():
            self.prov = ManhwaFilePlugin(self.settings.get_title(), self.settings.get_chapter(), self.settings.get_file_path(), self.data_folder, self.cache_folder)
            self.logo_path = f"{self.data_folder}empty.png"
            new_pixmap = QPixmap(self.logo_path)
            self.transparent_image.setPixmap(new_pixmap)
            self.settings.set_provider("file")
            #self.file_label.setEnabled(True)
            self.file_lineEdit.setEnabled(True)
            #self.provider_label.setEnabled(False)
            self.provider_dropdown.setEnabled(False)
            self.blacklist_button.setEnabled(False)
            self.export_button.setEnabled(False)
            self.export_settings_button.setEnabled(False)
            self.auto_export_checkbox.setEnabled(False)
            self.title_selector.setEnabled(False)
        elif self.plugin_radio_button_auto.isChecked():
            self.settings.set_provider("auto")
            #self.file_label.setEnabled(False)
            self.file_lineEdit.setEnabled(False)
            #self.provider_label.setEnabled(True)
            self.provider_dropdown.setEnabled(True)
            self.blacklist_button.setEnabled(True)
            self.export_button.setEnabled(True)
            self.export_settings_button.setEnabled(True)
            self.auto_export_checkbox.setEnabled(True)
            self.fileLocationToolButton.setEnabled(False)
            self.title_selector.setEnabled(True)
            self.change_provider()
        #self.repaint()
            
    def change_provider(self):
        temp = self.prov
        self.prov = self.providers[f"AutoProviderPlugin{self.provider_dropdown.currentText()}"](self.prov.get_title(), self.prov.get_chapter(), self.data_folder, self.cache_folder, 'direct')
        self.settings.set_autoprovider(self.provider_dropdown.currentText())
        self.prov.set_blacklisted_websites(self.settings.get_blacklisted_websites())
        self.logo_path = self.prov.get_logo_path()
        new_pixmap = QPixmap(self.logo_path)
        self.transparent_image.setPixmap(new_pixmap)
        self.update_provider_logo()
        #QApplication.processEvents()
        #time.sleep(2)
        result = QMessageBox.question(self, "Reload Chapter?", 
                                      "You must reload the chapter.\nDo you wish to continue?",
                                      QMessageBox.StandardButtons(QMessageBox.Yes | QMessageBox.No),
                                      QMessageBox.Yes)
        if result == QMessageBox.Yes:
            self.prov.reload_chapter()
            self.reload_images()
        else:
            #state = True if self.prov == temp else False
            self.prov = temp
            #if state: self.prov.redo_prep()
            #self.prov.reload_chapter()
            prov_name = type(self.prov).__name__
            self.logo_path = self.prov.get_logo_path() if prov_name != "ManhwaFilePlugin" else f"{self.data_folder}empty.png"
            new_pixmap = QPixmap(self.logo_path)
            self.transparent_image.setPixmap(new_pixmap)
            self.update_provider_logo()
            if prov_name != "ManhwaFilePlugin":
                self.provider_dropdown.currentIndexChanged.disconnect()
                self.provider_dropdown.setCurrentText(prov_name.replace("AutoProviderPlugin", "")) # x.__class__.__name__
                self.provider_dropdown.currentIndexChanged.connect(self.change_provider)
            else:
                self.plugin_radio_button_file.setChecked(True)
        
    def set_title(self):
        self.settings.set_title(self.title_selector.text())
        self.prov.set_title(self.title_selector.text())
        
    def set_chapter(self):
        new_chapter = float("0" + self.chapter_selector.text())
        if new_chapter >= 0 and new_chapter < 1000:
            #self.settings.set_chapter(new_chapter)
            self.prov.set_chapter(new_chapter) # fix -> leave it to chapter methods
        else:
            self.settings.set_chapter(0)
            self.chapter_selector.setText("0")
            
    def toggle_borderless(self):
        if self.windowFlags() & Qt.FramelessWindowHint:
            self.setWindowFlags(self.windowFlags() & ~Qt.FramelessWindowHint)
        else:
            self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.settings.set_borderless(self.borderless_checkbox.isChecked())
        self.show()
        
    def toggle_invisible_background(self):
        print("This is a work in progress, please check back when it's completed")
        self.settings.set_invisible_background(self.invisible_background_checkbox.isChecked())
        
    def toggle_scrollbar(self):
        if self.scroll_area.verticalScrollBarPolicy() == Qt.ScrollBarAlwaysOff:
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        else:
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.settings.set_hide_scrollbar(self.hide_scrollbar_checkbox.isChecked())
            
    def toggle_stay_on_top(self):
        if self.windowFlags() & Qt.WindowStaysOnTopHint:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.settings.set_stay_on_top(self.stay_on_top_checkbox.isChecked())
        self.show()
        
    def resizeEvent(self, event):
        self.window_width = self.width()
        self.settings.set_geometry([100, 100, self.width(), self.height()])
        
        self.side_menu.move(self.window_width, 0) # Update the position of the side menu
        self.animation.setStartValue(QRect(self.window_width, 0, 0, self.height()))
        self.animation.setEndValue(QRect(self.window_width - 200, 0, 200, self.height()))  # Adjust 200 as per the desired width of the side menu
        self.menu_button.move(self.window_width - 40, 20) # Update the position of the menu button
        
        self.update_provider_logo()
        
        super().resizeEvent(event)
        
    def update_provider_logo(self):
        max_size = self.width() // 3
        min_size = self.width() // 10
        current_image_width = self.transparent_image.pixmap().width() if self.transparent_image.pixmap() else 0 # Adjust the size of the transparent image based on window width
        if not min_size <= current_image_width <= max_size: # If the current image width is outside the min and max size range, resize it
            scaled_pixmap = QPixmap(self.logo_path).scaledToWidth(max_size, Qt.SmoothTransformation)
            self.transparent_image.setPixmap(scaled_pixmap)
        self.transparent_image.setFixedSize(max_size, max_size)
        
    def toggle_menu(self):
        width = 200
        height = self.height()

        if self.side_menu.x() >= self.width():
            start_value = QRect(self.width(), 0, width, height)
            end_value = QRect(self.width() - width, 0, width, height)
        else:
            start_value = QRect(self.width() - width, 0, width, height)
            end_value = QRect(self.width(), 0, width, height)

        self.animation.setStartValue(start_value)
        self.animation.setEndValue(end_value)
        self.animation.start()
        
    def update_button_position(self, value):
        self.menu_button.move(value.x() - self.menu_button.width(), 20)
        
    def downscale_checkbox_toggled(self):
        self.settings.set_downscaling(self.downscale_checkbox.isChecked())
        self.update_images()
        
    def upscale_checkbox_toggled(self):
        self.settings.set_upscaling(self.upscale_checkbox.isChecked())
        self.update_images()
        
    def apply_manual_width(self):
        self.manual_width = self.width_spinbox.value()
        self.settings.set_manual_width(self.width_spinbox.value())
        self.update_images()
        
    def get_image_paths(self): # Make better
        image_files = sorted([f for f in os.listdir(self.cache_folder) if f.endswith('.png')])
        image_paths = [os.path.join(self.cache_folder, f) for f in image_files]
        return image_paths
        
    def update_images(self):
        scroll_area_width = self.scroll_area.viewport().width()
        try: self.current_image_width = self.image_labels[0].pixmap().width() if self.image_labels[0].pixmap() else 0 # Obtaining the current width of the pixmaps in the labels
        except: return False
        self.standart_image_width = self.current_image_width if not self.manual_width else self.manual_width
        conditions = [
            self.window_width != self.current_width,
            self.prev_downscale_state != self.downscale_checkbox.isChecked() or self.downscale_checkbox.isChecked() and self.standart_image_width > scroll_area_width,
            self.prev_upscale_state != self.upscale_checkbox.isChecked() or self.upscale_checkbox.isChecked() and self.standart_image_width < scroll_area_width,
            self.manual_width and self.manual_width != self.current_image_width and not 
            ((self.downscale_checkbox.isChecked() and self.standart_image_width >= scroll_area_width) or 
            (self.upscale_checkbox.isChecked() and self.standart_image_width <= scroll_area_width))
        ]
        if any(conditions) or self.current_image_width == 0: # Check if images are not loaded yet
            self.current_width = self.window_width
            self.prev_downscale_state = self.downscale_checkbox.isChecked()
            self.prev_upscale_state = self.upscale_checkbox.isChecked()
            new_image_width = None
            
            if self.manual_width:
                new_image_width = self.manual_width
            else:
                new_image_width = QPixmap(self.image_paths[0]).width()  # Use original image width as fallback
                
            if self.downscale_checkbox.isChecked():
                if self.manual_width and self.manual_width > scroll_area_width:
                    new_image_width = scroll_area_width
                elif not self.manual_width and new_image_width > scroll_area_width:
                    new_image_width = scroll_area_width
            if self.upscale_checkbox.isChecked(): # two ifs are okay, as the other conditions can't be fullfilled at the same time
                if self.manual_width and self.manual_width < scroll_area_width:
                    new_image_width = scroll_area_width
                elif not self.manual_width and new_image_width < scroll_area_width:
                    new_image_width = scroll_area_width
                    
            if new_image_width and self.current_image_width != new_image_width:
                for i, image_path in enumerate(self.image_paths):
                    pixmap = QPixmap(image_path)
                    pixmap = pixmap.scaledToWidth(new_image_width, Qt.SmoothTransformation)
                    self.current_image_width = new_image_width
                    self.image_labels[i].setPixmap(pixmap)
        
    def reload_images(self):
        # Update image paths dynamically
        self.image_paths = self.get_image_paths()

        # If the number of images has changed, recreate the image labels
        if len(self.image_labels) != len(self.image_paths):
            for label in self.image_labels:
                self.content_layout.removeWidget(label)
                label.deleteLater()

            self.image_labels = []
            for image_path in self.image_paths:
                image_label = QLabel()
                image_label.setAlignment(Qt.AlignCenter)
                self.content_layout.addWidget(image_label)
                self.image_labels.append(image_label)

        # Load new images into the labels
        for i, image_path in enumerate(self.image_paths):
            pixmap = QPixmap(image_path)
            self.image_labels[i].setPixmap(pixmap)

        # Move the chapter buttons to the end
        self.content_layout.removeWidget(self.buttons_widget)
        self.content_layout.addWidget(self.buttons_widget)

        self.update_images()
        self.repaint()
        print("Images reloaded")
        
    def next_chapter(self):
        self.threading = True
        self.progressDialog = CustomProgressDialog(windowTitle="Loading ...", windowIcon=f"{self.data_folder}logo2.png", func=self.prov.next_chapter)
        self.progressDialog.exec_()

        self.task_successful = self.progressDialog.task_successful
        self.threading = False

        if self.task_successful:
            self.setWindowTitle(f'MV 1.2 | {self.prov.get_title().title()}, Chapter {self.prov.get_chapter()}')
            self.settings.set_chapter(self.prov.get_chapter())
            if self.settings.get_auto_export() and self.settings.get_provider() == "auto": self.export_chapter()
            self.task_successful = False
        else:
            self.prov.set_chapter(self.settings.get_chapter())
            self.prov.reload_chapter()
            QMessageBox.information(self, "Info | Loading of chapter has failed!", 
                                      "The loading of the next chapter has failed.\nLook in the logs for more info.",
                                      QMessageBox.StandardButtons(QMessageBox.Ok),
                                      QMessageBox.Ok)
        self.chapter_selector.setText(str(self.settings.get_chapter()))
        print("Reloading images...")
        self.scroll_area.verticalScrollBar().setValue(0) # Reset the scrollbar position to the top
        self.reload_images()
        
    def previous_chapter(self):
        self.threading = True
        self.progressDialog = CustomProgressDialog(windowTitle="Loading ...", windowIcon=f"{self.data_folder}logo2.png", func=self.prov.previous_chapter)
        self.progressDialog.exec_()

        self.task_successful = self.progressDialog.task_successful
        self.threading = False

        if self.task_successful:
            self.setWindowTitle(f'MV 1.2 | {self.prov.get_title().title()}, Chapter {self.prov.get_chapter()}')
            self.settings.set_chapter(self.prov.get_chapter())
            if self.settings.get_auto_export() and self.settings.get_provider() == "auto": self.export_chapter()
            self.task_successful = False
        else:
            self.prov.set_chapter(self.settings.get_chapter())
            self.prov.reload_chapter()
            QMessageBox.information(self, "Info | Loading of chapter has failed!", 
                                      "The loading of the previous chapter has failed.\nLook in the logs for more info.",
                                      QMessageBox.StandardButtons(QMessageBox.Ok),
                                      QMessageBox.Ok)
        self.chapter_selector.setText(str(self.settings.get_chapter()))
        print("Reloading images...")
        self.scroll_area.verticalScrollBar().setValue(0) # Reset the scrollbar position to the top
        self.reload_images()
        
    def reload_chapter(self):
        self.threading = True
        self.progressDialog = CustomProgressDialog(windowTitle="Loading ...", windowIcon=f"{self.data_folder}logo2.png", func=self.prov.reload_chapter)
        self.progressDialog.exec_()

        self.task_successful = self.progressDialog.task_successful
        self.threading = False

        if self.task_successful:
            self.setWindowTitle(f'MV 1.2 | {self.prov.get_title().title()}, Chapter {self.prov.get_chapter()}')
            self.settings.set_chapter(self.prov.get_chapter())
            if self.settings.get_auto_export() and self.settings.get_provider() == "auto": self.export_chapter() # Keep?
            self.task_successful = False
        else:
            self.prov.set_chapter(self.settings.get_chapter())
            self.prov.reload_chapter()
            QMessageBox.information(self, "Info | Reloading of chapter has failed", 
                                      "The reloading the current chapter has failed.\nLook in the logs for more info.",
                                      QMessageBox.StandardButtons(QMessageBox.Ok),
                                      QMessageBox.Ok)
        self.chapter_selector.setText(str(self.settings.get_chapter()))
        print("Reloading images...")
        self.scroll_area.verticalScrollBar().setValue(0) # Reset the scrollbar position to the top
        self.reload_images()

    def timer_tick(self):
        if not self.threading: self.update_images()
        #print("Update tick") # Debug

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ManhwaViewer()
    viewer.show()
    sys.exit(app.exec_())
