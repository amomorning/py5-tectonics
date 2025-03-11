from pymoo.core.problem import ElementwiseProblem
from pymoo.core.variable import Binary
from pymoo.core.mixed import MixedVariableGA
from pymoo.algorithms.moo.nsga2 import RankAndCrowdingSurvival
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter
from pymoo.visualization.pcp import PCP
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import random

class BinaryChoice(ElementwiseProblem):
    def __init__(self, edges, num):
        vs = {i:Binary() for i in range(len(edges))}
        self.num = num
        self.edges = edges
        super().__init__(vars=vs, n_obj=3, n_constr=1)

    def _evaluate(self, x, out, *args, **kwargs):
        tmp_edges = [self.edges[i][:2] for i in range(len(self.edges)) if x[i]]
        graph = nx.from_edgelist(tmp_edges)

        if graph.number_of_nodes() != self.num or not nx.is_connected(graph):
            out["F"] = [float('inf'), float('inf'), float('inf')]
            out["G"] = 1
        else:
            tot = 0
            for i in range(self.num):
                for j in range(self.num):
                    tot += nx.shortest_path_length(graph, i, j)

            out["F"] = [
                tot/(self.num*self.num),
                len(tmp_edges),
                sum([x[i] * self.edges[i][2] for i in range(len(self.edges))])
            ]
            out["G"] = -1


N = 8
vertex = np.random.random((N, 2)) * 10
complete_graph = [(i, j, np.linalg.norm(vertex[i]-vertex[j])) for i in range(N) for j in range(i)]
print(f'Generate a complete graph with {len(complete_graph)} edges.')
print(f'Optimize a problem with {2**len(complete_graph)} status.')
problem = BinaryChoice(complete_graph, N)
algorithm = MixedVariableGA(pop_size=100, survival=RankAndCrowdingSurvival())

res = minimize(problem,
               algorithm,
               verbose=False)


def plot():

    cols = 4
    rows = int(np.floor(len(res.X) / cols))

    result = [(res.F[i][2], res.X[i]) for i in range(len(res.X))]
    result = sorted(result, key=lambda x: x[0])

    print(len(result))


    fig, ax = plt.subplots(rows, cols, figsize=(cols*3, rows*3))

    for j in range(cols*rows):
        ax.flat[j].scatter(vertex[:, 0], vertex[:, 1], c='k', zorder=10)
        for i in result[j][1]:
            x = result[j][1][i]
            if x:
                u, v, w = complete_graph[i]
                xx = [vertex[u][0], vertex[v][0]]
                yy = [vertex[u][1], vertex[v][1]]
                ax.flat[j].plot(xx, yy, 'r-')
    plt.show()

plot()

pareto = Scatter(angle=(20, 20))
pareto.add(res.F, plot_type="line", color="c", alpha=0.6)
pareto.add(res.F, facecolor="white", edgecolor="red")
pareto.show()

pcp = PCP(n_ticks=10,
           legend=(True, {'loc': "upper left"}),
          labels=["ave dist", "edge num", "total length"])
pcp.set_axis_style(color="k", alpha=0.7)
pcp.add(res.F, color="grey", alpha=0.5)
idx = random.randint(0, len(res.F) - 1)
pcp.add(res.F[idx], linewidth=5, color="red", label=f"Solution {idx}")
pcp.show()
