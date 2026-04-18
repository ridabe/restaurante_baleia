GLOBAL_STYLE = """
/* Configurações Globais */
QMainWindow, QWidget {
    background-color: #F8FAFC;
    color: #1E293B;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}

/* Labels e Textos */
QLabel {
    color: #334155;
    font-weight: 500;
    background: transparent;
}

QLabel#headerTitle {
    font-size: 24px;
    font-weight: bold;
    color: #0F172A;
    margin-bottom: 10px;
}

QLabel#moduleTitle {
    font-size: 20px;
    font-weight: 600;
    color: #1E293B;
}

/* Inputs, ComboBoxes e SpinBoxes */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 8px 12px;
    min-height: 20px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #22C55E;
    background-color: #F0FDF4;
}

QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}

/* Botões - Definição de Base Robusta */
QPushButton {
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
    border: 1px solid transparent;
    outline: none;
    background-color: #E2E8F0; /* Fundo padrão neutro */
    color: #1E293B;
}

/* Botão Primário (Verde/Sucesso) */
QPushButton#primaryButton {
    background-color: #16A34A !important;
    color: #FFFFFF !important;
    border: 1px solid #15803D !important;
}

QPushButton#primaryButton:hover {
    background-color: #15803D !important;
    border-color: #166534 !important;
}

QPushButton#primaryButton:pressed {
    background-color: #166534 !important;
}

QPushButton#primaryButton:disabled {
    background-color: #CBD5E1 !important;
    color: #94A3B8 !important;
    border: 1px solid #94A3B8 !important;
}

/* Botão de Ação Neutra (Azul) */
QPushButton#actionButton {
    background-color: #3B82F6 !important;
    color: #FFFFFF !important;
    border: 1px solid #2563EB !important;
}

QPushButton#actionButton:hover {
    background-color: #2563EB !important;
    border-color: #1D4ED8 !important;
}

QPushButton#actionButton:pressed {
    background-color: #1D4ED8 !important;
}

QPushButton#actionButton:disabled {
    background-color: #CBD5E1 !important;
    color: #94A3B8 !important;
    border: 1px solid #94A3B8 !important;
}

/* Botão de Perigo (Vermelho) */
QPushButton#dangerButton {
    background-color: #EF4444 !important;
    color: #FFFFFF !important;
    border: 1px solid #DC2626 !important;
}

QPushButton#dangerButton:hover {
    background-color: #DC2626 !important;
    border-color: #B91C1C !important;
}

QPushButton#dangerButton:pressed {
    background-color: #B91C1C !important;
}

QPushButton#dangerButton:disabled {
    background-color: #CBD5E1 !important;
    color: #94A3B8 !important;
    border: 1px solid #94A3B8 !important;
}

/* Botão Secundário (Branco/Cinza) */
QPushButton#secondaryButton {
    background-color: #FFFFFF !important;
    color: #475569 !important;
    border: 1px solid #CBD5E1 !important;
}

QPushButton#secondaryButton:hover {
    background-color: #F1F5F9 !important;
    border-color: #94A3B8 !important;
}

QPushButton#secondaryButton:pressed {
    background-color: #E2E8F0 !important;
}

/* Cards e Containers */
QFrame#cardFrame {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
}

/* Tabelas */
QTableWidget {
    background-color: #FFFFFF;
    color: #334155;
    border: 1px solid #E2E8F0;
    gridline-color: #F1F5F9;
    border-radius: 8px;
    selection-background-color: #DCFCE7;
    selection-color: #166534;
    alternate-background-color: #F8FAFC;
}

QHeaderView::section {
    background-color: #F1F5F9;
    color: #475569;
    padding: 10px;
    border: none;
    border-bottom: 2px solid #E2E8F0;
    font-weight: 600;
    font-size: 13px;
}

QTableWidget::item {
    padding: 8px;
}

/* Diálogos */
QDialog {
    background-color: #FFFFFF;
}

/* Sidebar Especial */
QFrame#sidebarFrame {
    background-color: #0F172A;
    border-right: 1px solid #1E293B;
}

QPushButton#sidebarButton {
    background-color: transparent;
    color: #94A3B8;
    text-align: left;
    padding: 14px 24px;
    border-radius: 0px;
    font-size: 15px;
    border-left: 4px solid transparent;
}

QPushButton#sidebarButton:hover {
    background-color: #1E293B;
    color: #F8FAFC;
}

QPushButton#sidebarButton:checked {
    background-color: #1E293B;
    color: #22C55E;
    font-weight: bold;
    border-left: 4px solid #22C55E;
}

/* GroupBoxes (Cards) */
QGroupBox {
    font-weight: bold;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    margin-top: 15px;
    padding-top: 20px;
    background-color: #FFFFFF;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 5px;
    color: #64748B;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background: #F1F5F9;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #CBD5E1;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #94A3B8;
}
"""
