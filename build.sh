#!/usr/bin/env bash
set -o errexit

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# ¡NUEVA LÍNEA IMPORTANTE! Le da permiso de ejecución al script de arranque.
chmod +x ./start.sh