from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QFrame

from app.core.branding import get_branding_context
from app.ui.news_widget import NewsWidget
from app.core.config import load_settings


class DashboardWidget(QWidget):
    """Tela inicial com branding institucional e boas-vindas do sistema."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Cria a tela inicial destacando logotipo e identidade da empresa."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        card = QFrame()
        card.setObjectName("cardFrame")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(12)
        card_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        branding = get_branding_context()
        pixmap = QPixmap(branding["logo_path"])

        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        if not pixmap.isNull():
            self.logo_label.setPixmap(
                pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        card_layout.addWidget(self.logo_label)

        titulo = QLabel(branding["company_name"])
        titulo.setStyleSheet("font-size: 30px; font-weight: bold; color: #0F172A;")
        titulo.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(titulo)

        subtitulo = QLabel(branding["system_subtitle"])
        subtitulo.setStyleSheet("font-size: 14px; color: #64748B; text-transform: uppercase;")
        subtitulo.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(subtitulo)

        mensagem = QLabel("Painel Inicial")
        mensagem.setStyleSheet("font-size: 18px; font-weight: 600; color: #16A34A; margin-top: 14px;")
        mensagem.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(mensagem)

        layout.addWidget(card)

        s = load_settings()
        self.news_widget = NewsWidget(
            brnews_base_url=s.get("brnews_base_url", "http://127.0.0.1:5000"),
            rss_fallback_url=s.get("news_rss_fallback_url", "https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-419"),
            max_items=int(s.get("news_max_items", 12)),
        )
        self.news_widget.setMinimumHeight(320)
        layout.addWidget(self.news_widget, 1)

        self.news_timer = QTimer(self)
        self.news_timer.timeout.connect(self.news_widget.refresh)
        self.news_timer.start(int(s.get("news_refresh_interval_sec", 300)) * 1000)
