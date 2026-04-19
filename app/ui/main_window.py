from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedWidget, QLabel, QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap
from app.modules.caixa.ui import CaixaWidget
from app.modules.estoque.ui import EstoqueWidget
from app.modules.fiado.ui import FiadoWidget
from app.modules.fluxo_caixa.ui import FluxoCaixaWidget
from app.modules.configuracoes.tipos_despesa.ui import TiposDespesaWidget
from app.modules.dashboard.ui import DashboardWidget
from app.ui.settings_ui import SettingsWidget
from app.services.bible_service import BibleService
from app.core.branding import get_branding_context

class MainWindow(QMainWindow):
    """Janela Principal do Bar do Baleia."""
    def __init__(self):
        super().__init__()
        self.branding = get_branding_context()
        self.setWindowTitle(f"{self.branding['system_name']} - {self.branding['system_subtitle']}")
        self.setWindowIcon(QIcon(self.branding["logo_path"]))
        self.setMinimumSize(1200, 800)
        
        self.bible_service = BibleService()
        self.init_ui()
        
        # Timer para atualizar o versículo bíblico a cada 1 hora (3600000 ms)
        self.bible_timer = QTimer(self)
        self.bible_timer.timeout.connect(self.update_bible_verse)
        self.bible_timer.start(3600000)
        self.update_bible_verse()

    def init_ui(self):
        # Layout principal horizontal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar Lateral
        sidebar = QFrame()
        sidebar.setObjectName("sidebarFrame")
        sidebar.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Logo/Nome do Sistema (Container com Padding)
        logo_container = QFrame()
        logo_container.setStyleSheet("background-color: #0F172A; padding: 30px 20px;")
        logo_layout = QVBoxLayout(logo_container)

        logo_img_label = QLabel()
        logo_img_label.setAlignment(Qt.AlignCenter)
        logo_img = QPixmap(self.branding["logo_path"])
        if not logo_img.isNull():
            logo_img_label.setPixmap(
                logo_img.scaled(86, 86, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        logo_layout.addWidget(logo_img_label)

        logo_label = QLabel(self.branding["system_name"])
        logo_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #22C55E;")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_label)

        sub_logo = QLabel(self.branding["system_subtitle"])
        sub_logo.setStyleSheet("font-size: 12px; color: #94A3B8; text-transform: uppercase;")
        sub_logo.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(sub_logo)
        
        sidebar_layout.addWidget(logo_container)
        sidebar_layout.addSpacing(10)

        # Botões de Navegação
        self.btn_dashboard = QPushButton("  🏠  Início")
        self.btn_dashboard.setObjectName("sidebarButton")
        self.btn_dashboard.setCheckable(True)
        self.btn_dashboard.clicked.connect(lambda: self.switch_page(0))

        self.btn_caixa = QPushButton("  💰  Caixa")
        self.btn_caixa.setObjectName("sidebarButton")
        self.btn_caixa.setCheckable(True)
        self.btn_caixa.clicked.connect(lambda: self.switch_page(1))
        
        self.btn_estoque = QPushButton("  📦  Estoque")
        self.btn_estoque.setObjectName("sidebarButton")
        self.btn_estoque.setCheckable(True)
        self.btn_estoque.clicked.connect(lambda: self.switch_page(2))
        
        self.btn_fiado = QPushButton("  📒  Clientes / Fiado")
        self.btn_fiado.setObjectName("sidebarButton")
        self.btn_fiado.setCheckable(True)
        self.btn_fiado.clicked.connect(lambda: self.switch_page(3))
        
        self.btn_fluxo = QPushButton("  📊  Fluxo de Caixa")
        self.btn_fluxo.setObjectName("sidebarButton")
        self.btn_fluxo.setCheckable(True)
        self.btn_fluxo.clicked.connect(lambda: self.switch_page(4))

        self.btn_categorias = QPushButton("  🏷️  Tipos de Despesas")
        self.btn_categorias.setObjectName("sidebarButton")
        self.btn_categorias.setCheckable(True)
        self.btn_categorias.clicked.connect(lambda: self.switch_page(5))

        self.btn_settings = QPushButton("  ⚙️  Configurações")
        self.btn_settings.setObjectName("sidebarButton")
        self.btn_settings.setCheckable(True)
        self.btn_settings.clicked.connect(lambda: self.switch_page(6))

        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_caixa)
        sidebar_layout.addWidget(self.btn_estoque)
        sidebar_layout.addWidget(self.btn_fiado)
        sidebar_layout.addWidget(self.btn_fluxo)
        sidebar_layout.addWidget(self.btn_categorias)
        sidebar_layout.addWidget(self.btn_settings)
        
        sidebar_layout.addStretch()

        # Versículo Bíblico na Sidebar
        bible_container = QFrame()
        bible_container.setStyleSheet("background-color: #1E293B; border-top: 1px solid #334155;")
        bible_layout = QVBoxLayout(bible_container)
        
        self.lbl_versiculo = QLabel("Carregando versículo...")
        self.lbl_versiculo.setWordWrap(True)
        self.lbl_versiculo.setStyleSheet("font-size: 11px; font-style: italic; color: #94A3B8; line-height: 1.4;")
        bible_layout.addWidget(self.lbl_versiculo)
        
        sidebar_layout.addWidget(bible_container)

        main_layout.addWidget(sidebar)

        # Área de Conteúdo (StackedWidget)
        self.pages = QStackedWidget()
        self.pages.setContentsMargins(30, 30, 30, 30) # Padding global para as páginas
        
        # Inicialização dos Widgets de cada módulo
        self.dashboard_widget = DashboardWidget()
        if hasattr(self.dashboard_widget, "navigateRequested"):
            self.dashboard_widget.navigateRequested.connect(self.on_dashboard_navigate)
        self.caixa_widget = CaixaWidget()
        self.estoque_widget = EstoqueWidget()
        self.fiado_widget = FiadoWidget()
        self.fluxo_widget = FluxoCaixaWidget()
        self.categorias_widget = TiposDespesaWidget()
        self.settings_widget = SettingsWidget()

        self.pages.addWidget(self.dashboard_widget)
        self.pages.addWidget(self.caixa_widget)
        self.pages.addWidget(self.estoque_widget)
        self.pages.addWidget(self.fiado_widget)
        self.pages.addWidget(self.fluxo_widget)
        self.pages.addWidget(self.categorias_widget)
        self.pages.addWidget(self.settings_widget)

        main_layout.addWidget(self.pages)

        # Inicia na tela de dashboard
        self.switch_page(0)

    def on_dashboard_navigate(self, target: str, period_days: int):
        """Atalhos do dashboard para abrir módulos com contexto (período sugerido)."""
        mapping = {
            "caixa": 1,
            "estoque": 2,
            "fiado": 3,
            "fluxo_caixa": 4,
            "tipos_despesa": 5,
            "configuracoes": 6,
        }
        index = mapping.get(target)
        if index is None:
            return
        self.switch_page(index)
        widget = self.pages.currentWidget()
        if target == "fluxo_caixa" and hasattr(widget, "aplicar_periodo"):
            widget.aplicar_periodo(int(period_days or 7))

    def switch_page(self, index):
        """Alterna entre as páginas do StackedWidget e atualiza os botões."""
        self.pages.setCurrentIndex(index)
        
        # Desmarca todos os botões e marca o atual
        buttons = [
            self.btn_dashboard, self.btn_caixa, self.btn_estoque,
            self.btn_fiado, self.btn_fluxo, self.btn_categorias, self.btn_settings
        ]
        for i, btn in enumerate(buttons):
            btn.setChecked(i == index)
            
        # Atualiza dados do widget que se tornou visível
        widget = self.pages.currentWidget()
        if hasattr(widget, 'atualizar_tabela'):
            widget.atualizar_tabela()
        if hasattr(widget, 'atualizar_dados'):
            widget.atualizar_dados()
        if hasattr(widget, 'atualizar_combo_produtos'):
            widget.atualizar_combo_produtos()
        if hasattr(widget, 'atualizar_busca_produtos'):
            widget.atualizar_busca_produtos()
        if hasattr(widget, 'atualizar_combo_clientes'):
            widget.atualizar_combo_clientes()

    def update_bible_verse(self):
        """Busca e exibe um novo versículo bíblico."""
        verse = self.bible_service.get_random_verse()
        self.lbl_versiculo.setText(verse)
