import sys
import os
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app.core.database import init_db
from app.core.config import init_config
from app.core.branding import get_branding_context
from app.ui.main_window import MainWindow
from app.ui.styles import GLOBAL_STYLE

def setup_logging():
    """Configuração global de logs."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
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
    
    # 2. Inicializar banco de dados e configurações
    try:
        init_db()
        init_config()
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
