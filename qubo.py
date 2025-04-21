import dimod
import itertools


def build_qubo(tasks, people, slots,
               penalty_task=5.0,
               penalty_overlap=5.0,
               penalty_switch=1.0,
               base_cost=0.1):
    """
    タスクスケジューリング用のQUBOを構築
    tasks: list of (task_name, task_type)
    people: list of person_name
    slots: int (number of time slots)
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

    return bqm
