
import csv
import flet as ft


class TemplateBuilderView:
	def __init__(self, page: ft.Page, msg_map: dict[str, str]):
		self.page = page
		self.msg_map = msg_map
		self.files: dict[str, object] = {}
		self.status_msg = ft.Text(value=msg_map["start"], color="blue")
		self.file_picker = ft.FilePicker()

		self.upload_button = ft.Button(
			content="Upload Data Dictionary",
			data="data_dict",
			on_click=self.handle_file_picked,
		)
		self.buttons_column = ft.Column(controls=[self.upload_button])

		page.add(ft.Text("Welcome to the Template Builder!"))
		page.add(ft.Container(
			content=ft.Column([self.buttons_column, self.status_msg]),
			padding=20,
		))

	async def handle_file_picked(self, e: ft.ControlEvent):
		file = await self.file_picker.pick_files(allow_multiple=False)
		file_path = file[0].path if file else "No file selected"
		if not file or not file_path:
			return

		data = e.control.data
		with open(file_path, "r", encoding="utf-8") as f:
			if data == "data_dict" or data == "data_set":
				reader = csv.DictReader(f)
				rows = [row for row in reader]
				self.files[data] = rows
			elif data == "project_xml":
				content = f.read()
				self.files[data] = content

		self.status_msg.value = self.msg_map.get(data, "Error: Unknown file type.")
		self.update_button()
		self.page.update()

	def update_button(self):
		if not self.files.get("data_dict"):
			self.upload_button.content = "Upload DataDictionary"
			self.upload_button.data = "data_dict"
			self.upload_button.visible = True
		elif not self.files.get("project_xml"):
			self.upload_button.content = "Upload Project XML"
			self.upload_button.data = "project_xml"
			self.upload_button.visible = True
		elif not self.files.get("data_set"):
			self.upload_button.content = "Upload Example Data Set"
			self.upload_button.data = "data_set"
			self.upload_button.visible = True
		else:
			self.upload_button.visible = False
