import html
import os
from datetime import datetime
from pathlib import Path

from app.core.config import load_settings
from app.core.resources import resource_path

DEFAULT_LOGO_PATH = "app/img/logo_baleia.png"
DEFAULT_SYSTEM_NAME = "Bar do Baleia"
DEFAULT_SYSTEM_SUBTITLE = "Sistema de Gestao"


def get_branding_context(settings: dict | None = None) -> dict:
    """Monta um contexto centralizado de identidade visual e dados institucionais."""
    s = settings or load_settings()
    logo_cfg = (s.get("empresa_logo_path") or DEFAULT_LOGO_PATH).strip()
    logo_path = logo_cfg if os.path.isabs(logo_cfg) else resource_path(logo_cfg)
    if not os.path.exists(logo_path):
        logo_path = resource_path(DEFAULT_LOGO_PATH)

    nome_fantasia = (s.get("empresa_nome_fantasia") or DEFAULT_SYSTEM_NAME).strip()
    razao = (s.get("empresa_razao_social") or "").strip()
    cnpj = (s.get("empresa_cnpj") or "").strip()
    telefone = (s.get("empresa_telefone") or "").strip()
    email = (s.get("empresa_email") or "").strip()
    endereco = (s.get("empresa_endereco") or "").strip()
    numero = (s.get("empresa_numero") or "").strip()
    bairro = (s.get("empresa_bairro") or "").strip()
    cidade = (s.get("empresa_cidade") or "").strip()
    estado = (s.get("empresa_estado") or "").strip()

    endereco_linha = " ".join(
        part for part in [
            f"{endereco}," if endereco else "",
            numero,
            f"- {bairro}" if bairro else "",
            f"- {cidade}/{estado}" if cidade or estado else "",
        ] if part
    ).strip()

    return {
        "system_name": (s.get("sistema_nome") or DEFAULT_SYSTEM_NAME).strip(),
        "system_subtitle": (s.get("sistema_subtitulo") or DEFAULT_SYSTEM_SUBTITLE).strip(),
        "company_name": nome_fantasia,
        "company_legal_name": razao,
        "cnpj": cnpj,
        "phone": telefone,
        "email": email,
        "address_line": endereco_linha,
        "logo_path": logo_path,
        "logo_uri": Path(logo_path).resolve().as_uri(),
    }


def build_report_header_html(
    report_title: str,
    period_label: str = "",
    emitted_at: datetime | None = None,
    settings: dict | None = None,
    logo_width: int = 44,
) -> str:
    """Gera o cabeçalho institucional em HTML para relatórios impressos/PDF."""
    ctx = get_branding_context(settings)
    emitted = emitted_at or datetime.now()
    period_html = (
        f"<div style='font-size: 10px; color: #64748B; margin-top: 5px;'><b>Periodo:</b> {html.escape(period_label)}</div>"
        if period_label else ""
    )
    info_extra = " | ".join(
        part for part in [
            f"CNPJ: {ctx['cnpj']}" if ctx["cnpj"] else "",
            f"Tel: {ctx['phone']}" if ctx["phone"] else "",
            f"E-mail: {ctx['email']}" if ctx["email"] else "",
        ] if part
    )
    return f"""
        <div style='margin-bottom: 28px; border-bottom: 3px solid #16A34A; padding-bottom: 14px;'>
            <table style='width: 100%; border: 0; border-collapse: collapse; margin: 0;'>
                <tr>
                    <td style='width: {logo_width + 20}px; vertical-align: top; padding-right: 12px;'>
                        <img src='{ctx["logo_uri"]}' style='width: {logo_width}px; max-width: {logo_width}px; height: auto; max-height: {logo_width}px;' />
                    </td>
                    <td style='vertical-align: top; text-align: left;'>
                        <div style='font-size: 20px; font-weight: bold; color: #0F172A;'>{html.escape(ctx["company_name"])}</div>
                        <div style='font-size: 10px; color: #475569; margin-top: 3px;'>{html.escape(ctx["company_legal_name"])}</div>
                        <div style='font-size: 10px; color: #475569; margin-top: 2px;'>{html.escape(ctx["address_line"])}</div>
                        <div style='font-size: 10px; color: #475569; margin-top: 2px;'>{html.escape(info_extra)}</div>
                    </td>
                </tr>
            </table>
            <div style='margin-top: 8px; font-size: 16px; color: #16A34A; font-weight: 600;'>{html.escape(report_title)}</div>
            {period_html}
            <div style='font-size: 10px; color: #64748B; margin-top: 3px;'><b>Emitido em:</b> {emitted.strftime('%d/%m/%Y as %H:%M')}</div>
        </div>
    """


def build_ticket_header_html(settings: dict | None = None, logo_width: int = 32) -> str:
    """Gera o cabeçalho institucional em HTML para tickets e documentos nao fiscais."""
    ctx = get_branding_context(settings)
    return f"""
        <div style='text-align: center; border-bottom: 1px dashed #92400E; padding-bottom: 10px; margin-bottom: 10px;'>
            <img src='{ctx["logo_uri"]}' style='width: {logo_width}px; max-width: {logo_width}px; height: auto; max-height: {logo_width}px; margin: 0 auto 6px auto; display: block;' />
            <b style='font-size: 16px;'>{html.escape(ctx["company_name"].upper())}</b><br>
            {"CNPJ: " + html.escape(ctx["cnpj"]) + "<br>" if ctx["cnpj"] else ""}
            {"Tel: " + html.escape(ctx["phone"]) + "<br>" if ctx["phone"] else ""}
            {html.escape(ctx["address_line"])}
        </div>
    """
