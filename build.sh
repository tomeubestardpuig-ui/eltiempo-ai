 #!/usr/bin/env bash
    set -o errexit

    pip install --upgrade pip
    pip install -r requirements.txt

    echo "--- [BUILD SCRIPT] INSTALACIÓN COMPLETA ---"
    echo "--- [BUILD SCRIPT] Listando contenido de site-packages para depuración:"
    ls -l .venv/lib/python3.11/site-packages/