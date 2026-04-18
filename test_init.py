import sys
import os

# Adiciona o diretório atual ao path para facilitar imports
sys.path.append(os.getcwd())

try:
    from app.core.database import init_db
    from app.core.config import init_config
    from app.modules.estoque.service import EstoqueService
    from app.modules.caixa.service import CaixaService
    from app.modules.fiado.service import FiadoService
    from app.modules.fluxo_caixa.service import FluxoCaixaService
    
    print("Testando inicialização do banco e configurações...")
    init_db()
    init_config()
    print("Sucesso: Banco e configurações inicializados.")

    print("Testando serviços...")
    # Tenta adicionar um produto de teste
    res, msg = EstoqueService.adicionar("Cerveja de Teste", 10.50, 100, 5)
    print(f"EstoqueService: {msg}")
    
    # Tenta cadastrar um cliente de teste
    res, msg = FiadoService.cadastrar_cliente("Cliente Teste", "1234-5678", "teste@email.com")
    print(f"FiadoService: {msg}")

    print("\n--- Todos os testes de backend e inicialização passaram! ---")
    
except Exception as e:
    print(f"\n[ERRO] Falha no teste: {e}")
    sys.exit(1)
