import neal


def solve_qubo(bqm, num_reads=100):
    """
    Simulated Annealing を用いてQUBOを解く。
    bqm: dimod.BinaryQuadraticModel
    num_reads: 試行回数
    """
    sampler = neal.SimulatedAnnealingSampler()
    sampleset = sampler.sample(bqm, num_reads=num_reads)
    return sampleset


def parse_sampleset(sampleset, tasks, people, slots):
    """
    dimod.SampleSet から最適解（最初のサンプル）を取得し、
    (person, slot) -> task_name のスケジュール辞書とエネルギーを返す
    """
    # 最良サンプルを取得
    sample = sampleset.first.sample
    # 初期化
    schedule = {person: {k: None for k in range(slots)} for person in people}
    # 変数が1のものをタスク割当として登録
    for var, val in sample.items():
        if val == 1:
            i, j, k = var
            task_name = tasks[i][0]
            schedule[people[j]][k] = task_name
    # エネルギー値
    energy = sampleset.first.energy
    return schedule, energy
