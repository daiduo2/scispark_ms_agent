import os
from jinja2 import Environment, FileSystemLoader

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
templates_dir = os.path.join(project_root, "templates")

file_loader = FileSystemLoader(templates_dir)
tpl_env = Environment(loader=file_loader, enable_async=False)

