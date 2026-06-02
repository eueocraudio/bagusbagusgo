from PySide6.QtWebEngineCore import QWebEngineUrlRequestInterceptor;


class UserAgentInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        pass;
