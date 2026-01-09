import sys
import os
import webbrowser
import requests

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QToolBar,
    QLineEdit,
    QTabWidget,
    QWidget,
    QVBoxLayout,
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QUrl

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import (
    QWebEngineFullScreenRequest,
    QWebEngineProfile,
)


# ===========================
# OTIMIZAÇÕES
# ===========================
def optimize_webengine():
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--ignore-gpu-blocklist "
        "--enable-gpu-rasterization "
    )


# ===========================
# GOOGLE SEARCH (opcional)
# ===========================
GOOGLE_API_KEY = ""
GOOGLE_CX = ""

def google_search(query):
    if not GOOGLE_API_KEY or not GOOGLE_CX:
        return []
    try:
        r = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={"key": GOOGLE_API_KEY, "cx": GOOGLE_CX, "q": query},
            timeout=3
        )
        data = r.json()
        return [(i["title"], i["link"]) for i in data.get("items", [])]
    except:
        return []


# ===========================
# ABA DO NAVEGADOR
# ===========================
class BrowserTab(QWidget):
    def __init__(self, url, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow

        layout = QVBoxLayout(self)

        self.view = QWebEngineView()
        self.view.setUrl(QUrl(url))

        # ✅ Qt6 CORRETO
        self.view.page().fullScreenRequested.connect(self.handle_fullscreen)

        layout.addWidget(self.view)

    def handle_fullscreen(self, request: QWebEngineFullScreenRequest):
        if request.toggleOn():
            self.mainwindow.showFullScreen()
        else:
            self.mainwindow.showNormal()

        request.accept()


# ===========================
# JANELA PRINCIPAL
# ===========================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TurboBrowser PyQt6")
        self.resize(1150, 780)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.build_toolbar()
        self.add_new_tab("https://www.google.com")

        self.apply_qt_webengine_settings()

    def apply_qt_webengine_settings(self):
        profile: QWebEngineProfile = QWebEngineProfile.defaultProfile()
        profile.setCachePath("cache/")
        profile.setPersistentStoragePath("storage/")
        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
        profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies
        )

    def build_toolbar(self):
        tb = QToolBar("Navegação")
        self.addToolBar(tb)

        def add_btn(text, func):
            act = QAction(text, self)
            act.triggered.connect(func)
            tb.addAction(act)

        add_btn("◀", lambda: self.current_view().back())
        add_btn("▶", lambda: self.current_view().forward())
        add_btn("⟳", lambda: self.current_view().reload())
        add_btn("HOME", lambda: self.current_view().setUrl(QUrl("https://www.google.com")))

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.load_url)
        tb.addWidget(self.urlbar)

        add_btn("+", lambda: self.add_new_tab("https://www.google.com"))

    def current_view(self):
        tab = self.tabs.currentWidget()
        return tab.view if tab else None

    def add_new_tab(self, url):
        tab = BrowserTab(url, self)
        index = self.tabs.addTab(tab, "Nova Aba")
        self.tabs.setCurrentIndex(index)

        tab.view.titleChanged.connect(
            lambda title, i=index: self.tabs.setTabText(i, title)
        )
        tab.view.urlChanged.connect(
            lambda u, i=index: self.urlbar.setText(u.toString())
        )

    def load_url(self):
        url = self.urlbar.text().strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        self.current_view().setUrl(QUrl(url))


# ===========================
# MAIN
# ===========================
def main():
    optimize_webengine()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
