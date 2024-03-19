from nomad_camels.extensions.extension_interface import Extension
from nomad_camels.extensions.extension_contexts import ELN_Context

from . import elab_communication

from PySide6.QtWidgets import QPushButton, QLabel, QWidget, QGridLayout, QCheckBox, QComboBox, QDialog, QDialogButtonBox
from PySide6.QtCore import Signal

EXTENSION_CONFIG = {
    'required_contexts': ['ELN_Context'],
    'name': 'ELabFTW_Extension',
    'version': '0.1.0',
    'dependencies': {
        'nomad-camels': '>=1.0.0',
		'elabapi-python': '>=0.5.0'
    },
	'settings': {'url': 'https://demo.elabftw.net'}
}

class ELabFTW_Extension(Extension):
	def __init__(self, ELN_Context:ELN_Context):
		self.ELN_Context = ELN_Context
		self.user_widget = self.ELN_Context.user_widget
		self.sample_widget = self.ELN_Context.sample_widget
		self.session_upload_widget = self.ELN_Context.session_upload_widget
		self.comboBox_user_type = self.ELN_Context.comboBox_user_type
		self.user_widget_default = self.user_widget.findChild(QWidget, 'user_widget_default')
		self.user_widget_nomad = self.user_widget.findChild(QWidget, 'user_widget_nomad')
		self.sample_widget_nomad = self.sample_widget.findChild(QWidget, 'sample_widget_nomad')
		self.sample_widget_default = self.sample_widget.findChild(QWidget, 'sample_widget_default')


		self.elab_user_widget = Elab_User_Widget()
		self.user_widget.layout().addWidget(self.elab_user_widget)
		self.elab_user_widget.setHidden(True)

		self.elab_sample_widget = Elab_Sample_Widget()
		self.sample_widget.layout().addWidget(self.elab_sample_widget)
		self.elab_sample_widget.setHidden(True)

		self.comboBox_user_type.addItem("eLabFTW")
		self.comboBox_user_type.currentIndexChanged.connect(self.change_user_type)

		self.elab_user_widget.log_in_out_signal.connect(self.user_logged_in_out)
		self.elab_sample_widget.sample_selected_signal.connect(self.sample_selected)
		self.elab_sample_widget.sample_checked_signal.connect(self.sample_checked)

		self.upload_widget = UploadElabWidget()
		self.session_upload_widget.layout().addWidget(self.upload_widget)
		self.upload_widget.setHidden(True)

		self.sample = self.ELN_Context.extension_sample
		self.user = self.ELN_Context.extension_user
		self.ELN_Context.run_done_file_signal.connect(self.upload_data)
	
	def sample_selected(self, sample:dict):
		self.sample = sample
		self.upload_widget.update_boxes()

	def sample_checked(self, checked:bool):
		if checked and self.sample:
			self.sample_widget_default.setHidden(True)
		else:
			self.sample_widget_default.setHidden(False)
		self.upload_widget.update_boxes()
		
	def change_user_type(self):
		if self.comboBox_user_type.currentText() == "eLabFTW":
			self.user_widget_default.setHidden(True)
			self.user_widget_nomad.setHidden(True)
			self.elab_user_widget.setHidden(False)
			self.elab_user_widget.ensure_login()
		else:
			self.elab_user_widget.setHidden(True)
		if elab_communication.api_client:
			self.upload_widget.update_boxes()
	
	def user_logged_in_out(self, logged_in:bool):
		self.show_elab_sample(logged_in)
		self.show_upload_widget(logged_in)
		self.user = elab_communication.get_user_information()
		self.upload_widget.update_boxes()
	
	def show_elab_sample(self, logged_in:bool):
		self.elab_sample_widget.setHidden(not logged_in)
	
	def show_upload_widget(self, logged_in:bool):
		self.upload_widget.setHidden(not logged_in)
	
	def upload_data(self, file_path):
		if elab_communication.api_client is None:
			return
		entity_type = self.upload_widget.comboBox_entity_type.currentText()
		entity_type = 'experiments' if entity_type == 'Experiment' else 'items'
		entity_name = self.upload_widget.comboBox_entity.currentText()
		entity_id = [x.id for x in self.upload_widget.items if x.title == entity_name][0]
		if self.upload_widget.comboBox_upload_type.currentText() == 'auto upload':
			elab_communication.upload_file(file_path, entity_type, entity_id, self)
		elif self.upload_widget.comboBox_upload_type.currentText() == 'ask after run':
			dialog = AskUploadDialog(self.upload_widget, entity_name, entity_type)
			if dialog.exec():
				entity_name = dialog.upload_widget.comboBox_entity.currentText()
				entity_id = [x.id for x in dialog.upload_widget.items if x.title == entity_name][0]
				entity_type = dialog.upload_widget.comboBox_entity_type.currentText()
				entity_type = 'experiments' if entity_type == 'Experiment' else 'items'
				elab_communication.upload_file(file_path, entity_type, entity_id, self)


			
class AskUploadDialog(QDialog):
	def __init__(self, parent=None, entity_name='', entity_type=''):
		super().__init__(parent)
		self.label = QLabel('Upload to eLabFTW?')
		self.button_box = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
		self.upload_widget = UploadElabWidget(self)
		self.upload_widget.comboBox_entity_type.setCurrentText(entity_type)
		self.upload_widget.comboBox_entity.setCurrentText(entity_name)
		self.upload_widget.comboBox_upload_type.setHidden(True)
		self.upload_widget.update_boxes()
		self.button_box.accepted.connect(self.accept)
		self.button_box.rejected.connect(self.reject)

		layout = QGridLayout()
		layout.addWidget(self.label, 0, 0)
		layout.addWidget(self.upload_widget, 1, 0)
		layout.addWidget(self.button_box, 2, 0)
		self.setLayout(layout)
		

class Elab_User_Widget(QWidget):
	log_in_out_signal = Signal(bool)

	def __init__(self, parent=None):
		super().__init__(parent)
		self.label_user = QLabel('not logged in')
		self.button_log_in_out = QPushButton('eLabFTW login')

		layout = QGridLayout()
		layout.addWidget(self.label_user, 0, 0)
		layout.addWidget(self.button_log_in_out, 0, 1)
		layout.setContentsMargins(0, 3, 0, 3)

		self.setLayout(layout)
		self.logged_in = False

		self.button_log_in_out.clicked.connect(self.log_in_out)
	
	def ensure_login(self):
		if not self.logged_in:
			self.log_in_out()
	
	def log_in_out(self):
		if self.logged_in:
			self.label_user.setText('not logged in')
			self.button_log_in_out.setText('eLabFTW login')
			elab_communication.logout_of_elab()
			self.logged_in = False
		else:
			elab_communication.ensure_login(self)
			if not elab_communication.api_client:
				return
			try:
				user_info = elab_communication.get_user_information()
			except:
				return
			self.label_user.setText(user_info.fullname)
			self.button_log_in_out.setText('eLabFTW logout')
			self.logged_in = True
		self.log_in_out_signal.emit(self.logged_in)


class Elab_Sample_Widget(QWidget):
	sample_selected_signal = Signal(dict)
	sample_checked_signal = Signal(bool)

	def __init__(self, parent=None):
		super().__init__(parent)
		self.checkBox_use_elab_sample = QCheckBox('Use eLabFTW sample')
		self.button_select_sample = QPushButton('Select eLabFTW sample')

		layout = QGridLayout()
		layout.addWidget(self.checkBox_use_elab_sample, 0, 0)
		layout.addWidget(self.button_select_sample, 0, 1)
		layout.setContentsMargins(0, 3, 0, 3)
		self.setLayout(layout)

		self.checkBox_use_elab_sample.clicked.connect(self.sample_checked)
		self.button_select_sample.clicked.connect(self.select_sample)
	
	def sample_checked(self):
		self.sample_checked_signal.emit(self.checkBox_use_elab_sample.isChecked())

	def select_sample(self):
		dialog = elab_communication.ItemSelector(self)
		if dialog.exec():
			self.elab_sample = dialog.sample_data
			name = self.elab_sample['name']
			self.button_select_sample.setText(f'Selected: {name}')
			self.sample_selected_signal.emit(self.elab_sample)
			self.sample_checked()


class UploadElabWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.comboBox_upload_type = QComboBox()
		self.comboBox_entity_type = QComboBox()
		self.comboBox_entity = QComboBox()
		self.comboBox_upload_type.addItems(['auto upload', 'ask after run', 'don\'t upload'])

		self.comboBox_upload_type.currentIndexChanged.connect(self.update_boxes)
		self.comboBox_entity_type.currentIndexChanged.connect(self.item_type_changed)

		layout = QGridLayout()
		layout.addWidget(self.comboBox_upload_type, 0, 0)
		layout.addWidget(self.comboBox_entity_type, 0, 1)
		layout.addWidget(self.comboBox_entity, 0, 2)
		layout.setContentsMargins(0, 3, 0, 3)
		self.setLayout(layout)

	def update_boxes(self):
		current_type = self.comboBox_entity_type.currentText()
		self.comboBox_entity_type.clear()
		self.comboBox_entity_type.addItems(['Experiment'] + [x.title for x in elab_communication.get_item_types()])
		self.comboBox_entity_type.setCurrentText(current_type)
		self.item_type_changed()		
	
	def item_type_changed(self):
		current_item = self.comboBox_entity.currentText()
		if self.comboBox_entity_type.currentText() == 'Experiment':
			self.items = elab_communication.get_experiments()
			add_names = [x.title for x in self.items]
		else:
			self.items = elab_communication.get_items()
			add_names = [x.title for x in self.items if x.category_title == self.comboBox_entity_type.currentText()]
		self.comboBox_entity.clear()
		self.comboBox_entity.addItems(add_names)
		self.comboBox_entity.setCurrentText(current_item)


