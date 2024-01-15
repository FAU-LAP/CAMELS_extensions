from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QGridLayout, QDialogButtonBox
import sys
sys.path.append('C:/Users/od93yces/FAIRmat/CAMELS/')
sys.path.append('C:/Users/od93yces/FAIRmat/')
sys.path.append('C:/Users/od93yces/FAIRmat/CAMELS/nomad_camels')
sys.path.append(r'C:\Users\od93yces\FAIRmat\CAMELS')
from nomad_camels.utility import variables_handling

def get_elab_settings():
    """Returns the eLabFTW settings from the preferences."""
    if 'extension_settings' in variables_handling.preferences:
        extension_settings = variables_handling.preferences['extension_settings']
        if 'eLabFTW' in extension_settings:
            elab_settings = extension_settings['eLabFTW']
            if not 'url' in elab_settings:
                elab_settings['url'] = ''
            return elab_settings
    return {}


class LoginDialog(QDialog):
    """This UI dialog handles the login to elabFTW."""
    def __init__(self, parent=None):
        super().__init__(parent)
        elab_settings = get_elab_settings()
        elab_url = elab_settings['url']
        self.label_elab_url = QLabel('eLabFTW URL:')
        self.lineEdit_elab_url = QLineEdit(elab_url)

        self.label_token = QLabel('Authentification Token:')
        self.lineEdit_token = QLineEdit()

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QGridLayout()
        layout.addWidget(self.label_elab_url, 0, 0)
        layout.addWidget(self.lineEdit_elab_url, 0, 1)
        layout.addWidget(self.label_token, 1, 0)
        layout.addWidget(self.lineEdit_token, 1, 1)
        layout.addWidget(self.button_box, 2, 0, 1, 2)
        self.setLayout(layout)
        
        self.setWindowTitle('Login to eLabFTW')
        self.url = None
        self.token = None
    
    def accept(self):
        self.url = self.lineEdit_elab_url.text()
        self.token = self.lineEdit_token.text()
        super().accept()
