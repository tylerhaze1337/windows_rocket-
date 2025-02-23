
import os
import shutil
import ctypes
import subprocess
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QCheckBox, QProgressBar)
from PyQt6.QtCore import QThread, pyqtSignal

class CleanupThread(QThread):
    progress = pyqtSignal(int)
    output = pyqtSignal(str)

    def __init__(self, tasks):
        super().__init__()
        self.tasks = tasks

    def run(self):
        total_tasks = len(self.tasks)
        for i, task in enumerate(self.tasks):
            try:
                self.output.emit(f"Execution: {task['desc']}")
                os.system(task['cmd'])
            except Exception as e:
                self.output.emit(f"Erreur: {str(e)}")
            self.progress.emit(int(((i + 1) / total_tasks) * 100))

class CleanerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Optimisation et Nettoyage Windows")
        self.setGeometry(100, 100, 500, 400)
        layout = QVBoxLayout()

        self.checks = {
            "temp": QCheckBox("Nettoyage des fichiers temporaires"),
            "update_cache": QCheckBox("Nettoyage du cache Windows Update"),
            "browser_cache": QCheckBox("Nettoyage du cache du navigateur"),
            "registry": QCheckBox("Nettoyage du registre Windows"),
            "apps": QCheckBox("Desinstallation des applications inutiles"),
            "recycle": QCheckBox("Vidage de la corbeille"),
            "disk": QCheckBox("Optimisation du disque"),
            "services": QCheckBox("Desactivation des services inutiles"),
            "startup": QCheckBox("Desactivation des programmes au demarrage"),
            "performance": QCheckBox("Optimisation des performances systeme"),
            "visual": QCheckBox("Desactivation des effets visuels"),
            "defrag": QCheckBox("Defragmentation du disque (HDD uniquement)"),
            "power": QCheckBox("Activation du mode performance maximale")
        }

        for cb in self.checks.values():
            layout.addWidget(cb)

        self.start_button = QPushButton("Lancer l'optimisation")
        self.start_button.clicked.connect(self.startCleanup)
        layout.addWidget(self.start_button)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.output_log = QTextEdit()
        self.output_log.setReadOnly(True)
        layout.addWidget(self.output_log)

        self.setLayout(layout)

    def startCleanup(self):
        tasks = []
        commands = {
            "temp": {"desc": "Nettoyage des fichiers temporaires", "cmd": "rd /s /q %TEMP% & rd /s /q C:\\Windows\\Temp"},
            "update_cache": {"desc": "Nettoyage du cache Windows Update", "cmd": "net stop wuauserv & rd /s /q C:\\Windows\\SoftwareDistribution\\Download & net start wuauserv"},
            "browser_cache": {"desc": "Nettoyage du cache du navigateur", "cmd": "rd /s /q C:\\Users\\%USERNAME%\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Cache"},
            "registry": {"desc": "Nettoyage du registre Windows", "cmd": "reg delete HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RecentDocs /f"},
            "apps": {"desc": "Desinstallation des applications inutiles", "cmd": "powershell Get-AppxPackage *CandyCrush* | Remove-AppxPackage"},
            "recycle": {"desc": "Vidage de la corbeille", "cmd": "powershell Clear-RecycleBin -Force"},
            "disk": {"desc": "Optimisation du disque", "cmd": "cleanmgr /sagerun:1"},
            "services": {"desc": "Desactivation des services inutiles", "cmd": "powershell Get-Service | Where-Object {$_.StartType -eq 'Manual' -and $_.Status -eq 'Stopped'} | Set-Service -StartupType Disabled"},
            "startup": {"desc": "Desactivation des programmes au demarrage", "cmd": "powershell Get-CimInstance Win32_StartupCommand | ForEach-Object { REG DELETE HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /V $_.Name /F }"},
            "performance": {"desc": "Optimisation des performances systeme", "cmd": "wmic computersystem set AutomaticManagedPagefile=False"},
            "visual": {"desc": "Desactivation des effets visuels", "cmd": "reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects /v VisualFXSetting /t REG_DWORD /d 2 /f"},
            "defrag": {"desc": "Defragmentation du disque (HDD uniquement)", "cmd": "defrag C: /U /V"},
            "power": {"desc": "Activation du mode performance maximale", "cmd": "powercfg -setactive SCHEME_MIN"}
        }
        
        for key, cb in self.checks.items():
            if cb.isChecked():
                tasks.append(commands[key])

        if tasks:
            self.thread = CleanupThread(tasks)
            self.thread.progress.connect(self.progress_bar.setValue)
            self.thread.output.connect(self.output_log.append)
            self.thread.start()
        else:
            self.output_log.append("Aucune tache selectionnee.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CleanerApp()
    window.show()
    sys.exit(app.exec())
