from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QFormLayout, 
    QGroupBox, QDialog, QDoubleSpinBox, QFrame, QComboBox, QDateEdit, QCheckBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QTextDocument, QPageSize
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from datetime import datetime
from app.core.config import load_settings
from app.core.branding import build_report_header_html
from app.modules.fluxo_caixa.service import FluxoCaixaService
from app.modules.configuracoes.tipos_despesa.service import TipoDespesaService
from app.modules.caixa_sessao.service import CaixaSessaoService

class MovimentacaoDialog(QDialog):
    """Diálogo para registrar uma saída (despesa) ou entrada extra."""
    def __init__(self, parent=None, tipo="SAIDA"):
        super().__init__(parent)
        self.tipo_service = TipoDespesaService()
        # Força o tipo para string e garante que seja SAIDA ou ENTRADA
        self.tipo = str(tipo).upper()
        self.setWindowTitle("Registrar Saída" if self.tipo == "SAIDA" else "Registrar Entrada")
        self.setMinimumSize(450, 350)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Nova Movimentação")
        title.setObjectName("headerTitle")
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.valor_input = QDoubleSpinBox()
        self.valor_input.setRange(0.01, 99999.99)
        self.valor_input.setPrefix("R$ ")
        self.valor_input.setMinimumHeight(40)
        
        if self.tipo == "SAIDA":
            self.categoria_combo = QComboBox()
            self.categoria_combo.setMinimumHeight(40)
            
            # Carregar categorias dinâmicas do banco de dados
            categorias = self.tipo_service.get_ativos()
            if not categorias:
                self.categoria_combo.addItem("Nenhuma categoria cadastrada", None)
                self.categoria_combo.setEnabled(False)
            else:
                for cat in categorias:
                    self.categoria_combo.addItem(cat.nome, cat.id)
            
            form_layout.addRow("Categoria de Despesa:", self.categoria_combo)
        
        self.descricao_input = QLineEdit()
        self.descricao_input.setPlaceholderText("Ex: Ref. Nota Fiscal #123")
        self.descricao_input.setMinimumHeight(40)

        form_layout.addRow("Valor:", self.valor_input)
        if self.tipo == "ENTRADA":
            form_layout.addRow("Descrição:", self.descricao_input)
        else:
            form_layout.addRow("Observação Adicional:", self.descricao_input)

        layout.addLayout(form_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("secondaryButton")
        btn_cancel.clicked.connect(self.reject)
        
        self.btn_salvar = QPushButton("Confirmar")
        self.btn_salvar.setObjectName("primaryButton" if self.tipo == "ENTRADA" else "dangerButton")
        self.btn_salvar.clicked.connect(self.accept)
        
        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(self.btn_salvar)
        
        layout.addLayout(buttons_layout)

    def get_data(self):
        descricao = self.descricao_input.text()
        tipo_despesa_id = None
        
        if self.tipo == "SAIDA":
            tipo_despesa_id = self.categoria_combo.currentData()
            categoria_nome = self.categoria_combo.currentText()
            final_desc = f"[{categoria_nome}] {descricao}" if descricao else categoria_nome
        else:
            final_desc = descricao
            
        return {
            "valor": self.valor_input.value(),
            "descricao": final_desc,
            "tipo_despesa_id": tipo_despesa_id
        }


class CaixaAberturaDialog(QDialog):
    """Diálogo para abertura de caixa com valor inicial e observação."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Abertura de Caixa")
        self.setMinimumSize(460, 260)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        title = QLabel("Abrir Caixa")
        title.setObjectName("headerTitle")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(14)

        self.valor_input = QDoubleSpinBox()
        self.valor_input.setRange(0.0, 999999.99)
        self.valor_input.setPrefix("R$ ")
        self.valor_input.setDecimals(2)
        self.valor_input.setMinimumHeight(40)
        form.addRow("Valor de abertura (troco):", self.valor_input)

        self.obs_input = QLineEdit()
        self.obs_input.setPlaceholderText("Opcional (ex.: Troco inicial conferido)")
        self.obs_input.setMinimumHeight(40)
        form.addRow("Observação:", self.obs_input)

        layout.addLayout(form)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("secondaryButton")
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton("Abrir")
        btn_ok.setObjectName("primaryButton")
        btn_ok.clicked.connect(self.accept)

        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(btn_ok)
        layout.addLayout(buttons_layout)

    def get_data(self):
        """Retorna valor de abertura e observação."""
        return float(self.valor_input.value()), self.obs_input.text()


class CaixaFechamentoDialog(QDialog):
    """Diálogo para fechamento de caixa com conferência de saldo esperado."""

    def __init__(self, parent=None, sessao=None):
        super().__init__(parent)
        self.sessao = sessao
        self.setWindowTitle("Fechamento de Caixa")
        self.setMinimumSize(520, 340)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        title = QLabel("Fechar Caixa")
        title.setObjectName("headerTitle")
        layout.addWidget(title)

        totals = CaixaSessaoService.calcular_totais_sessao(self.sessao.id)
        esperado = float(totals.get("saldo_esperado", 0.0))
        entradas = float(totals.get("entradas", 0.0))
        saidas = float(totals.get("saidas", 0.0))

        resumo = QLabel(
            f"Sessão #{self.sessao.id} aberta em {self.sessao.aberta_em.strftime('%d/%m/%Y %H:%M')}<br>"
            f"Troco (abertura): <b>R$ {float(self.sessao.valor_abertura or 0.0):.2f}</b><br>"
            f"Entradas (sessão): <b>R$ {entradas:.2f}</b> | Saídas (sessão): <b>R$ {saidas:.2f}</b><br>"
            f"Saldo esperado no caixa: <b>R$ {esperado:.2f}</b>"
        )
        resumo.setWordWrap(True)
        resumo.setStyleSheet("font-size: 12px; color: #475569;")
        layout.addWidget(resumo)

        form = QFormLayout()
        form.setSpacing(14)

        self.valor_contado = QDoubleSpinBox()
        self.valor_contado.setRange(0.0, 999999.99)
        self.valor_contado.setPrefix("R$ ")
        self.valor_contado.setDecimals(2)
        self.valor_contado.setMinimumHeight(40)
        self.valor_contado.setValue(esperado)
        form.addRow("Valor contado (gaveta):", self.valor_contado)

        self.obs_input = QLineEdit()
        self.obs_input.setPlaceholderText("Opcional (ex.: Diferença por sangria/erro)")
        self.obs_input.setMinimumHeight(40)
        form.addRow("Observação:", self.obs_input)

        layout.addLayout(form)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("secondaryButton")
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton("Fechar")
        btn_ok.setObjectName("dangerButton")
        btn_ok.clicked.connect(self.accept)

        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(btn_ok)
        layout.addLayout(buttons_layout)

    def get_data(self):
        """Retorna valor contado e observação."""
        return float(self.valor_contado.value()), self.obs_input.text()

class FluxoCaixaWidget(QWidget):
    """Interface do Fluxo de Caixa / Relatórios Financeiros."""
    def __init__(self):
        super().__init__()
        self.service = FluxoCaixaService()
        self.init_ui()
        self.atualizar_dados()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Cabeçalho com Resumo (Cards)
        cards_layout = QHBoxLayout()
        
        # Card Saldo Atual
        saldo_card = QFrame()
        saldo_card.setStyleSheet("background-color: white; border-radius: 10px; border-left: 5px solid #22C55E;")
        saldo_layout = QVBoxLayout(saldo_card)
        saldo_layout.addWidget(QLabel("Saldo em Caixa"))
        self.lbl_saldo = QLabel("R$ 0.00")
        self.lbl_saldo.setStyleSheet("font-size: 28px; font-weight: bold; color: #16A34A;")
        saldo_layout.addWidget(self.lbl_saldo)
        cards_layout.addWidget(saldo_card)

        # Card Entradas Mês
        entradas_card = QFrame()
        entradas_card.setStyleSheet("background-color: white; border-radius: 10px; border-left: 5px solid #3B82F6;")
        entradas_layout = QVBoxLayout(entradas_card)
        entradas_layout.addWidget(QLabel("Entradas (Mês)"))
        self.lbl_entradas_mes = QLabel("R$ 0.00")
        self.lbl_entradas_mes.setStyleSheet("font-size: 24px; font-weight: bold; color: #2563EB;")
        entradas_layout.addWidget(self.lbl_entradas_mes)
        cards_layout.addWidget(entradas_card)

        # Card Saídas Mês
        saidas_card = QFrame()
        saidas_card.setStyleSheet("background-color: white; border-radius: 10px; border-left: 5px solid #EF4444;")
        saidas_layout = QVBoxLayout(saidas_card)
        saidas_layout.addWidget(QLabel("Saídas (Mês)"))
        self.lbl_saidas_mes = QLabel("R$ 0.00")
        self.lbl_saidas_mes.setStyleSheet("font-size: 24px; font-weight: bold; color: #DC2626;")
        saidas_layout.addWidget(self.lbl_saidas_mes)
        cards_layout.addWidget(saidas_card)

        layout.addLayout(cards_layout)

        # Ações do Fluxo
        acoes_layout = QHBoxLayout()

        self.btn_abrir_caixa = QPushButton("Abrir Caixa")
        self.btn_abrir_caixa.setObjectName("primaryButton")
        self.btn_abrir_caixa.setMinimumHeight(45)
        self.btn_abrir_caixa.clicked.connect(self.abrir_caixa)

        self.btn_fechar_caixa = QPushButton("Fechar Caixa")
        self.btn_fechar_caixa.setObjectName("secondaryButton")
        self.btn_fechar_caixa.setMinimumHeight(45)
        self.btn_fechar_caixa.clicked.connect(self.fechar_caixa)
        
        self.btn_saida = QPushButton("  - Registrar Despesa / Retirada")
        self.btn_saida.setObjectName("dangerButton")
        self.btn_saida.setMinimumHeight(45)
        self.btn_saida.clicked.connect(lambda: self.abrir_dialogo_movimentacao("SAIDA"))
        
        self.btn_entrada = QPushButton("  + Registrar Entrada Extra")
        self.btn_entrada.setObjectName("actionButton")
        self.btn_entrada.setMinimumHeight(45)
        self.btn_entrada.clicked.connect(lambda: self.abrir_dialogo_movimentacao("ENTRADA"))
        
        acoes_layout.addWidget(self.btn_abrir_caixa)
        acoes_layout.addWidget(self.btn_fechar_caixa)
        acoes_layout.addSpacing(10)
        acoes_layout.addWidget(self.btn_entrada)
        acoes_layout.addWidget(self.btn_saida)
        acoes_layout.addStretch()
        
        self.lbl_balanco_mes = QLabel("Balanço Mensal: R$ 0.00")
        self.lbl_balanco_mes.setStyleSheet("font-weight: bold; color: #475569; font-size: 16px;")
        acoes_layout.addWidget(self.lbl_balanco_mes)
        
        layout.addLayout(acoes_layout)

        # Tabela de Movimentações (Card)
        tabela_container = QFrame()
        tabela_container.setObjectName("cardFrame")
        tabela_layout = QVBoxLayout(tabela_container)
        tabela_layout.setContentsMargins(15, 15, 15, 15)

        # Cabeçalho da Tabela com Filtros
        tabela_header = QHBoxLayout()
        tabela_label = QLabel("Histórico de Movimentações")
        tabela_label.setObjectName("moduleTitle")
        tabela_header.addWidget(tabela_label)
        
        tabela_header.addStretch()
        
        # Filtros de Data
        tabela_header.addWidget(QLabel("De:"))
        self.date_de = QDateEdit()
        self.date_de.setCalendarPopup(True)
        self.date_de.setDate(QDate.currentDate().addDays(-7)) # Padrão última semana
        self.date_de.setMinimumHeight(35)
        tabela_header.addWidget(self.date_de)
        
        tabela_header.addWidget(QLabel("Até:"))
        self.date_ate = QDateEdit()
        self.date_ate.setCalendarPopup(True)
        self.date_ate.setDate(QDate.currentDate())
        self.date_ate.setMinimumHeight(35)
        tabela_header.addWidget(self.date_ate)

        self.chk_incluir_fiado = QCheckBox("Incluir vendas fiado (rastreio)")
        self.chk_incluir_fiado.setChecked(False)
        self.chk_incluir_fiado.setStyleSheet("color: #64748B; font-size: 12px;")
        tabela_header.addWidget(self.chk_incluir_fiado)
        
        self.btn_filtrar = QPushButton("Filtrar")
        self.btn_filtrar.setObjectName("actionButton")
        self.btn_filtrar.setMinimumHeight(35)
        self.btn_filtrar.clicked.connect(self.atualizar_dados)
        tabela_header.addWidget(self.btn_filtrar)
        
        self.btn_imprimir = QPushButton("Imprimir Relatório")
        self.btn_imprimir.setObjectName("secondaryButton")
        self.btn_imprimir.setMinimumHeight(35)
        self.btn_imprimir.clicked.connect(self.imprimir_historico)
        tabela_header.addWidget(self.btn_imprimir)
        
        tabela_layout.addLayout(tabela_header)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["Data/Hora", "Tipo", "Categoria", "Descrição", "Valor (R$)"])
        header = self.tabela.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tabela.setColumnWidth(3, 520)
        self.tabela.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        self.tabela.setAlternatingRowColors(True)
        tabela_layout.addWidget(self.tabela)
        
        layout.addWidget(tabela_container)

    def aplicar_periodo(self, period_days: int):
        """Aplica rapidamente um período padrão (Hoje/7/30 dias) e atualiza a tabela."""
        days = 1 if period_days <= 1 else (30 if period_days >= 30 else 7)
        self.date_ate.setDate(QDate.currentDate())
        self.date_de.setDate(QDate.currentDate().addDays(-(days - 1)))
        self.atualizar_dados()

    def atualizar_dados(self):
        """Atualiza todas as informações financeiras na tela."""
        self.atualizar_status_caixa()
        # 1. Saldo Atual
        saldo = self.service.get_saldo_atual()
        self.lbl_saldo.setText(f"R$ {saldo:.2f}")

        # 2. Resumo Mensal
        resumo = self.service.get_resumo_mes()
        self.lbl_entradas_mes.setText(f"R$ {resumo['entradas']:.2f}")
        self.lbl_saidas_mes.setText(f"R$ {resumo['saidas']:.2f}")
        self.lbl_balanco_mes.setText(f"Balanço Mensal: R$ {resumo['saldo']:.2f}")

        # 3. Movimentações por Período
        data_de = self.date_de.date().toPython()
        data_ate = self.date_ate.date().toPython()
        
        movimentacoes = self.service.get_movimentacoes_por_periodo(
            data_de,
            data_ate,
            incluir_venda_fiado=self.chk_incluir_fiado.isChecked()
        )
        self.tabela.setRowCount(len(movimentacoes))
        
        for row, mov in enumerate(movimentacoes):
            data_item = QTableWidgetItem(mov.data_registro.strftime("%d/%m/%Y %H:%M"))
            data_item.setTextAlignment(Qt.AlignCenter)
            
            tipo_item = QTableWidgetItem(mov.tipo)
            tipo_item.setTextAlignment(Qt.AlignCenter)
            
            # Categoria (se houver)
            cat_nome = mov.categoria_despesa.nome if mov.categoria_despesa else "---"
            cat_item = QTableWidgetItem(cat_nome)
            cat_item.setTextAlignment(Qt.AlignCenter)
            
            desc_text = mov.descricao or "---"
            desc_item = QTableWidgetItem(desc_text)
            desc_item.setToolTip(desc_text)
            
            valor_item = QTableWidgetItem(f"R$ {mov.valor:.2f}")
            valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            if mov.tipo in ['SAIDA', 'FECHAMENTO_CAIXA']:
                valor_item.setForeground(Qt.red)
                valor_item.setBackground(QColor(254, 242, 242))
            elif mov.tipo == 'VENDA_FIADO':
                valor_item.setForeground(QColor(71, 85, 105))
            else:
                valor_item.setForeground(QColor(22, 163, 74)) # Success Green

            self.tabela.setItem(row, 0, data_item)
            self.tabela.setItem(row, 1, tipo_item)
            self.tabela.setItem(row, 2, cat_item)
            self.tabela.setItem(row, 3, desc_item)
            self.tabela.setItem(row, 4, valor_item)

    def imprimir_historico(self):
        """Gera e imprime o relatório do fluxo de caixa por período com layout profissional."""
        s = load_settings()
        observacao_padrao = s.get("relatorio_observacao", "")

        data_de = self.date_de.date().toPython()
        data_ate = self.date_ate.date().toPython()
        movimentacoes = self.service.get_movimentacoes_por_periodo(
            data_de,
            data_ate,
            incluir_venda_fiado=self.chk_incluir_fiado.isChecked()
        )
        
        if not movimentacoes:
            QMessageBox.warning(self, "Aviso", "Não há movimentações no período selecionado.")
            return

        total_entradas = 0
        total_saidas = 0
        
        rows_html = ""
        for i, mov in enumerate(movimentacoes):
            valor_f = f"R$ {mov.valor:.2f}"
            cat_nome = mov.categoria_despesa.nome if mov.categoria_despesa else "Geral"
            zebra_class = "zebra" if i % 2 == 0 else ""
            
            if mov.tipo in ['ENTRADA', 'ABERTURA_CAIXA']:
                total_entradas += mov.valor
                tipo_display = "Entrada"
                color_class = "text-green"
            elif mov.tipo == 'VENDA_FIADO':
                tipo_display = "Venda Fiado"
                color_class = "text-gray"
            else:
                total_saidas += mov.valor
                tipo_display = "Saída"
                color_class = "text-red"
                
            rows_html += f"""
                <tr class='{zebra_class}'>
                    <td style='width: 15%;'>{mov.data_registro.strftime('%d/%m/%Y %H:%M')}</td>
                    <td style='width: 10%; font-weight: bold;'>{tipo_display}</td>
                    <td style='width: 20%;'>{cat_nome}</td>
                    <td style='width: 40%;'>{mov.descricao or '---'}</td>
                    <td style='width: 15%; text-align: right;' class='{color_class}'><b>{valor_f}</b></td>
                </tr>
            """

        saldo_periodo = total_entradas - total_saidas
        periodo = f"{data_de.strftime('%d/%m/%Y')} ate {data_ate.strftime('%d/%m/%Y')}"
        header_html = build_report_header_html(
            report_title="Relatorio de Fluxo de Caixa",
            period_label=periodo,
            emitted_at=datetime.now(),
            settings=s
        )
        
        html = f"""
        <html>
        <head>
            <style>
                @page {{ margin: 1.5cm; }}
                body {{ 
                    font-family: 'Segoe UI', Arial, sans-serif; 
                    color: #1E293B; 
                    line-height: 1.5;
                }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin-top: 5px;
                }}
                th {{ 
                    background-color: #F8FAFC; 
                    color: #475569;
                    font-weight: bold; 
                    text-transform: uppercase;
                    font-size: 10px;
                    padding: 8px 6px;
                    border-bottom: 2px solid #E2E8F0;
                    text-align: left;
                }}
                td {{ 
                    padding: 6px; 
                    border-bottom: 1px solid #F1F5F9;
                    font-size: 10px;
                    vertical-align: middle;
                }}
                .zebra {{ background-color: #FBFDFF; }}
                .text-green {{ color: #15803D; }}
                .text-red {{ color: #DC2626; }}
                .text-gray {{ color: #475569; }}
                
                .summary-container {{ 
                    margin-top: 40px;
                    page-break-inside: avoid;
                }}
                .summary-card {{
                    float: right;
                    width: 300px;
                    background-color: #F8FAFC;
                    border: 1px solid #E2E8F0;
                    border-radius: 8px;
                    padding: 20px;
                }}
                .summary-title {{
                    font-size: 14px;
                    font-weight: bold;
                    color: #475569;
                    margin-bottom: 15px;
                    border-bottom: 1px solid #CBD5E1;
                    padding-bottom: 5px;
                }}
                .summary-row {{
                    display: table;
                    width: 100%;
                    margin-bottom: 8px;
                    font-size: 13px;
                }}
                .summary-label {{ display: table-cell; text-align: left; color: #64748B; }}
                .summary-value {{ display: table-cell; text-align: right; font-weight: 600; }}
                .total-row {{
                    margin-top: 10px;
                    padding-top: 10px;
                    border-top: 2px solid #E2E8F0;
                    font-size: 16px;
                }}
                .total-label {{ color: #0F172A; font-weight: bold; }}
                .total-value {{ color: #16A34A; font-weight: bold; }}
                .footer-obs {{
                    margin-top: 20px;
                    font-size: 10px;
                    color: #94A3B8;
                    font-style: italic;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            {header_html}
            
            <table>
                <thead>
                    <tr>
                        <th>Data/Hora</th>
                        <th>Tipo</th>
                        <th>Categoria</th>
                        <th>Descrição</th>
                        <th style='text-align: right;'>Valor</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            
            <div class='summary-container'>
                <div class='summary-card'>
                    <div class='summary-title'>Resumo do Período</div>
                    
                    <div class='summary-row'>
                        <span class='summary-label'>Total de Entradas:</span>
                        <span class='summary-value text-green'>R$ {total_entradas:.2f}</span>
                    </div>
                    
                    <div class='summary-row'>
                        <span class='summary-label'>Total de Saídas:</span>
                        <span class='summary-value text-red'>R$ {total_saidas:.2f}</span>
                    </div>
                    
                    <div class='summary-row total-row'>
                        <span class='summary-label total-label'>Saldo Final:</span>
                        <span class='summary-value total-value'>R$ {saldo_periodo:.2f}</span>
                    </div>
                </div>
            </div>
            <div style='clear: both;'></div>
            <div class='footer-obs'>{observacao_padrao}</div>
        </body>
        </html>
        """

        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPageSize(QPageSize.A4))
        printer.setFullPage(True)
        
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.Accepted:
            doc = QTextDocument()
            # Define a largura do documento para 800 pixels (aproximado para A4 sem perdas de escala)
            doc.setPageSize(printer.pageRect(QPrinter.Point).size())
            doc.setHtml(html)
            doc.print_(printer)

    def abrir_dialogo_movimentacao(self, tipo):
        """Abre o diálogo correto para registrar entrada ou saída."""
        dialog = MovimentacaoDialog(self, tipo)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["descricao"]:
                QMessageBox.warning(self, "Erro", "A descrição é obrigatória.")
                return
            
            if tipo == "SAIDA":
                sucesso, msg = self.service.registrar_saida(
                    valor=data["valor"],
                    descricao=data["descricao"],
                    tipo_despesa_id=data.get("tipo_despesa_id")
                )
            else:
                sucesso, msg = self.service.registrar_entrada(
                    valor=data["valor"],
                    descricao=data["descricao"]
                )

            if sucesso:
                self.atualizar_dados()
            else:
                QMessageBox.critical(self, "Erro", msg)

    def atualizar_status_caixa(self):
        """Atualiza estado dos botões de abrir/fechar conforme sessão atual."""
        sessao = CaixaSessaoService.get_sessao_aberta()
        is_open = sessao is not None
        self.btn_abrir_caixa.setEnabled(not is_open)
        self.btn_fechar_caixa.setEnabled(is_open)

    def abrir_caixa(self):
        """Abre sessão de caixa com valor inicial."""
        dialog = CaixaAberturaDialog(self)
        if dialog.exec() == QDialog.Accepted:
            valor, obs = dialog.get_data()
            sucesso, msg = CaixaSessaoService.abrir_caixa(valor, obs)
            if sucesso:
                self.atualizar_dados()
            else:
                QMessageBox.warning(self, "Aviso", msg)

    def fechar_caixa(self):
        """Fecha sessão aberta com conferência de contado vs esperado."""
        sessao = CaixaSessaoService.get_sessao_aberta()
        if not sessao:
            QMessageBox.warning(self, "Aviso", "Não existe caixa aberto.")
            return

        dialog = CaixaFechamentoDialog(self, sessao)
        if dialog.exec() == QDialog.Accepted:
            valor_contado, obs = dialog.get_data()
            sucesso, msg = CaixaSessaoService.fechar_caixa(valor_contado, obs)
            if sucesso:
                self.atualizar_dados()
            else:
                QMessageBox.critical(self, "Erro", msg)
