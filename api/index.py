import sys
import os
from pathlib import Path

# Adicionar o diretório backend ao path
backend_path = str(Path(__file__).parent.parent / "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Set environment variables for Vercel
os.environ.setdefault('PYTHONUNBUFFERED', '1')

try:
    from server import app
except ImportError as e:
    print(f"Erro ao importar server: {e}")
    raise

# Vercel espera a app como default export
__all__ = ["app"]

# Suporte para handler Vercel
handler = app
