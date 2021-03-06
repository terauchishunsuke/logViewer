from PySide2.QtWidgets import QListWidget, QListWidgetItem

from src import event_key, event_dispatcher


class CategoryWindow:
    def __init__(self, window: QListWidget):
        self.list_window = window
        self.list_window.itemDoubleClicked.connect(self.select_category)
        self.category_list = []

    def receive_log(self, log_list: list):
        for log in log_list:
            if not self.is_contain(log["category"]):
                self.add_category(log["category"])

    def add_category(self, category):
        self.category_list.append(category)
        self.list_window.addItem(category)

    def is_contain(self, category: str) -> bool:
        return True if category in self.category_list else False

    def clear(self):
        self.category_list.clear()
        self.list_window.clear()

    def select_category(self, item: QListWidgetItem):
        select_category = item.text()
        event_dispatcher.emit_event(event_key.SELECT_CATEGORY_FILTER_ITEM, select_category)
