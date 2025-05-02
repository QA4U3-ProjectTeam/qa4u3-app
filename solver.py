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


def solve_qubo(bqm, num_reads=100, sweeps=1000, beta_range=None):
    """
    Simulated Annealing を用いてQUBOを解きます。
    
    パラメータ:
    ----------
    bqm : dimod.BinaryQuadraticModel
        解くべきQUBOモデル
    num_reads : int, optional (default=100)
        シミュレーテッドアニーリングの試行回数
        大きい値ほど良い解が見つかる可能性が高まりますが、計算時間も増加します
    sweeps : int, optional (default=1000)
        各試行におけるスイープ回数（変数更新の回数）
        大きい値ほど探索が詳細になりますが、計算時間も増加します
    beta_range : tuple(float, float), optional (default=None)
        逆温度パラメータの範囲 (beta_min, beta_max)
        Noneの場合は、ソルバーがデフォルト値を使用します
        
    戻り値:
    -------
    sampleset : dimod.SampleSet
        シミュレーテッドアニーリングの結果。エネルギー順に並べられたサンプルのセット
    """
    sampler = neal.SimulatedAnnealingSampler()
    
    # シミュレーテッドアニーリングのパラメータを設定
    params = {'num_reads': num_reads, 'num_sweeps': sweeps}
    if beta_range is not None:
        params['beta_range'] = beta_range
    
    # 問題サイズに基づいて自動的にスイープ回数を調整
    num_variables = len(bqm.variables)
    if num_variables > 500:
        params['num_sweeps'] = max(sweeps, 2000)  # より多くの変数がある場合、より多くのスイープが必要
    
    sampleset = sampler.sample(bqm, **params)
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
