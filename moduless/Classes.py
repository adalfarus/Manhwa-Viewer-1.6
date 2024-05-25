from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, QLineEdit,
                               QLabel, QCheckBox, QToolButton, QRadioButton, QDialogButtonBox, QFileDialog,
                               QApplication, QProgressDialog, QWidget, QListWidget, QSizePolicy, QListWidgetItem,
                               QMessageBox, QStyledItemDelegate, QComboBox)
from PySide6.QtCore import Qt, Signal, QThread, QTimer, Slot, QSize, QModelIndex
from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QPalette, QIcon
from aplustools.io import environment as env
import threading
import random
import ctypes
import queue
import time


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
        self.nameLayout.addRow(QLabel("Title"), self.titleLineEdit)

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
        self.nameLayout.addRow(QLabel("File Location"), self.fileLocationLayout)

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
        value = QFileDialog.getSaveFileName(self, 'Save File', '',
                                            'Manhwa Viewer Files (*.mwa *.mwa1 *.mvf);;Images (*.png *.xpm *.jpg *.webp)',
                                            'Manhwa Viewer Files')
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
        if new_thread == True: self.progress_queue = queue.Queue()

    class TaskCanceledException(Exception):
        """Exception to be raised when the task is canceled"""

        def __init__(self, message="A intended error occured"):
            self.message = message
            super().__init__(self.message)

    def run(self):
        if not self.is_running:
            return

        try:
            if self.new_thread == True:
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
                self.worker_func()
            self.task_completed.emit(self.success, self.result)

        except Exception as e:
            self.task_completed.emit(False, None)
            print(e)

    def worker_func(self):
        try:
            if self.new_thread == True:
                self.result = self.func(*self.args, **self.kwargs, progress_queue=self.progress_queue)
            else:
                self.result = self.func(*self.args, **self.kwargs, progress_signal=self.progress_signal)
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


class CustomProgressDialog(QProgressDialog):
    def __init__(self, parent, windowTitle, windowIcon, windowLable="Doing a task...", buttonText="Cancel",
                 new_thread=True, func=lambda: None, *args, **kwargs):
        super().__init__(parent=parent, cancelButtonText=buttonText, minimum=0, maximum=100)
        self.setWindowTitle(windowTitle)
        # self.setWindowIcon(QIcon(windowIcon))
        # self.setStyleSheet(parent.styleSheet())
        # self.setWindowFlags(parent.windowFlags())
        self.setValue(0)

        self.customLayout = QVBoxLayout(self)
        self.customLabel = QLabel(windowLable, self)
        self.customLayout.addWidget(self.customLabel)
        self.customLayout.setAlignment(self.customLabel, Qt.AlignTop | Qt.AlignHCenter)

        self.taskRunner = TaskRunner(new_thread, func, *args, **kwargs)
        self.taskRunner.task_completed.connect(self.onTaskCompleted)
        self.taskRunner.progress_signal.connect(self.setV)  # Connect progress updates
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

    def updateProgress(self):
        if self.value() <= 100 and not self.wasCanceled() and self.taskRunner.isRunning():
            if self.current_value == 0 and self.value() < 10:
                self.setValue(self.value() + 1)
                time.sleep(random.randint(2, 10) * 0.1)
            elif self.current_value >= 10:
                self.go_to_value()
            time.sleep(0.1)
            QApplication.processEvents()

    def setV(self, v):
        self.current_value = v

    def go_to_value(self):
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
        label = self.findChild(QLabel)
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
    def __init__(self, parent=None, icon=None, windowTitle='', text='', detailedText='',
                 checkbox=None, standardButtons=QMessageBox.Ok, defaultButton=None):
        """
        An advanced QMessageBox with additional configuration options.

        :param parent: The parent widget.
        :param icon: The icon to display.
        :param windowTitle: The title of the message box window.
        :param text: The text to display.
        :param detailedText: The detailed text to display.
        :param checkbox: A QCheckBox instance.
        :param standardButtons: The standard buttons to include.
        :param defaultButton: The default button.
        """
        super().__init__(parent)
        if icon: self.setIcon(icon)
        if windowTitle: self.setWindowTitle(windowTitle)
        if text: self.setText(text)
        if detailedText: self.setDetailedText(detailedText)
        if checkbox: self.setCheckBox(checkbox)
        self.setStandardButtons(standardButtons)
        if defaultButton: self.setDefaultButton(defaultButton)

        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMaximized)  # Set the window to stay on top initially

        self.raise_()
        self.activateWindow()


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
