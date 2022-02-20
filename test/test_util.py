import os
import subprocess

import beschi.writers

CODE_OUTPUT_DIR = "out/generated"
DATA_OUTPUT_DIR = "out/data"
HARNESS_SRC_DIR = "test/_harnesses"
HARNESS_BIN_DIR = "out/executables"

def generate_for(protocol: str, output_name: str):
    for label, writer_class in beschi.writers.all_writers.items():
        out_file_dir =  os.path.join(CODE_OUTPUT_DIR, label)
        out_file_path = os.path.join(out_file_dir, f"{output_name}{writer_class.default_extension}")

        if os.path.exists(out_file_path):
            os.unlink(out_file_path)
        assert(not os.path.exists(out_file_path))

        if not os.path.exists(out_file_dir):
            os.makedirs(out_file_dir)

        subprocess.check_call(["beschi",
            "--lang", label,
            "--protocol", protocol,
            "--output", out_file_path
        ])
        assert(os.path.exists(out_file_path))

def build_for(language: str, srcfile: str, libfile: str):
    writer_class = beschi.writers.all_writers[language]
    if not os.path.exists(HARNESS_BIN_DIR):
        os.makedirs(HARNESS_BIN_DIR)
    harness_path = os.path.join(HARNESS_SRC_DIR, language)
    invoke_build = [
        "python", f"{harness_path}/builder.py",
        "--srcfile", f"{srcfile}{writer_class.default_extension}",
        "--libfile", f"{libfile}{writer_class.default_extension}",
    ]
    subprocess.check_call(invoke_build + ["--clean"])
    subprocess.check_call(invoke_build)
