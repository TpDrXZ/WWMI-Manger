import sys
import os
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QListWidget, QVBoxLayout, QHBoxLayout, QLabel, QSplitter, QMenu
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

if hasattr(sys, 'frozen'):
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
M_PATH = os.path.join(BASE_PATH, "Mods")
HERO_PATH = os.path.join(M_PATH, "hero")
LOADER_PATH = os.path.join(BASE_PATH, "3DMigoto Loader.exe")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("MC Mod管理")
        self.setGeometry(400, 400, 1600, 960)
        
        layout = QHBoxLayout()
        splitter = QSplitter()
        
        font = QFont()
        font.setPointSize(18)
        
        left_layout = QVBoxLayout()
        self.label = QLabel("英雄")
        self.label.setFont(font)
        left_layout.addWidget(self.label)
        
        self.listWidget = QListWidget()
        self.listWidget.setFont(font)
        self.listWidget.itemClicked.connect(self.load_mods)
        left_layout.addWidget(self.listWidget)
        
        self.runButton = QPushButton("启动 3DMigoto")
        self.runButton.setFont(font)
        self.runButton.clicked.connect(self.run_loader)
        left_layout.addWidget(self.runButton)
        
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)
        
        right_layout = QVBoxLayout()
        self.mod_label = QLabel("Mod")
        self.mod_label.setFont(font)
        right_layout.addWidget(self.mod_label)
        
        self.modListWidget = QListWidget()
        self.modListWidget.setFont(font)
        self.modListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.modListWidget.customContextMenuRequested.connect(self.show_context_menu)
        self.modListWidget.itemDoubleClicked.connect(self.toggle_mod)
        right_layout.addWidget(self.modListWidget)
        
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)
        
        layout.addWidget(splitter)
        self.setLayout(layout)
        self.load_heroes()
    
    def load_heroes(self):
        self.listWidget.clear()
        if os.path.exists(HERO_PATH):
            heroes = [d for d in os.listdir(HERO_PATH)
                      if os.path.isdir(os.path.join(HERO_PATH, d)) and d != "disabled"]
            self.listWidget.addItems(heroes)
    
    def load_mods(self, item):
        self.category = item.text()
        self.category_path = os.path.join(HERO_PATH, self.category)
        self.mod_label.setText(f"管理 {self.category} 模组")
        
        self.modListWidget.clear()
        enabled_path = self.category_path
        disabled_path = os.path.join(self.category_path, "disabled")
        if not os.path.exists(enabled_path) or not os.path.exists(disabled_path):
            return
        
        enabled_mods = [d for d in os.listdir(enabled_path)
                        if os.path.isdir(os.path.join(enabled_path, d)) and d != "disabled"]
        disabled_mods = [d for d in os.listdir(disabled_path)
                         if os.path.isdir(os.path.join(disabled_path, d))]
        all_mods = enabled_mods + disabled_mods
        for mod in all_mods:
            if os.path.exists(os.path.join(enabled_path, mod)):
                self.modListWidget.addItem(f"{mod} (已生效)")
            else:
                self.modListWidget.addItem(mod)
    
    def update_mod_list_items(self):
        enabled_path = self.category_path
        for i in range(self.modListWidget.count()):
            item = self.modListWidget.item(i)
            mod_name = item.text().rsplit(" (", 1)[0]
            if os.path.exists(os.path.join(enabled_path, mod_name)):
                item.setText(f"{mod_name} (已生效)")
            else:
                item.setText(mod_name)
    
    def toggle_mod(self, item):
        mod_name = item.text().rsplit(" (", 1)[0]
        enabled_path = self.category_path
        disabled_path = os.path.join(self.category_path, "disabled")
        if not os.path.exists(enabled_path) or not os.path.exists(disabled_path):
            return
        try:
            if "已生效" in item.text():
                mod_path = os.path.join(enabled_path, mod_name)
                if os.path.exists(mod_path):
                    shutil.move(mod_path, os.path.join(disabled_path, mod_name))
            else:
                current_enabled = [d for d in os.listdir(enabled_path)
                                   if os.path.isdir(os.path.join(enabled_path, d)) and d != "disabled"]
                for mod in current_enabled:
                    mod_path = os.path.join(enabled_path, mod)
                    if os.path.exists(mod_path):
                        shutil.move(mod_path, os.path.join(disabled_path, mod))
                mod_path = os.path.join(disabled_path, mod_name)
                if os.path.exists(mod_path):
                    shutil.move(mod_path, os.path.join(enabled_path, mod_name))
        except Exception as e:
            print(f"发生错误：{e}")
        self.update_mod_list_items()
    
    def show_context_menu(self, position):
        item = self.modListWidget.itemAt(position)
        if item and "已生效" in item.text():
            menu = QMenu(self)
            delete_action = menu.addAction("删除")
            action = menu.exec_(self.modListWidget.mapToGlobal(position))
            if action == delete_action:
                self.delete_mod(item)
    
    def delete_mod(self, item):
        mod_name = item.text().rsplit(" (", 1)[0]
        mod_path = os.path.join(self.category_path, mod_name)
        un_path = os.path.join(BASE_PATH, "un")
        if not os.path.exists(un_path):
            os.makedirs(un_path)
        try:
            if os.path.exists(mod_path):
                shutil.move(mod_path, os.path.join(un_path, mod_name))
                self.update_mod_list_items()
        except Exception as e:
            print(f"删除失败：{e}")
    
    def run_loader(self):
        os.startfile(LOADER_PATH)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
