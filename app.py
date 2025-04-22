import streamlit as st
from qubo import build_qubo
from solver import solve_qubo, parse_sampleset


def validate_tasks(tasks_input):
    """タスク入力のバリデーションを行い、問題があればエラーメッセージを返す"""
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
    """担当者入力のバリデーションを行い、問題があればエラーメッセージを返す"""
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
    st.title('QA Scheduling Tool MVP')

    st.sidebar.header('入力')
    tasks_input = st.sidebar.text_area('タスク名と種類 (1行に「タスク名,種類」)', '')
    people_input = st.sidebar.text_area('担当者名 (1行1人)', '')
    
    # スロット数の上限・下限チェック
    MAX_SLOTS = 20  # スロット数の上限
    slots = st.sidebar.number_input('タイムスロット数', min_value=1, max_value=MAX_SLOTS, value=5)
    if slots > 10:
        st.sidebar.warning(f"スロット数が多いと計算時間が長くなる可能性があります（現在: {slots}）")

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
            if len(tasks) * len(people) * slots > 1000:
                st.warning("問題サイズが大きいため、計算に時間がかかる場合があります。")

            # QUBO定式化と解探索
            with st.spinner('スケジュールを計算中...'):
                bqm = build_qubo(tasks, people, slots)
                sampleset = solve_qubo(bqm)

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
            st.success(f'完了: エネルギー {energy}')
            
            # 完了タスク数の確認
            assigned_tasks = set()
            for person_tasks in schedule_dict.values():
                for task in person_tasks.values():
                    if task:
                        assigned_tasks.add(task)
            
            if len(assigned_tasks) < len(tasks):
                st.warning(f"注意: 全てのタスクが割り当てられていません。（割当: {len(assigned_tasks)}/{len(tasks)}）")
                
        except Exception as e:
            st.error(f'エラーが発生しました: {e}')


if __name__ == '__main__':
    main()