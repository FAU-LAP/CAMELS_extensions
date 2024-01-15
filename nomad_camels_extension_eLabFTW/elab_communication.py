import elabapi_python as elabapi
from PySide6.QtWidgets import QDialog

from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QGridLayout, QDialogButtonBox


configuration = elabapi.Configuration()
test_key = '2-bfa1f693b02ea88f4cb23d9b059ec85fe66c8686f7eeb61ce4dc49073f0a758ca2dcfb4094f61a9603812'
configuration.api_key_prefix['api_key'] = 'Authorization'
configuration.debug = False
configuration.verify_ssl = False
configuration.host = 'https://demo.elabftw.net/api/v2'

token = ''
url = ''
api_client = None


def login_to_elab(parent=None):
    global url, token, api_client
    dialog = LoginDialog(parent)
    if dialog.exec() != QDialog.Accepted:
        return
    url = dialog.url
    token = dialog.token
    if not url or not token:
        raise ValueError('No URL or token provided!')
    configuration.host = url
    configuration.api_key['api_key'] = token

    api_client = elabapi.ApiClient(configuration)
    api_client.set_default_header(header_name='Authorization', header_value=token)
    elabapi.InfoApi(api_client).get_info()

def ensure_login(parent=None):
    global url, token, api_client
    elab_settings = get_elab_settings()
    if elab_settings['url'] != url:
        logout_of_elab()
    if not api_client:
        login_to_elab(parent)

def logout_of_elab():
    global token, api_client
    token = ''
    api_client = None

def get_elab_settings():
    """Returns the eLabFTW settings from the preferences."""
    elab_settings = {}
    if 'extension_settings' in variables_handling.preferences:
        extension_settings = variables_handling.preferences['extension_settings']
        if 'eLabFTW' in extension_settings:
            elab_settings = extension_settings['eLabFTW']
    if not 'url' in elab_settings:
        elab_settings['url'] = ''
    return elab_settings


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




if __name__ == '__main__':
    import sys
    sys.path.append('C:/Users/od93yces/FAIRmat/CAMELS/')
    from nomad_camels.utility import variables_handling
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    login_to_elab()
