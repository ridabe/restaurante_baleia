import PyInstaller.__main__
import os

def build_executable():
    """Gera o executável .exe do sistema Bar do Baleia."""
    
    # Nome do projeto
    app_name = "BarDoBaleia"
    main_script = "main.py"
    
    print(f"--- Iniciando build de {app_name} ---")

    # Opções do PyInstaller
    options = [
        main_script,
        '--name=%s' % app_name,
        '--onefile',        # Empacotar em um único arquivo .exe
        '--noconsole',      # Não abrir console ao executar (apenas GUI)
        '--clean',          # Limpar cache antes de buildar
        '--add-data=app;app', # Incluir a pasta app no pacote
    ]

    # Aplica ícone nativo do Windows quando o arquivo .ico existir.
    icon_path = os.path.join("app", "img", "logo_baleia.ico")
    if os.path.exists(icon_path):
        options.append(f'--icon={icon_path}')

    # Executar build
    try:
        PyInstaller.__main__.run(options)
        print(f"--- Build concluído com sucesso! Verifique a pasta 'dist' ---")
    except Exception as e:
        print(f"Erro durante o build: {e}")

if __name__ == "__main__":
    build_executable()
