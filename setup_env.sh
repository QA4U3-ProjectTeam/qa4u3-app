#!/usr/bin/env bash

# 仮想環境作成
python -m venv .venv

# 仮想環境有効化
source .venv/bin/activate

# 依存パッケージインストール
pip install --upgrade pip
pip install -r requirements.txt
