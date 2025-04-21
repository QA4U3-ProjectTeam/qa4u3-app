import dimod


def build_qubo(tasks, people, slots):
    """
    タスクスケジューリング用のQUBOを構築する雛形。
    tasks: list of (task_name, task_type)
    people: list of person_name
    slots: int (number of time slots)
    """
    # TODO: 実際のQUBO定式化ロジックを実装
    bqm = dimod.BinaryQuadraticModel({}, {}, 0.0, dimod.BINARY)
    return bqm
