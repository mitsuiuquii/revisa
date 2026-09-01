import sys
import os
from pathlib import Path

# Adicionar o diretório backend ao path
backend_path = str(Path(__file__).parent / "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Variáveis de ambiente
os.environ.setdefault('PYTHONUNBUFFERED', '1')

# Importar o aplicativo FastAPI
try:
    from server import app
    print("✅ FastAPI app carregado com sucesso de backend/server.py")
except Exception as e:
    print(f"❌ Erro ao carregar FastAPI: {e}")
    import traceback
    traceback.print_exc()
    raise

# Exportar a app para Vercel
__all__ = ["app"]
