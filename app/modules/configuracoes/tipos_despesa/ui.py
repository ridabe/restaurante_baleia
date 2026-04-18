from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QFormLayout, 
    QDialog, QTextEdit, QFrame, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from app.modules.configuracoes.tipos_despesa.service import TipoDespesaService

class TipoDespesaDialog(QDialog):
    """Diálogo para cadastrar ou editar um tipo de despesa."""
    def __init__(self, parent=None, tipo=None):
        super().__init__(parent)
        self.tipo = tipo
        self.setWindowTitle("Novo Tipo de Despesa" if not tipo else f"Editar: {tipo.nome}")
        self.setMinimumSize(450, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Informações da Categoria")
        title.setObjectName("headerTitle")
        layout.addWidget(title)

        form_container = QFrame()
        form_layout = QFormLayout(form_container)
        form_layout.setSpacing(15)

        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Ex: Fornecedor de Bebidas")
        self.nome_input.setMinimumHeight(40)
        
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Descrição opcional sobre este tipo de gasto...")
        self.desc_input.setMaximumHeight(100)
        
        self.ativo_check = QCheckBox("Categoria Ativa")
        self.ativo_check.setChecked(True)

        if self.tipo:
            self.nome_input.setText(self.tipo.nome)
            self.desc_input.setText(self.tipo.descricao or "")
            self.ativo_check.setChecked(self.tipo.ativo == 1)

        form_layout.addRow("Nome:", self.nome_input)
        form_layout.addRow("Descrição:", self.desc_input)
        form_layout.addRow("", self.ativo_check)

        layout.addWidget(form_container)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("secondaryButton")
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("Salvar")
        btn_save.setObjectName("primaryButton")
        btn_save.clicked.connect(self.accept)
        
        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(btn_save)
        
        layout.addLayout(buttons_layout)

    def get_data(self):
        return {
            "nome": self.nome_input.text(),
            "descricao": self.desc_input.toPlainText(),
            "ativo": self.ativo_check.isChecked()
        }

class TiposDespesaWidget(QWidget):
    """Interface para gerenciamento de tipos de despesas."""
    def __init__(self):
        super().__init__()
        self.service = TipoDespesaService()
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
        header_label = QLabel("Categorias de Despesas")
        header_label.setObjectName("moduleTitle")
        title_layout.addWidget(header_label)
        
        self.lbl_stats = QLabel("Gerencie os tipos de gastos do seu negócio")
        self.lbl_stats.setStyleSheet("color: #64748B; font-size: 12px;")
        title_layout.addWidget(self.lbl_stats)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        # Busca
        self.busca_input = QLineEdit()
        self.busca_input.setPlaceholderText("🔍 Buscar categoria...")
        self.busca_input.setFixedWidth(250)
        self.busca_input.setMinimumHeight(40)
        self.busca_input.textChanged.connect(self.filtrar_tabela)
        header_layout.addWidget(self.busca_input)

        self.btn_novo = QPushButton("+ Novo Tipo")
        self.btn_novo.setObjectName("primaryButton")
        self.btn_novo.setMinimumHeight(40)
        self.btn_novo.clicked.connect(self.novo_tipo)
        header_layout.addWidget(self.btn_novo)

        layout.addWidget(header_container)

        # Tabela
        tabela_container = QFrame()
        tabela_container.setObjectName("cardFrame")
        tabela_layout = QVBoxLayout(tabela_container)
        tabela_layout.setContentsMargins(15, 15, 15, 15)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Descrição", "Status", "Ações"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.tabela.setColumnWidth(4, 250)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.verticalHeader().setDefaultSectionSize(50)
        
        tabela_layout.addWidget(self.tabela)
        layout.addWidget(tabela_container)

    def atualizar_tabela(self):
        tipos = self.service.get_todos()
        self.tabela.setRowCount(len(tipos))
        
        for row, t in enumerate(tipos):
            self.tabela.setItem(row, 0, QTableWidgetItem(str(t.id)))
            self.tabela.setItem(row, 1, QTableWidgetItem(t.nome))
            self.tabela.setItem(row, 2, QTableWidgetItem(t.descricao or "---"))
            
            status_item = QTableWidgetItem("Ativo" if t.ativo == 1 else "Inativo")
            status_item.setTextAlignment(Qt.AlignCenter)
            if t.ativo == 0:
                status_item.setForeground(Qt.red)
            else:
                status_item.setForeground(QColor(22, 163, 74))
            self.tabela.setItem(row, 3, status_item)

            # Ações
            container = QFrame()
            container.setObjectName("actionContainer")
            container.setStyleSheet("QFrame#actionContainer { background: transparent; border: none; }")
            h_layout = QHBoxLayout(container)
            h_layout.setContentsMargins(10, 5, 10, 5)
            h_layout.setSpacing(10)
            
            btn_edit = QPushButton("Editar")
            btn_edit.setObjectName("actionButton")
            btn_edit.setMinimumHeight(30)
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.clicked.connect(lambda checked=False, item=t: self.editar_tipo(item))
            
            btn_del = QPushButton("Excluir" if t.ativo == 1 else "Reativar")
            btn_del.setObjectName("dangerButton" if t.ativo == 1 else "primaryButton")
            btn_del.setMinimumHeight(30)
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.clicked.connect(lambda checked=False, item=t: self.remover_tipo(item))
            
            h_layout.addWidget(btn_edit)
            h_layout.addWidget(btn_del)
            self.tabela.setCellWidget(row, 4, container)

    def filtrar_tabela(self, texto):
        texto = texto.lower()
        for row in range(self.tabela.rowCount()):
            nome = self.tabela.item(row, 1).text().lower()
            desc = self.tabela.item(row, 2).text().lower()
            self.tabela.setRowHidden(row, not (texto in nome or texto in desc))

    def novo_tipo(self):
        dialog = TipoDespesaDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            sucesso, msg = self.service.cadastrar(**data)
            if sucesso:
                self.atualizar_tabela()
                QMessageBox.information(self, "Sucesso", msg)
            else:
                QMessageBox.critical(self, "Erro", msg)

    def editar_tipo(self, tipo):
        dialog = TipoDespesaDialog(self, tipo)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            sucesso, msg = self.service.atualizar(tipo.id, **data)
            if sucesso:
                self.atualizar_tabela()
                QMessageBox.information(self, "Sucesso", msg)
            else:
                QMessageBox.critical(self, "Erro", msg)

    def remover_tipo(self, tipo):
        if tipo.ativo == 1:
            confirm = QMessageBox.question(
                self, "Confirmar Exclusão", 
                f"Deseja realmente excluir '{tipo.nome}'?\n\nNota: Se houver movimentações, ele será apenas inativado.",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                sucesso, msg = self.service.deletar(tipo.id)
                if sucesso:
                    self.atualizar_tabela()
                    QMessageBox.information(self, "Ação Realizada", msg)
                else:
                    QMessageBox.critical(self, "Erro", msg)
        else:
            # Reativar
            sucesso, msg = self.service.atualizar(tipo.id, tipo.nome, tipo.descricao, True)
            if sucesso:
                self.atualizar_tabela()
                QMessageBox.information(self, "Sucesso", "Categoria reativada com sucesso!")
            else:
                QMessageBox.critical(self, "Erro", msg)
