"""
Generador de PPT a partir de las evidencias recopiladas por el bot.
"""

import tempfile
import subprocess
import json
from pathlib import Path
from datetime import datetime


def generate_ppt(evidencias: list) -> str:
    """Genera la PPT y devuelve la ruta al archivo .pptx"""

    # Serializar evidencias para pasarlas al script Node
    tmp_data = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    )
    json.dump(evidencias, tmp_data, ensure_ascii=False)
    tmp_data.close()

    output_path = tempfile.mktemp(suffix=".pptx")

    # Llamar al script Node.js que genera la PPT
    script_path = Path(__file__).parent / "generate_ppt.js"
    result = subprocess.run(
        ["node", str(script_path), tmp_data.name, output_path],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Error en Node: {result.stderr}")

    return output_path
