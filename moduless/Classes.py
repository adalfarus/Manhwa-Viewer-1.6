from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QScrollArea, QLineEdit,
                               QLabel,
                               QApplication, QProgressDialog, QWidget, QListWidget, QSizePolicy, QListWidgetItem,
                               QMessageBox, QStyledItemDelegate, QComboBox)
from PySide6.QtCore import Qt, Signal, QThread, QTimer, Slot, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QPalette, QIcon, QPixmap, QFont, QWheelEvent
from aplustools.io import environment as env
from typing import Literal, Optional, List
import threading
import importlib
import random
import ctypes
import queue
import time
import os
from aplustools.package.timid import TimidTimer


class CustomLabel(QLabel):
    def paintEvent(self, event):
        painter = QPainter(self)

        if self.text():
            main_window = self.window()
            while main_window.parent() is not None:
                main_window = main_window.parent()
            # If the label has text, apply background color based on the current theme
            if main_window.theme == "light":
                painter.setBrush(QBrush(QColor('#d0d0d0')))
            else:
                painter.setBrush(QBrush(QColor('#555555')))

            painter.setPen(QPen(Qt.NoPen))  # No border outline
            radius = 5
            painter.drawRoundedRect(self.rect(), radius, radius)

        painter.end()
        # super().paintEvent(event)


class TaskRunner(QThread):
    task_completed = Signal(bool, object)
    progress_signal = Signal(int)

    def __init__(self, new_thread, func, *args, **kwargs):
        super().__init__()
        self.new_thread = new_thread
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.is_running = True
        self.worker_thread = None
        self.result = None
        self.success = False
        if new_thread:
            self.progress_queue = queue.Queue()

    class TaskCanceledException(Exception):
        """Exception to be raised when the task is canceled"""
        def __init__(self, message="A intended error occured"):
            self.message = message
            super().__init__(self.message)

    def run(self):
        if not self.is_running:
            return

        try:
            if self.new_thread:
                self.worker_thread = threading.Thread(target=self.worker_func)
                self.worker_thread.start()
                while self.worker_thread.is_alive():
                    try:
                        progress = self.progress_queue.get_nowait()
                        self.progress_signal.emit(progress)
                    except queue.Empty:
                        pass
                    self.worker_thread.join(timeout=0.1)
                print("Worker thread died. Emitting result now ...")
            else:
                print("Directly executing")
                update = False
                for update in self.func(*self.args, **self.kwargs)():
                    if isinstance(update, int):
                        self.progress_signal.emit(update)
                self.result = update
                print("RES", self.result)
            self.task_completed.emit(self.success, self.result)

        except Exception as e:
            self.task_completed.emit(False, None)
            print(e)

    def worker_func(self):
        try:
            if self.new_thread:
                self.result = self.func(*self.args, **self.kwargs, progress_queue=self.progress_queue)
            else:
                return self.func(*self.args, **self.kwargs)
            self.success = True
        except SystemExit:
            self.success = False
            self.result = None
            print("Task was forcefully stopped.")
        except Exception as e:
            self.success = False
            self.result = None
            print(f"Error in TaskRunner: {e}")

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
    def __init__(self, parent, window_title, window_icon, window_label="Doing a task...", button_text="Cancel",
                 new_thread=True, func=lambda: None, *args, **kwargs):
        super().__init__(parent=parent, cancelButtonText=button_text, minimum=0, maximum=100)
        self.ttimer = TimidTimer()
        self.setWindowTitle(window_title)
        # self.setValue(0)
        # self.setWindowIcon(QIcon(window_icon))

        self.customLayout = QVBoxLayout(self)
        self.customLabel = QLabel(window_label, self)
        self.customLayout.addWidget(self.customLabel)
        self.customLayout.setAlignment(self.customLabel, Qt.AlignTop | Qt.AlignHCenter)

        self.taskRunner = TaskRunner(new_thread, func, *args, **kwargs)
        self.taskRunner.task_completed.connect(self.onTaskCompleted)
        self.taskRunner.progress_signal.connect(self.set_value)  # Connect progress updates
        self.task_successful = False

        self.setAutoClose(False)
        self.setAutoReset(False)
        self.setWindowModality(Qt.ApplicationModal)
        self.canceled.connect(self.cancelTask)
        self.show()

        self.last_value = 0
        self.current_value = 0
        QTimer.singleShot(50, self.taskRunner.start)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateProgress)
        self.timer.start(100)
        print(self.ttimer.tick(), "INIT DONE")

    def updateProgress(self):
        if self.value() <= 100 and not self.wasCanceled() and self.taskRunner.isRunning():
            if self.current_value == 0 and self.value() < 10:
                self.setValue(self.value() + 1)
                time.sleep(random.randint(2, 10) * 0.1)
            elif self.current_value >= 10:
                self.smooth_value()
            QApplication.processEvents()

    def set_value(self, v):
        self.current_value = v

    def smooth_value(self):
        # If the difference is significant, set the value immediately
        if abs(self.current_value - self.last_value) > 10:  # You can adjust this threshold
            self.setValue(self.current_value)
            self.last_value = self.current_value
            return

        for i in range(max(10, self.last_value), self.current_value):
            self.setValue(i + 1)
            self.last_value = i + 1
            time.sleep(0.1)
        # print(f"Exiting go_to_value with value {self.current_value} and last_value {self.last_value}") # Debug

    def resizeEvent(self, event):
        super(CustomProgressDialog, self).resizeEvent(event)

        # Attempt to find the label as a child widget
        label: QLabel = self.findChild(QLabel)
        if label:
            label.setStyleSheet("""background: transparent;""")

    @Slot(bool, object)
    def onTaskCompleted(self, success, result):
        print("Task completed method called.")
        self.taskRunner.quit()
        self.taskRunner.wait()

        if not self.wasCanceled():
            if success:
                self.task_successful = True
                self.setValue(100)
                print("Task completed successfully! Result:" + str(
                    "Finished" if result else "Not finished"))  # Adjust as needed
                QTimer.singleShot(1000, self.accept)  # Close after 1 second if successful
            else:
                palette = QPalette(self.palette())
                palette.setColor(QPalette.Highlight, QColor(Qt.red))
                self.setPalette(palette)
                self.customLabel.setText("Task failed!")
                self.setCancelButtonText("Close")
        print("DONE", self.ttimer.end())

    def cancelTask(self):
        self.taskRunner.stop()
        self.taskRunner.wait()
        self.setValue(0)
        self.customLabel.setText("Task cancelled")
        self.close()

    def closeEvent(self, event):
        if self.taskRunner.isRunning():
            self.cancelTask()
        event.accept()


class ImageLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SearchResultItem(QWidget):
    def __init__(self, title, description, icon_path):
        super().__init__()

        self.layout = QHBoxLayout(self)

        self.icon_label = QLabel(self)
        self.icon_label.setPixmap(QPixmap(icon_path).scaledToWidth(50, Qt.SmoothTransformation))
        self.layout.addWidget(self.icon_label)

        self.text_layout = QVBoxLayout()
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont('Arial', 14, QFont.Bold))
        self.text_layout.addWidget(self.title_label)

        self.description_label = QLabel(description)
        self.description_label.setFont(QFont('Arial', 10))
        self.text_layout.addWidget(self.description_label)

        self.layout.addLayout(self.text_layout)


class SearchWidget(QWidget):
    selectedItem = Signal(str)

    def __init__(self, search_results_func):
        super().__init__()
        self.initUI()
        self.search_results_func = search_results_func

    def set_search_results_func(self, new_func):
        self.search_results_func = new_func

    def sizeHint(self):
        search_bar_size_hint = self.search_bar.sizeHint()
        if self.results_list.isVisible():
            results_list_size_hint = self.results_list.sizeHint()
            # Combine the heights and take the maximum width
            combined_height = search_bar_size_hint.height() + results_list_size_hint.height()
            combined_width = max(search_bar_size_hint.width(), results_list_size_hint.width())
            return QSize(combined_width, combined_height)
        else:
            return search_bar_size_hint  # Return size hint of search_bar

    def minimumSizeHint(self):
        return self.search_bar.minimumSizeHint()

    def initUI(self):
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.textChanged.connect(self.on_text_changed)
        self.search_bar.returnPressed.connect(self.on_return_pressed)

        self.results_list = QListWidget(self)
        self.results_list.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Ignored)
        self.results_list.hide()
        self.results_list.itemActivated.connect(self.on_item_activated)

        layout = QVBoxLayout(self)
        layout.addWidget(self.search_bar)
        layout.addWidget(self.results_list)
        layout.setContentsMargins(0, 0, 0, 0)  # Set margins to zero
        layout.setSpacing(0)  # Set spacing to zero

    def on_text_changed(self, text):
        self.results_list.clear()
        if text and self.search_bar.hasFocus():
            # Assume get_search_results is a function that returns a list of tuples with the result text and icon path.
            results = self.search_results_func(text)
            for result_text, icon_path in results:
                item = QListWidgetItem(result_text)
                item.setIcon(QIcon(env.absolute_path(icon_path)))
                self.results_list.addItem(item)
            self.results_list.show()
        else:
            self.results_list.hide()

        self.adjustSize()
        self.updateGeometry()  # Notify the layout system of potential size change
        self.results_list.updateGeometry()  # Notify the layout system of potential size change
        # self.window().adjustSize()  # Adjust the size of the parent window

    def on_return_pressed(self):
        item = self.results_list.currentItem() or self.results_list.item(0)
        if item:
            self.select_item(item)

    def on_item_activated(self, item):
        self.select_item(item)

    def select_item(self, item):
        title = item.text()
        print(f'Selected: {title}')
        self.search_bar.setText('')
        self.results_list.hide()
        self.selectedItem.emit(title)


class AdvancedQMessageBox(QMessageBox):
    def __init__(self, parent=None, icon=None, window_title='', text='', detailed_text='',
                 checkbox=None, standard_buttons=QMessageBox.StandardButton.Ok, default_button=None):
        """
        An advanced QMessageBox with additional configuration options.

        :param parent: The parent widget.
        :param icon: The icon to display.
        :param window_title: The title of the message box window.
        :param text: The text to display.
        :param detailed_text: The detailed text to display.
        :param checkbox: A QCheckBox instance.
        :param standard_buttons: The standard buttons to include.
        :param default_button: The default button.
        """
        super().__init__(parent)
        self.setStandardButtons(standard_buttons)
        for arg, func in zip([icon, window_title, text, detailed_text, checkbox, default_button],
                             ["setIcon", "setWindowTitle", "setText", "setDetailedText", "setCheckBox", "setDefaultButton"]):
            if arg:
                getattr(self, func)(arg)

        # Set the window to stay on top initially
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMaximized)

        self.raise_()
        self.activateWindow()


class QAdvancedSmoothScrollingArea(QScrollArea):
    def __init__(self, parent=None, sensitivity: int = 1):
        super().__init__(parent)
        self.setWidgetResizable(True)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Scroll animations for both scrollbars
        self.v_scroll_animation = QPropertyAnimation(self.verticalScrollBar(), b"value")
        self.h_scroll_animation = QPropertyAnimation(self.horizontalScrollBar(), b"value")
        for anim in (self.v_scroll_animation, self.h_scroll_animation):
            anim.setEasingCurve(QEasingCurve.OutCubic)
            anim.setDuration(500)

        self.sensitivity = sensitivity

        # Scroll accumulators
        self.v_toScroll = 0
        self.h_toScroll = 0

        self.primary_scrollbar = "vertical"

    def set_primary_scrollbar(self, new_primary_scrollbar: Literal["vertical", "horizontal"]):
        self.primary_scrollbar = new_primary_scrollbar

    def change_scrollbar_state(self, scrollbar: Literal["vertical", "horizontal"], state: bool = False):
        state = Qt.ScrollBarPolicy.ScrollBarAsNeeded if state else Qt.ScrollBarPolicy.ScrollBarAlwaysOff

        if scrollbar == "vertical":
            self.setVerticalScrollBarPolicy(state)
        else:
            self.setHorizontalScrollBarPolicy(state)

    def wheelEvent(self, event: QWheelEvent):
        horizontal_event_dict = {
            "scroll_bar": self.horizontalScrollBar(),
            "animation": self.h_scroll_animation,
            "toScroll": self.h_toScroll
        }
        vertical_event_dict = {
            "scroll_bar": self.verticalScrollBar(),
            "animation": self.v_scroll_animation,
            "toScroll": self.v_toScroll
        }

        # Choose scroll bar based on right mouse button state
        if event.buttons() & Qt.MouseButton.RightButton:
            event_dict = horizontal_event_dict if self.primary_scrollbar == "vertical" else vertical_event_dict
        else:
            event_dict = vertical_event_dict if self.primary_scrollbar == "vertical" else horizontal_event_dict

        angle_delta = event.angleDelta().y()
        steps = angle_delta / 120
        pixel_step = int(event_dict.get("scroll_bar").singleStep() * self.sensitivity)

        if event_dict.get("animation").state() == QPropertyAnimation.Running:
            event_dict.get("animation").stop()
            event_dict["toScroll"] += event_dict.get("animation").endValue() - event_dict.get("scroll_bar").value()

        current_value = event_dict.get("scroll_bar").value()
        max_value = event_dict.get("scroll_bar").maximum()
        min_value = event_dict.get("scroll_bar").minimum()

        # Inverted scroll direction calculation
        event_dict["toScroll"] -= pixel_step * steps
        proposed_value = current_value + event_dict["toScroll"]  # Reflecting changes

        if proposed_value > max_value and steps > 0:
            event_dict["toScroll"] = 0
        elif proposed_value < min_value and steps < 0:
            event_dict["toScroll"] = 0

        new_value = current_value + event_dict["toScroll"]
        event_dict.get("animation").setStartValue(current_value)
        event_dict.get("animation").setEndValue(new_value)
        event_dict.get("animation").start()

        event.accept()  # Prevent further processing of the event


class Settings:
    def __init__(self, new, db, overwrite_settings: Optional[dict] = None):
        self.new = new
        self.db = db
        self.default_settings = {
            "provider": "ManhwaClan",
            "title": "Thanks for using ManhwaViewer!",
            "chapter": "1",
            "downscaling": "True",
            "upscaling": "False",
            "manual_content_width": "1200",
            "borderless": "True",
            "hide_titlebar": "False",
            "hover_effect_all": "True",
            "acrylic_menus": "True",
            "acrylic_background": "False",
            "hide_scrollbar": "True",
            "stay_on_top": "False",
            "geometry": "100, 100, 640, 480",
            "blacklisted_websites": "247manga.com, ww6.mangakakalot.tv, jimanga.com, mangapure.net, mangareader.mobi, onepiece.fandom.com, mangaowl.io",
            "advanced_settings": "",
            "provider_type": "direct",
            "chapter_rate": "0.5",
            "no_update_info": "True",
            "update_info": "True",
            "last_scroll_positions": "0, 0",
            "scrolling_sensitivity": "4.0",
            "lazy_loading": "True",
            "save_last_titles": "True"
        }
        self.settings = self.default_settings
        if overwrite_settings:
            self.settings.update(overwrite_settings)
        if self.new is True:
            self.setup_database(self.settings)
        self.fetch_data()

    def get_default_setting(self, setting: str):
        return self.default_settings.get(setting)

    def boolean(self, to_boolean: str) -> bool:
        return to_boolean.lower() == "true"

    def str_to_list(self, s: str) -> List[str]:
        return s.split(", ")

    def list_to_str(self, lst: List[str]) -> str:
        return ', '.join(lst)

    def get(self, key: str):
        value = self.settings.get(key)
        if key in ["blacklisted_websites", "advanced_settings"]:
            return self.str_to_list(value)
        elif key in ["chapter"]:
            return int(value) if float(value).is_integer() else float(value)
        elif key in ["chapter_rate", "scrolling_sensitivity"]:
            return float(value)
        elif key in ["downscaling", "upscaling", "borderless", "hide_titlebar", "hover_effect_all",
                     "acrylic_menus", "acrylic_background", "hide_scrollbar", "stay_on_top", "no_update_info",
                     "update_info", "lazy_loading", "save_last_titles"]:
            return self.boolean(value)
        elif key in ["manual_content_width"]:
            return int(value)
        elif key in ["geometry", "last_scroll_positions"]:
            return [int(x) for x in value.split(", ")]
        return value

    def set(self, key: str, value):
        if key in ["blacklisted_websites", "advanced_settings"]:
            value = self.list_to_str(value)
        elif key in ["chapter"]:
            value = str(int(value) if float(value).is_integer() else value)
        elif key in ["chapter_rate", "scrolling_sensitivity"]:
            value = str(float(value))
        elif key in ["downscaling", "upscaling", "borderless", "hide_titlebar", "hover_effect_all",
                     "acrylic_menus", "acrylic_background", "hide_scrollbar", "stay_on_top", "no_update_info",
                     "update_info", "lazy_loading", "save_last_titles"]:
            value = str(value)
        elif key in ["manual_content_width"]:
            value = str(int(value))
        elif key in ["geometry", "last_scroll_positions"]:
            value = ', '.join([str(x) for x in value])
        self.settings[key] = value
        self.update_data()

    def get_provider(self):
        return self.get("provider")

    def set_provider(self, value):
        self.set("provider", value)

    def get_title(self):
        return self.get("title")

    def set_title(self, value):
        self.set("title", value)

    def get_chapter(self):
        return self.get("chapter")

    def set_chapter(self, value):
        self.set("chapter", value)

    def get_downscaling(self):
        return self.get("downscaling")

    def set_downscaling(self, value):
        self.set("downscaling", value)

    def get_upscaling(self):
        return self.get("upscaling")

    def set_upscaling(self, value):
        self.set("upscaling", value)

    def get_manual_content_width(self):
        return self.get("manual_content_width")

    def set_manual_content_width(self, value):
        self.set("manual_content_width", value)

    def get_borderless(self):
        return self.get("borderless")

    def set_borderless(self, value):
        self.set("borderless", value)

    def get_hide_titlebar(self):
        return self.get("hide_titlebar")

    def set_hide_titlebar(self, value):
        self.set("hide_titlebar", value)

    def get_hover_effect_all(self):
        return self.get("hover_effect_all")

    def set_hover_effect_all(self, value):
        self.set("hover_effect_all", value)

    def get_acrylic_menus(self):
        return self.get("acrylic_menus")

    def set_acrylic_menus(self, value):
        self.set("acrylic_menus", value)

    def get_acrylic_background(self):
        return self.get("acrylic_background")

    def set_acrylic_background(self, value):
        self.set("acrylic_background", value)

    def get_hide_scrollbar(self):
        return self.get("hide_scrollbar")

    def set_hide_scrollbar(self, value):
        self.set("hide_scrollbar", value)

    def get_stay_on_top(self):
        return self.get("stay_on_top")

    def set_stay_on_top(self, value):
        self.set("stay_on_top", value)

    def get_geometry(self):
        return self.get("geometry")

    def set_geometry(self, value):
        self.set("geometry", value)

    def get_blacklisted_websites(self):
        return self.get("blacklisted_websites")

    def set_blacklisted_websites(self, value):
        self.set("blacklisted_websites", value)

    def get_advanced_settings(self):
        return self.get("advanced_settings")

    def set_advanced_settings(self, value):
        self.set("advanced_settings", value)

    def get_provider_type(self):
        return self.get("provider_type")

    def set_provider_type(self, value):
        self.set("provider_type", value)

    def get_chapter_rate(self):
        return self.get("chapter_rate")

    def set_chapter_rate(self, value):
        self.set("chapter_rate", value)

    def get_no_update_info(self):
        return self.get("no_update_info")

    def set_no_update_info(self, value):
        self.set("no_update_info", value)

    def get_update_info(self):
        return self.get("update_info")

    def set_update_info(self, value):
        self.set("update_info", value)

    def get_last_scroll_positions(self):
        return self.get("last_scroll_positions")

    def set_last_scroll_positions(self, value):
        self.set("last_scroll_positions", value)

    def get_scrolling_sensitivity(self):
        return self.get("scrolling_sensitivity")

    def set_scrolling_sensitivity(self, value):
        self.set("scrolling_sensitivity", value)

    def get_lazy_loading(self):
        return self.get("lazy_loading")

    def set_lazy_loading(self, value):
        self.set("lazy_loading", value)

    def get_save_last_titles(self):
        return self.get("save_last_titles")

    def set_save_last_titles(self, value):
        self.set("save_last_titles", value)

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
        fetched_data = self.db.get_info("settings", ["key", "value"])
        for item in fetched_data:
            key, value = item
            self.settings[key] = value

    def update_data(self):
        for key, value in self.settings.items():
            self.db.update_info((key, value), "settings", ["key", "value"])

    def close(self):
        self.db.close()


class AutoProviderManager:
    def __init__(self, path, prov_plug, prov_sub_plugs: list):
        self.path = path
        self.prov_plug = prov_plug
        self.prov_sub_plugs = prov_sub_plugs
        self.providers = self._load_providers()

    def _load_providers(self):
        providers = {}
        for file in os.listdir(self.path):
            if file.endswith('.py') or file.endswith('.pyd') and file != '__init__.py':
                module_name = file.split(".")[0]
                module_path = os.path.join(self.path, file)
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)
                    if (isinstance(attribute, type) and issubclass(attribute, self.prov_plug) and attribute not in
                            self.prov_sub_plugs):
                        providers[attribute_name] = attribute
        return providers

    def get_providers(self):
        return self.providers


class UnselectableDelegate(QStyledItemDelegate):
    def editorEvent(self, event, model, option, index):
        # Prevent selection of disabled items
        data = model.itemData(index)
        if Qt.UserRole in data and data[Qt.UserRole] == "disabled":
            return False
        return super().editorEvent(event, model, option, index)


class CustomComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.setItemDelegate(UnselectableDelegate())
        self.currentIndexChanged.connect(self.handleIndexChanged)
        self.previousIndex = 0

    def handleIndexChanged(self, index):
        # If the newly selected item is disabled, revert to the previous item
        if index in range(self.count()):
            if self.itemData(index, Qt.UserRole) == "disabled":
                self.setCurrentIndex(self.previousIndex)
            else:
                self.previousIndex = index

    def setItemUnselectable(self, index):
        # Set data role to indicate item is disabled
        self.model().setData(self.model().index(index, 0), "disabled", Qt.UserRole)
