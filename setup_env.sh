#!/usr/bin/env bash

# ログディレクトリ作成
mkdir -p logs
LOG_FILE="logs/setup_$(date +%Y%m%d_%H%M%S).log"

echo "Setup started at $(date)" | tee -a "$LOG_FILE"
echo "===== QA4U3 App Setup =====" | tee -a "$LOG_FILE"

# Pythonのインストール確認
echo "[Step 1/4] Checking Python..." | tee -a "$LOG_FILE"
python --version 2>&1 | tee -a "$LOG_FILE"
if [ $? -ne 0 ]; then
    echo "ERROR: Python not found. Please install Python." | tee -a "$LOG_FILE"
    read -p "Press any key to continue..."
    exit 1
fi

# 仮想環境作成
echo "[Step 2/4] Creating virtual environment..." | tee -a "$LOG_FILE"
python -m venv .venv 2>&1 | tee -a "$LOG_FILE"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment." | tee -a "$LOG_FILE"
    read -p "Press any key to continue..."
    exit 1
fi

# 仮想環境有効化
echo "[Step 3/4] Activating virtual environment..." | tee -a "$LOG_FILE"
source .venv/bin/activate 2>&1 | tee -a "$LOG_FILE"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment." | tee -a "$LOG_FILE"
    read -p "Press any key to continue..."
    exit 1
fi

# 依存パッケージインストール
echo "[Step 4/4] Installing packages..." | tee -a "$LOG_FILE"

echo "Upgrading pip..." | tee -a "$LOG_FILE"
python -m pip install --upgrade pip 2>&1 | tee -a "$LOG_FILE"

echo "Installing streamlit..." | tee -a "$LOG_FILE"
pip install streamlit>=1.20 2>&1 | tee -a "$LOG_FILE"

echo "Installing dimod..." | tee -a "$LOG_FILE"
pip install dimod>=0.10.11 2>&1 | tee -a "$LOG_FILE"

echo "Installing dwave-neal..." | tee -a "$LOG_FILE"
pip install dwave-neal==0.6.0 2>&1 | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "Setup completed successfully!" | tee -a "$LOG_FILE"
echo "Installation logs saved to: $LOG_FILE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Virtual environment is activated and packages are installed." | tee -a "$LOG_FILE"
echo "To run the application: streamlit run app.py" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "Setup completed at $(date)" >> "$LOG_FILE"
echo "All logs saved to: $LOG_FILE" >> "$LOG_FILE"

read -p "Press Enter to continue..."
