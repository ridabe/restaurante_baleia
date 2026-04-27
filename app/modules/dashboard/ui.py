from __future__ import annotations

import html
import os
import shutil
import tempfile
import traceback
from datetime import datetime

from PySide6.QtCharts import (
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QChartView,
    QHorizontalBarSeries,
    QValueAxis,
)
from PySide6.QtCore import Qt, Signal, QMarginsF
from PySide6.QtGui import QColor, QPainter, QPageLayout, QPageSize, QTextDocument, QFont
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
    QFileDialog,
    QMessageBox,
)

from app.modules.dashboard.components import MetricCard, SectionFrame
from app.modules.dashboard.service import DashboardService
from app.core.branding import build_report_header_html
from app.core.resources import app_data_path


class DashboardWidget(QWidget):
    """Dashboard gerencial principal com KPIs, gráficos e blocos operacionais."""

    navigateRequested = Signal(str, int)

    def __init__(self):
        super().__init__()
        self.service = DashboardService()
        self._last_snapshot = None
        self._build_ui()
        self.atualizar_dados()

    def _build_ui(self):
        """Monta a interface enterprise do dashboard com blocos e hierarquia visual."""
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        root_layout.addWidget(scroll)

        container = QWidget()
        self.main_layout = QVBoxLayout(container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(14)
        scroll.setWidget(container)

        self._build_header()
        self._build_kpis()
        self._build_charts_row()
        self._build_operacao_row()
        self._build_fiado_row()

    def _build_header(self):
        """Cria o cabeçalho com título, filtro de período e ação de atualização."""
        header = QFrame()
        header.setObjectName("cardFrame")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)

        title = QLabel("Dashboard Gerencial")
        title.setObjectName("headerTitle")
        layout.addWidget(title)

        layout.addStretch()

        layout.addWidget(QLabel("Período:"))
        self.combo_periodo = QComboBox()
        self.combo_periodo.addItem("Hoje", 1)
        self.combo_periodo.addItem("Últimos 7 dias", 7)
        self.combo_periodo.addItem("Últimos 30 dias", 30)
        self.combo_periodo.setCurrentIndex(1)
        self.combo_periodo.setMinimumWidth(170)
        self.combo_periodo.currentIndexChanged.connect(self.atualizar_dados)
        layout.addWidget(self.combo_periodo)

        self.btn_refresh = QPushButton("Atualizar")
        self.btn_refresh.setObjectName("actionButton")
        self.btn_refresh.clicked.connect(self.atualizar_dados)
        layout.addWidget(self.btn_refresh)

        self.btn_export = QPushButton("Exportar PDF")
        self.btn_export.setObjectName("secondaryButton")
        self.btn_export.clicked.connect(self.exportar_pdf)
        layout.addWidget(self.btn_export)

        self.lbl_updated = QLabel("Atualização: --:--")
        self.lbl_updated.setObjectName("mutedLabel")
        layout.addWidget(self.lbl_updated)

        self.main_layout.addWidget(header)

    def _build_kpis(self):
        """Cria os cards de indicadores rápidos financeiros e operacionais."""
        kpi_container = QWidget()
        grid = QGridLayout(kpi_container)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)

        self.card_entradas = MetricCard("Entradas do Dia", "#16A34A")
        self.card_saidas = MetricCard("Saídas do Dia", "#EF4444")
        self.card_saldo = MetricCard("Saldo do Dia", "#0EA5E9")
        self.card_fiado_total = MetricCard("Total em Fiado", "#F59E0B")
        self.card_fiado_clientes = MetricCard("Clientes com Fiado", "#6366F1")
        self.card_caixa_status = MetricCard("Status do Caixa", "#14B8A6")

        self.card_entradas.clicked.connect(lambda: self.navigateRequested.emit("fluxo_caixa", 1))
        self.card_saidas.clicked.connect(lambda: self.navigateRequested.emit("fluxo_caixa", 1))
        self.card_saldo.clicked.connect(lambda: self.navigateRequested.emit("fluxo_caixa", 1))
        self.card_fiado_total.clicked.connect(lambda: self.navigateRequested.emit("fiado", 30))
        self.card_fiado_clientes.clicked.connect(lambda: self.navigateRequested.emit("fiado", 30))
        self.card_caixa_status.clicked.connect(lambda: self.navigateRequested.emit("fluxo_caixa", 7))

        cards = [
            self.card_entradas,
            self.card_saidas,
            self.card_saldo,
            self.card_fiado_total,
            self.card_fiado_clientes,
            self.card_caixa_status,
        ]

        for idx, card in enumerate(cards):
            row = idx // 3
            col = idx % 3
            grid.addWidget(card, row, col)

        self.main_layout.addWidget(kpi_container)

    def _build_charts_row(self):
        """Cria a linha de gráficos: tendência financeira e despesas por categoria."""
        row = QHBoxLayout()
        row.setSpacing(12)

        self.section_financeiro = SectionFrame("Entradas x Saídas")
        self.chart_financeiro = QChartView()
        self.chart_financeiro.setRenderHint(QPainter.Antialiasing)
        self.chart_financeiro.setMinimumHeight(300)
        self.section_financeiro.content_layout.addWidget(self.chart_financeiro)
        row.addWidget(self.section_financeiro, 2)

        self.section_despesas = SectionFrame("Despesas por Categoria")
        self.chart_despesas = QChartView()
        self.chart_despesas.setRenderHint(QPainter.Antialiasing)
        self.chart_despesas.setMinimumHeight(300)
        self.section_despesas.content_layout.addWidget(self.chart_despesas)
        row.addWidget(self.section_despesas, 2)

        self.main_layout.addLayout(row)

    def _build_operacao_row(self):
        """Cria a linha operacional com top produtos e alertas de estoque baixo."""
        row = QHBoxLayout()
        row.setSpacing(12)

        self.section_top_produtos = SectionFrame("Produtos Mais Vendidos")
        self.table_top_produtos = QTableWidget()
        self._setup_table(
            self.table_top_produtos,
            ["Produto", "Qtd.", "Total Vendido"],
            stretch_description=False,
        )
        self.section_top_produtos.content_layout.addWidget(self.table_top_produtos)
        row.addWidget(self.section_top_produtos, 2)

        self.section_estoque = SectionFrame("Alertas de Estoque Baixo")
        self.table_estoque = QTableWidget()
        self._setup_table(
            self.table_estoque,
            ["Produto", "Atual", "Mínimo"],
            stretch_description=False,
        )
        self.section_estoque.content_layout.addWidget(self.table_estoque)
        row.addWidget(self.section_estoque, 2)

        self.main_layout.addLayout(row)

    def _build_fiado_row(self):
        """Cria a linha de gestão de fiado e últimas movimentações financeiras."""
        row = QHBoxLayout()
        row.setSpacing(12)

        self.section_fiado = SectionFrame("Gestão de Fiado")
        self.lbl_fiado_resumo = QLabel("Total a receber: R$ 0,00 | Devedores: 0")
        self.lbl_fiado_resumo.setObjectName("textSecondaryLabel")
        self.section_fiado.content_layout.addWidget(self.lbl_fiado_resumo)
        self.table_fiado = QTableWidget()
        self._setup_table(
            self.table_fiado,
            ["Cliente", "Telefone", "Dívida"],
            stretch_description=False,
        )
        self.section_fiado.content_layout.addWidget(self.table_fiado)
        row.addWidget(self.section_fiado, 2)

        self.section_recentes = SectionFrame("Últimas Movimentações")
        self.table_recentes = QTableWidget()
        self._setup_table(
            self.table_recentes,
            ["Data/Hora", "Tipo", "Descrição", "Valor"],
            stretch_description=True,
            description_col=2,
        )
        self.section_recentes.content_layout.addWidget(self.table_recentes)
        row.addWidget(self.section_recentes, 3)

        self.main_layout.addLayout(row)

    def _setup_table(
        self,
        table: QTableWidget,
        headers: list[str],
        stretch_description: bool,
        description_col: int = 0,
    ):
        """Aplica padrão visual de tabela e configuração de colunas para legibilidade."""
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setMinimumHeight(260)

        header = table.horizontalHeader()
        for i in range(len(headers)):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        if stretch_description:
            header.setSectionResizeMode(description_col, QHeaderView.Stretch)

    def atualizar_dados(self):
        """Atualiza todos os blocos do dashboard conforme período selecionado."""
        period_days = int(self.combo_periodo.currentData() or 7)
        snapshot = self.service.get_snapshot(period_days)
        self._last_snapshot = snapshot

        self._fill_cards(snapshot.get("cards", {}))
        self._fill_financial_chart(snapshot.get("series_financeira", {}))
        self._fill_expenses_chart(snapshot.get("despesas_categoria", []))
        self._fill_top_products(snapshot.get("top_produtos", []))
        self._fill_low_stock(snapshot.get("estoque_baixo", []))
        self._fill_fiado(snapshot.get("fiado", {}))
        self._fill_recent_movements(snapshot.get("movimentacoes_recentes", []))

        updated_at = snapshot.get("updated_at") or datetime.now()
        self.lbl_updated.setText(f"Atualização: {updated_at.strftime('%d/%m %H:%M:%S')}")

    def _fill_cards(self, cards: dict):
        """Preenche os cards de resumo com os valores financeiros e operacionais."""
        entradas = float(cards.get("entradas_dia", 0.0))
        saidas = float(cards.get("saidas_dia", 0.0))
        saldo = float(cards.get("saldo_dia", 0.0))
        entradas_ontem = float(cards.get("entradas_ontem", 0.0))
        saidas_ontem = float(cards.get("saidas_ontem", 0.0))
        saldo_ontem = float(cards.get("saldo_ontem", 0.0))
        fiado_total = float(cards.get("total_fiado", 0.0))
        fiado_qtd = int(cards.get("qtd_clientes_fiado", 0))
        status_caixa = cards.get("status_caixa", {"label": "---", "detalhe": "---"})

        self.card_entradas.set_data(self._money(entradas), self._trend_subtitle(entradas, entradas_ontem, "vs ontem"))
        self.card_saidas.set_data(self._money(saidas), self._trend_subtitle(saidas, saidas_ontem, "vs ontem"))
        self.card_saldo.set_data(self._money(saldo), self._trend_subtitle(saldo, saldo_ontem, "vs ontem"))
        self.card_fiado_total.set_data(self._money(fiado_total), "Total pendente a receber")
        self.card_fiado_clientes.set_data(str(fiado_qtd), "Clientes com dívida em aberto")
        self.card_caixa_status.set_data(status_caixa.get("label", "---"), status_caixa.get("detalhe", ""))

    def _fill_financial_chart(self, series_data: dict):
        """Atualiza o gráfico de tendência de entradas e saídas por período."""
        labels = series_data.get("labels", [])
        entradas = series_data.get("entradas", [])
        saidas = series_data.get("saidas", [])

        chart = QChart()
        chart.setTitle("Tendência Financeira")
        chart.legend().setVisible(True)
        chart.setAnimationOptions(QChart.SeriesAnimations)

        if labels:
            set_entradas = QBarSet("Entradas")
            set_entradas.setColor(QColor("#16A34A"))
            set_saidas = QBarSet("Saídas")
            set_saidas.setColor(QColor("#EF4444"))

            for v in entradas:
                set_entradas.append(float(v))
            for v in saidas:
                set_saidas.append(float(v))

            series = QBarSeries()
            series.append(set_entradas)
            series.append(set_saidas)
            chart.addSeries(series)

            axis_x = QBarCategoryAxis()
            axis_x.append(labels)
            chart.addAxis(axis_x, Qt.AlignBottom)
            series.attachAxis(axis_x)

            max_val = max([*entradas, *saidas, 1.0])
            axis_y = QValueAxis()
            axis_y.setLabelFormat("R$ %.0f")
            axis_y.setRange(0, max_val * 1.2)
            chart.addAxis(axis_y, Qt.AlignLeft)
            series.attachAxis(axis_y)
        else:
            chart.setTitle("Tendência Financeira (sem dados no período)")

        self.chart_financeiro.setChart(chart)

    def _fill_expenses_chart(self, despesas: list[dict]):
        """Atualiza o gráfico de despesas por categoria para análise de custo."""
        chart = QChart()
        chart.setTitle("Despesas por Categoria")
        chart.legend().setVisible(False)
        chart.setAnimationOptions(QChart.SeriesAnimations)

        if despesas:
            set_despesas = QBarSet("Despesas")
            set_despesas.setColor(QColor("#F97316"))
            categorias = []
            max_val = 1.0
            for item in despesas[:8]:
                categorias.append(item["categoria"])
                valor = float(item["valor"])
                set_despesas.append(valor)
                if valor > max_val:
                    max_val = valor

            series = QHorizontalBarSeries()
            series.append(set_despesas)
            chart.addSeries(series)

            axis_y = QBarCategoryAxis()
            axis_y.append(categorias)
            chart.addAxis(axis_y, Qt.AlignLeft)
            series.attachAxis(axis_y)

            axis_x = QValueAxis()
            axis_x.setLabelFormat("R$ %.0f")
            axis_x.setRange(0, max_val * 1.2)
            chart.addAxis(axis_x, Qt.AlignBottom)
            series.attachAxis(axis_x)
        else:
            chart.setTitle("Despesas por Categoria (sem dados no período)")

        self.chart_despesas.setChart(chart)

    def _fill_top_products(self, rows: list[dict]):
        """Preenche o ranking dos produtos mais vendidos no período selecionado."""
        self.table_top_produtos.setRowCount(len(rows))
        for r, row in enumerate(rows):
            self.table_top_produtos.setItem(r, 0, QTableWidgetItem(row["produto"]))
            qtd_item = QTableWidgetItem(str(row["quantidade"]))
            qtd_item.setTextAlignment(Qt.AlignCenter)
            self.table_top_produtos.setItem(r, 1, qtd_item)
            total_item = QTableWidgetItem(self._money(row["total_vendido"]))
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table_top_produtos.setItem(r, 2, total_item)

    def _fill_low_stock(self, rows: list[dict]):
        """Preenche alertas de estoque baixo para ação rápida de reposição."""
        self.table_estoque.setRowCount(len(rows))
        for r, row in enumerate(rows):
            self.table_estoque.setItem(r, 0, QTableWidgetItem(row["produto"]))
            atual_item = QTableWidgetItem(str(row["quantidade_atual"]))
            atual_item.setTextAlignment(Qt.AlignCenter)
            minimo_item = QTableWidgetItem(str(row["estoque_minimo"]))
            minimo_item.setTextAlignment(Qt.AlignCenter)

            self.table_estoque.setItem(r, 1, atual_item)
            self.table_estoque.setItem(r, 2, minimo_item)

            if row["quantidade_atual"] <= row["estoque_minimo"]:
                for c in range(3):
                    item = self.table_estoque.item(r, c)
                    if item:
                        item.setBackground(QColor(254, 242, 242))
                        item.setForeground(QColor(220, 38, 38))

    def _fill_fiado(self, fiado_data: dict):
        """Preenche resumo e ranking de clientes com maior dívida em aberto."""
        total = float(fiado_data.get("total", 0.0))
        qtd = int(fiado_data.get("qtd_clientes", 0))
        self.lbl_fiado_resumo.setText(
            f"Total a receber: {self._money(total)} | Clientes devedores: {qtd}"
        )

        top_rows = fiado_data.get("top_clientes", [])
        self.table_fiado.setRowCount(len(top_rows))
        for r, row in enumerate(top_rows):
            self.table_fiado.setItem(r, 0, QTableWidgetItem(row["nome"]))
            self.table_fiado.setItem(r, 1, QTableWidgetItem(row["telefone"]))
            divida_item = QTableWidgetItem(self._money(row["divida"]))
            divida_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            divida_item.setForeground(QColor("#B45309"))
            self.table_fiado.setItem(r, 2, divida_item)

    def _fill_recent_movements(self, rows: list[dict]):
        """Preenche lista de últimas movimentações para visão operacional imediata."""
        self.table_recentes.setRowCount(len(rows))
        for r, row in enumerate(rows):
            self.table_recentes.setItem(
                r, 0, QTableWidgetItem(row["data"].strftime("%d/%m %H:%M"))
            )
            self.table_recentes.setItem(r, 1, QTableWidgetItem(row["tipo"]))
            desc = row["descricao"]
            desc_item = QTableWidgetItem(desc)
            desc_item.setToolTip(desc)
            self.table_recentes.setItem(r, 2, desc_item)
            value_item = QTableWidgetItem(self._money(row["valor"]))
            value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if row["tipo"] == "Saída":
                value_item.setForeground(QColor("#DC2626"))
            else:
                value_item.setForeground(QColor("#15803D"))
            self.table_recentes.setItem(r, 3, value_item)

    def exportar_pdf(self):
        """Exporta um snapshot do dashboard para PDF (KPIs + tabelas) com cabeçalho institucional."""
        snapshot = self._last_snapshot or self.service.get_snapshot(int(self.combo_periodo.currentData() or 7))
        period_days = int(self.combo_periodo.currentData() or 7)
        period_label = "Hoje" if period_days == 1 else f"Últimos {period_days} dias"

        default_dir = app_data_path("relatorios")
        filename = f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        path, _ = QFileDialog.getSaveFileName(self, "Exportar Dashboard (PDF)", str(default_dir) + "\\" + filename, "PDF (*.pdf)")
        if not path:
            return

        if not path.lower().endswith(".pdf"):
            path += ".pdf"

        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        except Exception:
            QMessageBox.critical(self, "Erro", "Não foi possível criar a pasta de destino para o PDF.")
            return

        try:
            try:
                with open(path, "ab"):
                    pass
            except Exception:
                QMessageBox.critical(self, "Erro", "Não foi possível gravar no caminho selecionado (permissão/arquivo em uso).")
                return

            tmp_dir = os.path.dirname(path) or "."
            fd, tmp_path = tempfile.mkstemp(prefix="dashboard_", suffix=".pdf", dir=tmp_dir)
            os.close(fd)

            html_doc = self._build_dashboard_html(snapshot, period_label)
            printer = QPrinter(QPrinter.HighResolution)
            printer.setPageSize(QPageSize(QPageSize.A4))
            printer.setPageMargins(QMarginsF(12, 12, 12, 12), QPageLayout.Millimeter)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(tmp_path)

            doc = QTextDocument()
            doc.setPageSize(printer.pageRect(QPrinter.Point).size())
            doc.setDefaultFont(QFont("Segoe UI", 10))
            doc.setHtml(html_doc)
            doc.print_(printer)

            if not os.path.exists(tmp_path) or os.path.getsize(tmp_path) < 1024:
                try:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                except Exception:
                    pass
                QMessageBox.critical(
                    self,
                    "Erro",
                    "O PDF não foi gerado. Verifique permissões de pasta e tente novamente em outro local."
                )
                return

            shutil.move(tmp_path, path)
            QMessageBox.information(self, "Exportação concluída", f"PDF gerado em:\n{path}")
        except Exception:
            QMessageBox.critical(self, "Erro ao exportar PDF", traceback.format_exc())

    def _build_dashboard_html(self, snapshot: dict, period_label: str) -> str:
        """Monta HTML do snapshot do dashboard para impressão/exportação."""
        cards = snapshot.get("cards", {})
        fiado = snapshot.get("fiado", {})
        top_produtos = snapshot.get("top_produtos", [])
        estoque_baixo = snapshot.get("estoque_baixo", [])
        recentes = snapshot.get("movimentacoes_recentes", [])

        header_html = build_report_header_html(
            report_title="Dashboard Gerencial (Snapshot)",
            period_label=period_label,
            emitted_at=snapshot.get("updated_at") or datetime.now(),
        )

        def esc(v: str) -> str:
            return html.escape(v or "")

        def money(v: float) -> str:
            return f"R$ {float(v):.2f}"

        kpi_html = f"""
            <table width='100%' cellspacing='8' cellpadding='0' style='border-collapse:separate; margin-top:8px;'>
                <tr>
                    <td width='33%' style='padding:10px; border: 1px solid #E2E8F0; background:#FFFFFF; vertical-align:top;'>
                        <b>Entradas do dia</b><br>{money(cards.get('entradas_dia', 0.0))}
                    </td>
                    <td width='33%' style='padding:10px; border: 1px solid #E2E8F0; background:#FFFFFF; vertical-align:top;'>
                        <b>Saídas do dia</b><br>{money(cards.get('saidas_dia', 0.0))}
                    </td>
                    <td width='33%' style='padding:10px; border: 1px solid #E2E8F0; background:#FFFFFF; vertical-align:top;'>
                        <b>Saldo do dia</b><br>{money(cards.get('saldo_dia', 0.0))}
                    </td>
                </tr>
                <tr>
                    <td width='33%' style='padding:10px; border: 1px solid #E2E8F0; background:#FFFFFF; vertical-align:top;'>
                        <b>Total em fiado</b><br>{money(fiado.get('total', 0.0))}
                    </td>
                    <td width='33%' style='padding:10px; border: 1px solid #E2E8F0; background:#FFFFFF; vertical-align:top;'>
                        <b>Clientes com fiado</b><br>{int(fiado.get('qtd_clientes', 0))}
                    </td>
                    <td width='33%' style='padding:10px; border: 1px solid #E2E8F0; background:#FFFFFF; vertical-align:top;'>
                        <b>Status do caixa</b><br>{esc(cards.get('status_caixa', {}).get('label', '---'))}
                    </td>
                </tr>
            </table>
        """

        def build_rows(items: list[dict], cols: list[tuple[str, str]]):
            trs = []
            for it in items:
                tds = []
                for key, align in cols:
                    val = it.get(key, "")
                    if isinstance(val, float):
                        val = money(val)
                    tds.append(f"<td style='padding:8px 10px; border-bottom:1px solid #F1F5F9; text-align:{align};'>{esc(str(val))}</td>")
                trs.append("<tr>" + "".join(tds) + "</tr>")
            colspan = len(cols)
            return "\n".join(trs) if trs else f"<tr><td colspan='{colspan}' style='padding:10px; color:#64748B;'>Sem dados</td></tr>"

        top_html = f"""
            <h3 style='margin-top:22px; color:#0F172A; font-size:14pt;'>Produtos mais vendidos</h3>
            <table width='100%' cellspacing='0' cellpadding='0' style='border-collapse: collapse;'>
                <tr style='background:#F8FAFC;'>
                    <th style='text-align:left; padding:8px; border-bottom:2px solid #E2E8F0; font-size:10pt;'>Produto</th>
                    <th style='text-align:center; padding:8px; border-bottom:2px solid #E2E8F0; font-size:10pt;'>Qtd</th>
                    <th style='text-align:right; padding:8px; border-bottom:2px solid #E2E8F0; font-size:10pt;'>Total</th>
                </tr>
                {build_rows(top_produtos, [('produto','left'), ('quantidade','center'), ('total_vendido','right')])}
            </table>
        """

        estoque_html = f"""
            <h3 style='margin-top:22px; color:#0F172A; font-size:14pt;'>Estoque baixo</h3>
            <table width='100%' cellspacing='0' cellpadding='0' style='border-collapse: collapse;'>
                <tr style='background:#F8FAFC;'>
                    <th style='text-align:left; padding:8px; border-bottom:2px solid #E2E8F0; font-size:10pt;'>Produto</th>
                    <th style='text-align:center; padding:8px; border-bottom:2px solid #E2E8F0; font-size:10pt;'>Atual</th>
                    <th style='text-align:center; padding:8px; border-bottom:2px solid #E2E8F0; font-size:10pt;'>Mínimo</th>
                </tr>
                {build_rows(estoque_baixo, [('produto','left'), ('quantidade_atual','center'), ('estoque_minimo','center')])}
            </table>
        """

        recentes_slim = []
        for m in recentes[:10]:
            recentes_slim.append(
                {
                    "data": m["data"].strftime("%d/%m %H:%M"),
                    "tipo": m["tipo"],
                    "descricao": m["descricao"],
                    "valor": m["valor"],
                }
            )

        recentes_html = f"""
            <h3 style='margin-top:22px; color:#0F172A; font-size:14pt;'>Últimas movimentações</h3>
            <table width='100%' cellspacing='0' cellpadding='0' style='border-collapse: collapse;'>
                <tr style='background:#F8FAFC;'>
                    <th style='text-align:left; padding:8px; border-bottom:2px solid #E2E8F0; font-size:10pt;'>Data/Hora</th>
                    <th style='text-align:left; padding:8px; border-bottom:2px solid #E2E8F0; font-size:10pt;'>Tipo</th>
                    <th style='text-align:left; padding:8px; border-bottom:2px solid #E2E8F0; font-size:10pt;'>Descrição</th>
                    <th style='text-align:right; padding:8px; border-bottom:2px solid #E2E8F0; font-size:10pt;'>Valor</th>
                </tr>
                {build_rows(recentes_slim, [('data','left'), ('tipo','left'), ('descricao','left'), ('valor','right')])}
            </table>
        """

        return f"""
        <html>
        <head>
            <style>
                @page {{ size: A4; margin: 12mm; }}
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    color: #1E293B;
                    font-size: 10pt;
                    line-height: 1.35;
                }}
                h3 {{ margin: 18px 0 10px 0; }}
            </style>
        </head>
        <body>
            {header_html}
            {kpi_html}
            {top_html}
            {estoque_html}
            {recentes_html}
        </body>
        </html>
        """

    @staticmethod
    def _trend_subtitle(current: float, previous: float, suffix: str) -> str:
        """Gera subtítulo de tendência simples (vs ontem) com seta e percentual."""
        if previous == 0:
            if current == 0:
                return f"0% {suffix}"
            return f"↑ {suffix}"
        delta = ((current - previous) / abs(previous)) * 100.0
        arrow = "↑" if delta >= 0 else "↓"
        return f"{arrow} {abs(delta):.0f}% {suffix}"

    @staticmethod
    def _money(value: float) -> str:
        """Formata valores monetários no padrão brasileiro simplificado."""
        return f"R$ {float(value):.2f}"
