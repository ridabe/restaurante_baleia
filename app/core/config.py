import os
import json
import logging
from app.core.resources import app_data_path

# Configuração de logs
os.makedirs(app_data_path("logs"), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=app_data_path("logs", "app.log"),
    filemode='a'
)
logger = logging.getLogger('Config')

# Caminho para o arquivo de configurações
CONFIG_DIR = app_data_path("config")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")

# Configurações padrão
DEFAULT_SETTINGS = {
    # Identidade Visual
    "sistema_nome": "Bar do Baleia",
    "sistema_subtitulo": "Sistema de Gestao",
    "empresa_logo_path": "app/img/logo_baleia.png",

    # Dados Institucionais
    "empresa_nome_fantasia": "Bar do Baleia",
    "empresa_razao_social": "Bar do Baleia LTDA",
    "empresa_cnpj": "00.000.000/0001-00",
    "empresa_telefone": "(11) 95030-1607",
    "empresa_email": "contato@bardobaleia.com.br",
    
    # Endereço
    "empresa_endereco": "Rua Exemplo",
    "empresa_numero": "123",
    "empresa_complemento": "",
    "empresa_bairro": "Centro",
    "empresa_cidade": "Mogi das Cruzes",
    "empresa_estado": "SP",
    "empresa_cep": "08700-000",
    
    # Preferências do Sistema
    "database_url": "",
    "modulo_senha": "baleia@2026",
    "relatorios_path": "relatorios",
    "tema": "moderno",
    "estoque_minimo_padrao": 5,
    "versiculo_api_url": "https://bible-api.com/random",
    "versiculo_update_interval": 3600, # 1 hora em segundos

    # Acessibilidade (UI)
    "ui_font_size": "Normal",
    "ui_theme": "padrao",
    "ui_accessibility_enabled": False,

    # Noticias (Dashboard)
    "brnews_base_url": "http://127.0.0.1:5000",
    "news_rss_fallback_url": "https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-419",
    "news_refresh_interval_sec": 300,
    "news_max_items": 12,
    
    # Documentos e Impressão
    "ticket_rodape": "Obrigado pela preferência! Volte sempre.",
    "relatorio_observacao": "Documento gerado para fins administrativos."
}

def init_config():
    """Inicializa o arquivo de configurações se não existir."""
    try:
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
            logger.info(f"Diretório de configuração criado: {CONFIG_DIR}")

        if not os.path.exists(SETTINGS_FILE):
            save_settings(DEFAULT_SETTINGS)
            logger.info(f"Arquivo de configurações padrão criado: {SETTINGS_FILE}")
    except Exception as e:
        logger.error(f"Erro ao inicializar configurações: {e}")
        raise

def load_settings():
    """Carrega as configurações do arquivo JSON."""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return DEFAULT_SETTINGS
    except Exception as e:
        logger.error(f"Erro ao carregar configurações: {e}")
        return DEFAULT_SETTINGS

def save_settings(settings):
    """Salva as configurações no arquivo JSON."""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        logger.info("Configurações salvas com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao salvar configurações: {e}")
        raise

if __name__ == "__main__":
    init_config()
    print("Configurações inicializadas.")
