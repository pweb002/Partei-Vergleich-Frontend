#!/bin/bash

# Zeigt alle ausgeführten Befehle im Terminal
set -x

# Setzt die CUDA-GPU auf 2
export CUDA_VISIBLE_DEVICES="1,2,3,4"

# Name der Conda-Umgebung
ENV_NAME="vllm"

# Prüfen, ob Conda installiert ist
if ! command -v conda &> /dev/null; then
    echo "Fehler: Conda ist nicht installiert! Bitte installiere Anaconda oder Miniconda."
    exit 1
fi

# Prüfen, ob die Conda-Umgebung existiert
if ! conda env list | grep -q "$ENV_NAME"; then
    echo "Conda-Umgebung '$ENV_NAME' existiert nicht. Erstelle sie..."
    conda create -n "$ENV_NAME" python=3.12 -y
fi

# Lade Conda-Umgebungen richtig
source "$(conda info --base)/etc/profile.d/conda.sh"

# Aktiviert die Conda-Umgebung
conda activate "$ENV_NAME"

# Prüfen, ob vllm installiert ist
if ! pip show vllm &> /dev/null; then
    echo "vllm ist nicht installiert. Installiere es..."
    pip install vllm
else
    echo "vllm ist bereits installiert."
fi

# Starte den vllm-Server mit dem Modell
echo "Starte den vllm-Server mit Qwen/Qwen2.5-1.5B-Instruct..."
vllm serve Qwen/Qwen2.5-1.5B-Instruct
