from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QFormLayout, 
    QDialog, QDoubleSpinBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextDocument, QColor, QPageSize
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from datetime import datetime
from app.core.config import load_settings
from app.core.branding import build_report_header_html
from app.modules.fiado.service import FiadoService

class ClienteDialog(QDialog):
    """Diálogo para cadastrar um novo cliente."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastrar Novo Cliente")
        self.setMinimumSize(450, 350)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Informações do Cliente")
        title.setObjectName("headerTitle")
        layout.addWidget(title)

        form_container = QFrame()
        form_layout = QFormLayout(form_container)
        form_layout.setSpacing(15)

        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome completo do cliente")
        
        self.telefone_input = QLineEdit()
        self.telefone_input.setPlaceholderText("(00) 00000-0000")
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("cliente@email.com")

        form_layout.addRow("Nome:", self.nome_input)
        form_layout.addRow("Telefone:", self.telefone_input)
        form_layout.addRow("E-mail:", self.email_input)

        layout.addWidget(form_container)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("secondaryButton")
        self.btn_cancelar.clicked.connect(self.reject)
        
        self.btn_salvar = QPushButton("Cadastrar")
        self.btn_salvar.setObjectName("primaryButton")
        self.btn_salvar.clicked.connect(self.accept)
        
        buttons_layout.addWidget(self.btn_cancelar)
        buttons_layout.addWidget(self.btn_salvar)
        
        layout.addLayout(buttons_layout)

    def get_data(self):
        return {
            "nome": self.nome_input.text(),
            "telefone": self.telefone_input.text(),
            "email": self.email_input.text()
        }

class PagamentoDialog(QDialog):
    """Diálogo para registrar um pagamento de dívida."""
    def __init__(self, parent=None, nome_cliente=""):
        super().__init__(parent)
        self.setWindowTitle(f"Receber de: {nome_cliente}")
        self.setMinimumSize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Registrar Pagamento")
        title.setObjectName("headerTitle")
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.valor_input = QDoubleSpinBox()
        self.valor_input.setRange(0.01, 99999.99)
        self.valor_input.setPrefix("R$ ")
        self.valor_input.setMinimumHeight(40)
        
        self.descricao_input = QLineEdit()
        self.descricao_input.setPlaceholderText("Ex: Pago via Pix / Dinheiro")

        form_layout.addRow("Valor Recebido:", self.valor_input)
        form_layout.addRow("Observação:", self.descricao_input)

        layout.addLayout(form_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("secondaryButton")
        btn_cancel.clicked.connect(self.reject)
        
        self.btn_salvar = QPushButton("Confirmar Recebimento")
        self.btn_salvar.setObjectName("primaryButton")
        self.btn_salvar.clicked.connect(self.accept)
        
        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(self.btn_salvar)
        
        layout.addLayout(buttons_layout)

    def get_data(self):
        return {
            "valor": self.valor_input.value(),
            "descricao": self.descricao_input.text() or "Pagamento de dívida"
        }

class DetalhesFiadoDialog(QDialog):
    """Diálogo para exibir o histórico detalhado de compras e pagamentos do cliente."""
    def __init__(self, parent=None, cliente=None):
        super().__init__(parent)
        self.cliente = cliente
        self.setWindowTitle(f"Histórico: {cliente.nome}")
        self.setMinimumSize(600, 450)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel(f"Detalhamento de Fiados - {self.cliente.nome}")
        title.setObjectName("headerTitle")
        layout.addWidget(title)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["Data", "Tipo", "Descrição", "Valor"])
        header = self.tabela.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setWordWrap(True)
        
        # Preencher tabela com o histórico do cliente
        historico = sorted(self.cliente.fiados, key=lambda x: x.data_registro, reverse=True)
        self.tabela.setRowCount(len(historico))
        
        for row, f in enumerate(historico):
            self.tabela.setItem(row, 0, QTableWidgetItem(f.data_registro.strftime("%d/%m/%Y %H:%M")))
            
            tipo_item = QTableWidgetItem(f.tipo)
            tipo_item.setTextAlignment(Qt.AlignCenter)
            if f.tipo == 'DEBITO':
                tipo_item.setForeground(Qt.red)
            else:
                tipo_item.setForeground(QColor(22, 163, 74))
            self.tabela.setItem(row, 1, tipo_item)
            
            desc = f.descricao or "---"
            desc_item = QTableWidgetItem(desc)
            desc_item.setToolTip(desc)
            self.tabela.setItem(row, 2, desc_item)
            
            valor_item = QTableWidgetItem(f"R$ {f.valor:.2f}")
            valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabela.setItem(row, 3, valor_item)

        self.tabela.resizeRowsToContents()
        layout.addWidget(self.tabela)

        resumo_layout = QHBoxLayout()
        lbl_total = QLabel(f"Dívida Atual: R$ {self.cliente.divida_atual:.2f}")
        lbl_total.setStyleSheet("font-size: 18px; font-weight: bold; color: #EF4444;")
        resumo_layout.addStretch()
        resumo_layout.addWidget(lbl_total)
        layout.addLayout(resumo_layout)

        btn_close = QPushButton("Fechar")
        btn_close.setObjectName("secondaryButton")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

class FiadoWidget(QWidget):
    """Interface do módulo de fiado/clientes."""
    def __init__(self):
        super().__init__()
        self.service = FiadoService()
        self.init_ui()
        self.atualizar_tabela()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Cabeçalho
        header_container = QFrame()
        header_container.setObjectName("cardFrame")
        header_layout = QHBoxLayout(header_container)
        
        title_layout = QVBoxLayout()
        header_label = QLabel("Controle de Clientes e Fiados")
        header_label.setObjectName("moduleTitle")
        title_layout.addWidget(header_label)
        
        self.lbl_stats = QLabel("Carregando resumo...")
        self.lbl_stats.setStyleSheet("color: #64748B; font-size: 12px;")
        title_layout.addWidget(self.lbl_stats)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        self.btn_imprimir = QPushButton("Imprimir Lista")
        self.btn_imprimir.setObjectName("actionButton")
        self.btn_imprimir.setMinimumHeight(40)
        self.btn_imprimir.clicked.connect(self.imprimir_lista)
        header_layout.addWidget(self.btn_imprimir)

        self.btn_cadastrar = QPushButton("+ Novo Cliente")
        self.btn_cadastrar.setObjectName("primaryButton")
        self.btn_cadastrar.setMinimumHeight(40)
        self.btn_cadastrar.clicked.connect(self.cadastrar_cliente)
        header_layout.addWidget(self.btn_cadastrar)

        layout.addWidget(header_container)

        # Tabela (em um card)
        tabela_container = QFrame()
        tabela_container.setObjectName("cardFrame")
        tabela_layout = QVBoxLayout(tabela_container)
        tabela_layout.setContentsMargins(15, 15, 15, 15)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome do Cliente", "Telefone", "Dívida Acumulada", "Ações"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.tabela.setColumnWidth(4, 250) # Largura ideal para dois botões
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.verticalHeader().setDefaultSectionSize(60) # Aumenta altura da linha para botões respirarem
        tabela_layout.addWidget(self.tabela)
        
        layout.addWidget(tabela_container)

        # Ações Inferiores (Fallback caso não use os botões na linha)
        acoes_layout = QHBoxLayout()
        
        self.btn_receber = QPushButton("Receber Pagamento")
        self.btn_receber.setObjectName("actionButton")
        self.btn_receber.setMinimumHeight(40)
        self.btn_receber.clicked.connect(self.receber_pagamento)
        
        self.btn_remover = QPushButton("Excluir Cliente")
        self.btn_remover.setObjectName("dangerButton")
        self.btn_remover.setMinimumHeight(40)
        self.btn_remover.clicked.connect(self.remover_cliente)

        acoes_layout.addWidget(self.btn_receber)
        acoes_layout.addWidget(self.btn_remover)
        acoes_layout.addStretch()
        layout.addLayout(acoes_layout)

    def imprimir_lista(self):
        """Gera um documento para impressão com a lista de clientes usando layout profissional."""
        s = load_settings()
        observacao_padrao = s.get("relatorio_observacao", "")

        selected_rows = self.tabela.selectionModel().selectedRows()
        
        # Decide se imprime tudo ou apenas selecionados
        if selected_rows:
            msg = f"Deseja imprimir apenas os {len(selected_rows)} clientes selecionados?"
            reply = QMessageBox.question(self, "Imprimir", msg, 
                                       QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            
            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                clientes_para_imprimir = []
                for row_index in selected_rows:
                    row = row_index.row()
                    clientes_para_imprimir.append({
                        "id": self.tabela.item(row, 0).text(),
                        "nome": self.tabela.item(row, 1).text(),
                        "telefone": self.tabela.item(row, 2).text(),
                        "divida": self.tabela.item(row, 3).text()
                    })
            else: # No (Imprimir todos)
                clientes_para_imprimir = self.get_todos_clientes_da_tabela()
        else:
            clientes_para_imprimir = self.get_todos_clientes_da_tabela()

        if not clientes_para_imprimir:
            QMessageBox.warning(self, "Aviso", "Não há dados para imprimir.")
            return

        total_divida_geral = 0
        rows_html = ""
        for i, c in enumerate(clientes_para_imprimir):
            zebra_class = "zebra" if i % 2 == 0 else ""
            try:
                # Remove R$ e converte para float para somar
                val_str = c['divida'].replace('R$ ', '').replace(',', '.')
                total_divida_geral += float(val_str)
            except: pass
            
            rows_html += f"""
                <tr class='{zebra_class}'>
                    <td style='width: 10%; text-align: center;'>{c['id']}</td>
                    <td style='width: 50%; font-weight: bold;'>{c['nome']}</td>
                    <td style='width: 20%; text-align: center;'>{c['telefone']}</td>
                    <td style='width: 20%; text-align: right;'>{c['divida']}</td>
                </tr>
            """

        tipo_relatorio = "Selecao Manual" if selected_rows else "Lista Completa"
        header_html = build_report_header_html(
            report_title="Relatorio de Clientes e Debitos",
            period_label=f"Tipo: {tipo_relatorio}",
            emitted_at=datetime.now(),
            settings=s
        )

        # Monta o HTML para o documento
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
                .summary-row {{
                    display: table;
                    width: 100%;
                    font-size: 16px;
                }}
                .summary-label {{ display: table-cell; text-align: left; font-weight: bold; color: #0F172A; }}
                .summary-value {{ display: table-cell; text-align: right; font-weight: bold; color: #EF4444; }}
                
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
                        <th style='text-align: center;'>ID</th>
                        <th>Nome do Cliente</th>
                        <th style='text-align: center;'>Telefone</th>
                        <th style='text-align: right;'>Dívida Atual</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            
            <div class='summary-container'>
                <div class='summary-card'>
                    <div class='summary-row'>
                        <span class='summary-label'>TOTAL A RECEBER:</span>
                        <span class='summary-value'>R$ {total_divida_geral:.2f}</span>
                    </div>
                </div>
            </div>
            <div style='clear: both;'></div>
            <div class='footer-obs'>{observacao_padrao}</div>
        </body>
        </html>
        """

        # Configura a impressão
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPageSize(QPageSize.A4))
        printer.setFullPage(True)
        
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.Accepted:
            doc = QTextDocument()
            doc.setPageSize(printer.pageRect(QPrinter.Point).size())
            doc.setHtml(html)
            doc.print_(printer)

    def get_todos_clientes_da_tabela(self):
        """Auxiliar para extrair todos os dados atuais da tabela."""
        clientes = []
        for row in range(self.tabela.rowCount()):
            clientes.append({
                "id": self.tabela.item(row, 0).text(),
                "nome": self.tabela.item(row, 1).text(),
                "telefone": self.tabela.item(row, 2).text(),
                "divida": self.tabela.item(row, 3).text()
            })
        return clientes

    def atualizar_tabela(self):
        """Busca os clientes do banco e atualiza a tabela."""
        clientes = self.service.get_todos_clientes()
        self.tabela.setRowCount(len(clientes))
        
        total_divida = 0

        for row, c in enumerate(clientes):
            total_divida += c.divida_atual
            
            id_item = QTableWidgetItem(str(c.id))
            id_item.setTextAlignment(Qt.AlignCenter)
            
            nome_item = QTableWidgetItem(c.nome)
            
            tel_item = QTableWidgetItem(c.telefone or "---")
            tel_item.setTextAlignment(Qt.AlignCenter)
            
            divida_item = QTableWidgetItem(f"R$ {c.divida_atual:.2f}")
            divida_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            if c.divida_atual > 0:
                divida_item.setForeground(Qt.red)
                divida_item.setBackground(QColor(254, 242, 242))

            self.tabela.setItem(row, 0, id_item)
            self.tabela.setItem(row, 1, nome_item)
            self.tabela.setItem(row, 2, tel_item)
            self.tabela.setItem(row, 3, divida_item)
            
            # Botões de Ação na Linha - Definição Limpa e Robusta
            container = QFrame()
            container.setObjectName("actionContainer")
            # Força o container a ser transparente e sem bordas, garantindo que não oculte os filhos
            container.setStyleSheet("""
                QFrame#actionContainer { 
                    background-color: transparent; 
                    border: none; 
                }
            """)
            
            h_layout = QHBoxLayout(container)
            h_layout.setContentsMargins(10, 5, 10, 5)
            h_layout.setSpacing(12)
            h_layout.setAlignment(Qt.AlignCenter)
            
            btn_ver = QPushButton("Ver")
            btn_ver.setObjectName("actionButton")
            btn_ver.setMinimumHeight(32)
            btn_ver.setMinimumWidth(90)
            btn_ver.setCursor(Qt.PointingHandCursor)
            btn_ver.clicked.connect(lambda checked=False, cliente=c: self.ver_detalhes_fiado(cliente))
            
            btn_pagar_lin = QPushButton("Pagar")
            btn_pagar_lin.setObjectName("primaryButton")
            btn_pagar_lin.setMinimumHeight(32)
            btn_pagar_lin.setMinimumWidth(90)
            btn_pagar_lin.setCursor(Qt.PointingHandCursor)
            btn_pagar_lin.setEnabled(c.divida_atual > 0)
            btn_pagar_lin.clicked.connect(lambda checked=False, cliente=c: self.receber_pagamento_rapido(cliente))
            
            h_layout.addWidget(btn_ver)
            h_layout.addWidget(btn_pagar_lin)
            
            self.tabela.setCellWidget(row, 4, container)
            
        self.lbl_stats.setText(f"Total de Clientes: {len(clientes)} | Total a Receber: R$ {total_divida:.2f}")

    def ver_detalhes_fiado(self, cliente):
        """Abre o diálogo de detalhes para o cliente."""
        # Recarrega o cliente do banco para ter os fiados atualizados
        cliente_refrescado = self.service.buscar_cliente_por_id(cliente.id)
        dialog = DetalhesFiadoDialog(self, cliente_refrescado)
        dialog.exec()

    def receber_pagamento_rapido(self, cliente):
        """Abre o diálogo de pagamento já com o valor total da dívida."""
        dialog = PagamentoDialog(self, cliente.nome)
        dialog.valor_input.setValue(cliente.divida_atual)
        
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            sucesso, msg = self.service.pagar_divida(cliente.id, **data)
            if sucesso:
                self.atualizar_tabela()
                QMessageBox.information(self, "Sucesso", f"Dívida de {cliente.nome} liquidada com sucesso!")
            else:
                QMessageBox.critical(self, "Erro", msg)

    def cadastrar_cliente(self):
        dialog = ClienteDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["nome"]:
                QMessageBox.warning(self, "Erro", "O nome do cliente é obrigatório.")
                return

            sucesso, msg = self.service.cadastrar_cliente(**data)
            if sucesso:
                self.atualizar_tabela()
            else:
                QMessageBox.critical(self, "Erro", msg)

    def receber_pagamento(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um cliente para receber pagamento.")
            return

        id_cliente = int(self.tabela.item(row, 0).text())
        nome_cliente = self.tabela.item(row, 1).text()
        
        dialog = PagamentoDialog(self, nome_cliente)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            sucesso, msg = self.service.pagar_divida(id_cliente, **data)
            if sucesso:
                self.atualizar_tabela()
                QMessageBox.information(self, "Sucesso", msg)
            else:
                QMessageBox.critical(self, "Erro", msg)

    def remover_cliente(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um cliente para remover.")
            return

        id_cliente = int(self.tabela.item(row, 0).text())
        nome_cliente = self.tabela.item(row, 1).text()

        confirm = QMessageBox.question(
            self, "Confirmação", f"Deseja realmente remover '{nome_cliente}'? Isso apagará todo o histórico de fiados dele.",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            sucesso, msg = self.service.deletar_cliente(id_cliente)
            if sucesso:
                self.atualizar_tabela()
            else:
                QMessageBox.critical(self, "Erro", msg)
