from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QFormLayout, QMessageBox, QComboBox, QSpinBox, QFrame, QScrollArea
)
from PySide6.QtCore import Qt
from app.core.config import load_settings, save_settings
from app.core.database import get_database_status

class SettingsWidget(QWidget):
    """Interface de configurações do sistema com dados institucionais completos."""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Cabeçalho Fixo
        header_container = QFrame()
        header_container.setObjectName("cardFrame")
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("Configurações Institucionais e do Sistema")
        header.setObjectName("moduleTitle")
        header_layout.addWidget(header)
        
        sub_header = QLabel("Gerencie os dados da sua empresa e preferências globais")
        sub_header.setStyleSheet("color: #64748B; font-size: 13px;")
        header_layout.addWidget(sub_header)
        
        main_layout.addWidget(header_container)

        # Área de Rolagem para os Cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(20, 20, 20, 20)
        self.scroll_layout.setSpacing(25)

        # --- SEÇÃO 1: DADOS DA EMPRESA ---
        card_empresa = QFrame()
        card_empresa.setObjectName("cardFrame")
        layout_empresa = QVBoxLayout(card_empresa)
        
        title_empresa = QLabel("Dados da Empresa")
        title_empresa.setStyleSheet("font-size: 16px; font-weight: bold; color: #0F172A; margin-bottom: 10px;")
        layout_empresa.addWidget(title_empresa)
        
        form_empresa = QFormLayout()
        form_empresa.setSpacing(15)
        form_empresa.setLabelAlignment(Qt.AlignRight)
        
        self.fantasia_input = QLineEdit()
        self.fantasia_input.setPlaceholderText("Ex: Bar do Baleia")
        self.razao_input = QLineEdit()
        self.cnpj_input = QLineEdit()
        self.cnpj_input.setInputMask("99.999.999/9999-99")
        self.tel_input = QLineEdit()
        self.tel_input.setInputMask("(99) 99999-9999")
        self.email_input = QLineEdit()
        
        form_empresa.addRow("Nome Fantasia:", self.fantasia_input)
        form_empresa.addRow("Razão Social:", self.razao_input)
        form_empresa.addRow("CNPJ:", self.cnpj_input)
        form_empresa.addRow("Telefone:", self.tel_input)
        form_empresa.addRow("E-mail:", self.email_input)
        
        layout_empresa.addLayout(form_empresa)
        self.scroll_layout.addWidget(card_empresa)

        # --- SEÇÃO 2: ENDEREÇO ---
        card_endereco = QFrame()
        card_endereco.setObjectName("cardFrame")
        layout_endereco = QVBoxLayout(card_endereco)
        
        title_endereco = QLabel("Localização")
        title_endereco.setStyleSheet("font-size: 16px; font-weight: bold; color: #0F172A; margin-bottom: 10px;")
        layout_endereco.addWidget(title_endereco)
        
        form_endereco = QFormLayout()
        form_endereco.setSpacing(15)
        
        self.end_input = QLineEdit()
        self.num_input = QLineEdit()
        self.comp_input = QLineEdit()
        self.bairro_input = QLineEdit()
        self.cidade_input = QLineEdit()
        self.estado_input = QLineEdit()
        self.estado_input.setMaxLength(2)
        self.cep_input = QLineEdit()
        self.cep_input.setInputMask("99999-999")
        
        form_endereco.addRow("Logradouro:", self.end_input)
        
        # Layout horizontal para Numero e Complemento
        num_comp_layout = QHBoxLayout()
        num_comp_layout.addWidget(self.num_input)
        num_comp_layout.addWidget(QLabel("Compl.:"))
        num_comp_layout.addWidget(self.comp_input)
        form_endereco.addRow("Número:", num_comp_layout)
        
        form_endereco.addRow("Bairro:", self.bairro_input)
        
        # Layout horizontal para Cidade e Estado
        cid_est_layout = QHBoxLayout()
        cid_est_layout.addWidget(self.cidade_input)
        cid_est_layout.addWidget(QLabel("UF:"))
        cid_est_layout.addWidget(self.estado_input)
        form_endereco.addRow("Cidade:", cid_est_layout)
        
        form_endereco.addRow("CEP:", self.cep_input)
        
        layout_endereco.addLayout(form_endereco)
        self.scroll_layout.addWidget(card_endereco)

        # --- SEÇÃO 3: PREFERÊNCIAS E DOCUMENTOS ---
        card_docs = QFrame()
        card_docs.setObjectName("cardFrame")
        layout_docs = QVBoxLayout(card_docs)
        
        title_docs = QLabel("Preferências e Documentos")
        title_docs.setStyleSheet("font-size: 16px; font-weight: bold; color: #0F172A; margin-bottom: 10px;")
        layout_docs.addWidget(title_docs)
        
        form_docs = QFormLayout()
        form_docs.setSpacing(15)
        
        self.relatorios_input = QLineEdit()
        self.estoque_min_input = QSpinBox()
        self.estoque_min_input.setRange(1, 100)
        self.logo_path_input = QLineEdit()
        self.ticket_rodape_input = QLineEdit()
        self.relatorio_obs_input = QLineEdit()
        self.brnews_base_url_input = QLineEdit()
        self.modulo_senha_input = QLineEdit()
        self.modulo_senha_input.setEchoMode(QLineEdit.Password)
        
        form_docs.addRow("Pasta de Relatórios:", self.relatorios_input)
        form_docs.addRow("Estoque Mínimo Global:", self.estoque_min_input)
        form_docs.addRow("Logo da Empresa:", self.logo_path_input)
        form_docs.addRow("BRNews URL:", self.brnews_base_url_input)
        form_docs.addRow("Senha Módulos (Fiado/Fluxo):", self.modulo_senha_input)
        form_docs.addRow("Rodapé do Ticket:", self.ticket_rodape_input)
        form_docs.addRow("Observação Relatórios:", self.relatorio_obs_input)
        
        layout_docs.addLayout(form_docs)
        self.scroll_layout.addWidget(card_docs)

        # --- SEÇÃO 4: STATUS DO BANCO ---
        card_db = QFrame()
        card_db.setObjectName("cardFrame")
        layout_db = QVBoxLayout(card_db)

        title_db = QLabel("Status da Conexão / Banco Atual")
        title_db.setStyleSheet("font-size: 16px; font-weight: bold; color: #0F172A; margin-bottom: 10px;")
        layout_db.addWidget(title_db)

        self.lbl_db_url = QLabel("URL: ---")
        self.lbl_db_url.setWordWrap(True)
        self.lbl_db_url.setStyleSheet("font-size: 12px; color: #334155;")
        layout_db.addWidget(self.lbl_db_url)

        self.lbl_db_dialect = QLabel("Dialeto: ---")
        self.lbl_db_dialect.setStyleSheet("font-size: 12px; color: #334155;")
        layout_db.addWidget(self.lbl_db_dialect)

        self.lbl_db_status = QLabel("Status: ---")
        self.lbl_db_status.setStyleSheet("font-size: 12px; color: #334155; font-weight: 600;")
        layout_db.addWidget(self.lbl_db_status)

        btn_db = QPushButton("Testar Conexão")
        btn_db.setObjectName("actionButton")
        btn_db.setMinimumHeight(40)
        btn_db.clicked.connect(self.refresh_db_status)
        layout_db.addWidget(btn_db, alignment=Qt.AlignLeft)

        self.scroll_layout.addWidget(card_db)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # Rodapé com Botão Salvar - Garantindo visibilidade e estilo do caixa
        footer_container = QFrame()
        footer_container.setObjectName("cardFrame")
        footer_container.setStyleSheet("""
            QFrame#cardFrame { 
                background-color: white; 
                border-top: 1px solid #E2E8F0; 
                border-radius: 0px 0px 8px 8px;
            }
        """)
        footer_layout = QHBoxLayout(footer_container)
        footer_layout.setContentsMargins(20, 15, 20, 15)
        footer_layout.addStretch()
        
        self.btn_salvar = QPushButton("  💾  SALVAR ALTERAÇÕES")
        self.btn_salvar.setObjectName("primaryButton")
        self.btn_salvar.setMinimumHeight(55) # Altura similar aos botões do caixa
        self.btn_salvar.setFixedWidth(300)
        self.btn_salvar.setCursor(Qt.PointingHandCursor)
        self.btn_salvar.clicked.connect(self.salvar_dados)
        
        footer_layout.addWidget(self.btn_salvar)
        main_layout.addWidget(footer_container)

    def load_data(self):
        s = load_settings()
        
        # Empresa
        self.fantasia_input.setText(s.get("empresa_nome_fantasia", ""))
        self.razao_input.setText(s.get("empresa_razao_social", ""))
        self.cnpj_input.setText(s.get("empresa_cnpj", ""))
        self.tel_input.setText(s.get("empresa_telefone", ""))
        self.email_input.setText(s.get("empresa_email", ""))
        
        # Endereço
        self.end_input.setText(s.get("empresa_endereco", ""))
        self.num_input.setText(s.get("empresa_numero", ""))
        self.comp_input.setText(s.get("empresa_complemento", ""))
        self.bairro_input.setText(s.get("empresa_bairro", ""))
        self.cidade_input.setText(s.get("empresa_cidade", ""))
        self.estado_input.setText(s.get("empresa_estado", ""))
        self.cep_input.setText(s.get("empresa_cep", ""))
        
        # Preferências
        self.relatorios_input.setText(s.get("relatorios_path", "relatorios"))
        self.estoque_min_input.setValue(s.get("estoque_minimo_padrao", 5))
        self.logo_path_input.setText(s.get("empresa_logo_path", "app/img/logo_baleia.png"))
        self.brnews_base_url_input.setText(s.get("brnews_base_url", "http://127.0.0.1:5000"))
        self.modulo_senha_input.setText(s.get("modulo_senha", "baleia@2026"))
        self.ticket_rodape_input.setText(s.get("ticket_rodape", ""))
        self.relatorio_obs_input.setText(s.get("relatorio_observacao", ""))
        self.refresh_db_status()

    def salvar_dados(self):
        if not self.fantasia_input.text().strip():
            QMessageBox.warning(self, "Campo Obrigatório", "O Nome Fantasia da empresa é obrigatório.")
            return

        settings = load_settings()
        
        # Atualiza dicionário com novos valores
        settings.update({
            "empresa_nome_fantasia": self.fantasia_input.text(),
            "empresa_razao_social": self.razao_input.text(),
            "empresa_cnpj": self.cnpj_input.text(),
            "empresa_telefone": self.tel_input.text(),
            "empresa_email": self.email_input.text(),
            
            "empresa_endereco": self.end_input.text(),
            "empresa_numero": self.num_input.text(),
            "empresa_complemento": self.comp_input.text(),
            "empresa_bairro": self.bairro_input.text(),
            "empresa_cidade": self.cidade_input.text(),
            "empresa_estado": self.estado_input.text().upper(),
            "empresa_cep": self.cep_input.text(),
            
            "relatorios_path": self.relatorios_input.text(),
            "estoque_minimo_padrao": self.estoque_min_input.value(),
            "empresa_logo_path": self.logo_path_input.text(),
            "brnews_base_url": self.brnews_base_url_input.text(),
            "modulo_senha": self.modulo_senha_input.text() or "baleia@2026",
            "ticket_rodape": self.ticket_rodape_input.text(),
            "relatorio_observacao": self.relatorio_obs_input.text()
        })
        
        try:
            save_settings(settings)
            QMessageBox.information(self, "Sucesso", "Configurações institucionais salvas com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar: {e}")

    def refresh_db_status(self):
        """Atualiza informações de conexão do banco atual."""
        info = get_database_status()
        self.lbl_db_url.setText(f"URL: {info.get('url', '---')}")
        self.lbl_db_dialect.setText(f"Dialeto: {info.get('dialect', '---')}")

        if info.get("connected"):
            self.lbl_db_status.setText(f"Status: Conectado ({info.get('message', 'OK')})")
            self.lbl_db_status.setStyleSheet("font-size: 12px; color: #15803D; font-weight: 700;")
        else:
            self.lbl_db_status.setText(f"Status: Falha ({info.get('message', 'erro')})")
            self.lbl_db_status.setStyleSheet("font-size: 12px; color: #DC2626; font-weight: 700;")
