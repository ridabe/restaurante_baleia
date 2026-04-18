from __future__ import annotations

import html
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

from PySide6.QtCore import QObject, QRunnable, QThreadPool, QUrl, Signal, Slot, Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
)


class NewsWidget(QFrame):
    """Widget de notícias (BRNews ou RSS) com atualização periódica."""

    def __init__(
        self,
        brnews_base_url: str | None = None,
        rss_fallback_url: str | None = None,
        max_items: int = 10,
        parent=None,
    ):
        super().__init__(parent)
        self._brnews_base_url = (brnews_base_url or "").strip() or None
        self._rss_fallback_url = (rss_fallback_url or "").strip() or None
        self._max_items = max_items
        self._manager = QNetworkAccessManager(self)
        self._manager.finished.connect(self._on_finished)
        self._thread_pool = QThreadPool.globalInstance()
        self._last_updated: datetime | None = None
        self._last_attempted_provider = "brnews" if self._brnews_base_url else "rss"
        self._current_url: str | None = None
        self._init_ui()
        self.refresh()

    def _init_ui(self):
        self.setObjectName("cardFrame")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()

        title = QLabel("Notícias do Brasil")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #0F172A;")
        header.addWidget(title)

        self._lbl_status = QLabel("Carregando...")
        self._lbl_status.setStyleSheet("color: #64748B; font-size: 12px;")
        header.addWidget(self._lbl_status)

        header.addStretch()

        self._btn_refresh = QPushButton("Atualizar")
        self._btn_refresh.setObjectName("secondaryButton")
        self._btn_refresh.setMinimumHeight(36)
        self._btn_refresh.clicked.connect(self.refresh)
        header.addWidget(self._btn_refresh)

        layout.addLayout(header)

        self._browser = QTextBrowser()
        self._browser.setOpenExternalLinks(False)
        self._browser.anchorClicked.connect(lambda url: QDesktopServices.openUrl(url))
        self._browser.setStyleSheet(
            "QTextBrowser { border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; background: #FFFFFF; }"
        )
        layout.addWidget(self._browser, 1)

    def refresh(self):
        """Dispara atualização das notícias sem bloquear a UI."""
        self._last_attempted_provider = "brnews" if self._brnews_base_url else "rss"
        self._btn_refresh.setEnabled(False)
        self._lbl_status.setText("Atualizando...")

        url = self._get_request_url()
        if not url:
            self._btn_refresh.setEnabled(True)
            self._lbl_status.setText("Configuração de notícias ausente.")
            self._browser.setHtml(
                "<div style='color:#64748B; font-size: 13px;'>"
                "Configure a fonte de notícias nas configurações do sistema."
                "</div>"
            )
            return

        self._current_url = url
        if self._last_attempted_provider == "rss":
            self._fetch_with_python(url)
            return

        request = QNetworkRequest(QUrl(url))
        request.setRawHeader(b"User-Agent", b"BarDoBaleia/1.0")
        self._manager.get(request)

    def _on_finished(self, reply):
        self._btn_refresh.setEnabled(True)

        status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        try:
            status_code = int(status_code) if status_code is not None else None
        except Exception:
            status_code = None

        if status_code is not None and status_code >= 400:
            if self._last_attempted_provider == "brnews" and self._rss_fallback_url:
                self._last_attempted_provider = "rss"
                self._current_url = self._rss_fallback_url
                self._fetch_with_python(self._rss_fallback_url)
                reply.deleteLater()
                return

            self._lbl_status.setText("Falha ao buscar notícias.")
            self._browser.setHtml(self._build_error_html(status_code=status_code))
            reply.deleteLater()
            return

        if reply.error():
            if self._last_attempted_provider == "brnews" and self._rss_fallback_url:
                self._last_attempted_provider = "rss"
                self._current_url = self._rss_fallback_url
                self._fetch_with_python(self._rss_fallback_url)
                reply.deleteLater()
                return

            self._lbl_status.setText("Falha ao buscar notícias.")
            self._browser.setHtml(self._build_error_html(error=reply.errorString()))
            reply.deleteLater()
            return

        data = bytes(reply.readAll())
        reply.deleteLater()

        if self._last_attempted_provider == "brnews":
            items = self._parse_brnews_items(data)[: self._max_items]
        else:
            items = self._parse_rss_items(data)[: self._max_items]

        self._render_items(items)

    def _render_items(self, items: list[dict]):
        """Renderiza a lista de itens no painel, mantendo layout legível."""
        self._last_updated = datetime.now()
        provider = "BRNews" if self._last_attempted_provider == "brnews" else "RSS"
        self._lbl_status.setText(f"{provider} • {self._last_updated.strftime('%H:%M')}")

        if not items:
            self._browser.setHtml(
                "<div style='color:#64748B; font-size: 13px;'>Nenhuma notícia disponível no momento.</div>"
            )
            return

        cards_html = []
        for item in items:
            title = html.escape(item.get("title", "").strip() or "Sem título")
            link = html.escape(item.get("link", "").strip())
            source = html.escape(item.get("source", "").strip())
            pub = html.escape(item.get("pubDate", "").strip())
            summary = html.escape(item.get("summary", "").strip())

            meta_parts = [p for p in [source, pub] if p]
            meta = " • ".join(meta_parts)

            summary_html = (
                f"<div style='margin-top: 6px; color:#334155; font-size: 12px; line-height: 1.35;'>{summary}</div>"
                if summary
                else ""
            )
            cards_html.append(
                f"""
                <div style='padding: 10px 10px; border-bottom: 1px solid #F1F5F9;'>
                    <a href='{link}' style='color:#0F172A; font-size: 14px; font-weight: 700; text-decoration: none;'>
                        {title}
                    </a>
                    <div style='margin-top: 4px; color:#64748B; font-size: 11px;'>{meta}</div>
                    {summary_html}
                </div>
                """
            )

        container = (
            "<div style='font-family: Segoe UI, Arial, sans-serif;'>"
            + "\n".join(cards_html)
            + "</div>"
        )
        self._browser.setHtml(container)

    @staticmethod
    def _parse_rss_items(xml_bytes: bytes) -> list[dict]:
        """Extrai itens (title/link/pubDate/source) de um RSS."""
        try:
            root = ET.fromstring(xml_bytes)
        except Exception:
            return []

        channel = root.find("channel")
        if channel is None:
            channel = root.find(".//channel")
        if channel is None:
            return []

        items = []
        for item in channel.findall("item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            pub_date = (item.findtext("pubDate") or "").strip()

            source_el = item.find("source")
            source = (source_el.text or "").strip() if source_el is not None else ""

            items.append({"title": title, "link": link, "pubDate": pub_date, "source": source})
        return items

    def _get_request_url(self) -> str | None:
        """Resolve a URL do request conforme provider ativo (brnews -> rss fallback)."""
        if self._last_attempted_provider == "brnews" and self._brnews_base_url:
            base = self._brnews_base_url.rstrip("/")
            if base.endswith("/v1/news"):
                return f"{base}/"
            if base.endswith("/v1/news/"):
                return base
            if "/v1/" in base:
                return base
            return f"{base}/v1/news/"

        if self._rss_fallback_url:
            return self._rss_fallback_url
        return None

    @staticmethod
    def _build_error_html(error: str | None = None, status_code: int | None = None) -> str:
        """HTML de fallback para falhas de rede."""
        details = []
        if status_code is not None:
            details.append(f"HTTP {status_code}")
        if error:
            details.append(html.escape(str(error)))
        details_html = f"<div style='margin-top:6px; font-size: 11px; color:#94A3B8;'>{' • '.join(details)}</div>" if details else ""
        return (
            "<div style='color:#64748B; font-size: 13px;'>"
            "Não foi possível carregar as notícias agora. Clique em <b>Atualizar</b> para tentar novamente."
            f"{details_html}"
            "</div>"
        )

    @staticmethod
    def _parse_brnews_items(json_bytes: bytes) -> list[dict]:
        """Extrai itens (title/link/pubDate/source/summary) do endpoint /v1/news/ do BRNews."""
        try:
            payload = json.loads(json_bytes.decode("utf-8", errors="ignore"))
        except Exception:
            return []

        if isinstance(payload, list):
            raw_items = payload
        elif isinstance(payload, dict):
            raw_items = (
                payload.get("news")
                or payload.get("data")
                or payload.get("results")
                or payload.get("items")
                or []
            )
        else:
            raw_items = []

        items: list[dict] = []
        for obj in raw_items:
            if not isinstance(obj, dict):
                continue

            title = (obj.get("title") or obj.get("headline") or "").strip()
            summary = (obj.get("summary") or obj.get("description") or obj.get("content") or "").strip()
            link = (obj.get("url") or obj.get("link") or obj.get("permalink") or "").strip()
            pub_date = (
                obj.get("publication_date")
                or obj.get("published_at")
                or obj.get("pubDate")
                or obj.get("created_at")
                or ""
            )
            pub_date = str(pub_date).strip()

            source = ""
            source_obj = obj.get("source") or obj.get("site") or obj.get("provider")
            if isinstance(source_obj, dict):
                source = (source_obj.get("name") or source_obj.get("title") or "").strip()
            elif isinstance(source_obj, str):
                source = source_obj.strip()
            else:
                source = (obj.get("source_name") or obj.get("sourceTitle") or "").strip()

            if not link:
                continue

            if len(summary) > 220:
                summary = summary[:217].rstrip() + "..."

            items.append(
                {
                    "title": title or "Sem título",
                    "link": link,
                    "pubDate": pub_date,
                    "source": source,
                    "summary": summary,
                }
            )

        return items

    def _fetch_with_python(self, url: str):
        """Busca conteúdo via urllib em thread para evitar dependência de SSL do Qt em ambiente Windows."""
        self._btn_refresh.setEnabled(False)
        self._lbl_status.setText("Atualizando...")
        task = _PythonFetchTask(url=url)
        task.signals.finished.connect(self._on_python_fetch_success)
        task.signals.failed.connect(self._on_python_fetch_fail)
        self._thread_pool.start(task)

    @Slot(bytes)
    def _on_python_fetch_success(self, data: bytes):
        self._btn_refresh.setEnabled(True)
        items = self._parse_rss_items(data)[: self._max_items]
        self._last_attempted_provider = "rss"
        self._render_items(items)

    @Slot(str)
    def _on_python_fetch_fail(self, error: str):
        self._btn_refresh.setEnabled(True)
        self._lbl_status.setText("Falha ao buscar notícias.")
        self._browser.setHtml(self._build_error_html(error=error))


class _PythonFetchSignals(QObject):
    """Sinais do fetch em background."""

    finished = Signal(bytes)
    failed = Signal(str)


class _PythonFetchTask(QRunnable):
    """Tarefa de fetch via urllib para evitar travamento da UI."""

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.signals = _PythonFetchSignals()

    def run(self):
        """Executa a requisição HTTP e retorna o payload bruto."""
        try:
            req = urllib.request.Request(self.url, headers={"User-Agent": "BarDoBaleia/1.0"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = resp.read()
            self.signals.finished.emit(data)
        except Exception as e:
            self.signals.failed.emit(str(e))
