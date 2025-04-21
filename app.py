import streamlit as st
from qubo import build_qubo
from solver import solve_qubo, parse_sampleset


def main():
    st.title('QA Scheduling Tool MVP')

    st.sidebar.header('入力')
    tasks_input = st.sidebar.text_area('タスク名と種類 (1行に「タスク名,種類」)', '')
    people_input = st.sidebar.text_area('担当者名 (1行1人)', '')
    slots = st.sidebar.number_input('タイムスロット数', min_value=1, value=5)

    if st.sidebar.button('スケジュール作成'):
        try:
            # 入力解析
            tasks = []  # [(name, type)]形式にパース
            for line in tasks_input.strip().splitlines():
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 2:
                    tasks.append((parts[0], parts[1]))
            people = [p.strip() for p in people_input.strip().splitlines() if p.strip()]

            if not tasks or not people:
                st.error('タスクと担当者を正しく入力してください。')
                return

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
        except Exception as e:
            st.error(f'エラーが発生しました: {e}')


if __name__ == '__main__':
    main()