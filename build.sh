#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Crea explícitamente un entorno virtual
python3 -m venv .venv

# 2. Activa el entorno virtual. ¡Este es el paso clave que faltaba!
source .venv/bin/activate

# 3. Actualiza pip e instala las librerías DENTRO del entorno activado
pip install --upgrade pip
pip install -r requirements.txt