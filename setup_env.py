"""Script para configurar o .env do frontend com o IP correto."""
import subprocess
import socket
import sys
from pathlib import Path

def get_local_ip():
    """Obtém o IP local da máquina."""
    try:
        # Método 1: Conecta ao Google DNS
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        try:
            # Método 2: Usa ipconfig (Windows)
            result = subprocess.run(['ipconfig'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'IPv4 Address' in line:
                    return line.split()[-1]
        except:
            pass
    return "localhost"

def setup_env():
    """Configura o .env do frontend."""
    local_ip = get_local_ip()
    backend_url = f"http://{local_ip}:8000"
    
    frontend_env = Path(__file__).parent.parent / "frontend" / ".env"
    
    # Conteúdo do .env
    env_content = f"""REACT_APP_BACKEND_URL={backend_url}
WDS_SOCKET_PORT=443
ENABLE_HEALTH_CHECK=false"""
    
    # Escreve o arquivo
    frontend_env.write_text(env_content)
    
    print("="*70)
    print("✅ CONFIGURAÇÃO CONCLUÍDA")
    print("="*70)
    print(f"\n📍 IP Detectado: {local_ip}")
    print(f"🔗 Backend URL: {backend_url}")
    print(f"\n📝 Arquivo atualizado: {frontend_env}")
    print(f"\n📋 Conteúdo do .env:")
    print("-"*70)
    print(env_content)
    print("-"*70)
    print("\n⚠️  PRÓXIMOS PASSOS:")
    print("1. Reinicie o frontend: npm start")
    print("2. Acesse via navegador: http://localhost:3000 (local)")
    print(f"                     ou: http://{local_ip}:3000 (rede)")
    print("\n✨ Agora o cadastro deve funcionar!")

if __name__ == "__main__":
    setup_env()
