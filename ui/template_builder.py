import flet as ft

from ui.components import TemplateBuilderView


MSG_MAP = {
    "start": "Upload a Data Dictionary from RedCap to begin.",
    "data_dict": "Upload a Project XML from RedCap next.",
    "project_xml": "Upload an Example Data Set from RedCap now.",
    "data_set": "All files uploaded successfully! Press Button to proceed."
}


def main(page: ft.Page):
    page.title = "Template Builder"
    TemplateBuilderView(page, msg_map=MSG_MAP)
