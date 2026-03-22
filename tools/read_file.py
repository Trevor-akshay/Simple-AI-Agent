import os


def read_file(path: str):
    if not os.path.exists(path):
        return f"Path not found: {path}"

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return f"File contents of {path}:\n{content}"
