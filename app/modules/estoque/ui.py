from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QFormLayout, 
    QDialog, QDoubleSpinBox, QSpinBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QTextDocument, QPageSize
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from datetime import datetime
from app.core.config import load_settings
from app.core.branding import build_report_header_html
from app.modules.estoque.service import EstoqueService

class ProdutoDialog(QDialog):
    """Diálogo para adicionar ou editar um produto."""
    def __init__(self, parent=None, produto=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastro de Produto" if not produto else f"Editar Produto: {produto.nome}")
        self.produto = produto
        self.setMinimumSize(500, 450)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Informações do Produto")
        title.setObjectName("headerTitle")
        layout.addWidget(title)

        form_container = QFrame()
        form_layout = QFormLayout(form_container)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("Ex: 101")
        
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Ex: Cerveja Brahma 600ml")
        
        self.preco_input = QDoubleSpinBox()
        self.preco_input.setRange(0, 99999.99)
        self.preco_input.setPrefix("R$ ")
        self.preco_input.setDecimals(2)
        
        self.quantidade_input = QSpinBox()
        self.quantidade_input.setRange(0, 10000)
        
        self.estoque_min_input = QSpinBox()
        self.estoque_min_input.setRange(0, 1000)

        if self.produto:
            self.codigo_input.setText(self.produto.codigo)
            self.nome_input.setText(self.produto.nome)
            self.preco_input.setValue(self.produto.preco)
            self.quantidade_input.setValue(self.produto.quantidade)
            self.estoque_min_input.setValue(self.produto.estoque_minimo)
        else:
            self.estoque_min_input.setValue(5)

        form_layout.addRow("Código único:", self.codigo_input)
        form_layout.addRow("Nome do Produto:", self.nome_input)
        form_layout.addRow("Preço de Venda:", self.preco_input)
        form_layout.addRow("Qtd. em Estoque:", self.quantidade_input)
        form_layout.addRow("Estoque Mínimo:", self.estoque_min_input)

        layout.addWidget(form_container)

        # Botões de Ação
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("secondaryButton")
        self.btn_cancelar.setMinimumWidth(120)
        self.btn_cancelar.clicked.connect(self.reject)
        
        self.btn_salvar = QPushButton("Salvar Produto")
        self.btn_salvar.setObjectName("primaryButton")
        self.btn_salvar.setMinimumWidth(150)
        self.btn_salvar.clicked.connect(self.accept)
        
        buttons_layout.addWidget(self.btn_cancelar)
        buttons_layout.addWidget(self.btn_salvar)
        
        layout.addLayout(buttons_layout)

    def get_data(self):
        return {
            "codigo": self.codigo_input.text(),
            "nome": self.nome_input.text(),
            "preco": self.preco_input.value(),
            "quantidade": self.quantidade_input.value(),
            "estoque_minimo": self.estoque_min_input.value()
        }


class ReposicaoEstoqueDialog(QDialog):
    """Diálogo para atualizar rapidamente a quantidade de um produto com estoque baixo."""

    def __init__(self, parent=None, produto=None):
        super().__init__(parent)
        self.produto = produto
        self.setWindowTitle("Atualizar Estoque")
        self.setMinimumSize(420, 220)
        self.init_ui()

    def init_ui(self):
        """Monta o diálogo de reposição com quantidade atual, mínima e novo valor."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Reposição / Atualização de Estoque")
        title.setObjectName("headerTitle")
        layout.addWidget(title)

        info = QLabel(
            f"<b>{self.produto.codigo}</b> - {self.produto.nome}<br>"
            f"Qtd. atual: <b>{self.produto.quantidade}</b> | "
            f"Qtd. mínima: <b>{self.produto.estoque_minimo}</b>"
        )
        info.setWordWrap(True)
        info.setObjectName("textSecondaryLabel")
        layout.addWidget(info)

        form_container = QFrame()
        form_layout = QFormLayout(form_container)
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.qtd_nova = QSpinBox()
        self.qtd_nova.setRange(0, 1000000)
        self.qtd_nova.setValue(max(self.produto.quantidade, self.produto.estoque_minimo))
        form_layout.addRow("Nova quantidade:", self.qtd_nova)

        layout.addWidget(form_container)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("secondaryButton")
        btn_cancelar.setMinimumWidth(120)
        btn_cancelar.clicked.connect(self.reject)

        btn_confirmar = QPushButton("Atualizar")
        btn_confirmar.setObjectName("primaryButton")
        btn_confirmar.setMinimumWidth(140)
        btn_confirmar.clicked.connect(self.accept)

        buttons_layout.addWidget(btn_cancelar)
        buttons_layout.addWidget(btn_confirmar)
        layout.addLayout(buttons_layout)

    def get_nova_quantidade(self) -> int:
        """Retorna a nova quantidade definida pelo usuário."""
        return int(self.qtd_nova.value())


class EstoqueWidget(QWidget):
    """Interface do módulo de estoque."""
    def __init__(self):
        super().__init__()
        self.service = EstoqueService()
        self.init_ui()
        self.atualizar_tabela()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Cabeçalho / Barra de Ações
        header_container = QFrame()
        header_container.setObjectName("cardFrame")
        header_layout = QHBoxLayout(header_container)
        
        title_layout = QVBoxLayout()
        header_label = QLabel("Gerenciamento de Estoque")
        header_label.setObjectName("moduleTitle")
        title_layout.addWidget(header_label)
        
        self.lbl_stats = QLabel("Carregando estatísticas...")
        self.lbl_stats.setObjectName("mutedLabel")
        title_layout.addWidget(self.lbl_stats)

        self.lbl_low_stock_banner = QLabel()
        self.lbl_low_stock_banner.setWordWrap(True)
        self.lbl_low_stock_banner.setVisible(False)
        self.lbl_low_stock_banner.setObjectName("lowStockBanner")
        title_layout.addWidget(self.lbl_low_stock_banner)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        # Busca
        self.busca_input = QLineEdit()
        self.busca_input.setPlaceholderText("🔍 Buscar produto por nome...")
        self.busca_input.setMinimumWidth(300)
        self.busca_input.textChanged.connect(self.filtrar_tabela)
        header_layout.addWidget(self.busca_input)

        self.btn_adicionar = QPushButton("  + Adicionar Produto")
        self.btn_adicionar.setObjectName("primaryButton")
        self.btn_adicionar.clicked.connect(self.adicionar_produto)
        header_layout.addWidget(self.btn_adicionar)

        self.btn_imprimir = QPushButton("Imprimir Relatório")
        self.btn_imprimir.setObjectName("secondaryButton")
        self.btn_imprimir.clicked.connect(self.imprimir_relatorio_estoque)
        header_layout.addWidget(self.btn_imprimir)

        layout.addWidget(header_container)

        # Tabela (em um card)
        tabela_container = QFrame()
        tabela_container.setObjectName("cardFrame")
        tabela_layout = QVBoxLayout(tabela_container)
        tabela_layout.setContentsMargins(15, 15, 15, 15)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels(["ID", "Código", "Nome do Produto", "Preço Unit.", "Qtd. Atual", "Qtd. Mínima", "Ações"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.tabela.setColumnWidth(6, 170)
        self.tabela.verticalHeader().setDefaultSectionSize(52)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.doubleClicked.connect(self.editar_produto)
        tabela_layout.addWidget(self.tabela)

        layout.addWidget(tabela_container)

        # Barra Inferior de Ações Selecionadas
        footer_layout = QHBoxLayout()
        
        self.btn_editar = QPushButton("Editar Selecionado")
        self.btn_editar.setObjectName("secondaryButton")
        self.btn_editar.clicked.connect(self.editar_produto)
        
        self.btn_deletar = QPushButton("Remover Produto")
        self.btn_deletar.setObjectName("dangerButton")
        self.btn_deletar.clicked.connect(self.remover_produto)

        footer_layout.addWidget(self.btn_editar)
        footer_layout.addWidget(self.btn_deletar)
        footer_layout.addStretch()
        
        self.btn_atualizar = QPushButton("Atualizar Lista")
        self.btn_atualizar.setObjectName("secondaryButton")
        self.btn_atualizar.clicked.connect(self.atualizar_tabela)
        footer_layout.addWidget(self.btn_atualizar)

        layout.addLayout(footer_layout)

    def filtrar_tabela(self, texto):
        """Filtra a tabela em tempo real com base na busca (Nome ou Código)."""
        texto = texto.lower()
        for row in range(self.tabela.rowCount()):
            codigo = self.tabela.item(row, 1).text().lower()
            nome = self.tabela.item(row, 2).text().lower()
            
            if texto in codigo or texto in nome:
                self.tabela.setRowHidden(row, False)
            else:
                self.tabela.setRowHidden(row, True)

    def atualizar_tabela(self):
        """Busca os produtos do banco e atualiza a tabela."""
        produtos = self.service.get_todos()
        self.tabela.setRowCount(len(produtos))
        
        total_itens = 0
        baixo_estoque = 0
        low_stock_ids = set()
        low_alert_ids = set()
        low_stock_preview = []

        for row, p in enumerate(produtos):
            total_itens += p.quantidade
            
            id_item = QTableWidgetItem(str(p.id))
            id_item.setTextAlignment(Qt.AlignCenter)
            
            codigo_item = QTableWidgetItem(p.codigo)
            codigo_item.setTextAlignment(Qt.AlignCenter)
            
            nome_item = QTableWidgetItem(p.nome)
            
            preco_item = QTableWidgetItem(f"R$ {p.preco:.2f}")
            preco_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            qtd_item = QTableWidgetItem(str(p.quantidade))
            qtd_item.setTextAlignment(Qt.AlignCenter)
            
            min_item = QTableWidgetItem(str(p.estoque_minimo))
            min_item.setTextAlignment(Qt.AlignCenter)

            self.tabela.setItem(row, 0, id_item)
            self.tabela.setItem(row, 1, codigo_item)
            self.tabela.setItem(row, 2, nome_item)
            self.tabela.setItem(row, 3, preco_item)
            self.tabela.setItem(row, 4, qtd_item)
            self.tabela.setItem(row, 5, min_item)

            # Destaque para estoque baixo
            if p.quantidade <= p.estoque_minimo:
                baixo_estoque += 1
                low_stock_ids.add(p.id)
                if p.quantidade < p.estoque_minimo:
                    low_alert_ids.add(p.id)
                if len(low_stock_preview) < 5:
                    low_stock_preview.append(f"{p.codigo} - {p.nome}")
                for col in range(self.tabela.columnCount()):
                    cell = self.tabela.item(row, col)
                    if cell is not None:
                        cell.setForeground(Qt.red)
                        cell.setBackground(QColor(254, 242, 242))

                btn_repor = QPushButton("Atualizar")
                btn_repor.setObjectName("actionButton")
                btn_repor.setMinimumWidth(140)
                btn_repor.setCursor(Qt.PointingHandCursor)
                btn_repor.clicked.connect(lambda checked=False, produto_id=p.id: self.abrir_dialogo_reposicao(produto_id))

                action_container = QFrame()
                action_container.setObjectName("actionContainer")
                action_layout = QHBoxLayout(action_container)
                action_layout.setContentsMargins(0, 0, 0, 0)
                action_layout.setAlignment(Qt.AlignCenter)
                action_layout.addWidget(btn_repor)
                self.tabela.setCellWidget(row, 6, action_container)
            else:
                self.tabela.setCellWidget(row, 6, None)

        self.lbl_stats.setText(f"Total de Produtos: {len(produtos)} | Itens em Estoque: {total_itens} | ⚠️ Baixo Estoque: {baixo_estoque}")

        if low_alert_ids:
            preview = ", ".join(low_stock_preview)
            sufixo = "..." if len(low_alert_ids) > len(low_stock_preview) else ""
            detalhe = f" ({preview}{sufixo})" if preview else ""
            self.lbl_low_stock_banner.setText(
                f"⚠️ Estoque baixo: {len(low_alert_ids)} item(ns) abaixo do mínimo{detalhe}. "
                "Use o botão 'Atualizar' na coluna Ações para repor."
            )
            self.lbl_low_stock_banner.setVisible(True)
        else:
            self.lbl_low_stock_banner.setVisible(False)

    def adicionar_produto(self):
        dialog = ProdutoDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["nome"]:
                QMessageBox.warning(self, "Erro", "O nome do produto é obrigatório.")
                return

            sucesso, msg = self.service.adicionar(**data)
            if sucesso:
                self.atualizar_tabela()
            else:
                QMessageBox.critical(self, "Erro", msg)

    def editar_produto(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um produto para editar.")
            return

        id_produto = int(self.tabela.item(row, 0).text())
        produto = self.service.buscar_por_id(id_produto)
        
        dialog = ProdutoDialog(self, produto)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            sucesso, msg = self.service.atualizar(id_produto, **data)
            if sucesso:
                self.atualizar_tabela()
            else:
                QMessageBox.critical(self, "Erro", msg)

    def remover_produto(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um produto para remover.")
            return

        id_produto = int(self.tabela.item(row, 0).text())
        nome_produto = self.tabela.item(row, 1).text()

        confirm = QMessageBox.question(
            self, "Confirmação", f"Deseja realmente remover '{nome_produto}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            sucesso, msg = self.service.deletar(id_produto)
            if sucesso:
                self.atualizar_tabela()
            else:
                QMessageBox.critical(self, "Erro", msg)

    def imprimir_relatorio_estoque(self):
        """Gera relatório institucional de estoque com logo para impressão/PDF."""
        produtos = self.service.get_todos()
        if not produtos:
            QMessageBox.warning(self, "Aviso", "Não há produtos cadastrados para imprimir.")
            return

        s = load_settings()
        observacao_padrao = s.get("relatorio_observacao", "")
        header_html = build_report_header_html(
            report_title="Relatorio de Estoque",
            period_label="Posicao atual de produtos",
            emitted_at=datetime.now(),
            settings=s
        )

        total_itens = 0
        rows_html = ""
        for i, p in enumerate(produtos):
            total_itens += p.quantidade
            zebra_class = "zebra" if i % 2 == 0 else ""
            status = "Baixo Estoque" if p.quantidade <= p.estoque_minimo else "OK"
            status_class = "text-red" if status != "OK" else "text-green"
            rows_html += f"""
                <tr class='{zebra_class}'>
                    <td style='text-align: center;'>{p.codigo}</td>
                    <td>{p.nome}</td>
                    <td style='text-align: right;'>R$ {p.preco:.2f}</td>
                    <td style='text-align: center;'>{p.quantidade}</td>
                    <td style='text-align: center;'>{p.estoque_minimo}</td>
                    <td style='text-align: center;' class='{status_class}'><b>{status}</b></td>
                </tr>
            """

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
                .summary {{
                    margin-top: 20px;
                    font-size: 12px;
                    color: #0F172A;
                    font-weight: 600;
                }}
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
                        <th style='text-align: center;'>Código</th>
                        <th>Produto</th>
                        <th style='text-align: right;'>Preço</th>
                        <th style='text-align: center;'>Qtd. Atual</th>
                        <th style='text-align: center;'>Qtd. Mínima</th>
                        <th style='text-align: center;'>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            <div class='summary'>Total de itens em estoque: {total_itens}</div>
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
            doc.setPageSize(printer.pageRect(QPrinter.Point).size())
            doc.setHtml(html)
            doc.print_(printer)

    def abrir_dialogo_reposicao(self, produto_id: int):
        """Abre o diálogo de reposição de estoque para o produto indicado."""
        produto = self.service.buscar_por_id(produto_id)
        if not produto:
            QMessageBox.warning(self, "Aviso", "Produto não encontrado.")
            return

        dialog = ReposicaoEstoqueDialog(self, produto)
        if dialog.exec() == QDialog.Accepted:
            nova_qtd = dialog.get_nova_quantidade()
            sucesso, msg = self.service.atualizar(produto_id, quantidade=nova_qtd)
            if sucesso:
                self.atualizar_tabela()
            else:
                QMessageBox.critical(self, "Erro", msg)
