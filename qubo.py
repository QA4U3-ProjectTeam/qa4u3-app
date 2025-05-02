"""
QA Scheduling Tool MVP - QUBO定式化モジュール

このモジュールは、タスクスケジューリング問題をQUBOモデルに定式化する関数を提供します。
コンテキストスイッチコストを考慮した最適なスケジュール作成のための基盤となります。

定式化される制約：
1. 各タスクは1回実行されなければならない
2. 同一担当者は同時刻に1つ以上のタスクを実行できない
3. 異なるタイプのタスク間の切り替え（コンテキストスイッチ）にはコストがかかる
4. タスク種類と担当者の専門性が一致する場合は優先的に割り当てる

主な関数：
- build_qubo: タスク割り当て問題のQUBOモデルを構築する
"""

import dimod
import itertools


def build_qubo(tasks, people, slots,
               penalty_task=5.0,
               penalty_overlap=5.0,
               penalty_switch=1.0,
               reward_skill_match=2.0,
               base_cost=0.1):
    """
    タスクスケジューリング用のQUBOを構築します。
    
    パラメータ:
    ----------
    tasks : list of (task_name, task_type)
        タスク名とタスクタイプのタプルのリスト
    people : list of str
        担当者名のリスト
    slots : int
        タイムスロットの数
    penalty_task : float, optional (default=5.0)
        タスク実行回数制約のペナルティ重み
    penalty_overlap : float, optional (default=5.0)
        同時実行制約のペナルティ重み
    penalty_switch : float, optional (default=1.0)
        コンテキストスイッチ（異なるタイプのタスク間の切り替え）のコスト重み
    reward_skill_match : float, optional (default=2.0)
        タスク種類と担当者の専門性一致の報酬重み
    base_cost : float, optional (default=0.1)
        均一に適用される基本コスト（エネルギー縮退を防止）
        
    戻り値:
    -------
    bqm : dimod.BinaryQuadraticModel
        構築されたQUBOモデル
    
    変数表現:
    --------
    変数は(i, j, k)の3次元インデックスで表され、各要素は以下を意味します:
    - i: タスクのインデックス (0 to len(tasks)-1)
    - j: 担当者のインデックス (0 to len(people)-1)
    - k: タイムスロットのインデックス (0 to slots-1)
    
    値が1の場合、タスクiは担当者jによってタイムスロットkで実行されます。
    """
    bqm = dimod.BinaryQuadraticModel({}, {}, 0.0, dimod.BINARY)
    n_tasks = len(tasks)
    n_people = len(people)

    # 全変数に base_cost の線形バイアス
    for i in range(n_tasks):
        for j in range(n_people):
            for k in range(slots):
                bqm.add_linear((i, j, k), base_cost)

    # 各タスクは1回実行制約: A*(sum -1)^2
    for i in range(n_tasks):
        vars_i = [(i, j, k) for j in range(n_people) for k in range(slots)]
        # 線形項
        for v in vars_i:
            bqm.add_linear(v, -penalty_task)
        # 二次項
        for v1, v2 in itertools.combinations(vars_i, 2):
            bqm.add_quadratic(v1, v2, 2 * penalty_task)
        # 定数項（オフセット）
        bqm.offset += penalty_task

    # 同一担当者・同時刻は1タスク以下制約: B*sum*(sum-1) を sum^2 - sum で定式化
    for j in range(n_people):
        for k in range(slots):
            vars_jk = [(i, j, k) for i in range(n_tasks)]
            # 線形項
            for v in vars_jk:
                bqm.add_linear(v, -penalty_overlap)
            # 二次項
            for v1, v2 in itertools.combinations(vars_jk, 2):
                bqm.add_quadratic(v1, v2, 2 * penalty_overlap)

    # コンテキストスイッチコスト: タイプが異なるタスク間の切り替え
    for j in range(n_people):
        for k in range(slots - 1):
            for i1, i2 in itertools.product(range(n_tasks), repeat=2):
                if i1 != i2 and tasks[i1][1] != tasks[i2][1]:
                    bqm.add_quadratic((i1, j, k), (i2, j, k + 1), penalty_switch)
    
    # 新しい制約: タスク種類と担当者の専門性のマッチング
    for i in range(n_tasks):
        task_name, task_type = tasks[i]
        task_type_words = [word.strip() for word in task_type.replace('、', ',').split(',')]
        
        for j in range(n_people):
            person_name = people[j]
            # 担当者名とタスク種類のキーワードがマッチするか確認
            has_skill_match = False
            
            for keyword in task_type_words:
                if keyword in person_name:
                    has_skill_match = True
                    break
            
            if has_skill_match:
                # マッチする場合は、このタスクを担当者jに割り当てることにインセンティブを与える
                # （エネルギーを減少させるため、負の値を使用）
                for k in range(slots):
                    bqm.add_linear((i, j, k), -reward_skill_match)

    return bqm
