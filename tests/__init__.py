"""Pacote de testes unitários do AgendaSaúde.

Adiciona o diretório ``backend`` ao ``sys.path`` para permitir importar o
módulo ``app`` diretamente, sem depender de instalação ou de PYTHONPATH.
"""
from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
