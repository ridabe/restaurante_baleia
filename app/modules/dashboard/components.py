from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class MetricCard(QFrame):
    """Card reutilizável para exibição de KPI com título, valor principal e subtítulo."""

    clicked = Signal()

    def __init__(self, title: str, accent_color: str = "#3B82F6", parent=None):
        super().__init__(parent)
        self.title = title
        self.accent_color = accent_color
        self._build_ui()

    def _build_ui(self):
        """Monta o layout do card de KPI com destaque visual por cor semântica."""
        self.setObjectName("cardFrame")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        self.lbl_title = QLabel(self.title)
        self.lbl_title.setStyleSheet("font-size: 12px; color: #64748B; font-weight: 600;")
        layout.addWidget(self.lbl_title)

        self.lbl_value = QLabel("R$ 0,00")
        self.lbl_value.setStyleSheet(
            f"font-size: 28px; font-weight: 700; color: {self.accent_color};"
        )
        layout.addWidget(self.lbl_value)

        self.lbl_subtitle = QLabel("---")
        self.lbl_subtitle.setStyleSheet("font-size: 11px; color: #94A3B8;")
        self.lbl_subtitle.setWordWrap(True)
        layout.addWidget(self.lbl_subtitle)

        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            f"""
            QFrame#cardFrame {{
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-left: 4px solid {self.accent_color};
                border-radius: 8px;
            }}
            QFrame#cardFrame:hover {{
                border: 1px solid #CBD5E1;
                background-color: #FBFDFF;
            }}
            """
        )

    def set_data(self, value_text: str, subtitle_text: str = ""):
        """Atualiza os valores exibidos no KPI."""
        self.lbl_value.setText(value_text)
        self.lbl_subtitle.setText(subtitle_text or "---")

    def mousePressEvent(self, event):
        """Emite evento de clique para permitir atalhos de navegação no dashboard."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class SectionFrame(QFrame):
    """Container reutilizável de seção com título e área interna para conteúdo."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.content_layout = None
        self._build_ui()

    def _build_ui(self):
        """Monta um card de seção padronizado para tabelas e gráficos."""
        self.setObjectName("cardFrame")
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(14, 12, 14, 12)
        root_layout.setSpacing(10)

        lbl_title = QLabel(self.title)
        lbl_title.setStyleSheet("font-size: 16px; color: #0F172A; font-weight: 700;")
        lbl_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        root_layout.addWidget(lbl_title)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        root_layout.addLayout(self.content_layout)
