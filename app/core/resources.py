import os
import sys


def resource_path(relative_path: str) -> str:
    """Resolve caminho de assets para dev e executável PyInstaller."""
    # Quando empacotado com PyInstaller, os arquivos ficam em _MEIPASS.
    if hasattr(sys, "_MEIPASS"):
        base_path = getattr(sys, "_MEIPASS")
    else:
        # Em desenvolvimento, usa a raiz do projeto (duas pastas acima de app/core).
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_path, relative_path)


def app_base_dir() -> str:
    """Resolve o diretório base gravável (dev: raiz do projeto; exe: pasta do executável)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def app_data_path(*parts: str) -> str:
    """Monta caminho absoluto para arquivos graváveis (logs/config/db/relatórios)."""
    return os.path.join(app_base_dir(), *parts)
