import sys
import os.path
import json

from PySide2 import QtWidgets, QtCore
from PySide2.QtWidgets import QMessageBox, QFileDialog
from PySide2.QtUiTools import QUiLoader
from PySide2.QtNetwork import (QHostAddress)
from pyside_material import apply_stylesheet

from src import text_filter, log_window, session_data, type_filter, event_key, connect_state, event_dispatcher, \
    category_apply_window, category_window, log_server

CURRENT_PATH = os.path.dirname(os.path.join(os.path.abspath(sys.argv[0])))
SERVER_IP = QHostAddress(QHostAddress.LocalHost)
SERVER_PORT = 10001


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # load window
        self.ui = QUiLoader().load(os.path.join(CURRENT_PATH, "window_layout", "log_window.ui"))
        self.setCentralWidget(self.ui)

        # session log
        self.session_log = session_data.SessionLog()

        # server
        self.server = log_server.Server()
        # log view
        self.log_view = log_window.LogWindow(self.ui.LogView, self.ui.AutoScrollBox)
        self.log_filter_utility = type_filter.TypeFilter(self.ui.TypeFilterBox)

        # category view
        self.category_view = category_window.CategoryWindow(self.ui.CategoryView)
        self.category_apply_view = category_apply_window.CategoryApplyWindow(self.ui.CategoryFilter,
                                                                             self.ui.ClearFilterButton)

        # search box
        self.text_filter_edit = text_filter.text_filter_edit(self.ui.TextFilterEdit)

        # session connect state view
        self.connect_view = connect_state.ConnectState(self.ui.ConnectState)

        self.menu_file = self.ui.menuFile
        self.menu_tool = self.ui.menuTool

        # create menu
        self.create_menu_bar()
        self.create_tool_bar()

        # connect dispatch event
        self.register_log_event_to_dispatcher()
        self.register_connect_event()
        self.register_filter_log_event()
        self.begin_log_server(SERVER_IP, SERVER_PORT)

    def create_menu_bar(self) -> None:
        self.menu_file.addAction("Save as", self.save_session_log)
        self.menu_file.addAction("Load", self.load_log_session)

    def create_tool_bar(self):
        self.menu_tool.addAction("Clear Session", self.clear_session)

    def register_log_event_to_dispatcher(self) -> None:
        # recv log
        event_dispatcher.add_event(event_key.RECV_LOG, self.session_log.add)
        event_dispatcher.add_event(event_key.RECV_LOG, self.log_view.append_data_to_window)
        event_dispatcher.add_event(event_key.RECV_LOG, self.category_view.receive_log)

    def register_filter_log_event(self):
        event_dispatcher.add_event(event_key.LOG_FILTERING,
                                   self.filter_log)
        event_dispatcher.add_event(event_key.SELECT_CATEGORY_FILTER_ITEM,
                                   self.category_apply_view.receive_add_filter_event)
        event_dispatcher.add_event(event_key.SEND_TYPE_FILTER,
                                   self.log_view.set_log_type)
        event_dispatcher.add_event(event_key.SEND_CATEGORY_FILTER,
                                   self.log_view.set_category_filter)
        event_dispatcher.add_event(event_key.SEND_TEXT_FILTER,
                                   self.log_view.set_text_filter)

    def register_connect_event(self):
        event_dispatcher.add_event(event_key.CONNECT_CLIENT, self.connect_view.connect_client)
        event_dispatcher.add_event(event_key.DISCONNECT_CLIENT, self.connect_view.disconnect_client)

    def begin_log_server(self, address, port) -> None:
        print("begin listen ", (address.toString()))
        if not self.server.listen(address, port):
            QMessageBox.critical("logserver", "unable to start server")
            self.server.close()
            return

    def clear_session(self):
        self.session_log.clear()
        self.log_view.clear()
        self.category_view.clear()
        self.category_apply_view.clear()

    def save_session_log(self):
        path = QFileDialog.getSaveFileName(None, "save as", "*.log")
        self.session_log.save_to_file(path[0])

    def load_log_session(self):
        file_path = QFileDialog.getOpenFileName(None, "load log...", None, "*.log")
        if not os.path.exists(file_path[0]):
            print("failed log path {}".format(file_path[0]))
            return
        self.clear_filter()
        self.load_session_from_file(file_path[0])

    def load_session_from_file(self, file_path):
        fp = open(file_path, 'r')
        log_str = json.load(fp)
        data = json.loads(log_str)
        self.session_log.clear()
        self.session_log.set_session_data(data)
        self.log_view.clear()
        self.log_view.append_data_to_window(data)
        self.category_view.receive_log(data)

    def clear_filter(self):
        self.category_view.clear()
        self.category_apply_view.clear()

    def filter_log(self, dummy):
        session_log = self.session_log.get_session_data()
        if len(session_log) == 0:
            print("not session data")
            return
        self.log_view.clear()
        self.log_view.append_data_to_window(session_log)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    QtCore.QCoreApplication.setApplicationName("LogViewer")
    # init event dispatcher
    event_dispatcher.startup_dispatcher()

    window = MainWindow()
    # apply material design
    apply_stylesheet(app, theme="dark_teal.xml")
    # execute app
    window.show()
    sys.exit(app.exec_())
