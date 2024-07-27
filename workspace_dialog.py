import sys
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUiType

workspace_ui, _ = loadUiType('workspace.ui')

class WorkspaceDialog(QDialog, workspace_ui):
    def __init__(self, parent=None):
        super(WorkspaceDialog, self).__init__(parent)
        self.setupUi(self)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Manage Workspaces")
        
    
    def onSubmit(self):
        self.accept()  # Closes the dialog

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     dialog = CustomDialog()
#     if dialog.exec_() == QDialog.Accepted:
#         print("Dialog accepted")
#     sys.exit(app.exec_())
