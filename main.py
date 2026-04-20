import sys
import os
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app.core.database import init_db
from app.core.config import init_config
from app.core.branding import get_branding_context
from app.core.resources import app_base_dir, app_data_path
from app.ui.main_window import MainWindow
from app.ui.styles import GLOBAL_STYLE

def setup_logging():
    """Configuração global de logs."""
    log_dir = app_data_path("logs")
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'app.log'), encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger('Main')
    logger.info("Iniciando Sistema Bar do Baleia...")

def main():
    # 1. Configurar logs
    setup_logging()

    try:
        from dotenv import load_dotenv

        load_dotenv(os.path.join(app_base_dir(), ".env"), override=False)
    except Exception:
        pass
    
    # 2. Inicializar banco de dados e configurações
    try:
        init_config()
        init_db()
    except Exception as e:
        print(f"Erro crítico na inicialização: {e}")
        sys.exit(1)
    
    # 3. Iniciar aplicação PySide6
    app = QApplication(sys.argv)
    branding = get_branding_context()
    app.setWindowIcon(QIcon(branding["logo_path"]))
    
    # Aplicar Estilo Global
    app.setStyleSheet(GLOBAL_STYLE)
    
    # Aplicar estilo básico do sistema (fallback)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
