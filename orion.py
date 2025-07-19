#!/usr/bin/env python3
"""
Orion Launcher - Minecraft 启动器

主程序入口
"""

import logging
import os
import sys

from PySide6.QtCore import QLocale, QTranslator
from PySide6.QtWidgets import QApplication
from View import MainWindow

def main():
    """主程序入口"""
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("Orion Launcher")
    app.setApplicationDisplayName("Orion Launcher")

    # 设置中文本地化
    locale = QLocale(QLocale.Chinese, QLocale.China)
    translator = QTranslator()
    if translator.load(
        locale, "orion", "_", os.path.join(os.path.dirname(__file__), "translations")
    ):
        app.installTranslator(translator)

    # 设置样式表
    app.setStyleSheet(
        """
        QWidget {
            background-color: #2E2E2E;
            color: #EEEEEE;
            font-family: "Microsoft YaHei", "SimHei", sans-serif;
        }
        QLabel {
            background: transparent;
        }
        QCheckBox {
            background: transparent;
        }
    """
    )

    # 创建主窗口
    window = MainWindow()
    window.show()

    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
