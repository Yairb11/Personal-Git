from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import re

REPO_REGEX = r"^https:\/\/github\.com\/[a-zA-Z0-9\-]+\/[a-zA-Z0-9\-_\.]+$"
IGNORED_PATHS = ["/search", "/explore", "/trending", "/features", "/about"]

class GithubBrowserWindow(QWebEngineView):
    def __init__(self, link_found_callback = None):
        super().__init__()
        self.link_found_callback = link_found_callback
        self.found_link = False
        self.setWindowTitle("Browse to your target GitHub Repository")
        self.resize(1024, 768)
        
        self.urlChanged.connect(self.check_url)
        self.load(QUrl("https://github.com") )
        
    def check_url(self, url):
        url_str = url.toString()
        if re.match(REPO_REGEX, url_str) and not any(path in url_str for path in IGNORED_PATHS):
            self.found_link = True
            clone_link = f"{url_str}.git"
            self.link_found_callback(clone_link)
            self.close()
            
    def closeEvent(self, event):
        if not self.found_link:
            self.link_found_callback("")
        super().closeEvent(event)
    
        
        