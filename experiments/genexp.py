import gurobipy as gr

m = gr.Model()

var1 = m.addVar(lb=-10, ub=10, name='v1', vtype=gr.GRB.CONTINUOUS)
var2 = m.addVar(lb=-10, ub=10, name='v2', vtype=gr.GRB.CONTINUOUS)
and_var = m.addVar(lb=-100, ub=100, name='and_var', vtype=gr.GRB.BINARY)
and_constr = m.addConstr(and_var == gr.and_(var1, var2), name='and_var')
m.addConstr(var1 == 1, 'force_val')
m.setObjective(and_var + var1 + var2, gr.GRB.MAXIMIZE)

m.optimize()
print('var1', var1.x)
print('var2', var2.x)
print('and_var', and_var.x)


def print_genconstr_stats(m: gr.Model, constr: gr.GenConstr):
    stats_str = ''
    if constr.GenConstrType == gr.GRB.GENCONSTR_ABS:
        lhs_var, rhs_var = m.getGenConstrAbs(constr)
        stats_str = f'{lhs_var.x} = |{rhs_var.x}|'
    elif constr.GenConstrType == gr.GRB.GENCONSTR_AND:
        lhs_var, rhs_var = m.getGenConstrAnd(constr)
        stats_str = f'{lhs_var.x} = {" && ".join([str(v.x) for v in rhs_var])}'
    elif constr.GenConstrType == gr.GRB.GENCONSTR_OR:
        lhs_var, rhs_var = m.getGenConstrOr(constr)
        stats_str = f'{lhs_var.x} = {" || ".join([str(v.x) for v in rhs_var])}'
    elif constr.GenConstrType == gr.GRB.GENCONSTR_MAX:
        lhs_var, rhs_var, const_op = m.getGenConstrMax(constr)
        max_strs = [str(v.x) for v in rhs_var]
        if const_op > -gr.GRB.INFINITY:
            max_strs += ['%.2f' % const_op]
        stats_str = f'{lhs_var.x} = max({" && ".join([str(v.x) for v in rhs_var])})'
    elif constr.GenConstrType == gr.GRB.GENCONSTR_MIN:
        lhs_var, rhs_var, const_op = m.getGenConstrMin(constr)
        min_strs = [str(v.x) for v in rhs_var]
        if const_op < gr.GRB.INFINITY:
            min_strs += ['%.2f' % const_op]
        stats_str = f'{lhs_var.x} = min({" && ".join([str(v.x) for v in rhs_var])})'
    print(stats_str)

def print_constr_expr(expr):
    if isinstance(expr, gr.GenExpr):
        return expr.vars.x
    elif isinstance(expr, gr.LinExpr):
        return expr.getValue()
    else:
        return expr.x

print_genconstr_stats(m, and_constr)
# print('constrabs_spec[lhs]', print_constr_expr(constrabs_spec._lhs))
# print('constrabs_spec[rhs]', print_constr_expr(constrabs_spec._rhs))
# print('constrsum_spec[lhs]', print_constr_expr(constrsum_spec._lhs))
# print('constrsum_spec[rhs]', print_constr_expr(constrsum_spec._rhs))
