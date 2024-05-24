from PySide6.QtWidgets import (QApplication, QLabel, QVBoxLayout, QScrollArea,
                             QWidget, QMainWindow, QCheckBox, QHBoxLayout,
                             QSpinBox, QPushButton, QGraphicsOpacityEffect,
                             QFrame, QComboBox, QFormLayout, QSlider, QLineEdit,
                             QRadioButton)
from PySide6.QtGui import QPixmap, QPalette, QColor, QIcon, QDoubleValidator
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QRect
from extensions.ProviderPlugin import ProviderPlugin
from extensions.extra_provider_plugins import *
import importlib.util
import sys
import os

os.chdir("./_internal")

class DataBase:
    def __init__(self):
        self.provider = "ManhwaClan"
        self.name = ""
        self.chapter = 1 # Some start at 0
        
    def get_provider(self):
        return self.provider
        
    def get_name(self):
        return self.name
        
    def get_chapter(self):
        return self.chapter
        
class ProviderManager:
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
                    if isinstance(attribute, type) and issubclass(attribute, ProviderPlugin) and attribute is not ProviderPlugin:
                        providers[attribute_name] = attribute
        return providers

    def get_providers(self):
        return self.providers
        
class ManhwaViewer(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle('Manhwa Viewer')
        self.setGeometry(100, 100, 640, 480)
        self.setWindowIcon(QIcon('./data/logo2.png'))
        
        self.data_folder = '.\data\\'
        self.cache_folder = '.\cache\\'
        
        self.db = DataBase()
        
        self.manager = ProviderManager('./extensions')
        self.providers = self.manager.get_providers()
        print(self.providers)

        # Example to use a specific provider
        #duck_provider_class = providers.get('ProviderPluginDuckDuckGo')
        #duck_provider = duck_provider_class(title="One Piece", chapter="999", provider="direct")
        #duck_provider.update_current_url()
        #duck_provider.cache_current_chapter()
        
        self.prov = self.providers["ProviderPluginManhwaClan"](self.db.get_name(), self.db.get_chapter(), 'direct')
        self.logo_path = self.prov.get_logo_path()
        
        self.prov.reload_chapter()
        
        
        self.current_width = 0
        self.manual_width = 0
        self.window_width = 0
        self.current_image_width = 0
        self.prev_downscale_state = True
        self.prev_upscale_state = False
        self.image_paths = self.get_image_paths()
        
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
        
        # Image Labels
        self.image_labels = []
        for image_path in self.image_paths:
            image_label = QLabel()
            image_label.setAlignment(Qt.AlignCenter)
            self.content_layout.addWidget(image_label)
            self.image_labels.append(image_label)
            
        # Add buttons at the end of the images, side by side
        self.buttons_widget = QWidget()
        self.buttons_layout = QHBoxLayout(self.buttons_widget)
        self.prev_button = QPushButton('Previous')
        self.buttons_layout.addWidget(self.prev_button)
        self.next_button = QPushButton('Next')
        self.buttons_layout.addWidget(self.next_button)
        self.content_layout.addWidget(self.buttons_widget)
        
        # Timer to regularly check for resizing needs
        self.timer = QTimer(self)
        self.timer.start(500)
        
        # Add a transparent image on the top left
        self.transparent_image = QLabel(self)
        self.transparent_image.setPixmap(QPixmap(self.logo_path))  # Replace with your image path
        self.transparent_image.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        opacity = QGraphicsOpacityEffect(self.transparent_image)
        opacity.setOpacity(0.5)  # Adjust the opacity level
        self.transparent_image.setGraphicsEffect(opacity)
        
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
        
        self.provider_dropdown = QComboBox()#itemIcon(
        self.provider_dropdown.setMinimumWidth(120)
        for i in self.providers.keys():
            prov = self.providers[i]("", 1, "direct")
            icon_path = prov.get_logo_path()
            prov = None
            i = i.replace("ProviderPlugin", "")
            self.provider_dropdown.addItem(QIcon(icon_path), i)
        self.provider_dropdown.setCurrentText(self.db.get_provider())
        self.provider_layout = QHBoxLayout()
        self.provider_layout.addWidget(QLabel("Provider"))
        self.provider_layout.addWidget(self.provider_dropdown)
        self.side_menu_layout.addRow(self.provider_layout)
        
        self.side_menu_layout.addRow(QLabel("Title"))
        self.title_selector = QLineEdit(self.prov.get_title())
        self.side_menu_layout.addRow(self.title_selector)
        
        self.chapter_selector = QLineEdit(str(self.prov.get_chapter()))
        self.side_menu_layout.addRow("Chapter", self.chapter_selector)
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
        self.downscale_checkbox.setChecked(True)
        self.side_menu_layout.addRow(self.downscale_checkbox)
        
        self.upscale_checkbox = QCheckBox('Upscale if smaller than window')
        self.side_menu_layout.addRow(self.upscale_checkbox)
        
        # SpinBox for manual width input and Apply Button
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(10, 2000)
        self.width_spinbox.setValue(640)
        self.side_menu_layout.addRow(self.width_spinbox)
        
        self.apply_button = QPushButton('Apply Width')
        self.side_menu_layout.addRow(self.apply_button)
        
        [self.side_menu_layout.addRow(QWidget()) for _ in range(3)]
        
        # Checkboxes
        self.borderless_checkbox = QCheckBox('Borderless')
        self.invisible_background_checkbox = QCheckBox('Invisible W.I.P')
        self.side_menu_layout.addRow(self.borderless_checkbox, self.invisible_background_checkbox)
        self.hide_scrollbar_checkbox = QCheckBox('Hide Scrollbar')
        self.always_on_top_checkbox = QCheckBox('Stay on top')
        self.side_menu_layout.addRow(self.hide_scrollbar_checkbox, self.always_on_top_checkbox)
        
        # Menu Button
        self.menu_button = QPushButton(QIcon(f"{self.data_folder}menu_icon.png"), "", self.central_widget)  # Placeholder
        self.menu_button.setFixedSize(40, 40)
        
        # Connect signals
        self.downscale_checkbox.toggled.connect(self.update_images)
        self.upscale_checkbox.toggled.connect(self.update_images)
        self.borderless_checkbox.toggled.connect(self.toggle_borderless)
        self.invisible_background_checkbox.toggled.connect(self.toggle_invisible_background_only)
        self.hide_scrollbar_checkbox.toggled.connect(self.toggle_scrollbar)
        self.always_on_top_checkbox.toggled.connect(self.toggle_always_on_top)
        
        self.title_selector.textChanged.connect(self.set_title)
        self.chapter_selector.textChanged.connect(self.set_chapter)
        
        self.menu_button.clicked.connect(self.toggle_menu) # Menu
        self.apply_button.clicked.connect(self.apply_manual_width) # Menu
        self.prev_chapter_button.clicked.connect(self.previous_chapter) # Menu
        self.next_chapter_button.clicked.connect(self.next_chapter) # Menu
        self.reload_chapter_button.clicked.connect(self.reload_chapter) # Menu
        self.prev_button.clicked.connect(self.previous_chapter)
        self.next_button.clicked.connect(self.next_chapter)
        
        self.provider_dropdown.currentIndexChanged.connect(self.change_provider) # Menu
        self.animation.valueChanged.connect(self.update_button_position) # Menu
        self.timer.timeout.connect(self.update_images)
        #self.central_widget.setStyleSheet("background: transparent;")
        
        self.update_images()
        
    def change_provider(self):
        self.prov = self.providers[f"ProviderPlugin{self.provider_dropdown.currentText()}"](self.prov.get_title(), self.prov.get_chapter(), 'direct')
        self.logo_path = self.prov.get_logo_path()
        new_pixmap = QPixmap(self.logo_path)
        self.transparent_image.setPixmap(new_pixmap)
        self.update_provider_logo()
        
    def set_title(self):
        self.prov.set_title(self.title_selector.text())
        
    def set_chapter(self):
        new_chapter = float("0" + self.chapter_selector.text())
        if new_chapter > 0 and new_chapter < 1000:
            self.prov.set_chapter(new_chapter)
        else:
            self.chapter_selector.setText("1")
            
    def toggle_borderless(self):
        if self.windowFlags() & Qt.FramelessWindowHint:
            self.setWindowFlags(self.windowFlags() & ~Qt.FramelessWindowHint)
        else:
            self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.show()
        
    def toggle_invisible_background_only(self):
        print("This is a work in progress, please check back when it's completed")
        
    def toggle_scrollbar(self):
        if self.scroll_area.verticalScrollBarPolicy() == Qt.ScrollBarAlwaysOff:
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        else:
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
    def toggle_always_on_top(self):
        if self.windowFlags() & Qt.WindowStaysOnTopHint:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.show()
        
    def resizeEvent(self, event):
        self.window_width = self.width()
        
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

    def apply_manual_width(self):
        self.manual_width = self.width_spinbox.value()
        self.update_images()
        
    def get_image_paths(self): # Make better
        print("AAAA", os.getcwd())
        print(os.path.abspath(self.cache_folder))
        image_files = sorted([f for f in os.listdir(self.cache_folder) if f.endswith('.png')])
        image_paths = [os.path.join(self.cache_folder, f) for f in image_files]
        return image_paths
        
    def update_images(self):
        self.current_image_width = self.image_labels[0].pixmap().width() if self.image_labels[0].pixmap() else 0 # Obtaining the current width of the pixmaps in the labels
        self.standart_image_width = self.current_image_width if not self.manual_width else self.manual_width
        conditions = [
            self.window_width != self.current_width,
            self.prev_downscale_state != self.downscale_checkbox.isChecked() or self.downscale_checkbox.isChecked() and self.standart_image_width > self.window_width,
            self.prev_upscale_state != self.upscale_checkbox.isChecked() or self.upscale_checkbox.isChecked() and self.standart_image_width < self.window_width,
            self.manual_width and self.manual_width != self.manual_width and not 
            ((self.downscale_checkbox.isChecked() and self.standart_image_width <= self.window_width) or 
            (self.upscale_checkbox.isChecked() and self.standart_image_width >= self.window_width))
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
                if self.manual_width and self.manual_width > self.window_width:
                    new_image_width = self.window_width
                elif not self.manual_width and new_image_width > self.window_width:
                    new_image_width = self.window_width
            if self.upscale_checkbox.isChecked(): # two ifs are okay, as the other conditions can't be fullfilled at the same time
                if self.manual_width and self.manual_width < self.window_width:
                    new_image_width = self.window_width
                elif not self.manual_width and new_image_width < self.window_width:
                    new_image_width = self.window_width
                    
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
        print("Images reloaded")
        
    def next_chapter(self):
        self.prov.next_chapter()
        self.chapter_selector.setText(str(self.prov.get_chapter()))
        print("Reloading images...")
        self.scroll_area.verticalScrollBar().setValue(0) # Reset the scrollbar position to the top
        self.reload_images()
        
    def previous_chapter(self):
        self.prov.previous_chapter()
        self.chapter_selector.setText(str(self.prov.get_chapter()))
        print("Reloading images...")
        self.scroll_area.verticalScrollBar().setValue(0) # Reset the scrollbar position to the top
        self.reload_images()
        
    def reload_chapter(self):
        self.prov.reload_chapter()
        print("Reloading images...")
        self.scroll_area.verticalScrollBar().setValue(0) # Reset the scrollbar position to the top
        self.reload_images()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ManhwaViewer()
    viewer.show()
    sys.exit(app.exec_())
