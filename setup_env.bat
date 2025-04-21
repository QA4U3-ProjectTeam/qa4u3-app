@echo off
REM 仮想環境作成
python -m venv .venv

REM 仮想環境有効化
call .\.venv\Scripts\activate

REM 依存パッケージをアップグレードしてインストール
pip install --upgrade pip
pip install -r requirements.txt
