
class Theme:
    def __init__(self, stylesheet, app_style, theme_style):
        self.stylesheet = stylesheet
        self.app_style = app_style
        self.theme_style = theme_style


class Themes:
    """This is automatically used, if you have more than one word like light_light, the first will be in parentheses.
    The only app styles there are are 'windowsvista', 'Windows' and 'Fusion' of which only the last two are unique.
    If light or dark are in your theme name ' Theme' will be added at the end. Also anything with leading or ending __
    will be filtered out."""
    old = Theme(None, "Windows", "os")
    default = Theme(None, None, "os")
    light = Theme("""
            QWidget {
                color: rgb(0, 0, 0);
                background-color: #f0f0f0;           
            }
            QWidget:disabled {
                color: rgb(127, 127, 127);
                background-color: #e0e0e0;
            }
            QWidget#transparentImage {
                background: transparent;
            }
            QWidget#sideMenu {
                background: rgb(232, 230, 230); /*#e8e6e6#ededed*/
            }
            QCheckBox{
                /*background-color: #e0e0e0;*/
                border-radius: 5px;           
            }
            QRadioButton{
                /*background-color: #e0e0e0;*/
                border-radius: 5px;           
            }
            QLabel {
                border-radius: 5px;
                padding: 5px;
                background-color: #d6d6d6; /*Before #d0d0d0, made it 6 lighter*/
            }
            ImageLabel {
                padding: 0;
                background-color: transparent;
            }
            QPushButton {
                border: 1px solid #808080;
                border-radius: 5px;
                padding: 5px;
                background-color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #c0c0c0;
            }
            QToolButton {
                border: 1px solid #808080;
                border-radius: 5px;
                background-color: #e0e0e0;
            }
            QToolButton:hover {
                background-color: #c0c0c0;
            }
            /*QCheckBox::indicator:hover {
                background-color: rgba(192, 192, 192, 50);
            }*/
            QScrollBar:horizontal {
                border: none;
                background-color: transparent;
                height: 15px;
                border-radius: 7px;
            }
            QScrollBar::handle:horizontal {
                background-color: #aaaaaa;
                min-height: 15px;
                min-width: 40px;
                border-radius: 7px;
            }
            QScrollBar::handle:hover {
                background-color: #888888;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }

            QScrollBar:vertical {
                border: none;
                background-color: transparent;
                width: 15px;
                border-radius: 7px;
                /*border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;*/
            }
            QScrollBar::handle:vertical {
                background-color: #aaaaaa;
                min-height: 20px;
                border-radius: 7px;
            }
            QScrollBar::handle:hover {
                background-color: #888888;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }

            QScrollBar::corner {
                background: #f0f0f0;
                border: none;
            }
        """, "Fusion", "light")
    light_light = Theme("""
                QWidget {
                    color: rgb(0, 0, 0);
                    background-color: #f0f0f0;           
                }
                QWidget:disabled {
                    color: rgb(127, 127, 127);
                    background-color: #e0e0e0;
                }
                QComboBox {
                    border: 1px solid #808080;
                    border-radius: 5px;
                    padding: 5px;
                    background-color: #e0e0e0;
                    selection-background-color: #c0c0c0;
                    selection-color: black;
                }
                QComboBox::drop-down {
                    border: none;
                    background: transparent;
                }
                QComboBox::down-arrow {
                    image: url(data/arrow-down.png);
                }
                QComboBox QAbstractItemView {
                    border: 1px solid #808080;
                    background-color: #e0e0e0;
                    border-radius: 5px;
                    margin-top: -5px;
                }
                QCheckBox{
                    /*background-color: #e0e0e0;*/
                    border-radius: 5px;           
                }
                QLabel {
                    border-radius: 5px;
                    padding: 5px;
                    background-color: #d6d6d6; /*Before #d0d0d0, made it 6 lighter*/
                }
                ImageLabel {
                    padding: 0;
                    background-color: transparent;
                }
                QWidget#transparentImage {
                    background: transparent;
                }
                QPushButton {
                    border: 1px solid #808080;
                    border-radius: 5px;
                    padding: 5px;
                    background-color: #e0e0e0;
                }
                QPushButton:hover {
                    background-color: #c0c0c0;
                }
                QToolButton {
                    border: 1px solid #808080;
                    border-radius: 5px;
                    background-color: #e0e0e0;
                }
                QToolButton:hover {
                    background-color: #c0c0c0;
                }
                QScrollBar:horizontal {
                    border: none;
                    background-color: transparent;
                    height: 15px;
                    border-radius: 7px;
                }
                QScrollBar::handle:horizontal {
                    background-color: #aaaaaa;
                    min-height: 15px;
                    min-width: 40px;
                    border-radius: 7px;
                }
                QScrollBar::handle:hover {
                    background-color: #888888;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    border: none;
                    background: none;
                }
                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                    background: none;
                }

                QScrollBar:vertical {
                    border: none;
                    background-color: transparent;
                    width: 15px;
                    border-radius: 7px;
                    /*border-top-right-radius: 10px;
                    border-bottom-right-radius: 10px;*/
                }
                QScrollBar::handle:vertical {
                    background-color: #aaaaaa;
                    min-height: 20px;
                    border-radius: 7px;
                }
                QScrollBar::handle:hover {
                    background-color: #888888;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: none;
                }

                QScrollBar::corner {
                    background: #f0f0f0;
                    border: none;
                }
            """, None, "light")
    dark = Theme("""
            QWidget {
                color: rgb(255, 255, 255);
                background-color: #333333;
            }
            QWidget:disabled {
                color: rgb(127, 127, 127);
                background-color: #444444;
            }
            QWidget#transparentImage {
                background: transparent;
            }
            QWidget#sideMenu {
                background: #383838; /*Lighter color for the side menu background (#393939)*/
            }
            QCheckBox{
                /*background-color: #444444;*/
                border-radius: 5px;           
            }
            QRadioButton{
                /*background-color: #444444;*/
                border-radius: 5px;           
            }
            QLabel {
                border-radius: 5px;
                padding: 5px;
                background-color: #4f4f4f; /*Before #555555, made it 6 darker*/
            }
            ImageLabel {
                padding: 0;
                background-color: transparent;
            }
            QPushButton {
                border: 1px solid #aaaaaa;
                border-radius: 5px;
                padding: 5px;
                background-color: #444444;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QToolButton {
                border: 1px solid #aaaaaa;
                border-radius: 5px;
                background-color: #444444;
            }
            QToolButton:hover {
                background-color: #555555;
            }
            /*QCheckBox::indicator:hover {
                background-color: rgba(85, 85, 85, 50);
            }*/
            QScrollBar:horizontal {
                border: none;
                background: transparent;  /* Ensure the background is transparent */
                height: 15px;
                border-radius: 7px;
            }
            QScrollBar::handle:horizontal {
                background-color: #666666;
                min-height: 15px;
                min-width: 40px;
                border-radius: 7px;
            }
            QScrollBar::handle:hover {
                background-color: #555555;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }

            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 15px;
                border-radius: 7px;
                /*border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;*/
            }
            QScrollBar::handle:vertical {
                background: #666666;
                min-height: 20px;
                border-radius: 7px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                border: none;
                background: none;
            }

            QScrollBar::corner {
                background: #f0f0f0;
                border: none;
            }
        """, "Fusion", "dark")
    light_dark = Theme("""
            QWidget {
                color: rgb(255, 255, 255);
                background-color: #333333;
            }
            QWidget:disabled {
                color: rgb(127, 127, 127);
                background-color: #444444;
            }
            QComboBox {
                border: 1px solid #808080;
                border-radius: 5px;
                padding: 5px;
                background-color: #444444;
                selection-background-color: #555555;
                selection-color: white;
            }
            QComboBox::drop-down {
                border: none;
                background: transparent;
            }
            QComboBox::down-arrow {
                image: url(data/arrow-down.png);
            }
            QComboBox QAbstractItemView {
                border: 1px solid #808080;
                background-color: #444444;
                border-radius: 5px;
                margin-top: -5px;
            }
            QCheckBox{
                border-radius: 5px;           
            }
            QLabel {
                border-radius: 5px;
                padding: 5px;
                background-color: #555555;
            }
            ImageLabel {
                padding: 0;
                background-color: transparent;
            }
            QWidget#transparentImage {
                background: transparent;
            }
            QPushButton {
                border: 1px solid #aaaaaa;
                border-radius: 5px;
                padding: 5px;
                background-color: #444444;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QToolButton {
                border: 1px solid #aaaaaa;
                border-radius: 5px;
                background-color: #444444;
            }
            QToolButton:hover {
                background-color: #555555;
            }
            QScrollBar:horizontal {
                border: none;
                background-color: transparent;
                height: 15px;
                border-radius: 7px;
            }
            QScrollBar::handle:horizontal {
                background-color: #666666;
                min-height: 15px;
                min-width: 40px;
                border-radius: 7px;
            }
            QScrollBar::handle:hover {
                background-color: #555555;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }

            QScrollBar:vertical {
                border: none;
                background-color: transparent;
                width: 15px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background-color: #666666;
                min-height: 20px;
                border-radius: 7px;
            }
            QScrollBar::handle:hover {
                background-color: #555555;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }

            QScrollBar::corner {
                background: #333333;
                border: none;
            }
        """, None, "dark")
    modern = Theme(None, "Fusion", "os")
    custom_my_theme = Theme(None, None, "os")
