import re
from string import Template
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QWidget, QTableWidget


class ThemeManager:
    FONT_SIZE_OPTIONS = {
        "Pequeno": 0.90,
        "Normal": 1.00,
        "Grande": 1.20,
        "Extra Grande": 1.40,
    }

    THEME_OPTIONS = {
        "padrao": "padrao",
        "tema padrão": "padrao",
        "tema padrao": "padrao",
        "alto contraste": "alto_contraste_claro",
        "alto_contraste": "alto_contraste_claro",
        "alto contraste (claro)": "alto_contraste_claro",
        "alto_contraste_claro": "alto_contraste_claro",
        "alto contraste (escuro)": "alto_contraste_escuro",
        "alto_contraste_escuro": "alto_contraste_escuro",
    }

    PALETTES = {
        "padrao": {
            "bg": "#F8FAFC",
            "card": "#FFFFFF",
            "panel": "#FFFFFF",
            "border": "#CBD5E1",
            "text": "#1E293B",
            "text_secondary": "#475569",
            "muted": "#64748B",
            "input_bg": "#FFFFFF",
            "input_text": "#0F172A",
            "input_focus_bg": "#F0FDF4",
            "primary": "#16A34A",
            "primary_hover": "#15803D",
            "action": "#3B82F6",
            "action_hover": "#2563EB",
            "danger": "#EF4444",
            "danger_hover": "#DC2626",
            "button_bg": "#E2E8F0",
            "button_text": "#1E293B",
            "button_border": "#CBD5E1",
            "secondary_button_bg": "#FFFFFF",
            "secondary_button_text": "#475569",
            "secondary_button_border": "#CBD5E1",
            "sidebar_bg": "#0F172A",
            "sidebar_border": "#1E293B",
            "sidebar_text": "#FFFFFF",
            "sidebar_muted": "#94A3B8",
            "sidebar_hover_bg": "#1E293B",
            "sidebar_hover_text": "#F8FAFC",
            "table_bg": "#FFFFFF",
            "table_grid": "#F1F5F9",
            "table_header_bg": "#F1F5F9",
            "table_header_text": "#475569",
            "table_alt_bg": "#F8FAFC",
            "table_sel_bg": "#DCFCE7",
            "table_sel_text": "#166534",
            "combo_popup_bg": "#FFFFFF",
            "combo_popup_text": "#0F172A",
            "combo_popup_sel_bg": "#E2E8F0",
            "combo_popup_sel_text": "#0F172A",
            "scrollbar_bg": "#F1F5F9",
            "scrollbar_handle": "#CBD5E1",
            "scrollbar_handle_hover": "#94A3B8",
            "ticket_bg": "#FFFBEB",
            "ticket_border": "#D97706",
            "ticket_text": "#92400E",
            "ticket_note_bg": "#DBEAFE",
            "ticket_note_text": "#1E40AF",
        },
        "alto_contraste": {
            "bg": "#FFFFFF",
            "card": "#F8FAFC",
            "panel": "#F8FAFC",
            "border": "#0F172A",
            "text": "#000000",
            "text_secondary": "#111827",
            "muted": "#1F2937",
            "input_bg": "#FFFFFF",
            "input_text": "#000000",
            "input_focus_bg": "#E5E7EB",
            "primary": "#16A34A",
            "primary_hover": "#15803D",
            "action": "#1D4ED8",
            "action_hover": "#1E40AF",
            "danger": "#DC2626",
            "danger_hover": "#B91C1C",
            "button_bg": "#FFFFFF",
            "button_text": "#000000",
            "button_border": "#0F172A",
            "secondary_button_bg": "#FFFFFF",
            "secondary_button_text": "#000000",
            "secondary_button_border": "#0F172A",
            "sidebar_bg": "#0F172A",
            "sidebar_border": "#0B1220",
            "sidebar_text": "#FFFFFF",
            "sidebar_muted": "#E5E7EB",
            "sidebar_hover_bg": "#111827",
            "sidebar_hover_text": "#FFFFFF",
            "table_bg": "#FFFFFF",
            "table_grid": "#0F172A",
            "table_header_bg": "#0F172A",
            "table_header_text": "#FFFFFF",
            "table_alt_bg": "#F8FAFC",
            "table_sel_bg": "#16A34A",
            "table_sel_text": "#000000",
            "combo_popup_bg": "#FFFFFF",
            "combo_popup_text": "#000000",
            "combo_popup_sel_bg": "#16A34A",
            "combo_popup_sel_text": "#000000",
            "scrollbar_bg": "#F1F5F9",
            "scrollbar_handle": "#0F172A",
            "scrollbar_handle_hover": "#111827",
            "ticket_bg": "#FFFFFF",
            "ticket_border": "#0F172A",
            "ticket_text": "#000000",
            "ticket_note_bg": "#111827",
            "ticket_note_text": "#FFFFFF",
        },
        "alto_contraste_claro": {
            "bg": "#FFFFFF",
            "card": "#F8FAFC",
            "panel": "#F8FAFC",
            "border": "#0F172A",
            "text": "#000000",
            "text_secondary": "#111827",
            "muted": "#1F2937",
            "input_bg": "#FFFFFF",
            "input_text": "#000000",
            "input_focus_bg": "#E5E7EB",
            "primary": "#16A34A",
            "primary_hover": "#15803D",
            "action": "#1D4ED8",
            "action_hover": "#1E40AF",
            "danger": "#DC2626",
            "danger_hover": "#B91C1C",
            "button_bg": "#FFFFFF",
            "button_text": "#000000",
            "button_border": "#0F172A",
            "secondary_button_bg": "#FFFFFF",
            "secondary_button_text": "#000000",
            "secondary_button_border": "#0F172A",
            "sidebar_bg": "#0F172A",
            "sidebar_border": "#0B1220",
            "sidebar_text": "#FFFFFF",
            "sidebar_muted": "#E5E7EB",
            "sidebar_hover_bg": "#111827",
            "sidebar_hover_text": "#FFFFFF",
            "table_bg": "#FFFFFF",
            "table_grid": "#0F172A",
            "table_header_bg": "#0F172A",
            "table_header_text": "#FFFFFF",
            "table_alt_bg": "#F8FAFC",
            "table_sel_bg": "#16A34A",
            "table_sel_text": "#000000",
            "combo_popup_bg": "#FFFFFF",
            "combo_popup_text": "#000000",
            "combo_popup_sel_bg": "#16A34A",
            "combo_popup_sel_text": "#000000",
            "scrollbar_bg": "#F1F5F9",
            "scrollbar_handle": "#0F172A",
            "scrollbar_handle_hover": "#111827",
            "ticket_bg": "#FFFFFF",
            "ticket_border": "#0F172A",
            "ticket_text": "#000000",
            "ticket_note_bg": "#111827",
            "ticket_note_text": "#FFFFFF",
        },
        "alto_contraste_escuro": {
            "bg": "#000000",
            "card": "#111111",
            "panel": "#111111",
            "border": "#555555",
            "text": "#FFFFFF",
            "text_secondary": "#E5E7EB",
            "muted": "#E5E7EB",
            "input_bg": "#050505",
            "input_text": "#FFFFFF",
            "input_focus_bg": "#0B1220",
            "primary": "#22C55E",
            "primary_hover": "#16A34A",
            "action": "#2563EB",
            "action_hover": "#1D4ED8",
            "danger": "#EF4444",
            "danger_hover": "#DC2626",
            "button_bg": "#1F2937",
            "button_text": "#FFFFFF",
            "button_border": "#555555",
            "secondary_button_bg": "#1F2937",
            "secondary_button_text": "#FFFFFF",
            "secondary_button_border": "#555555",
            "sidebar_bg": "#000000",
            "sidebar_border": "#3A3A3A",
            "sidebar_text": "#FFFFFF",
            "sidebar_muted": "#E5E7EB",
            "sidebar_hover_bg": "#111111",
            "sidebar_hover_text": "#FFFFFF",
            "table_bg": "#111111",
            "table_grid": "#333333",
            "table_header_bg": "#1F2937",
            "table_header_text": "#FFFFFF",
            "table_alt_bg": "#0B0B0B",
            "table_sel_bg": "#14532D",
            "table_sel_text": "#FFFFFF",
            "combo_popup_bg": "#050505",
            "combo_popup_text": "#FFFFFF",
            "combo_popup_sel_bg": "#22C55E",
            "combo_popup_sel_text": "#000000",
            "scrollbar_bg": "#111111",
            "scrollbar_handle": "#3A3A3A",
            "scrollbar_handle_hover": "#4B5563",
            "ticket_bg": "#111111",
            "ticket_border": "#555555",
            "ticket_text": "#FFFFFF",
            "ticket_note_bg": "#1F2937",
            "ticket_note_text": "#FFFFFF",
        },
    }

    @staticmethod
    def normalize_settings(settings: dict) -> dict:
        raw_size = (settings.get("ui_font_size") or "Normal").strip()
        raw_theme = (settings.get("ui_theme") or "padrao").strip().lower()
        accessibility = bool(settings.get("ui_accessibility_enabled", False))

        scale = ThemeManager.FONT_SIZE_OPTIONS.get(raw_size, 1.0)
        theme_key = ThemeManager.THEME_OPTIONS.get(raw_theme, "padrao")

        if accessibility:
            scale = max(scale, 1.25)
            theme_key = "alto_contraste_claro" if theme_key == "padrao" else theme_key

        return {
            "scale": float(scale),
            "theme": theme_key,
            "accessibility": accessibility,
        }

    @staticmethod
    def _scale_px(text: str, scale: float) -> str:
        if not text or abs(scale - 1.0) < 0.001:
            return text

        rx = re.compile(r"(\d+(?:\.\d+)?)px")

        def repl(m):
            value = float(m.group(1))
            if value == 0:
                return "0px"
            scaled = int(round(value * scale))
            if scaled < 1:
                scaled = 1
            return f"{scaled}px"

        return rx.sub(repl, text)

    @staticmethod
    def transform_stylesheet(widget_stylesheet: str, *, scale: float, high_contrast: bool) -> str:
        out = widget_stylesheet or ""
        out = ThemeManager._scale_px(out, scale)
        return out

    @staticmethod
    def build_global_stylesheet(settings: dict) -> str:
        cfg = ThemeManager.normalize_settings(settings)
        scale = cfg["scale"]
        palette = ThemeManager.PALETTES.get(cfg["theme"], ThemeManager.PALETTES["padrao"])

        base_font_px = int(round(14 * scale))
        header_px = int(round(24 * scale))
        module_px = int(round(20 * scale))
        button_px = int(round((14 if cfg["accessibility"] else 13) * scale))

        control_min_h = int(round((44 if cfg["accessibility"] else 36) * scale))
        input_pad_v = int(round((10 if cfg["accessibility"] else 8) * scale))
        input_pad_h = int(round((14 if cfg["accessibility"] else 12) * scale))
        input_border_w = 2 if cfg["accessibility"] else 1
        input_focus_border_w = 3 if cfg["accessibility"] else 2

        card_border_w = 2 if cfg["accessibility"] else 1
        sidebar_btn_px = int(round((18 if cfg["accessibility"] else 15) * scale))
        sidebar_item_min_h = int(round((54 if cfg["accessibility"] else 44) * scale))
        sidebar_pad_v = int(round((16 if cfg["accessibility"] else 12) * scale))
        sidebar_pad_h = int(round((26 if cfg["accessibility"] else 22) * scale))
        sidebar_min_w = int(round((320 if cfg["accessibility"] else 260) * max(1.0, min(scale, 1.4))))

        table_header_px = int(round((16 if cfg["accessibility"] else 13) * scale))
        table_item_pad = int(round((12 if cfg["accessibility"] else 8) * scale))

        scrollbar_w = int(round((14 if cfg["accessibility"] else 10) * scale))
        button_pad_v = int(round((10 if cfg["accessibility"] else 8) * scale))
        button_pad_h = int(round((18 if cfg["accessibility"] else 16) * scale))
        header_padding = int(round(10 * scale))
        groupbox_border_w = 2 if cfg["accessibility"] else 1
        sidebar_logo_title_px = int(round(22 * scale))
        sidebar_logo_subtitle_px = int(round(12 * scale))
        sidebar_verse_px = int(round((12 if cfg["accessibility"] else 11) * scale))
        caixa_total_px = int(round((44 if cfg["accessibility"] else 42) * scale))
        caixa_total_min_h = int(round((86 if cfg["accessibility"] else 72) * scale))
        dashboard_metric_px = int(round(28 * scale))
        dashboard_metric_md_px = int(round(24 * scale))

        qss = Template(
            """
QMainWindow, QWidget {
    background-color: $bg;
    color: $text;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: $base_font_pxpx;
}

QDialog {
    background-color: $bg;
    color: $text;
}

QLabel {
    color: $text;
    font-weight: 500;
    background: transparent;
}

QLabel#mutedLabel {
    color: $muted;
    font-weight: 600;
}

QLabel#textSecondaryLabel {
    color: $text_secondary;
    font-weight: 600;
}

QLabel[db_status="ok"] {
    color: $primary;
    font-weight: 900;
}

QLabel[db_status="error"] {
    color: $danger;
    font-weight: 900;
}

QLabel#headerTitle {
    font-size: $header_pxpx;
    font-weight: 800;
    color: $text;
}

QLabel#moduleTitle {
    font-size: $module_pxpx;
    font-weight: 700;
    color: $text;
}

QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit {
    background-color: $input_bg;
    color: $input_text;
    border: $input_border_wpx solid $border;
    border-radius: 6px;
    padding: $input_pad_vpx $input_pad_hpx;
    min-height: $control_min_hpx;
    selection-background-color: $primary;
    selection-color: #000000;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
    border: $input_focus_border_wpx solid $primary;
    background-color: $input_focus_bg;
}

QComboBox {
    background-color: $input_bg;
    color: $input_text;
    border: $input_border_wpx solid $border;
    border-radius: 6px;
    padding: $input_pad_vpx $input_pad_hpx;
    min-height: $control_min_hpx;
}

QComboBox:focus {
    border: $input_focus_border_wpx solid $primary;
    background-color: $input_focus_bg;
}

QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: $combo_popup_bg;
    color: $combo_popup_text;
    border: $input_border_wpx solid $border;
    selection-background-color: $combo_popup_sel_bg;
    selection-color: $combo_popup_sel_text;
    outline: none;
}

QPushButton {
    border-radius: 6px;
    padding: $button_pad_vpx $button_pad_hpx;
    font-weight: 700;
    font-size: $button_pxpx;
    border: $input_border_wpx solid $button_border;
    outline: none;
    background-color: $button_bg;
    color: $button_text;
    min-height: $control_min_hpx;
}

QPushButton#primaryButton {
    background-color: $primary !important;
    color: #FFFFFF !important;
    border: $input_border_wpx solid $primary !important;
}

QPushButton#primaryButton:hover {
    background-color: $primary_hover !important;
    border-color: $primary_hover !important;
}

QPushButton#actionButton {
    background-color: $action !important;
    color: #FFFFFF !important;
    border: $input_border_wpx solid $action !important;
}

QPushButton#actionButton:hover {
    background-color: $action_hover !important;
    border-color: $action_hover !important;
}

QPushButton#dangerButton {
    background-color: $danger !important;
    color: #FFFFFF !important;
    border: $input_border_wpx solid $danger !important;
}

QPushButton#dangerButton:hover {
    background-color: $danger_hover !important;
    border-color: $danger_hover !important;
}

QPushButton#secondaryButton {
    background-color: $secondary_button_bg !important;
    color: $secondary_button_text !important;
    border: $input_border_wpx solid $secondary_button_border !important;
}

QPushButton#secondaryButton:hover {
    background-color: $button_bg !important;
    border-color: $border !important;
}

QFrame#cardFrame {
    background-color: $card;
    border: $card_border_wpx solid $border;
    border-radius: 8px;
}

QFrame#metricCardPositive {
    background-color: $card;
    border: $card_border_wpx solid $border;
    border-left: 6px solid $primary;
    border-radius: 10px;
}

QFrame#metricCardAction {
    background-color: $card;
    border: $card_border_wpx solid $border;
    border-left: 6px solid $action;
    border-radius: 10px;
}

QFrame#metricCardDanger {
    background-color: $card;
    border: $card_border_wpx solid $border;
    border-left: 6px solid $danger;
    border-radius: 10px;
}

QLabel#metricValuePositive {
    color: $primary;
    font-weight: 900;
}

QLabel#metricValueAction {
    color: $action;
    font-weight: 900;
}

QLabel#metricValueDanger {
    color: $danger;
    font-weight: 900;
}

QLabel#metricValueDashboard {
    font-size: $dashboard_metric_pxpx;
    font-weight: 900;
}

QLabel#metricValuePositive[metric_size="lg"] {
    font-size: $dashboard_metric_pxpx;
}

QLabel#metricValueAction[metric_size="md"],
QLabel#metricValueDanger[metric_size="md"] {
    font-size: $dashboard_metric_md_pxpx;
}

QLabel#lowStockBanner {
    color: $danger;
    background-color: $card;
    border: $input_border_wpx solid $danger;
    border-radius: 6px;
    padding: 8px 10px;
    font-weight: 700;
}

QFrame#actionContainer {
    background: transparent;
    border: none;
}

QGroupBox {
    font-weight: 800;
    border: $groupbox_border_wpx solid $border;
    border-radius: 8px;
    margin-top: 15px;
    padding-top: 20px;
    background-color: $card;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 5px;
    color: $text_secondary;
}

QScrollArea, QScrollArea QWidget {
    background-color: transparent;
}

QTableWidget {
    background-color: $table_bg;
    color: $text;
    border: $card_border_wpx solid $border;
    gridline-color: $table_grid;
    border-radius: 8px;
    selection-background-color: $table_sel_bg;
    selection-color: $table_sel_text;
    alternate-background-color: $table_alt_bg;
}

QHeaderView::section {
    background-color: $table_header_bg;
    color: $table_header_text;
    padding: $header_paddingpx;
    border: none;
    border-bottom: $input_focus_border_wpx solid $border;
    font-weight: 800;
    font-size: $table_header_pxpx;
}

QTableWidget::item {
    padding: $table_item_padpx;
}

QCheckBox {
    color: $text;
    spacing: 10px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
}

QFrame#sidebarFrame {
    background-color: $sidebar_bg;
    border-right: $card_border_wpx solid $sidebar_border;
    min-width: $sidebar_min_wpx;
}

QFrame#sidebarBibleContainer {
    background-color: $sidebar_hover_bg;
    border-top: $input_border_wpx solid $sidebar_border;
    padding: 10px;
}

QPushButton#sidebarButton {
    background-color: transparent;
    color: $sidebar_muted;
    text-align: left;
    padding: $sidebar_pad_vpx $sidebar_pad_hpx;
    border-radius: 0px;
    font-size: $sidebar_btn_pxpx;
    border-left: 4px solid transparent;
    min-height: $sidebar_item_min_hpx;
}

QPushButton#sidebarButton:hover {
    background-color: $sidebar_hover_bg;
    color: $sidebar_hover_text;
}

QPushButton#sidebarButton:checked {
    background-color: $sidebar_hover_bg;
    color: $primary;
    font-weight: 900;
    border-left: 4px solid $primary;
}

QPushButton#sidebarToggle {
    background-color: $button_bg;
    color: $button_text;
    text-align: left;
    padding: $sidebar_pad_vpx $sidebar_pad_hpx;
    border-radius: 0px;
    font-size: $sidebar_btn_pxpx;
    border-left: 4px solid transparent;
    min-height: $sidebar_item_min_hpx;
}

QPushButton#sidebarToggle:checked {
    border-left: 4px solid $primary;
    background-color: $sidebar_hover_bg;
    font-weight: 900;
}

QLabel#sidebarLogoTitle {
    color: $primary;
    font-weight: 900;
    font-size: $sidebar_logo_title_pxpx;
}

QLabel#sidebarLogoSubtitle {
    color: $sidebar_muted;
    font-size: $sidebar_logo_subtitle_pxpx;
}

QLabel#sidebarVerse {
    color: $sidebar_muted;
    font-size: $sidebar_verse_pxpx;
    font-style: italic;
}

QLabel#caixaTotalValue {
    font-size: $caixa_total_pxpx;
    font-weight: 900;
    color: $primary;
    min-height: $caixa_total_min_hpx;
}

QLabel#ticketPreview {
    background-color: $ticket_bg;
    border: $input_border_wpx dashed $ticket_border;
    color: $ticket_text;
    padding: 20px;
    font-family: 'Courier New';
}

QScrollBar:vertical {
    border: none;
    background: $scrollbar_bg;
    width: $scrollbar_wpx;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: $scrollbar_handle;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: $scrollbar_handle_hover;
}
"""
        ).substitute(
            bg=palette["bg"],
            card=palette["card"],
            border=palette["border"],
            text=palette["text"],
            text_secondary=palette["text_secondary"],
            muted=palette["muted"],
            input_bg=palette["input_bg"],
            input_text=palette["input_text"],
            input_focus_bg=palette["input_focus_bg"],
            primary=palette["primary"],
            primary_hover=palette["primary_hover"],
            action=palette["action"],
            action_hover=palette["action_hover"],
            danger=palette["danger"],
            danger_hover=palette["danger_hover"],
            button_bg=palette["button_bg"],
            button_text=palette["button_text"],
            button_border=palette["button_border"],
            secondary_button_bg=palette["secondary_button_bg"],
            secondary_button_text=palette["secondary_button_text"],
            secondary_button_border=palette["secondary_button_border"],
            sidebar_bg=palette["sidebar_bg"],
            sidebar_border=palette["sidebar_border"],
            sidebar_text=palette["sidebar_text"],
            sidebar_muted=palette["sidebar_muted"],
            sidebar_hover_bg=palette["sidebar_hover_bg"],
            sidebar_hover_text=palette["sidebar_hover_text"],
            table_bg=palette["table_bg"],
            table_grid=palette["table_grid"],
            table_header_bg=palette["table_header_bg"],
            table_header_text=palette["table_header_text"],
            table_alt_bg=palette["table_alt_bg"],
            table_sel_bg=palette["table_sel_bg"],
            table_sel_text=palette["table_sel_text"],
            combo_popup_bg=palette["combo_popup_bg"],
            combo_popup_text=palette["combo_popup_text"],
            combo_popup_sel_bg=palette["combo_popup_sel_bg"],
            combo_popup_sel_text=palette["combo_popup_sel_text"],
            scrollbar_bg=palette["scrollbar_bg"],
            scrollbar_handle=palette["scrollbar_handle"],
            scrollbar_handle_hover=palette["scrollbar_handle_hover"],
            ticket_bg=palette["ticket_bg"],
            ticket_border=palette["ticket_border"],
            ticket_text=palette["ticket_text"],
            base_font_pxpx=f"{base_font_px}px",
            header_pxpx=f"{header_px}px",
            module_pxpx=f"{module_px}px",
            button_pxpx=f"{button_px}px",
            control_min_hpx=f"{control_min_h}px",
            input_pad_vpx=f"{input_pad_v}px",
            input_pad_hpx=f"{input_pad_h}px",
            input_border_wpx=f"{input_border_w}px",
            input_focus_border_wpx=f"{input_focus_border_w}px",
            button_pad_vpx=f"{button_pad_v}px",
            button_pad_hpx=f"{button_pad_h}px",
            card_border_wpx=f"{card_border_w}px",
            sidebar_btn_pxpx=f"{sidebar_btn_px}px",
            sidebar_item_min_hpx=f"{sidebar_item_min_h}px",
            sidebar_pad_vpx=f"{sidebar_pad_v}px",
            sidebar_pad_hpx=f"{sidebar_pad_h}px",
            sidebar_min_wpx=f"{sidebar_min_w}px",
            table_header_pxpx=f"{table_header_px}px",
            header_paddingpx=f"{header_padding}px",
            table_item_padpx=f"{table_item_pad}px",
            groupbox_border_wpx=f"{groupbox_border_w}px",
            sidebar_logo_title_pxpx=f"{sidebar_logo_title_px}px",
            sidebar_logo_subtitle_pxpx=f"{sidebar_logo_subtitle_px}px",
            sidebar_verse_pxpx=f"{sidebar_verse_px}px",
            caixa_total_pxpx=f"{caixa_total_px}px",
            caixa_total_min_hpx=f"{caixa_total_min_h}px",
            dashboard_metric_pxpx=f"{dashboard_metric_px}px",
            dashboard_metric_md_pxpx=f"{dashboard_metric_md_px}px",
            scrollbar_wpx=f"{scrollbar_w}px",
        )
        return qss

    @staticmethod
    def apply(app: QApplication, settings: dict, root: QWidget | None = None) -> dict:
        cfg = ThemeManager.normalize_settings(settings)
        base_px = int(round(14 * cfg["scale"]))
        base_pt = max(10, int(round(base_px * 0.75)))
        app.setFont(QFont("Segoe UI", base_pt))
        app.setStyleSheet(ThemeManager.build_global_stylesheet(settings))
        if root is not None:
            ThemeManager.apply_to_widget_tree(root, settings)
        return cfg

    @staticmethod
    def apply_to_widget_tree(root: QWidget, settings: dict) -> None:
        cfg = ThemeManager.normalize_settings(settings)
        scale = cfg["scale"]
        high_contrast = str(cfg["theme"]).startswith("alto_contraste")

        widgets = [root] + root.findChildren(QWidget)
        for w in widgets:
            orig = w.property("_baleia_orig_qss")
            if orig is None:
                orig = w.styleSheet()
                w.setProperty("_baleia_orig_qss", orig)
            if orig:
                w.setStyleSheet(ThemeManager.transform_stylesheet(orig, scale=scale, high_contrast=high_contrast))

            if isinstance(w, QTableWidget):
                base_row = w.property("_baleia_base_row_h")
                if base_row is None:
                    base_row = int(w.verticalHeader().defaultSectionSize() or 0)
                    w.setProperty("_baleia_base_row_h", base_row)
                target_row = int(round((42 if cfg["accessibility"] else 30) * scale))
                if base_row:
                    target_row = max(target_row, int(round(base_row * scale)))
                w.verticalHeader().setDefaultSectionSize(target_row)

                header = w.horizontalHeader()
                base_hdr = header.property("_baleia_base_hdr_h") if hasattr(header, "property") else None
                if base_hdr is None:
                    base_hdr = int(header.defaultSectionSize() or 0)
                    if hasattr(header, "setProperty"):
                        header.setProperty("_baleia_base_hdr_h", base_hdr)
                target_hdr = int(round((38 if cfg["accessibility"] else 30) * scale))
                if base_hdr:
                    target_hdr = max(target_hdr, int(round(base_hdr * scale)))
                header.setDefaultSectionSize(target_hdr)


GLOBAL_STYLE = ThemeManager.build_global_stylesheet({})
