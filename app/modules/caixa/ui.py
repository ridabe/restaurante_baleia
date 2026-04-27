from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QComboBox, QSpinBox, QGroupBox, QFrame, QCompleter
)
from PySide6.QtCore import Qt, QStringListModel, QSizeF
from PySide6.QtGui import QTextDocument, QPageSize, QFont
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from datetime import datetime
from app.core.config import load_settings
from app.core.branding import build_ticket_header_html
from app.ui.styles import ThemeManager
from app.modules.caixa.service import CaixaService
from app.modules.estoque.service import EstoqueService
from app.modules.fiado.service import FiadoService

class CaixaWidget(QWidget):
    """Interface do Ponto de Venda (Caixa) Refatorada."""
    def __init__(self):
        super().__init__()
        self.caixa_service = CaixaService()
        self.estoque_service = EstoqueService()
        self.fiado_service = FiadoService()
        
        self.pedido_atual = [] # Lista de itens no pedido [{'produto': obj, 'qtd': int}]
        self.venda_confirmada = False
        self.init_ui()
        self.atualizar_busca_produtos()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        # ==========================================
        # COLUNA ESQUERDA: MONTAGEM DO PEDIDO
        # ==========================================
        esquerda_layout = QVBoxLayout()
        
        # 1. Busca Inteligente (Card)
        busca_group = QGroupBox("Adicionar Itens ao Pedido")
        busca_layout = QVBoxLayout(busca_group)
        busca_layout.setSpacing(15)
        
        lbl_instrucao = QLabel("Busque por Nome ou Código:")
        lbl_instrucao.setObjectName("mutedLabel")
        busca_layout.addWidget(lbl_instrucao)

        self.produto_busca = QComboBox()
        self.produto_busca.setEditable(True)
        self.produto_busca.setMinimumHeight(45)
        self.produto_busca.setInsertPolicy(QComboBox.NoInsert)
        self.produto_busca.setPlaceholderText("Digite o Nome ou Código do Produto...")
        
        # Ajuste no Completer para melhor busca
        self.produto_busca.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.produto_busca.completer().setFilterMode(Qt.MatchContains)
        self.produto_busca.lineEdit().returnPressed.connect(self.adicionar_item_pedido)
        busca_layout.addWidget(self.produto_busca)
        
        qtd_btn_layout = QHBoxLayout()
        self.qtd_spin = QSpinBox()
        self.qtd_spin.setRange(1, 1000)
        self.qtd_spin.setMinimumHeight(45)
        self.qtd_spin.setMinimumWidth(100)
        
        self.btn_add = QPushButton("  + ADICIONAR ITEM")
        self.btn_add.setObjectName("actionButton")
        self.btn_add.setMinimumHeight(45)
        self.btn_add.clicked.connect(self.adicionar_item_pedido)
        
        qtd_btn_layout.addWidget(QLabel("Qtd:"))
        qtd_btn_layout.addWidget(self.qtd_spin)
        qtd_btn_layout.addWidget(self.btn_add, 1)
        
        busca_layout.addLayout(qtd_btn_layout)
        esquerda_layout.addWidget(busca_group)

        # 2. Tabela de Pedido Atual (Card)
        pedido_group = QGroupBox("Pedido Atual (Itens Selecionados)")
        pedido_layout = QVBoxLayout(pedido_group)

        self.tabela_pedido = QTableWidget()
        self.tabela_pedido.setColumnCount(5)
        self.tabela_pedido.setHorizontalHeaderLabels(["Cód", "Produto", "Qtd", "Unitário", "Subtotal"])
        self.tabela_pedido.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela_pedido.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela_pedido.setAlternatingRowColors(True)
        pedido_layout.addWidget(self.tabela_pedido)

        self.btn_remover = QPushButton("Remover Item Selecionado")
        self.btn_remover.setObjectName("secondaryButton")
        self.btn_remover.clicked.connect(self.remover_item_pedido)
        pedido_layout.addWidget(self.btn_remover)
        
        esquerda_layout.addWidget(pedido_group)
        main_layout.addLayout(esquerda_layout, 2)

        # ==========================================
        # COLUNA DIREITA: TOTAL, PAGAMENTO E TICKET
        # ==========================================
        direita_layout = QVBoxLayout()
        
        # 1. Card de Resumo e Pagamento
        resumo_group = QGroupBox("Finalização")
        resumo_layout = QVBoxLayout(resumo_group)
        resumo_layout.setSpacing(15)
        
        self.lbl_total = QLabel("R$ 0.00")
        self.lbl_total.setObjectName("caixaTotalValue")
        self.lbl_total.setAlignment(Qt.AlignCenter)
        resumo_layout.addWidget(self.lbl_total)
        
        resumo_layout.addWidget(QLabel("Forma de Pagamento:"))
        self.combo_pagamento = QComboBox()
        self.combo_pagamento.addItems(["Dinheiro", "Cartão", "Pix", "FIADO"])
        self.combo_pagamento.currentIndexChanged.connect(self.on_pagamento_changed)
        resumo_layout.addWidget(self.combo_pagamento)

        self.lbl_cliente = QLabel("Cliente (Opcional):")
        self.combo_cliente = QComboBox()
        self.atualizar_combo_clientes()
        resumo_layout.addWidget(self.lbl_cliente)
        cliente_layout = QHBoxLayout()
        cliente_layout.setSpacing(10)

        self.btn_refresh_clientes = QPushButton("↻")
        self.btn_refresh_clientes.setObjectName("secondaryButton")
        self.btn_refresh_clientes.setMinimumSize(44, 44)
        self.btn_refresh_clientes.setToolTip("Atualizar lista de clientes")
        self.btn_refresh_clientes.clicked.connect(self.atualizar_combo_clientes)

        cliente_layout.addWidget(self.combo_cliente, 1)
        cliente_layout.addWidget(self.btn_refresh_clientes)
        resumo_layout.addLayout(cliente_layout)

        btn_layout = QHBoxLayout()
        self.btn_limpar = QPushButton("Limpar")
        self.btn_limpar.setObjectName("secondaryButton")
        self.btn_limpar.clicked.connect(self.limpar_pedido)
        
        self.btn_confirmar = QPushButton("GERAR PRÉVIA")
        self.btn_confirmar.setObjectName("actionButton")
        self.btn_confirmar.clicked.connect(self.confirmar_pedido)
        
        btn_layout.addWidget(self.btn_limpar)
        btn_layout.addWidget(self.btn_confirmar, 2)
        resumo_layout.addLayout(btn_layout)
        
        direita_layout.addWidget(resumo_group)

        # 2. Prévia do Ticket (Visual)
        ticket_group = QGroupBox("Prévia do Ticket")
        ticket_layout = QVBoxLayout(ticket_group)
        
        self.ticket_view = QLabel("Aguardando confirmação...")
        self.ticket_view.setObjectName("ticketPreview")
        self.ticket_view.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.ticket_view.setWordWrap(True)
        self.ticket_view.setMinimumHeight(250)
        ticket_layout.addWidget(self.ticket_view)
        
        self.btn_receber = QPushButton("FINALIZAR VENDA")
        self.btn_receber.setObjectName("primaryButton")
        self.btn_receber.setEnabled(False)
        self.btn_receber.clicked.connect(self.receber_pagamento)
        ticket_layout.addWidget(self.btn_receber)

        direita_layout.addWidget(ticket_group)
        main_layout.addLayout(direita_layout, 1)

    def atualizar_busca_produtos(self):
        """Preenche o combo de busca com Nome e Código."""
        self.produto_busca.clear()
        self.produto_busca.addItem("--- Selecione ou Digite ---", None)
        produtos = self.estoque_service.get_todos()
        for p in produtos:
            if p.quantidade > 0:
                texto = f"{p.codigo} - {p.nome} (R$ {p.preco:.2f})"
                self.produto_busca.addItem(texto, p)

    def atualizar_combo_clientes(self):
        """Atualiza a lista de clientes."""
        self.combo_cliente.clear()
        self.combo_cliente.addItem("Não informado", None)
        clientes = self.fiado_service.get_todos_clientes()
        for c in clientes:
            self.combo_cliente.addItem(c.nome, c)

    def on_pagamento_changed(self, index):
        """Obriga seleção de cliente se for FIADO."""
        metodo = self.combo_pagamento.currentText()
        is_fiado = metodo == "FIADO"
        self.lbl_cliente.setText("Cliente (Obrigatório):" if is_fiado else "Cliente (Opcional):")
        if is_fiado:
            self.atualizar_combo_clientes()

    def adicionar_item_pedido(self):
        """Adiciona o produto selecionado à lista temporária."""
        if self.venda_confirmada:
            QMessageBox.warning(self, "Aviso", "Venda já confirmada. Finalize ou limpe o pedido.")
            return

        # Busca o produto pelo índice atual do combo ou tenta achar pelo texto digitado
        produto = self.produto_busca.currentData()
        
        # Fallback: Se não selecionou da lista, tenta buscar pelo código ou nome exato
        if not produto:
            texto_busca = self.produto_busca.currentText().strip()
            if not texto_busca: return
            
            produtos = self.estoque_service.get_todos()
            for p in produtos:
                if p.codigo == texto_busca or p.nome.lower() == texto_busca.lower():
                    produto = p
                    break
        
        if not produto:
            QMessageBox.warning(self, "Erro", "Produto não encontrado. Selecione um item da lista ou digite o código exato.")
            return
        
        qtd = self.qtd_spin.value()
        if qtd > produto.quantidade:
            QMessageBox.warning(self, "Estoque Insuficiente", f"Apenas {produto.quantidade} unidades de '{produto.nome}' disponíveis.")
            return

        # Verifica se já está no pedido
        for item in self.pedido_atual:
            if item['produto'].id == produto.id:
                item['qtd'] += qtd
                self.atualizar_tabela_pedido()
                self.produto_busca.setCurrentIndex(0)
                return

        # Adiciona novo item
        self.pedido_atual.append({'produto': produto, 'qtd': qtd})
        self.atualizar_tabela_pedido()
        self.produto_busca.setCurrentIndex(0)

    def remover_item_pedido(self):
        if self.venda_confirmada: return
        row = self.tabela_pedido.currentRow()
        if row >= 0:
            self.pedido_atual.pop(row)
            self.atualizar_tabela_pedido()

    def atualizar_tabela_pedido(self):
        """Atualiza a visualização e o total."""
        self.tabela_pedido.setRowCount(len(self.pedido_atual))
        total = 0.0
        
        for row, item in enumerate(self.pedido_atual):
            p = item['produto']
            subtotal = item['qtd'] * p.preco
            total += subtotal
            
            self.tabela_pedido.setItem(row, 0, QTableWidgetItem(p.codigo))
            self.tabela_pedido.setItem(row, 1, QTableWidgetItem(p.nome))
            self.tabela_pedido.setItem(row, 2, QTableWidgetItem(str(item['qtd'])))
            self.tabela_pedido.setItem(row, 3, QTableWidgetItem(f"R$ {p.preco:.2f}"))
            self.tabela_pedido.setItem(row, 4, QTableWidgetItem(f"R$ {subtotal:.2f}"))
            
        self.lbl_total.setText(f"R$ {total:.2f}")

    def confirmar_pedido(self):
        """Gera a prévia do ticket e habilita o recebimento."""
        if not self.pedido_atual:
            QMessageBox.warning(self, "Pedido Vazio", "Adicione itens antes de confirmar.")
            return

        metodo = self.combo_pagamento.currentText()
        cliente_obj = self.combo_cliente.currentData()
        
        if metodo == "FIADO" and not cliente_obj:
            QMessageBox.warning(self, "Erro", "Selecione um cliente para venda FIADA.")
            return

        self.venda_confirmada = True
        self.btn_confirmar.setEnabled(False)
        self.btn_receber.setEnabled(True)
        self.gerar_preview_ticket()

    def _build_ticket_html(self, include_preview_note: bool, *, for_print: bool) -> str:
        """Monta o HTML do ticket (prévia ou final) com dados dinâmicos da empresa."""
        s = load_settings()
        cfg = ThemeManager.normalize_settings(s)
        preview_scale = cfg["scale"] * (1.15 if cfg["accessibility"] else 1.0)
        body_px = 13 if for_print else int(round(13 * preview_scale))
        total_px = 16 if for_print else int(round(16 * preview_scale))
        note_px = 11 if for_print else int(round(12 * preview_scale))
        rodape = s.get("ticket_rodape", "Obrigado pela preferência!")

        nome_cliente = self.combo_cliente.currentText()
        total = self.lbl_total.text()
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

        if for_print:
            ticket = f"<div style=\"font-family:'Courier New'; font-size:{body_px}px; color:#92400E;\">"
        else:
            ticket = f"<div style=\"font-family:'Courier New'; font-size:{body_px}px;\">"
        ticket += build_ticket_header_html(settings=s)
        if include_preview_note:
            if for_print:
                ticket += (
                    "<div style='background-color:#DBEAFE; color:#1E40AF; "
                    f"padding:6px 8px; margin: 0 0 10px 0; border-radius:6px; font-size:{note_px}px;'>"
                    "<b>Prévia do ticket:</b> a venda ainda não foi registrada. "
                    "Clique em <b>FINALIZAR VENDA</b> para concluir."
                    "</div>"
                )
            else:
                ticket += (
                    f"<div style='padding:6px 8px; margin: 0 0 10px 0; border-radius:6px; font-size:{note_px}px;'>"
                    "<b>Prévia do ticket:</b> a venda ainda não foi registrada. "
                    "Clique em <b>FINALIZAR VENDA</b> para concluir."
                    "</div>"
                )
        ticket += f"Data: {data_hora}<br>"
        ticket += f"Cliente: {nome_cliente}<br>"
        ticket += "-" * 35 + "<br>"

        for item in self.pedido_atual:
            p = item["produto"]
            sub = item["qtd"] * p.preco
            ticket += f"<b>{p.codigo} - {p.nome}</b><br>"
            ticket += f"   {item['qtd']} x R$ {p.preco:.2f} = R$ {sub:.2f}<br>"

        ticket += "-" * 35 + "<br>"
        ticket += f"<div style='text-align: right; font-size:{total_px}px;'><b>TOTAL: {total}</b></div><br>"
        ticket += "<div style='text-align: center; font-size: 11px; margin-top: 10px;'>"
        ticket += f"<i>{rodape}</i><br>"
        ticket += "DOCUMENTO NÃO FISCAL</div>"
        ticket += "</div>"
        return ticket

    def gerar_preview_ticket(self):
        """Monta o visual do ticket em HTML com dados dinâmicos da empresa."""
        self.ticket_view.setText(self._build_ticket_html(include_preview_note=True, for_print=False))

    def imprimir_ticket(self, ticket_html: str) -> bool:
        """Abre o diálogo de impressão e imprime o ticket com o mesmo layout do HTML."""
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPageSize(QSizeF(80, 297), QPageSize.Unit.Millimeter))
        printer.setFullPage(True)

        dialog = QPrintDialog(printer, self)
        if dialog.exec() != QPrintDialog.Accepted:
            return False

        doc = QTextDocument()
        doc.setDefaultFont(QFont("Courier New", 10))
        doc.setPageSize(printer.pageRect(QPrinter.Point).size())
        doc.setHtml(ticket_html)
        doc.print_(printer)
        return True

    def receber_pagamento(self):
        """Efetivamente persiste a venda no banco de dados."""
        metodo = self.combo_pagamento.currentText()
        cliente_obj = self.combo_cliente.currentData()
        
        itens_para_servico = []
        for item in self.pedido_atual:
            itens_para_servico.append({
                'produto_id': item['produto'].id,
                'quantidade': item['qtd'],
                'preco': item['produto'].preco
            })

        sucesso, msg, venda_id = self.caixa_service.registrar_venda(
            itens_venda=itens_para_servico,
            metodo_pagamento=metodo,
            cliente_id=cliente_obj.id if cliente_obj else None,
            cliente_nome=cliente_obj.nome if cliente_obj else "Não informado"
        )

        if sucesso:
            ticket_final_html = self._build_ticket_html(include_preview_note=False, for_print=True)
            reply = QMessageBox.question(
                self,
                "Imprimir Ticket",
                "Venda registrada. Deseja imprimir o ticket?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.imprimir_ticket(ticket_final_html)
            QMessageBox.information(self, "Sucesso", f"Venda registrada com sucesso!{f' (Venda #{venda_id})' if venda_id else ''}")
            self.limpar_pedido()
        else:
            QMessageBox.critical(self, "Erro", msg)

    def limpar_pedido(self):
        """Reseta o estado do caixa para um novo pedido."""
        self.pedido_atual = []
        self.venda_confirmada = False
        self.btn_confirmar.setEnabled(True)
        self.btn_receber.setEnabled(False)
        self.atualizar_tabela_pedido()
        self.atualizar_busca_produtos()
        self.ticket_view.setText("Aguardando confirmação...")
        self.produto_busca.setCurrentIndex(0)
        self.qtd_spin.setValue(1)
