import os
import importlib

from ..writer import Writer


all_writers: dict[str, Writer] = {}
experimental_writers: dict[str, Writer] = {}

_writer_dir = os.path.abspath(os.path.dirname(__file__))
for entry in os.listdir(_writer_dir):
    if not entry.endswith(".py"): continue
    if entry == "__init__.py": continue

    writer_module = importlib.import_module(f"beschi.writers.{os.path.splitext(entry)[0]}")
    writer_class = getattr(writer_module, f"{writer_module.LANGUAGE_NAME}Writer")
    if not writer_class.in_progress:
        all_writers[writer_module.LANGUAGE_NAME.lower()] = writer_class
    else:
        experimental_writers[writer_module.LANGUAGE_NAME.lower()] = writer_class

