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

## 仮想環境セットアップスクリプト

- **Windows**:
  ```bash
  .\setup_env.bat
  ```
- **macOS/Linux**:
  ```bash
  chmod +x setup_env.sh
  ./setup_env.sh
  ```

## 実行方法
```bash
# Streamlitアプリを起動
streamlit run app.py
```

## ドキュメント一覧
- **USAGE_GUIDE.md** - 詳細な使用方法と応用テクニックの解説
- **FAQ.md** - よくある質問と回答
- **requirements.md** - 要件定義書
- **ROADMAP.md** - 開発ロードマップと進捗状況

## サンプルデータ
`samples/` ディレクトリに、アプリケーションのテストに使用できる以下のサンプルデータが含まれています：

- **small_case.txt** - 小規模な基本テストケース
- **medium_case.txt** - 中規模の実践的テストケース
- **edge_case.txt** - タスク数が処理能力を超えるエッジケース
- **context_switch_case.txt** - コンテキストスイッチ効果の検証用ケース

サンプルデータは、アプリケーション内の「サンプルデータを選択」ドロップダウンから利用できます。

## プロジェクト構成
```
qa4u3-app/
├── app.py            # Streamlitアプリ本体
├── qubo.py           # QUBO定式化ロジック
├── solver.py         # dwave-neal実行ラッパー
├── requirements.txt  # 依存パッケージ一覧
├── .gitignore
├── README.md
├── USAGE_GUIDE.md    # 使用方法ガイド
├── FAQ.md            # よくある質問と回答
├── ROADMAP.md        # 開発ロードマップ
├── requirements.md   # 要件定義書
├── LICENSE
├── setup_env.bat     # Windows環境構築スクリプト
├── setup_env.sh      # Linux/Mac環境構築スクリプト
├── logs/             # 実行ログ
└── samples/          # サンプルデータ
```

## ライセンス
本プロジェクトはMITライセンスの下で公開します。LICENSEファイルをご覧ください。