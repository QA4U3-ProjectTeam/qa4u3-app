# qa4u3-app

量子アニーリング（QA）シミュレーションを用いた小規模チームや個人向けのスケジューリングツールMVP

## 特長
- コンテキストスイッチコストを最小化するスケジュールを提案
- Python + StreamlitによりシンプルなWeb UIを提供
- QUBO定式化とdwave-nealによるシミュレーテッドアニーリングで解探索

## 動作環境
- Python 3.8 以上
- Windows / Mac / Linux

## 依存パッケージ
- streamlit
- dimod
- dwave-neal

## インストール
```bash
# リポジトリをクローン
git clone <リポジトリURL>
cd qa4u3-app

# 仮想環境作成・有効化
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 依存パッケージをインストール
pip install -r requirements.txt
```

## 実行方法
```bash
# Streamlitアプリを起動
streamlit run app.py
```

## プロジェクト構成例
```
qa4u3-app/
├── app.py            # Streamlitアプリ本体
├── qubo.py           # QUBO定式化ロジック
├── solver.py         # dwave-neal実行ラッパー
├── requirements.txt  # 依存パッケージ一覧
├── .gitignore
├── README.md
├── LICENSE
└── requirements.md   # 要件定義書
```

## ライセンス
本プロジェクトはMITライセンスの下で公開します。LICENSEファイルをご覧ください。