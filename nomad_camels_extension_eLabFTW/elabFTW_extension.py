from nomad_camels.extensions.extension_interface import Extension
from nomad_camels.extensions.extension_contexts import ELN_Context

from PySide6.QtWidgets import QComboBox, QPushButton, QLabel

EXTENSION_CONFIG = {
    'required_contexts': ['ELN_Context'],
    'name': 'ELabFTW_Extension',
    'version': '0.1',
    'dependencies': {
        'nomad-camels': '>=0.2.4'
    }
}

class ELabFTW_Extension(Extension):
	def __init__(self, ELN_Context:ELN_Context):
		self.ELN_Context = ELN_Context
		self.user_widget = self.ELN_Context.user_widget
		self.sample_widget = self.ELN_Context.sample_widget
		self.session_upload_widget = self.ELN_Context.session_upload_widget
		self.comboBox_user_type = self.ELN_Context.comboBox_user_type
		self.comboBox_user = self.user_widget.findChild(QComboBox, 'comboBox_user')
		self.pushButton_editUserInfo = self.user_widget.findChild(QPushButton, 'pushButton_editUserInfo')
		self.pushButton_login_nomad = self.user_widget.findChild(QPushButton, 'pushButton_login_nomad')
		self.label_nomad_user = self.user_widget.findChild(QLabel, 'label_nomad_user')

		self.comboBox_user_type.addItem("eLabFTW")
		self.comboBox_user_type.currentIndexChanged.connect(self.change_user_type)
		
	def change_user_type(self):
		if self.comboBox_user_type.currentText() == "eLabFTW":
			self.comboBox_user.setHidden(True)
			self.pushButton_editUserInfo.setHidden(True)
			self.label_nomad_user.setHidden(True)
			self.pushButton_login_nomad.setHidden(True)
			
class Elab_User_Widget(QWidget):
	pass
