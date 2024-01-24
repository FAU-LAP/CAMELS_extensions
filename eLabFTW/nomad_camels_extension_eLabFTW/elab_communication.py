import elabapi_python as elabapi
from PySide6.QtWidgets import QDialog, QComboBox, QTextEdit
from PySide6.QtCore import Qt
import yaml

import sys
sys.path.append('C:/Users/od93yces/FAIRmat/CAMELS/')
from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QGridLayout, QDialogButtonBox
from nomad_camels.utility import variables_handling

def get_elab_settings():
    """Returns the eLabFTW settings from the preferences."""
    elab_settings = {}
    extension_settings = {}
    if 'extension_settings' in variables_handling.preferences:
        extension_settings = variables_handling.preferences['extension_settings']
    else:
        variables_handling.preferences['extension_settings'] = extension_settings
    if 'eLabFTW' in extension_settings:
        elab_settings = extension_settings['eLabFTW']
    else:
        extension_settings['eLabFTW'] = elab_settings
    if not 'url' in elab_settings:
        elab_settings['url'] = ''
    return elab_settings


configuration = elabapi.Configuration()
test_key = '2-453b0d3f8637e3dcc68af411905f7df4429e09a7b1c2f815c16b03b93572b5bd26fbbd732f116e1713592'
configuration.api_key_prefix['api_key'] = 'Authorization'
configuration.debug = False
configuration.verify_ssl = False
configuration.host = 'https://demo.elabftw.net/api/v2'

token = ''
url = get_elab_settings()['url']
api_client = None


def login_to_elab(parent=None):
    global url, token, api_client
    dialog = LoginDialog(parent)
    if dialog.exec() != QDialog.Accepted:
        logout_of_elab()
        return
    if dialog.url != url:
        elab_settings = get_elab_settings()
        elab_settings['url'] = dialog.url
    url = dialog.url
    token = dialog.token
    if not url or not token:
        raise ValueError('No URL or token provided!')
    configuration.host = url
    configuration.api_key['api_key'] = token

    api_client = elabapi.ApiClient(configuration)
    api_client.set_default_header(header_name='Authorization', header_value=token)
    try:
        elabapi.InfoApi(api_client).get_info()
    except:
        token = ''
        api_client = None
        raise ValueError('Invalid URL or token!')

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

def get_user_information(parent=None):
    """Returns the user information from eLabFTW."""
    ensure_login(parent)
    user = elabapi.UsersApi(api_client).read_user('me')
    return user

def get_items(parent=None):
    """Returns the items from eLabFTW."""
    ensure_login(parent)
    items = elabapi.ItemsApi(api_client).read_items()
    return items

def get_item_types(parent=None):
    """Returns the item types from eLabFTW."""
    ensure_login(parent)
    item_types = elabapi.ItemsTypesApi(api_client).read_items_types()
    return item_types

def get_experiments(parent=None):
    """Returns the experiments from eLabFTW."""
    ensure_login(parent)
    experiments = elabapi.ExperimentsApi(api_client).read_experiments()
    return experiments

def upload_file(file_path, entity_type, entity_id, parent=None):
    ensure_login(parent)
    elabapi.UploadsApi(api_client).post_upload(entity_type, entity_id, file=file_path)


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
        self.lineEdit_token.setEchoMode(QLineEdit.Password)

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

class ItemSelector(QDialog):
    """This UI dialog handles the selection of an item from eLabFTW."""
    def __init__(self, parent=None):
        super().__init__(parent)
        items = get_items()
        if not items:
            raise Exception('No Items found!')
        self.item_metadata = []
        self.item_names = []
        self.item_types = []
        for item in items:
            self.item_metadata.append(item.__dict__)
            self.item_names.append(item.title)
            self.item_types.append(item.category_title)
        label_item_type = QLabel('Item Type:')
        self.item_type_box = QComboBox()
        self.item_type_box.addItems(sorted(list(set(self.item_types))))
        
        label_item = QLabel('Item:')
        self.item_box = QComboBox()
        self.item_box.addItems(sorted(self.item_names))
        
        self.item_info = QTextEdit()
        self.item_info.setTextInteractionFlags(Qt.TextSelectableByKeyboard | Qt.TextSelectableByMouse)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        layout = QGridLayout()
        layout.addWidget(label_item_type, 1, 0)
        layout.addWidget(self.item_type_box, 1, 1)
        layout.addWidget(label_item, 10, 0)
        layout.addWidget(self.item_box, 10, 1)
        layout.addWidget(self.item_info, 0, 2, 12, 1)
        layout.addWidget(self.button_box, 20, 0, 1, 3)
        self.setLayout(layout)
        self.item_filtering()
        self.item_change()
        
        self.item_type_box.currentTextChanged.connect(self.item_filtering)
        self.item_box.currentTextChanged.connect(self.item_change)

        self.adjustSize()
    
    def item_filtering(self):
        item_type = self.item_type_box.currentText()
        items = []
        for i, item in enumerate(self.item_names):
            if self.item_types[i] == item_type:
                items.append(item)
        self.item_box.clear()
        self.item_box.addItems(sorted(items))
    
    def get_current_item_data(self):
        item = self.item_box.currentText()
        for i, it in enumerate(self.item_names):
            if it == item:
                return self.item_metadata[i]
        return {}
    
    def item_change(self):
        self.item_info.setText(yaml.dump(self.get_current_item_data()))
    
    def accept(self):
        self.sample_data = self.get_current_item_data()
        self.sample_data['name'] = self.sample_data['_title']
        super().accept()






if __name__ == '__main__':
    configuration.api_key['api_key'] = test_key
    api_client = elabapi.ApiClient(configuration)
    api_client.set_default_header(header_name='Authorization', header_value=test_key)
    
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    selector = ItemSelector()
    selector.exec()
    

    # its = elabapi.ItemsApi(api_client).read_items()
    # print('hi')
    # cats = elabapi.ItemsTypesApi(api_client).read_items_types()
    # print(cats)
