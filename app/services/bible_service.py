import requests
import logging

logger = logging.getLogger('BibleService')

class BibleService:
    """Serviço para buscar versículos bíblicos da API pública."""
    
    API_URL = "https://bible-api.com/random?translation=almeida" # Usando Tradução em Português se possível ou fallback

    @staticmethod
    def get_random_verse():
        """Busca um versículo aleatório."""
        try:
            # A API bible-api.com é gratuita e não requer chave.
            # Por padrão é em inglês, mas podemos tentar buscar referências específicas ou usar um fallback.
            response = requests.get("https://bible-api.com/random", timeout=5)
            if response.status_code == 200:
                data = response.json()
                text = data.get('text', '').strip()
                ref = data.get('reference', '')
                return f'"{text}"\n— {ref}'
            return "O Senhor é o meu pastor, nada me faltará. (Salmos 23:1)"
        except Exception as e:
            logger.error(f"Erro ao buscar versículo: {e}")
            return "Tudo posso naquele que me fortalece. (Filipenses 4:13)"
