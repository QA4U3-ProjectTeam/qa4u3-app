"""
QA Scheduling Tool MVP - メインアプリケーション

このモジュールはStreamlitを使用したWebベースUIを提供し、
QAスケジューリングツールのフロントエンド機能を実装します。
ユーザーはこのインターフェースを通じてタスク割り当て問題を設定・実行できます。

主な機能:
- タスクと担当者情報の入力フォーム
- サンプルデータ読み込み機能
- 入力バリデーション
- QUBO定式化と解探索の実行
- スケジュール結果の表示

依存モジュール:
- qubo.py: QUBO定式化ロジック
- solver.py: シミュレーテッドアニーリング実行とスケジュール解析
"""

import streamlit as st
from qubo import build_qubo
from solver import solve_qubo, parse_sampleset
import os
import glob


def load_sample_data(sample_file):
    """
    サンプルデータファイルからタスク、担当者、スロット情報を読み込みます。
    
    パラメータ:
    ----------
    sample_file : str
        サンプルデータファイルのパス
        
    戻り値:
    -------
    tasks : list of (task_name, task_type)
        タスク名とタスクタイプのタプルのリスト
    people : list of str
        担当者名のリスト
    slots : int
        タイムスロットの数
    """
    tasks = []
    people = []
    slots = 5  # デフォルト値
    
    section = None
    
    with open(sample_file, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            # コメント行や空行はスキップ
            if not line or line.startswith('#'):
                continue
            
            # セクション判定
            if "タスク" in line:
                section = "tasks"
                continue
            elif "担当者" in line:
                section = "people"
                continue
            elif "タイムスロット" in line:
                section = "slots"
                continue
            
            # データ読み込み
            if section == "tasks":
                parts = line.split(',')
                if len(parts) >= 2:
                    tasks.append((parts[0].strip(), parts[1].strip()))
            elif section == "people":
                people.append(line)
            elif section == "slots":
                try:
                    slots = int(line)
                except ValueError:
                    pass
    
    return tasks, people, slots


def load_csv_data(csv_file):
    """
    CSVファイルからタスク、担当者、スロット情報を読み込みます。
    1つのCSVファイル内の各セクションを識別して読み込みます。
    
    パラメータ:
    ----------
    csv_file : file object
        CSVファイルオブジェクト
        
    戻り値:
    -------
    tasks : list of (task_name, task_type)
        タスク名とタスクタイプのタプルのリスト
    people : list of str
        担当者名のリスト
    slots : int
        タイムスロットの数
    """
    import pandas as pd
    import io
    
    # ファイル内容を読み込む
    content = csv_file.read()
    if isinstance(content, bytes):
        content = content.decode('utf-8')
    
    # 初期値設定
    tasks = []
    people = []
    slots = 5  # デフォルト値
    
    # セクション分けのためのマーカー
    section = None
    lines = content.splitlines()
    
    # テンポラリストレージ
    section_data = {
        "tasks": [],
        "people": [],
        "config": []
    }
    
    for line in lines:
        line = line.strip()
        # 空行はスキップ
        if not line:
            continue
            
        # セクションマーカーをチェック - 大文字小文字を区別せず、空白も許容
        line_lower = line.lower()
        if "[tasks]" in line_lower or "#tasks" in line_lower:
            section = "tasks"
            continue
        elif "[people]" in line_lower or "#people" in line_lower:
            section = "people"
            continue
        elif "[config]" in line_lower or "#config" in line_lower:
            section = "config"
            continue
        
        # 有効なセクションの場合、データを保存
        if section in section_data:
            section_data[section].append(line)
    
    # セクションデータが空の場合（標準CSVフォーマット）
    if not any(section_data.values()):
        # 従来の方法：最初の列をタスク名、2番目の列をタスク種類として扱う
        df = pd.read_csv(io.StringIO(content))
        if len(df.columns) >= 2:
            tasks = list(zip(df.iloc[:, 0], df.iloc[:, 1]))
        return tasks, people, slots
    
    # タスクデータの処理
    if section_data["tasks"]:
        try:
            # 先頭行がヘッダーかどうかを確認
            task_lines = section_data["tasks"]
            header_line = task_lines[0].lower() if task_lines else ""
            
            if "タスク名" in header_line and "タスク種類" in header_line:
                # ヘッダー行がある場合、2行目以降を処理
                for line in task_lines[1:]:
                    if ',' in line:
                        parts = line.split(',')
                        if len(parts) >= 2:
                            task_name = parts[0].strip()
                            task_type = parts[1].strip()
                            if task_name and task_type:
                                tasks.append((task_name, task_type))
            else:
                # ヘッダーがない場合、すべての行を処理
                for line in task_lines:
                    if ',' in line:
                        parts = line.split(',')
                        if len(parts) >= 2:
                            task_name = parts[0].strip()
                            task_type = parts[1].strip()
                            if task_name and task_type:
                                tasks.append((task_name, task_type))
        except Exception as e:
            print(f"タスクデータ処理中にエラー: {e}")
            # 例外発生時のフォールバック処理
            for line in section_data["tasks"]:
                if line.startswith('#') or ',' not in line:  # コメント行やヘッダー行（カンマがない）はスキップ
                    continue
                parts = line.split(',')
                if len(parts) >= 2:
                    task_name = parts[0].strip()
                    task_type = parts[1].strip()
                    if task_name and task_type and not (task_name.lower() == "タスク名" and task_type.lower() == "タスク種類"):
                        tasks.append((task_name, task_type))
    
    # 担当者データの処理
    for line in section_data["people"]:
        # コメント行はスキップ
        if line.startswith('#'):
            continue
        parts = line.split(',')
        person = parts[0].strip()
        if person:
            people.append(person)
    
    # 設定データの処理
    for line in section_data["config"]:
        # コメント行はスキップ
        if line.startswith('#'):
            continue
        parts = line.split(',')
        if len(parts) >= 2:
            key = parts[0].strip()
            value = parts[1].strip()
            if key.lower() == "slots":
                try:
                    slots = int(value)
                except ValueError:
                    pass
    
    # デバッグ情報
    print(f"タスクデータ行数: {len(section_data['tasks']) if 'tasks' in section_data else 0}")
    print(f"読み込まれたタスク数: {len(tasks)}")
    print(f"読み込まれた担当者数: {len(people)}")
    print(f"設定されたスロット数: {slots}")
    
    return tasks, people, slots


def validate_tasks(tasks_input):
    """
    タスク入力のバリデーションを行い、問題があればエラーメッセージを返します。
    
    パラメータ:
    ----------
    tasks_input : str
        タスク入力テキスト（各行が「タスク名,種類」の形式）
        
    戻り値:
    -------
    error_msg : str or None
        エラーメッセージ（問題がない場合はNone）
    tasks : list of (task_name, task_type)
        パース済みのタスクリスト（エラーがある場合は空リスト）
    """
    if not tasks_input.strip():
        return "タスクが入力されていません。", []
    
    tasks = []  # [(name, type)]形式にパース
    seen_tasks = set()  # タスク名の重複チェック用
    
    for line_num, line in enumerate(tasks_input.strip().splitlines(), 1):
        parts = [p.strip() for p in line.split(',')]
        
        # 形式チェック
        if len(parts) < 2:
            return f"行 {line_num}: タスク形式が不正です。'タスク名,種類' の形式で入力してください。", []
        
        task_name, task_type = parts[0], parts[1]
        
        # 空の値チェック
        if not task_name:
            return f"行 {line_num}: タスク名を入力してください。", []
        if not task_type:
            return f"行 {line_num}: タスク種類を入力してください。", []
        
        # 重複チェック
        if task_name in seen_tasks:
            return f"タスク名 '{task_name}' が重複しています。タスク名は一意にしてください。", []
        
        seen_tasks.add(task_name)
        tasks.append((task_name, task_type))
    
    return None, tasks


def validate_people(people_input):
    """
    担当者入力のバリデーションを行い、問題があればエラーメッセージを返します。
    
    パラメータ:
    ----------
    people_input : str
        担当者入力テキスト（各行に1人の担当者名）
        
    戻り値:
    -------
    error_msg : str or None
        エラーメッセージ（問題がない場合はNone）
    people : list of str
        パース済みの担当者リスト（エラーがある場合は空リスト）
    """
    if not people_input.strip():
        return "担当者が入力されていません。", []
    
    people = []
    seen_people = set()  # 担当者名の重複チェック用
    
    for line_num, line in enumerate(people_input.strip().splitlines(), 1):
        person = line.strip()
        
        # 空の値チェック
        if not person:
            continue
        
        # 重複チェック
        if person in seen_people:
            return f"担当者名 '{person}' が重複しています。担当者名は一意にしてください。", []
        
        seen_people.add(person)
        people.append(person)
    
    if not people:
        return "有効な担当者が入力されていません。", []
    
    return None, people


def main():
    """
    メイン関数：Streamlitアプリケーションのエントリポイント
    
    アプリケーションの流れ:
    1. UI要素の表示（タイトル、入力フォーム、サンプルデータ選択など）
    2. 「スケジュール作成」ボタン押下時の処理
       - 入力バリデーション
       - QUBO定式化
       - シミュレーテッドアニーリング実行
       - 結果表示
    """
    st.title('QA Scheduling Tool MVP')

    st.sidebar.header('入力')
    
    # --- Excel アップロード -------------------------------------------------
    uploaded_file = st.sidebar.file_uploader(
        "Excel (QA4U3.xlsx など) をアップロード",
        type=["xlsx", "xls", "csv"]
    )

    if uploaded_file is not None:
        import pandas as pd

        try:
            # 期待フォーマット:
            #   シート "Tasks":   Task, Type
            #   シート "People":  Name
            #   シート "Config":  Key | Value  （例: Slots | 5）
            if uploaded_file.name.endswith('.csv'):
                # CSVファイルの場合 - 拡張形式に対応
                tasks, people, slots = load_csv_data(uploaded_file)
            else:
                # Excelファイルの場合
                xl = pd.ExcelFile(uploaded_file)

                df_tasks = xl.parse("Tasks")
                df_people = xl.parse("People")
                df_conf = xl.parse("Config")

                tasks = list(df_tasks.itertuples(index=False, name=None))  # [(Task, Type), ...]
                people = df_people["Name"].dropna().tolist()
                slots = int(df_conf.query("Key == 'Slots'")["Value"].iloc[0])

            # テキストエリアへ反映して既存バリデータを再利用
            st.session_state["tasks_input"] = "\n".join(f"{t},{ty}" for t, ty in tasks)
            st.session_state["tasks_input"] = "\n".join(f"{t},{ty}" for t, ty in tasks)
            st.session_state["people_input"] = "\n".join(people)
            st.session_state["slots"] = slots

            st.success(f"ファイルを読み込みました: タスク {len(tasks)} 件, 担当者 {len(people)} 名, スロット {slots}")
        except Exception as e:
            st.error(f"ファイル読込に失敗しました: {e}")
    
    # サンプルデータ選択オプション
    sample_files = glob.glob(os.path.join('samples', '*.txt'))
    if sample_files:
        st.sidebar.subheader('サンプルデータ')
        selected_sample = st.sidebar.selectbox(
            'サンプルデータを選択',
            ['なし'] + [os.path.basename(f) for f in sample_files]
        )
        
        if selected_sample != 'なし':
            if st.sidebar.button('サンプルデータを読み込む'):
                sample_path = os.path.join('samples', selected_sample)
                tasks, people, slots = load_sample_data(sample_path)
                
                # サンプルデータを表示
                st.sidebar.subheader('読み込んだサンプルデータ')
                st.sidebar.markdown(f'**タスク数**: {len(tasks)}')
                st.sidebar.markdown(f'**担当者数**: {len(people)}')
                st.sidebar.markdown(f'**タイムスロット数**: {slots}')
                
                # フォームにデータをセット
                tasks_input = '\n'.join([f"{t[0]},{t[1]}" for t in tasks])
                people_input = '\n'.join(people)
                
                # キャッシュに保存
                st.session_state['tasks_input'] = tasks_input
                st.session_state['people_input'] = people_input
                st.session_state['slots'] = slots
    
    # 入力フォーム（サンプルデータがあれば反映）
    tasks_input = st.sidebar.text_area(
        'タスク名と種類 (1行に「タスク名,種類」)', 
        value=st.session_state.get('tasks_input', '')
    )
    people_input = st.sidebar.text_area(
        '担当者名 (1行1人)', 
        value=st.session_state.get('people_input', '')
    )
    
    # スロット数の上限・下限チェック
    MAX_SLOTS = 20  # スロット数の上限
    slots = st.sidebar.number_input(
        'タイムスロット数', 
        min_value=1, 
        max_value=MAX_SLOTS, 
        value=st.session_state.get('slots', 5)
    )
    if slots > 10:
        st.sidebar.warning(f"スロット数が多いと計算時間が長くなる可能性があります（現在: {slots}）")
    
    # 詳細設定を表示するための展開可能なセクション
    with st.sidebar.expander("シミュレーテッドアニーリング詳細設定"):
        st.caption("これらの設定はシミュレーテッドアニーリングの性能に影響します。デフォルト値でも十分な結果が得られます。")
        
        num_reads = st.number_input(
            '試行回数 (num_reads)', 
            min_value=10, 
            max_value=1000, 
            value=100, 
            help="多いほど良い解が見つかる可能性が高まりますが、計算時間も増加します"
        )
        
        sweeps = st.number_input(
            'スイープ回数 (num_sweeps)', 
            min_value=100, 
            max_value=10000, 
            value=1000, 
            help="1回の試行における変数更新回数。多いほど探索が詳細になりますが、計算時間も増加します"
        )
        
        use_custom_beta = st.checkbox(
            '逆温度パラメータを手動設定', 
            value=False, 
            help="オンにすると温度スケジュールを手動で制御できます"
        )
        
        beta_min = beta_max = None
        if use_custom_beta:
            beta_min = st.number_input(
                '最小逆温度 (beta_min)', 
                min_value=0.01, 
                max_value=10.0, 
                value=0.1, 
                format="%.2f",
                help="低い値は高温で、より広い探索を行います"
            )
            
            beta_max = st.number_input(
                '最大逆温度 (beta_max)', 
                min_value=1.0, 
                max_value=50.0, 
                value=10.0, 
                format="%.2f",
                help="高い値は低温で、より局所的な探索を行います"
            )
            
            if beta_min >= beta_max:
                st.warning("最小逆温度は最大逆温度より小さい値に設定してください")
    
    # QUBOパラメータ設定を表示するためのエキスパンダー
    with st.sidebar.expander("QUBOモデルパラメータ設定"):
        st.caption("これらの設定はスケジューリングの優先度に影響します。")
        
        penalty_task = st.number_input(
            'タスク実行回数制約 (penalty_task)', 
            min_value=1.0, 
            max_value=20.0, 
            value=5.0, 
            format="%.1f",
            help="各タスクを1回だけ実行する制約の重み"
        )
        
        penalty_overlap = st.number_input(
            '同時実行制約 (penalty_overlap)', 
            min_value=1.0, 
            max_value=20.0, 
            value=5.0, 
            format="%.1f",
            help="同じ担当者が同じ時間に複数のタスクを実行できない制約の重み"
        )
        
        penalty_switch = st.number_input(
            'コンテキストスイッチコスト (penalty_switch)', 
            min_value=0.1, 
            max_value=10.0, 
            value=1.0, 
            format="%.1f",
            help="異なるタイプのタスク間の切り替えコストの重み。大きいほど同種タスクを連続して配置します"
        )
        
        reward_skill_match = st.number_input(
            'スキルマッチング報酬 (reward_skill_match)', 
            min_value=0.0, 
            max_value=10.0, 
            value=2.0, 
            format="%.1f",
            help="タスク種類と担当者の専門性が一致する場合の報酬の重み。大きいほど専門性に応じた割り当てになります"
        )

    if st.sidebar.button('スケジュール作成'):
        try:
            # タスク入力のバリデーション
            tasks_error, tasks = validate_tasks(tasks_input)
            if tasks_error:
                st.error(tasks_error)
                return
                
            # 担当者入力のバリデーション
            people_error, people = validate_people(people_input)
            if people_error:
                st.error(people_error)
                return

            # 問題サイズのチェック
            problem_size = len(tasks) * len(people) * slots
            if problem_size > 1000:
                st.warning(f"問題サイズが大きいため、計算に時間がかかる場合があります。(変数数: {problem_size})")

            # QUBO定式化と解探索
            with st.spinner('スケジュールを計算中...'):
                # 設定したQUBOパラメータを渡す
                bqm = build_qubo(
                    tasks, 
                    people, 
                    slots,
                    penalty_task=penalty_task,
                    penalty_overlap=penalty_overlap,
                    penalty_switch=penalty_switch,
                    reward_skill_match=reward_skill_match
                )
                
                # シミュレーテッドアニーリングのパラメータを設定
                beta_range = None
                if use_custom_beta and beta_min is not None and beta_max is not None and beta_min < beta_max:
                    beta_range = (beta_min, beta_max)
                
                sampleset = solve_qubo(bqm, num_reads=num_reads, sweeps=sweeps, beta_range=beta_range)

            # 結果解析
            schedule_dict, energy = parse_sampleset(sampleset, tasks, people, slots)

            # 結果表示
            st.subheader('スケジュール結果')
            import pandas as pd
            df = pd.DataFrame(schedule_dict)
            # タイムスロットを1-basedにし、行ラベルに設定
            df.index = df.index + 1
            df.index.name = 'タイムスロット'
            st.table(df)
            st.success(f'完了: エネルギー {energy:.4f}')
            
            # CSV ダウンロード機能
            if st.button("結果を CSV でダウンロード"):
                import io
                csv = df.to_csv(index=True).encode("utf-8")
                st.download_button("Download schedule.csv", data=csv, file_name="schedule.csv", mime="text/csv")
            
            # 完了タスク数の確認
            assigned_tasks = set()
            for person_tasks in schedule_dict.values():
                for task in person_tasks.values():
                    if task:
                        assigned_tasks.add(task)
            
            if len(assigned_tasks) < len(tasks):
                st.warning(f"注意: 全てのタスクが割り当てられていません。（割当: {len(assigned_tasks)}/{len(tasks)}）")
                st.info("タスク数がタイムスロット数×担当者数より多い場合、全てのタスクを割り当てることはできません。")
            
            # 使用した計算設定の表示
            st.subheader("計算設定")
            st.markdown(f"""
            - **問題サイズ**: {problem_size} 変数 ({len(tasks)} タスク × {len(people)} 担当者 × {slots} スロット)
            - **試行回数**: {num_reads}
            - **スイープ回数**: {sweeps}
            - **逆温度範囲**: {"カスタム設定" if beta_range else "デフォルト"}
            """)
                
        except Exception as e:
            st.error(f'エラーが発生しました: {e}')


if __name__ == '__main__':
    main()