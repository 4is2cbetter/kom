from google.apputils import app
from ortools.linear_solver import pywraplp

class Node: 
  def __init__(self, id, mmem, mcpu, occupied):
        self.id = id
        self.mmem = mmem
        self.mcpu = mcpu
        self.occupied = occupied

class Topology:
    def __init__(self, tiers, nodes):
        self.nodes = nodes
        self.tiers = tiers
    

def setup_solver(topology, plan):
  
  solver = pywraplp.Solver('ew_solver', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
  vars_matrix = map(lambda node:  map(lambda tier_name: (solver.IntVar(0, node.mmem, ''), solver.IntVar(0, node.mcpu, '')), topology.tiers), topology.nodes)
  
  for i in range(0, len(plan)):
    cm = solver.Constraint(plan[i][0], plan[i][0])
    cc = solver.Constraint(plan[i][1], plan[i][1])
    for row in vars_matrix:
      cm.SetCoefficient(row[i][0], 1)
      cc.SetCoefficient(row[i][1], 1)
  for i in range(0, len(topology.nodes)):
    cm = solver.Constraint(0, topology.nodes[i].mmem)
    cc = solver.Constraint(0, topology.nodes[i].mcpu)
    for vars in vars_matrix[i]:
      cm.SetCoefficient(vars[0], 1)
      cc.SetCoefficient(vars[1], 1)

  expr = None
  for i in range(0, len(topology.nodes)):
    for j in range(0, len(topology.nodes[i].occupied)):
      if cmp(topology.nodes[i].occupied[j], (0, 0)) is not 0:
        if expr is None:
          expr=vars_matrix[i][j][0] + vars_matrix[i][j][1]
        else:
          expr=expr + vars_matrix[i][j][0] + vars_matrix[i][j][1]

  if expr is not None:
    solver.Maximize(expr)

  return (solver, vars_matrix)


def solve_n_print(solver, vars_matrix):
  solver.Solve()
  for i in range(0, len(vars_matrix)):
    for j in range(0, len(vars_matrix[i])):
      print "VM", i, "Tier", j, "= (", +vars_matrix[i][j][0].solution_value(), ",",vars_matrix[i][j][1].solution_value(), ")"

def main(_):

  plan=[(1024,1), (2500,1)]

  topology = Topology(['tier1', 'tier2'], [Node("VM1", 2048, 4, [(0, 0),  (512,1)]), Node("VM2", 2048, 4, [(512, 1),  (0, 0)])])

  (solver, vars_matrix) = setup_solver(topology, plan)
  solve_n_print(solver, vars_matrix)


if __name__ == '__main__':
  app.run()