import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
from conf import api

workspace_ui, _ = loadUiType('workspace.ui')

class WorkspaceDialog(QDialog, workspace_ui):
    def __init__(self, parent=None):
        super(WorkspaceDialog, self).__init__(parent)
        self.setupUi(self)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Manage Workspaces")
        self.show_items()
        self.new_btn.clicked.connect(self.add_new_element)
        self.save_btn.clicked.connect(self.save_workspace)
        self.delete_btn.clicked.connect(self.delete_workspace)
        self.action_taken = None
    
    def accept(self):
        if self.selected_workspace():
            super().accept()
            self.action_taken = 'open'
        

    def add_new_element(self):
        list_item = QListWidgetItem(f"workspace {self.workspace_list.count()}")
        list_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
        self.workspace_list.addItem(list_item)
        self.workspaces = None

    def show_items(self):
        global api
        self.workspaces = api.fetch_workspaces()
        names = [workspace['workspace_name'] for workspace in self.workspaces]
        for name in names:
            list_item = QListWidgetItem(f"{name}")
            list_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            self.workspace_list.addItem(list_item)
    def selected_workspace(self):
        selected_items = self.workspace_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Error', 'Please select a workspace to open.')
        elif len(selected_items) > 1:
            QMessageBox.warning(self, 'Error', 'you can only select one workspace')
        else:
            for workspace in self.workspaces:
                if workspace['workspace_name'] == selected_items[0].text():
                    return workspace
            QMessageBox.warning(self, 'Error', 'workspace does not exist')

    def selected_workspace_name(self):
        selected_items = self.workspace_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Error', 'Please select a workspace to open.')
        elif len(selected_items) > 1:
            QMessageBox.warning(self, 'Error', 'you can only select one workspace')
        else:
            return selected_items[0].text()

    def save_workspace(self):
        super().accept()
        self.action_taken = 'save'

    def delete_workspace(self):
        workspace = self.selected_workspace_name()
        global api
        api.delete_workspace_by_name(workspace)
        self.workspace_list.clear()
        self.show_items()

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     dialog = CustomDialog()
#     if dialog.exec_() == QDialog.Accepted:
#         print("Dialog accepted")
#     sys.exit(app.exec_())
