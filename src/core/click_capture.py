from PySide6.QtCore import QObject, Slot;


CLICK_LISTENER_JS = """
(function() {
    if (typeof QWebChannel === 'undefined') return;
    new QWebChannel(qt.webChannelTransport, function(channel) {
        document.addEventListener('click', function(e) {
            var el = e.target;
            if (!el || !el.tagName) return;
            var tag  = el.tagName.toLowerCase();
            var id   = el.id || '';
            var name = el.getAttribute ? (el.getAttribute('name') || '') : '';
            channel.objects.capture.elementClicked(tag, id, name);
        }, true);
    });
})();
""";


class ClickCapture(QObject):
    def __init__(self, parent=None):
        super().__init__(parent);

    @Slot(str, str, str)
    def elementClicked(self, tag: str, id_: str, name: str):
        parts = [f"tag=<{tag}>"];
        if id_:
            parts.append(f"id=\"{id_}\"");
        if name:
            parts.append(f"name=\"{name}\"");
        print(f"[clique] {',  '.join(parts)}");
