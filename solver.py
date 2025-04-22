"""
QA Scheduling Tool MVP - ソルバーモジュール

このモジュールは、QUBOモデルをシミュレーテッドアニーリングで解き、
結果をスケジュール形式に変換する機能を提供します。

主な機能：
- QUBO問題を解くためのシミュレーテッドアニーリングの実行
- 最適化結果の解析と人間可読なスケジュール形式への変換

主な関数：
- solve_qubo: dwave-nealを使用してQUBO問題を解く
- parse_sampleset: 最適化結果をスケジュール辞書に変換
"""

import neal


def solve_qubo(bqm, num_reads=100):
    """
    Simulated Annealing を用いてQUBOを解きます。
    
    パラメータ:
    ----------
    bqm : dimod.BinaryQuadraticModel
        解くべきQUBOモデル
    num_reads : int, optional (default=100)
        シミュレーテッドアニーリングの試行回数
        大きい値ほど良い解が見つかる可能性が高まりますが、計算時間も増加します
        
    戻り値:
    -------
    sampleset : dimod.SampleSet
        シミュレーテッドアニーリングの結果。エネルギー順に並べられたサンプルのセット
    """
    sampler = neal.SimulatedAnnealingSampler()
    sampleset = sampler.sample(bqm, num_reads=num_reads)
    return sampleset


def parse_sampleset(sampleset, tasks, people, slots):
    """
    dimod.SampleSet から最適解（最小エネルギーのサンプル）を取得し、
    人間可読なスケジュール形式に変換します。
    
    パラメータ:
    ----------
    sampleset : dimod.SampleSet
        solve_qubo関数から返されるサンプルセット
    tasks : list of (task_name, task_type)
        タスク名とタスクタイプのタプルのリスト
    people : list of str
        担当者名のリスト
    slots : int
        タイムスロットの数
        
    戻り値:
    -------
    schedule : dict
        {person: {slot: task_name}} 形式のスケジュール辞書
        person: 担当者名
        slot: タイムスロットインデックス (0-based)
        task_name: 割り当てられたタスク名、未割り当ての場合はNone
    energy : float
        最適解のエネルギー値（低いほど良い解）
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
