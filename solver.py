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
