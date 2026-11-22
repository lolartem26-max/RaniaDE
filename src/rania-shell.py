#!/usr/bin/env python3
import os
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import Qt, QTimer, QSize, QObject, QRunnable, QThreadPool, pyqtSignal, QEvent
from PyQt5.QtGui import QColor, QFont, QPainter, QPixmap, QIcon
from PyQt5.QtWidgets import (
    QApplication, QWidget, QFrame, QLabel, QPushButton, QToolButton,
    QHBoxLayout, QVBoxLayout, QGridLayout, QMenu, QDialog, QLineEdit,
    QListWidget, QListWidgetItem, QTabWidget, QFileDialog, QMessageBox,
    QProgressBar, QScrollArea, QSizePolicy,
)

HOME = Path.home()
WALLPAPER = Path(os.environ.get("RANIADE_WALLPAPER", str(HOME / "Pictures/wallpaper.png")))
START_ICON = HOME / ".local/share/icons/rania-start-white.png"
APP_DIRS = [
    HOME / ".local/share/applications",
    Path("/usr/local/share/applications"),
    Path("/usr/share/applications"),
    HOME / ".local/share/flatpak/exports/share/applications",
    Path("/var/lib/flatpak/exports/share/applications"),
    Path("/var/lib/snapd/desktop/applications"),
]
ACCENT = "#d0bcff"
LANGUAGE_FILE = HOME / ".config/rania/language"


def load_language():
    try:
        return "en" if LANGUAGE_FILE.read_text(encoding="utf-8").strip().lower() == "en" else "ru"
    except OSError:
        return "ru"


CURRENT_LANGUAGE = load_language()

TRANSLATIONS = {
    "Все приложения · RaniaDE": "All Applications · RaniaDE",
    "Все приложения": "All Applications",
    "Поиск среди установленных приложений…": "Search installed applications…",
    "Закрыть": "Close",
    "Магазин приложений RaniaDE · интерфейс Liquid Glass + Material You": "RaniaDE app store · Liquid Glass + Material You interface",
    "Готово": "Ready",
    "Найти": "Search",
    "Установить выбранное": "Install selected",
    "Flatpak · настроенный каталог Flathub. Поиск выполняется по каталогу приложений; выберите результат для установки в профиль пользователя.": "Flatpak · configured Flathub catalog. Search the app catalog, then choose a result to install for your user.",
    "Например: VLC, GIMP, Telegram…": "For example: VLC, GIMP, Telegram…",
    "Flatpak не установлен на этой системе.": "Flatpak is not installed on this system.",
    "Flatpak доступен · Flathub подключён": "Flatpak is available · Flathub is connected",
    "Команда flatpak не найдена": "The flatpak command was not found.",
    "Загружаю каталог Flathub…": "Loading the Flathub catalog…",
    "Не удалось прочитать Flathub: ": "Could not read Flathub: ",
    "проверьте подключение": "check your connection",
    "Сначала выберите приложение из результатов поиска": "Select an app from the search results first.",
    "Установка Flatpak": "Install Flatpak",
    "Flatpak устанавливает приложение…": "Flatpak is installing the app…",
    "Установка завершена — приложение появится в «Все приложения».": "Installation complete — the app will appear in All Applications.",
    "Команда завершилась с ошибкой; подробности в системном журнале.": "The command failed; see the system log for details.",
    "Операция завершена.": "Operation completed.",
    "Не удалось выполнить команду: ": "Could not run command: ",
    "Snap · поиск через Snap Store. Snap-команда присутствует, но работа службы snapd зависит от конфигурации системы.": "Snap · search the Snap Store. The Snap command is present, but snapd availability depends on system configuration.",
    "Snap · офлайн": "Snap · offline",
    "Название Snap-пакета…": "Snap package name…",
    "Введите запрос для поиска Snap": "Enter a query to search Snap.",
    "Snap CLI не установлен": "The Snap CLI is not installed.",
    "Ищу в Snap Store…": "Searching the Snap Store…",
    "Поиск Snap не выполнен": "Snap search failed.",
    "Выберите пакет из результатов": "Select a package from the results.",
    "Установка Snap": "Install Snap",
    "Запрашиваю системную установку Snap…": "Requesting a system-wide Snap installation…",
    "Открыл терминал для Snap; после установки обновите «Все приложения».": "Opened a terminal for Snap; refresh All Applications after installation.",
    "Не удалось открыть терминал для sudo snap install": "Could not open a terminal for sudo snap install.",
    "AppImage · автономные файлы приложений из вашей папки Applications и Downloads. Добавление копирует выбранный файл в ~/Applications и делает его исполняемым.": "AppImage · standalone apps from your Applications and Downloads folders. Adding copies the selected file to ~/Applications and marks it executable.",
    "Добавить AppImage…": "Add AppImage…",
    "Запустить выбранное": "Run selected",
    "Обновить список": "Refresh list",
    "Пока нет локальных AppImage. Нажмите «Добавить AppImage…».": "No local AppImages yet. Click “Add AppImage…”.",
    "Выбрать AppImage": "Select an AppImage",
    "AppImage (*.AppImage *.appimage);;Все файлы (*)": "AppImage (*.AppImage *.appimage);;All files (*)",
    "Запущен AppImage": "AppImage launched.",
    "ZeroInstall использует адреса feed/каталогов 0install, а не единый поисковый магазин. Команда 0install сейчас не установлена.": "ZeroInstall uses 0install feed/catalog URLs rather than one central app store. The 0install command is not installed.",
    "Проверить наличие ZeroInstall": "Check whether ZeroInstall is installed",
    "ZeroInstall доступен": "ZeroInstall is available",
    "Backend ZeroInstall отсутствует: команда 0install не установлена.": "ZeroInstall backend is unavailable: the 0install command is not installed.",
    "ZeroInstall · нет backend": "ZeroInstall · backend unavailable",
    "ZeroInstall использует": "ZeroInstall uses",
    "Wine · здесь будут отображаться Windows-приложения, для которых установщик Wine создал ярлыки. Можно выбрать .exe/.msi и запустить через Wine, если Wine установлен.": "Wine · Windows apps with Wine-created shortcuts appear here. Choose an .exe/.msi to run it with Wine, if Wine is installed.",
    "Wine · не установлен": "Wine · not installed",
    "Wine доступен": "Wine is available",
    "Wine не установлен: можно просматривать вкладку, запуск Windows-программ пока недоступен.": "Wine is not installed: you can view this tab, but running Windows apps is unavailable.",
    "Ярлыки Wine-приложений не найдены.": "No Wine application shortcuts found.",
    "Для запуска этих ярлыков сначала установите Wine": "Install Wine before launching these shortcuts.",
    "Wine не установлен": "Wine is not installed",
    "Wine backend сейчас отсутствует. После установки Wine здесь можно будет запускать .exe и .msi.": "The Wine backend is not available. After installing Wine, you can run .exe and .msi files here.",
    "Выбрать установщик Windows": "Choose a Windows installer",
    "Windows installer (*.exe *.msi);;Все файлы (*)": "Windows installer (*.exe *.msi);;All files (*)",
    "Установщик запущен через Wine": "Installer launched with Wine.",
    "Открыть .exe / .msi…": "Open .exe / .msi…",
    "Добавлен": "Added",
    "Не удалось добавить файл: ": "Could not add file: ",
    "Не удалось запустить: ": "Could not launch: ",
    "Не удалось выполнить действие": "Could not perform the action",
    "Питание · выключить или перезагрузить": "Power · shut down or restart",
    "Меню питания": "Power menu",
    "Приложения": "Applications",
    "Рабочий стол": "Desktop",
    "Избранное": "Favorites",
    "Справка": "Help",
    "Звук": "Sound",
    "Сеть": "Network",
    "Язык": "Language",
    "Русский": "Russian",
    "Обновить рабочий стол": "Refresh desktop",
    "Открыть терминал": "Open terminal",
    "Файлы": "Files",
    "Терминал": "Terminal",
    "Параметры системы": "System Settings",
    "Перезагрузить…": "Restart…",
    "Выключить…": "Shut down…",
    "Подтверждение": "Confirmation",
    "Точно": "Are you sure you want to",
    "Недоступно": "Unavailable",
    "Команда systemctl не найдена.": "The systemctl command was not found.",
    "Snap Store недоступен: ": "Snap Store is unavailable: ",
    "служба snapd не ответила": "snapd did not respond",
    "Установка завершена — приложение появится в «Все приложения».": "Installation complete — the app will appear in All Applications.",
    "Сеть": "Network",
    "Звук": "Sound",
    "Открыть терминал": "Open terminal",
    "Файлы": "Files",
    "Терминал": "Terminal",
    "Параметры системы": "System Settings",
    "Язык": "Language",
    "English": "English",
    "Русский": "Russian",
    "Выбрать язык интерфейса": "Choose interface language",
    "Изменение языка перезапустит только оболочку RaniaDE.": "Changing the language restarts only the RaniaDE shell.",
    "перезагрузить компьютер": "restart the computer",
    "выключить компьютер": "shut down the computer",
    "Не удалось выполнить действие": "Could not perform the action",
    "О RaniaDE": "About RaniaDE",
    "RaniaDE — лёгкая рабочая среда на Openbox + Python/Qt.\nПрежние обои сохранены.\nМеню приложений читает desktop-файлы установленных программ.\nRania App Market соединяет доступные источники пакетов.": "RaniaDE is a lightweight desktop environment built with Openbox + Python/Qt.\nYour existing wallpaper is preserved.\nThe app menu reads desktop files for installed programs.\nRania App Market connects available package sources.",
    "Пуск · все приложения": "Start · all applications",
}

DYNAMIC_TRANSLATIONS = [
    (r"^(\d+) приложений · список перечитывается из системных ярлыков при открытии$", r"\1 apps · the list refreshes from installed desktop entries each time it opens"),
    (r"^Найдено: (\d+) · показаны первые (\d+)$", r"Found: \1 · showing the first \2"),
    (r"^Результатов Snap: (\d+)$", r"Snap results: \1"),
    (r"^Добавлен (.+)$", r"Added \1"),
    (r"^Не удалось добавить файл: (.+)$", r"Could not add file: \1"),
    (r"^Не удалось запустить: (.+)$", r"Could not launch: \1"),
    (r"^Точно перезагрузить компьютер\?$", r"Are you sure you want to restart the computer?"),
    (r"^Точно выключить компьютер\?$", r"Are you sure you want to shut down the computer?"),
    (r"^Точно (.+)\?$", r"Are you sure you want to \1?"),
    (r"^Установить (.+) из Flathub в ваш профиль пользователя\?$", r"Install \1 from Flathub for your user?"),
    (r"^Установить Snap-пакет (.+)\? Для системной установки может потребоваться пароль администратора\.$", r"Install Snap package \1? Administrator authorization may be required for a system-wide install."),
]


def tr(text):
    if CURRENT_LANGUAGE != "en":
        return text
    translated = TRANSLATIONS.get(text)
    if translated is not None:
        return translated
    for pattern, replacement in DYNAMIC_TRANSLATIONS:
        if re.match(pattern, text):
            return re.sub(pattern, replacement, text)
    return text


def change_language(language):
    global CURRENT_LANGUAGE
    language = "en" if language == "en" else "ru"
    if language == CURRENT_LANGUAGE:
        return
    LANGUAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    LANGUAGE_FILE.write_text(language + "\n", encoding="utf-8")
    CURRENT_LANGUAGE = language
    # Replace this shell process in-place so the session manager and window manager stay alive.
    QTimer.singleShot(150, lambda: os.execv(sys.executable, [sys.executable, str(Path(__file__).resolve())]))


def launch_first(candidates, args=None):
    for name in candidates:
        path = shutil.which(name)
        if path:
            try:
                subprocess.Popen([path] + (args or []), start_new_session=True)
                return True
            except Exception:
                pass
    return False


def parse_desktop_file(path):
    data = {}
    in_entry = False
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line.startswith("["):
                in_entry = (line == "[Desktop Entry]")
                continue
            if in_entry and "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                if k not in data or k.startswith("Name["):
                    data[k] = v
    except OSError:
        return None
    name = data.get("Name") or next((v for k, v in data.items() if k.startswith("Name[")), path.stem)
    if data.get("Type", "Application") != "Application" or data.get("Hidden", "false").lower() == "true" or data.get("NoDisplay", "false").lower() == "true":
        return None
    if not data.get("Exec") and data.get("DBusActivatable", "false").lower() != "true":
        return None
    return {"name": name, "exec": data.get("Exec", ""), "icon": data.get("Icon", "application-x-executable"),
            "categories": data.get("Categories", "").strip(";"), "path": str(path),
            "terminal": data.get("Terminal", "false").lower() == "true"}


def installed_applications():
    # Higher-priority per-user entries override system copies with the same desktop filename.
    apps = {}
    for directory in reversed(APP_DIRS):
        if not directory.is_dir():
            continue
        for path in directory.glob("*.desktop"):
            entry = parse_desktop_file(path)
            if entry:
                apps[path.name] = entry
    return sorted(apps.values(), key=lambda a: a["name"].casefold())


def launch_entry(entry):
    command = entry.get("exec", "").strip()
    if not command:
        return False
    try:
        args = shlex.split(command)
        cleaned = []
        skip_next_icon = False
        for arg in args:
            if skip_next_icon:
                skip_next_icon = False
                continue
            if arg == "%i":
                continue
            if arg == "--icon" and len(cleaned) and cleaned[-1] == "--icon":
                skip_next_icon = True
                continue
            if re.fullmatch(r"%[fFuUdDnNickvm]", arg):
                continue
            arg = re.sub(r"%[fFuUdDnNickvm]", "", arg)
            if arg:
                cleaned.append(arg)
        if not cleaned:
            return False
        subprocess.Popen(cleaned, cwd=str(HOME), start_new_session=True)
        return True
    except Exception:
        return False


def icon_for(name):
    if name and (name.startswith("/") or Path(name).is_file()):
        return QIcon(name)
    return QIcon.fromTheme(name or "application-x-executable")


class WorkerSignals(QObject):
    result = pyqtSignal(object)


class CommandWorker(QRunnable):
    def __init__(self, command, timeout=45):
        super().__init__()
        self.command = command
        self.timeout = timeout
        self.signals = WorkerSignals()

    def run(self):
        try:
            result = subprocess.run(self.command, capture_output=True, text=True, timeout=self.timeout)
            self.signals.result.emit((result.returncode, result.stdout, result.stderr, self.command))
        except Exception as e:
            self.signals.result.emit((1, "", str(e), self.command))


class GlassDialog(QDialog):
    def __init__(self, title, parent=None, width=760, height=580):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(width, height)
        self.setStyleSheet("""
            QDialog { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #30283b,stop:0.42 #211c2d,stop:1 #181521); color:#f3effa; }
            QLabel { color:#f3effa; background:transparent; }
            QLineEdit { background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #3a3346,stop:1 #2b2636); color:#fff; border:1px solid #6a5c79; border-radius:17px; padding:10px 15px; selection-background-color:#6750a4; }
            QPushButton { background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #494054,stop:1 #342d40); color:#f3effa; border:1px solid #655975; border-radius:15px; padding:8px 14px; }
            QPushButton:hover { background:#584970; }
            QPushButton#primary { background:#d0bcff; color:#281d3b; border:0; font-weight:700; }
            QPushButton#primary:hover { background:#e5d8ff; }
            QListWidget { background:#292333; color:#f3effa; border:1px solid #51465e; border-radius:16px; padding:8px; outline:0; }
            QListWidget::item { padding:10px; border-radius:10px; }
            QListWidget::item:selected { background:#514264; }
            QTabWidget::pane { border:1px solid #645875; border-radius:16px; background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #302a39,stop:1 #24202d); top:-1px; }
            QTabBar::tab { background:#302a3b; color:#d8d0e4; border:1px solid #50465c; padding:9px 15px; border-top-left-radius:12px; border-top-right-radius:12px; margin-right:4px; }
            QTabBar::tab:selected { background:#d0bcff; color:#281d3b; }
            QProgressBar { border:0; background:#393145; border-radius:5px; height:9px; text-align:center; color:transparent; }
            QProgressBar::chunk { background:#d0bcff; border-radius:5px; }
        """)


class InstalledAppsDialog(GlassDialog):
    def __init__(self, parent=None):
        super().__init__(tr("Все приложения · RaniaDE"), parent, 760, 620)
        root = QVBoxLayout(self)
        heading = QLabel(tr("Все приложения"))
        heading.setStyleSheet("font-size:25px;font-weight:700;padding:3px 4px;")
        root.addWidget(heading)
        self.search = QLineEdit()
        self.search.setPlaceholderText(tr("Поиск среди установленных приложений…"))
        self.search.textChanged.connect(self.populate)
        root.addWidget(self.search)
        self.list = QListWidget()
        self.list.setIconSize(QSize(34, 34))
        self.list.itemActivated.connect(self.open_selected)
        root.addWidget(self.list, 1)
        bottom = QHBoxLayout()
        self.count = QLabel()
        bottom.addWidget(self.count)
        bottom.addStretch(1)
        market = QPushButton("Rania App Market")
        market.setObjectName("primary")
        market.clicked.connect(self.open_market)
        bottom.addWidget(market)
        close = QPushButton(tr("Закрыть"))
        close.clicked.connect(self.accept)
        bottom.addWidget(close)
        root.addLayout(bottom)
        self.apps = []
        self.populate()

    def populate(self):
        self.apps = installed_applications()
        query = self.search.text().casefold().strip()
        self.list.clear()
        visible = 0
        for entry in self.apps:
            if query and query not in (entry["name"] + " " + entry["categories"]).casefold():
                continue
            item = QListWidgetItem(icon_for(entry["icon"]), entry["name"])
            item.setData(Qt.UserRole, entry)
            item.setToolTip(entry["categories"] or entry["path"])
            self.list.addItem(item)
            visible += 1
        self.count.setText(tr(f"{visible} приложений · список перечитывается из системных ярлыков при открытии"))

    def open_selected(self, item):
        if launch_entry(item.data(Qt.UserRole)):
            self.accept()

    def open_market(self):
        self.accept()
        AppMarketDialog(self.parent()).exec_()


class AppMarketDialog(GlassDialog):
    def __init__(self, parent=None):
        super().__init__("Rania App Market", parent, 900, 650)
        self.pool = QThreadPool.globalInstance()
        self.flatpak_cache = None
        root = QVBoxLayout(self)
        top = QHBoxLayout()
        titlebox = QVBoxLayout()
        title = QLabel("Rania App Market")
        title.setStyleSheet("font-size:27px;font-weight:700;")
        subtitle = QLabel(tr("Магазин приложений RaniaDE · интерфейс Liquid Glass + Material You"))
        subtitle.setStyleSheet("color:#c8bfd5;")
        titlebox.addWidget(title)
        titlebox.addWidget(subtitle)
        top.addLayout(titlebox)
        top.addStretch(1)
        close = QPushButton(tr("Закрыть"))
        close.clicked.connect(self.accept)
        top.addWidget(close)
        root.addLayout(top)

        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)
        self.status = QLabel(tr("Готово"))
        self.status.setStyleSheet("color:#d0bcff;padding:4px 7px;")
        root.addWidget(self.status)

        self.build_flatpak_tab()
        self.build_snap_tab()
        self.build_appimage_tab()
        self.build_zeroinstall_tab()
        self.build_wine_tab()

    def make_search_page(self, source, placeholder):
        page = QWidget()
        lay = QVBoxLayout(page)
        intro = QLabel(source)
        intro.setWordWrap(True)
        intro.setStyleSheet("color:#d6cce2;padding:3px 4px;")
        lay.addWidget(intro)
        row = QHBoxLayout()
        search = QLineEdit()
        search.setPlaceholderText(placeholder)
        button = QPushButton(tr("Найти"))
        button.setObjectName("primary")
        row.addWidget(search, 1)
        row.addWidget(button)
        lay.addLayout(row)
        results = QListWidget()
        results.setIconSize(QSize(28, 28))
        lay.addWidget(results, 1)
        actions = QHBoxLayout()
        install = QPushButton(tr("Установить выбранное"))
        install.setObjectName("primary")
        actions.addWidget(install)
        actions.addStretch(1)
        lay.addLayout(actions)
        return page, search, button, results, install

    def build_flatpak_tab(self):
        page, self.fp_search, search_btn, self.fp_results, install_btn = self.make_search_page(
            tr("Flatpak · настроенный каталог Flathub. Поиск выполняется по каталогу приложений; выберите результат для установки в профиль пользователя."),
            tr("Например: VLC, GIMP, Telegram…"))
        self.tabs.addTab(page, "Flatpak")
        search_btn.clicked.connect(self.search_flatpak)
        self.fp_search.returnPressed.connect(self.search_flatpak)
        install_btn.clicked.connect(self.install_flatpak)
        if not shutil.which("flatpak"):
            self.fp_results.addItem(tr("Flatpak не установлен на этой системе."))
        else:
            self.status.setText(tr("Flatpak доступен · Flathub подключён"))

    def search_flatpak(self):
        if not shutil.which("flatpak"):
            self.status.setText(tr("Команда flatpak не найдена"))
            return
        query = self.fp_search.text().strip().casefold()
        self.fp_results.clear()
        self.status.setText(tr("Загружаю каталог Flathub…"))
        command = ["flatpak", "remote-ls", "--app", "--columns=application,name,description", "flathub"]
        worker = CommandWorker(command, timeout=60)
        worker.signals.result.connect(lambda res: self.flatpak_results_ready(res, query))
        self.pool.start(worker)

    def flatpak_results_ready(self, result, query):
        code, out, err, _ = result
        self.fp_results.clear()
        if code:
            self.status.setText(tr("Не удалось прочитать Flathub: ") + (err.strip() or tr("проверьте подключение")))
            return
        rows = []
        for line in out.splitlines():
            cols = line.split("\t")
            if len(cols) < 2:
                cols = re.split(r"\s{2,}", line.strip(), maxsplit=2)
            appid = cols[0].strip() if cols else ""
            name = cols[1].strip() if len(cols) > 1 else appid
            desc = cols[2].strip() if len(cols) > 2 else ""
            if not appid or appid.lower() in ("application", "application id"):
                continue
            if query and query not in (appid + " " + name + " " + desc).casefold():
                continue
            rows.append((appid, name, desc))
        rows.sort(key=lambda row: (query not in (row[0] + " " + row[1]).casefold(), row[1].casefold()))
        for appid, name, desc in rows[:250]:
            item = QListWidgetItem(QIcon.fromTheme("application-x-executable"), f"{name}  ·  {appid}")
            item.setData(Qt.UserRole, appid)
            item.setToolTip(desc)
            self.fp_results.addItem(item)
        self.status.setText(tr(f"Найдено: {len(rows)} · показаны первые {min(250, len(rows))}"))

    def install_flatpak(self):
        item = self.fp_results.currentItem()
        if not item or not item.data(Qt.UserRole):
            self.status.setText(tr("Сначала выберите приложение из результатов поиска"))
            return
        appid = item.data(Qt.UserRole)
        answer = QMessageBox.question(self, tr("Установка Flatpak"), tr(f"Установить {appid} из Flathub в ваш профиль пользователя?"), QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
        if answer != QMessageBox.Yes:
            return
        self.status.setText(tr("Flatpak устанавливает приложение…"))
        worker = CommandWorker(["flatpak", "install", "--user", "--noninteractive", "-y", "flathub", appid], timeout=600)
        worker.signals.result.connect(self.install_result)
        self.pool.start(worker)

    def install_result(self, result):
        code, out, err, command = result
        detail = (out + "\n" + err).strip()
        if code == 0:
            self.status.setText(tr("Установка завершена — приложение появится в «Все приложения»."))
        else:
            self.status.setText(tr("Команда завершилась с ошибкой; подробности в системном журнале."))
        QMessageBox.information(self, "Rania App Market", (detail[-2000:] if detail else (tr("Операция завершена.") if code == 0 else tr("Не удалось выполнить команду: ") + " ".join(command))))

    def build_snap_tab(self):
        page, self.snap_search, search_btn, self.snap_results, install_btn = self.make_search_page(
            tr("Snap · поиск через Snap Store. Snap-команда присутствует, но работа службы snapd зависит от конфигурации системы."),
            tr("Название Snap-пакета…"))
        snap_online = Path("/run/snapd.socket").exists()
        self.tabs.addTab(page, "Snap" if snap_online else tr("Snap · офлайн"))
        search_btn.clicked.connect(self.search_snap)
        self.snap_search.returnPressed.connect(self.search_snap)
        install_btn.clicked.connect(self.install_snap)

    def search_snap(self):
        query = self.snap_search.text().strip()
        if not query:
            self.status.setText(tr("Введите запрос для поиска Snap"))
            return
        if not shutil.which("snap"):
            self.status.setText(tr("Snap CLI не установлен"))
            return
        self.snap_results.clear()
        self.status.setText(tr("Ищу в Snap Store…"))
        worker = CommandWorker(["snap", "find", query], timeout=30)
        worker.signals.result.connect(self.snap_results_ready)
        self.pool.start(worker)

    def snap_results_ready(self, result):
        code, out, err, _ = result
        self.snap_results.clear()
        if code:
            self.snap_results.addItem(tr("Snap Store недоступен: ") + (err.strip() or tr("служба snapd не ответила")))
            self.status.setText(tr("Поиск Snap не выполнен"))
            return
        lines = [line for line in out.splitlines() if line.strip()]
        for line in lines[1:]:
            parts = line.split()
            if not parts or parts[0].lower() == "name":
                continue
            name = parts[0]
            item = QListWidgetItem(QIcon.fromTheme("package-x-generic"), line.strip())
            item.setData(Qt.UserRole, name)
            self.snap_results.addItem(item)
        self.status.setText(tr(f"Результатов Snap: {self.snap_results.count()}"))

    def install_snap(self):
        item = self.snap_results.currentItem()
        if not item or not item.data(Qt.UserRole):
            self.status.setText(tr("Выберите пакет из результатов"))
            return
        name = item.data(Qt.UserRole)
        answer = QMessageBox.question(self, tr("Установка Snap"), tr(f"Установить Snap-пакет {name}? Для системной установки может потребоваться пароль администратора."), QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
        if answer != QMessageBox.Yes:
            return
        self.status.setText(tr("Запрашиваю системную установку Snap…"))
        if launch_first(["xterm"], ["-e", "sh", "-lc", f"sudo snap install {shlex.quote(name)}; echo; read -p 'Press Enter to close'"]):
            self.status.setText(tr("Открыл терминал для Snap; после установки обновите «Все приложения»."))
        else:
            self.status.setText(tr("Не удалось открыть терминал для sudo snap install"))

    def build_appimage_tab(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        desc = QLabel(tr("AppImage · автономные файлы приложений из вашей папки Applications и Downloads. Добавление копирует выбранный файл в ~/Applications и делает его исполняемым."))
        desc.setWordWrap(True)
        desc.setStyleSheet("color:#d6cce2;padding:3px 4px;")
        lay.addWidget(desc)
        self.appimage_list = QListWidget()
        self.appimage_list.setIconSize(QSize(30, 30))
        self.appimage_list.itemActivated.connect(self.launch_appimage)
        lay.addWidget(self.appimage_list, 1)
        buttons = QHBoxLayout()
        add = QPushButton(tr("Добавить AppImage…"))
        add.setObjectName("primary")
        add.clicked.connect(self.add_appimage)
        run = QPushButton(tr("Запустить выбранное"))
        run.clicked.connect(self.launch_selected_appimage)
        refresh = QPushButton(tr("Обновить список"))
        refresh.clicked.connect(self.refresh_appimages)
        buttons.addWidget(add)
        buttons.addWidget(run)
        buttons.addStretch(1)
        buttons.addWidget(refresh)
        lay.addLayout(buttons)
        self.tabs.addTab(page, "AppImage")
        self.refresh_appimages()

    def refresh_appimages(self):
        self.appimage_list.clear()
        paths = set()
        for folder in [HOME / "Applications", HOME / "Downloads"]:
            if folder.exists():
                paths.update(p for p in folder.iterdir() if p.is_file() and (p.suffix.lower() == ".appimage" or p.name.lower().endswith(".appimage")))
        for path in sorted(paths, key=lambda p: p.name.casefold()):
            item = QListWidgetItem(QIcon.fromTheme("application-x-executable"), path.name)
            item.setData(Qt.UserRole, str(path))
            item.setToolTip(str(path))
            self.appimage_list.addItem(item)
        if not paths:
            self.appimage_list.addItem(tr("Пока нет локальных AppImage. Нажмите «Добавить AppImage…»."))

    def add_appimage(self):
        path, _ = QFileDialog.getOpenFileName(self, tr("Выбрать AppImage"), str(HOME / "Downloads"), tr("AppImage (*.AppImage *.appimage);;Все файлы (*)"))
        if not path:
            return
        source = Path(path)
        destination_dir = HOME / "Applications"
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / source.name
        try:
            if source.resolve() != destination.resolve():
                shutil.copy2(source, destination)
            destination.chmod(destination.stat().st_mode | 0o111)
            self.refresh_appimages()
            self.status.setText(tr(f"Добавлен {destination.name}"))
        except Exception as e:
            QMessageBox.warning(self, "AppImage", tr(f"Не удалось добавить файл: {e}"))

    def launch_selected_appimage(self):
        item = self.appimage_list.currentItem()
        path = item.data(Qt.UserRole) if item else None
        if path:
            self.launch_appimage(path)

    def launch_appimage(self, item_or_path):
        path = item_or_path.data(Qt.UserRole) if isinstance(item_or_path, QListWidgetItem) else str(item_or_path)
        if path and Path(path).exists():
            try:
                Path(path).chmod(Path(path).stat().st_mode | 0o111)
                subprocess.Popen([path], cwd=str(Path(path).parent), start_new_session=True)
                self.status.setText(tr("Запущен AppImage"))
            except Exception as e:
                QMessageBox.warning(self, "AppImage", tr(f"Не удалось запустить: {e}"))

    def build_zeroinstall_tab(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        text = QLabel(tr("ZeroInstall использует адреса feed/каталогов 0install, а не единый поисковый магазин. Команда 0install сейчас не установлена."))
        text.setWordWrap(True)
        text.setStyleSheet("font-size:16px;padding:18px;color:#e4d9f4;")
        lay.addWidget(text)
        button = QPushButton(tr("Проверить наличие ZeroInstall"))
        button.clicked.connect(lambda: self.status.setText(tr("ZeroInstall доступен") if shutil.which("0install") or shutil.which("zeroinstall") else tr("Backend ZeroInstall отсутствует: команда 0install не установлена.")))
        lay.addWidget(button, 0, Qt.AlignLeft)
        lay.addStretch(1)
        self.tabs.addTab(page, "ZeroInstall" if shutil.which("0install") or shutil.which("zeroinstall") else tr("ZeroInstall · нет backend"))

    def build_wine_tab(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        text = QLabel(tr("Wine · здесь будут отображаться Windows-приложения, для которых установщик Wine создал ярлыки. Можно выбрать .exe/.msi и запустить через Wine, если Wine установлен."))
        text.setWordWrap(True)
        text.setStyleSheet("color:#d6cce2;padding:3px 4px;")
        lay.addWidget(text)
        self.wine_list = QListWidget()
        self.wine_list.itemActivated.connect(self.launch_wine_shortcut)
        lay.addWidget(self.wine_list, 1)
        buttons = QHBoxLayout()
        run = QPushButton(tr("Запустить выбранное"))
        run.clicked.connect(lambda: self.launch_wine_shortcut(self.wine_list.currentItem()) if self.wine_list.currentItem() else None)
        choose = QPushButton(tr("Открыть .exe / .msi…"))
        choose.setObjectName("primary")
        choose.clicked.connect(self.choose_wine_installer)
        refresh = QPushButton(tr("Обновить список"))
        refresh.clicked.connect(self.refresh_wine)
        buttons.addWidget(run)
        buttons.addWidget(choose)
        buttons.addStretch(1)
        buttons.addWidget(refresh)
        lay.addLayout(buttons)
        self.tabs.addTab(page, "Wine" if shutil.which("wine") else tr("Wine · не установлен"))
        self.refresh_wine()

    def refresh_wine(self):
        self.wine_list.clear()
        wine_dirs = [HOME / ".local/share/applications/wine", HOME / ".local/share/applications/wine/Programs"]
        files = []
        for folder in wine_dirs:
            if folder.exists():
                files += list(folder.rglob("*.desktop"))
        for path in files:
            entry = parse_desktop_file(path)
            if entry:
                item = QListWidgetItem(icon_for(entry["icon"]), entry["name"])
                item.setData(Qt.UserRole, entry)
                self.wine_list.addItem(item)
        if not files:
            self.wine_list.addItem(tr("Ярлыки Wine-приложений не найдены."))
        self.status.setText(tr("Wine доступен") if shutil.which("wine") else tr("Wine не установлен: можно просматривать вкладку, запуск Windows-программ пока недоступен."))

    def launch_wine_shortcut(self, item):
        if not item:
            return
        entry = item.data(Qt.UserRole)
        if not entry:
            return
        if not shutil.which("wine"):
            self.status.setText(tr("Для запуска этих ярлыков сначала установите Wine"))
            return
        launch_entry(entry)

    def choose_wine_installer(self):
        if not shutil.which("wine"):
            QMessageBox.information(self, tr("Wine не установлен"), tr("Wine backend сейчас отсутствует. После установки Wine здесь можно будет запускать .exe и .msi."))
            return
        path, _ = QFileDialog.getOpenFileName(self, tr("Выбрать установщик Windows"), str(HOME / "Downloads"), tr("Windows installer (*.exe *.msi);;Все файлы (*)"))
        if path:
            subprocess.Popen(["wine", path], cwd=str(Path(path).parent), start_new_session=True)
            self.status.setText(tr("Установщик запущен через Wine"))


_apps_dialog = None


def toggle_apps_dialog(parent=None):
    global _apps_dialog
    if _apps_dialog is not None and _apps_dialog.isVisible():
        _apps_dialog.hide()
        return
    if _apps_dialog is None:
        _apps_dialog = InstalledAppsDialog(parent)
        screen = QApplication.primaryScreen().availableGeometry()
        dialog_x = screen.x() + max(0, (screen.width() - _apps_dialog.width()) // 2)
        dialog_y = screen.y() + 80
        _apps_dialog.move(dialog_x, dialog_y)
    _apps_dialog.populate()
    _apps_dialog.show()
    _apps_dialog.raise_()
    _apps_dialog.activateWindow()


class Desktop(QWidget):
    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint)
        self.setObjectName("RaniaDesktop")
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setGeometry(QApplication.primaryScreen().geometry())
        self.show()
        self.lower()

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#171322"))
        pix = QPixmap(str(WALLPAPER)) if WALLPAPER.exists() else QPixmap()
        if not pix.isNull():
            scaled = pix.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = max(0, (scaled.width() - self.width()) // 2)
            y = max(0, (scaled.height() - self.height()) // 2)
            p.drawPixmap(-x, -y, scaled)
        else:
            p.fillRect(self.rect(), QColor("#171322"))
        p.fillRect(self.rect(), QColor(9, 7, 20, 24))


class TopBar(QWidget):
    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.active_menu = None
        self.power_menu = None
        self.menu_anchor = None
        self.power_buttons = []
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet("""
            QWidget#topbar { background:#211c2ddf; border:1px solid #51465e; border-radius:14px; }
            QLabel { color:#f3effa; background:transparent; border:0; }
            QToolButton { color:#e6def0; background:transparent; border:0; border-radius:10px; padding:5px 9px; font-size:12px; }
            QToolButton:hover { background:#514264; color:#fff; }
            QToolButton#brand { color:#fff; font-weight:700; padding-left:7px; }
            QToolButton#logo { padding:2px 7px; }
        """)
        self.setObjectName("topbar")
        self.setFixedHeight(40)
        row = QHBoxLayout(self)
        row.setContentsMargins(9, 2, 11, 2)
        row.setSpacing(2)
        logo = QToolButton()
        logo.setObjectName("logo")
        logo.setIcon(QIcon(str(START_ICON)))
        logo.setIconSize(QSize(19, 19))
        logo.setToolTip(tr("Питание · выключить или перезагрузить"))
        logo.clicked.connect(self.toggle_power_menu)
        self.power_buttons.append(logo)
        row.addWidget(logo)
        brand = QToolButton()
        brand.setObjectName("brand")
        brand.setText("RaniaDE")
        brand.setToolTip(tr("Меню питания"))
        brand.clicked.connect(self.toggle_power_menu)
        self.power_buttons.append(brand)
        row.addWidget(brand)
        self.add_menu_button(row, tr("Приложения"), self.open_start)
        self.add_menu_button(row, "Rania App Market", self.open_market)
        self.add_menu_button(row, tr("Рабочий стол"), self.show_desktop_menu)
        self.add_menu_button(row, tr("Избранное"), self.show_favorites)
        self.add_menu_button(row, tr("Справка"), self.show_about)
        self.language_button = QToolButton()
        self.language_button.setText(CURRENT_LANGUAGE.upper())
        self.language_button.setToolTip(tr("Язык"))
        self.language_button.clicked.connect(self.show_language_menu)
        row.addWidget(self.language_button)
        row.addStretch(1)
        self.clock = QLabel()
        self.clock.setStyleSheet("font-size:12px; padding-right:8px;")
        row.addWidget(self.clock)
        for icon_name, tip in [("network-wireless", tr("Сеть")), ("audio-volume-high", tr("Звук"))]:
            b = QToolButton()
            b.setIcon(QIcon.fromTheme(icon_name))
            b.setIconSize(QSize(17, 17))
            b.setToolTip(tip)
            b.setStyleSheet("QToolButton{background:transparent;border:0;border-radius:8px;padding:4px 5px;}")
            row.addWidget(b)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()
        self.place()

    def add_menu_button(self, row, text, slot):
        button = QToolButton()
        button.setText(text)
        button.clicked.connect(slot)
        row.addWidget(button)

    def place(self):
        g = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(g.x() + 8, g.y() + 7, g.width() - 16, 40)

    def update_clock(self):
        self.clock.setText(datetime.now().strftime("%H:%M   ·   %d.%m.%Y"))

    def show_language_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu{background:#292333;color:#f3effa;border:1px solid #645875;padding:7px;} QMenu::item{padding:9px 26px;border-radius:9px;} QMenu::item:selected{background:#514264;}")
        menu.setTitle(tr("Выбрать язык интерфейса"))
        ru_action = menu.addAction(tr("Русский"))
        ru_action.setCheckable(True)
        ru_action.setChecked(CURRENT_LANGUAGE == "ru")
        en_action = menu.addAction(tr("English"))
        en_action.setCheckable(True)
        en_action.setChecked(CURRENT_LANGUAGE == "en")
        ru_action.triggered.connect(lambda: change_language("ru"))
        en_action.triggered.connect(lambda: change_language("en"))
        menu.popup(self.language_button.mapToGlobal(self.language_button.rect().bottomLeft()))

    def menu_at(self, items):
        if self.active_menu and self.active_menu.isVisible():
            self.active_menu.close()
            self.active_menu = None
            return
        menu = QMenu(self)
        menu.setStyleSheet("QMenu{background:#292333;color:#f3effa;border:1px solid #645875;padding:7px;} QMenu::item{padding:9px 26px;border-radius:9px;} QMenu::item:selected{background:#514264;} QMenu::separator{height:1px;background:#51465e;margin:5px 8px;}")
        for label, callback, *icon_name in items:
            if label is None:
                menu.addSeparator()
            else:
                icon = icon_for(icon_name[0]) if icon_name and icon_name[0] else QIcon()
                action = menu.addAction(icon, label) if not icon.isNull() else menu.addAction(label)
                if callback:
                    action.triggered.connect(callback)
        self.active_menu = menu
        button = self.sender()
        self.menu_anchor = button if isinstance(button, QToolButton) else None
        menu.aboutToHide.connect(lambda m=menu: self.popup_hidden(m))
        anchor = button.mapToGlobal(button.rect().bottomLeft()) if isinstance(button, QToolButton) else self.mapToGlobal(self.rect().topLeft() + self.rect().center())
        QApplication.instance().installEventFilter(self)
        menu.popup(anchor)

    def popup_hidden(self, menu):
        if self.active_menu is menu:
            self.active_menu = None
            self.menu_anchor = None
        if self.power_menu is menu:
            self.power_menu = None
        if self.active_menu is None and self.power_menu is None:
            QApplication.instance().removeEventFilter(self)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.MouseButtonPress:
            position = event.globalPos()
            targets = []
            if self.power_menu and self.power_menu.isVisible():
                targets.extend(self.power_buttons)
            if self.active_menu and self.active_menu.isVisible() and self.menu_anchor:
                targets.append(self.menu_anchor)
            for button in targets:
                if button.isVisible() and button.rect().contains(button.mapFromGlobal(position)):
                    menu = self.power_menu if self.power_menu and self.power_menu.isVisible() else self.active_menu
                    if menu:
                        menu.close()
                    return True
        return super().eventFilter(watched, event)

    def open_start(self):
        toggle_apps_dialog(self)

    def toggle_power_menu(self):
        if self.power_menu and self.power_menu.isVisible():
            self.power_menu.close()
            return
        menu = QMenu(self)
        menu.setStyleSheet("QMenu{background:#292333;color:#f3effa;border:1px solid #645875;padding:7px;} QMenu::item{padding:9px 26px;border-radius:9px;} QMenu::item:selected{background:#514264;}")
        restart = menu.addAction(QIcon.fromTheme("system-reboot"), tr("Перезагрузить…"))
        shutdown = menu.addAction(QIcon.fromTheme("system-shutdown"), tr("Выключить…"))
        restart.triggered.connect(lambda: self.confirm_power_action("reboot", tr("перезагрузить компьютер")))
        shutdown.triggered.connect(lambda: self.confirm_power_action("poweroff", tr("выключить компьютер")))
        self.power_menu = menu
        menu.aboutToHide.connect(lambda m=menu: self.popup_hidden(m))
        button = self.sender()
        QApplication.instance().installEventFilter(self)
        menu.popup(button.mapToGlobal(button.rect().bottomLeft()))

    def confirm_power_action(self, action, label):
        answer = QMessageBox.question(self, tr("Подтверждение"), tr(f"Точно {tr(label)}?"), QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
        if answer != QMessageBox.Yes:
            return
        command = shutil.which("systemctl")
        if not command:
            QMessageBox.warning(self, tr("Недоступно"), tr("Команда systemctl не найдена."))
            return
        try:
            subprocess.Popen([command, action], start_new_session=True)
        except OSError as exc:
            QMessageBox.warning(self, tr("Не удалось выполнить действие"), str(exc))

    def open_market(self):
        AppMarketDialog(self).exec_()

    def show_desktop_menu(self):
        self.menu_at([(tr("Обновить рабочий стол"), lambda: QApplication.activeWindow().update(), None), (tr("Открыть терминал"), lambda: launch_first(["konsole", "xterm"]), "utilities-terminal")])

    def show_favorites(self):
        self.menu_at([(tr("Файлы"), lambda: launch_first(["dolphin", "pcmanfm", "thunar"]), "system-file-manager"), (tr("Терминал"), lambda: launch_first(["konsole", "xterm"]), "utilities-terminal"), ("Chromium", lambda: launch_first(["chromium", "firefox"]), "chromium")])

    def show_about(self):
        QMessageBox.information(self, tr("О RaniaDE"), tr("RaniaDE — лёгкая рабочая среда на Openbox + Python/Qt.\nПрежние обои сохранены.\nМеню приложений читает desktop-файлы установленных программ.\nRania App Market соединяет доступные источники пакетов."))

    def showEvent(self, event):
        super().showEvent(event)
        self.place()


class Dock(QWidget):
    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("""
            QWidget#dock { background:transparent; border:0; }
            QToolButton { color:#eee8f4; background:transparent; border:0; border-radius:10px; min-width:50px; min-height:50px; padding:3px; }
            QToolButton:hover { background:#514264; }
            QToolButton#launcher { background:#3c314d; }
            QLabel#divider { color:#71677b; font-size:22px; padding:0 4px; }
        """)
        self.setObjectName("dock")
        self.setFixedHeight(68)
        row = QHBoxLayout(self)
        row.setContentsMargins(10, 7, 10, 7)
        row.setSpacing(5)
        self.add_button(row, str(START_ICON), tr("Пуск · все приложения"), self.open_start, "launcher")
        self.add_button(row, "system-file-manager", tr("Файлы"), lambda: launch_first(["dolphin", "pcmanfm", "thunar", "nautilus"]))
        self.add_button(row, "utilities-terminal", tr("Терминал"), lambda: launch_first(["konsole", "xterm"]))
        self.add_button(row, "chromium", "Chromium", lambda: launch_first(["chromium", "firefox"]))
        divider = QLabel("│")
        divider.setObjectName("divider")
        row.addWidget(divider)
        self.add_button(row, "applications-other", "Rania App Market", self.open_market)
        self.add_button(row, "preferences-system", tr("Параметры системы"), lambda: launch_first(["systemsettings"]))
        self.place()

    def add_button(self, row, icon_name, tooltip, callback, object_name=""):
        button = QToolButton()
        button.setIcon(QIcon(icon_name) if icon_name.startswith("/") else QIcon.fromTheme(icon_name))
        button.setIconSize(QSize(37, 37))
        button.setToolTip(tooltip)
        if object_name:
            button.setObjectName(object_name)
        button.clicked.connect(callback)
        row.addWidget(button)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(QColor(178, 164, 196, 190))
        painter.setBrush(QColor(33, 28, 45, 168))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -2, -2), 14, 14)

    def place(self):
        g = QApplication.primaryScreen().availableGeometry()
        width = min(590, g.width() - 24)
        self.setGeometry(g.x() + (g.width() - width) // 2, g.y() + g.height() - 82, width, 68)

    def open_start(self):
        toggle_apps_dialog(self)

    def open_market(self):
        AppMarketDialog(self).exec_()

    def showEvent(self, event):
        super().showEvent(event)
        self.place()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("RaniaDE")
    app.setFont(QFont("Noto Sans", 10))
    QIcon.setThemeName("breeze")
    desktop = Desktop()
    top = TopBar()
    dock = Dock()
    desktop.lower()
    top.show()
    dock.show()
    top.raise_()
    dock.raise_()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
