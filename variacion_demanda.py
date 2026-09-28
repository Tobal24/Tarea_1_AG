
import pyomo.environ as pyo
import pandas as pd
from generar_parametros import obtener_parametros_generadores, obtener_parametros_sistema


def construir_modelo_demanda(datos_instancia, c_shed):
    gen_params = obtener_parametros_generadores()
    sys_params = obtener_parametros_sistema()
    
    T = list(range(1, sys_params['T'] + 1))
    G = list(gen_params.keys())
    
    d_t = datos_instancia['d_t']
    lambda_t = datos_instancia['lambda_t']
    res_t = datos_instancia['res_t']
    G_bar_red = sys_params['G_bar_red']
    
    l_bar_h = sys_params['l_bar_h']  # 0.20
    l_bar_s = sys_params['l_bar_s']  # 0.05
    demanda_total_semanal = sum(d_t.values())
    
    m = pyo.ConcreteModel(name=f"Unit_Commitment_Demanda_{c_shed}")
    
    m.T = pyo.Set(initialize=T)
    m.G = pyo.Set(initialize=G)
    
    m.u = pyo.Var(m.G, m.T, domain=pyo.Binary)
    m.v = pyo.Var(m.G, m.T, domain=pyo.NonNegativeReals, bounds=(0, 1))
    m.p = pyo.Var(m.G, m.T, domain=pyo.NonNegativeReals)
    m.g_red = pyo.Var(m.T, domain=pyo.NonNegativeReals, bounds=(0, G_bar_red))
    
    m.r = pyo.Var(m.T, domain=pyo.NonNegativeReals, doc="Carga interrumpida en hora t [MW]")
    
    def startup_rule(model, g, t):
        u_prev = gen_params[g]['u_0'] if t == 1 else model.u[g, t - 1]
        return model.v[g, t] >= model.u[g, t] - u_prev
    m.con_startup = pyo.Constraint(m.G, m.T, rule=startup_rule)
    
    def p_min_rule(model, g, t):
        return model.p[g, t] >= gen_params[g]['P_min'] * model.u[g, t]
    m.con_pmin = pyo.Constraint(m.G, m.T, rule=p_min_rule)
    
    def p_max_rule(model, g, t):
        return model.p[g, t] <= gen_params[g]['P_max'] * model.u[g, t]
    m.con_pmax = pyo.Constraint(m.G, m.T, rule=p_max_rule)
    
    def ramp_up_rule(model, g, t):
        p_prev = gen_params[g]['p_0'] if t == 1 else model.p[g, t - 1]
        u_prev = gen_params[g]['u_0'] if t == 1 else model.u[g, t - 1]
        SU = max(gen_params[g]['P_min'], gen_params[g]['R_g'])
        return model.p[g, t] - p_prev <= gen_params[g]['R_g'] * u_prev + SU * (1 - u_prev)
    m.con_ramp_up = pyo.Constraint(m.G, m.T, rule=ramp_up_rule)
    
    def ramp_down_rule(model, g, t):
        p_prev = gen_params[g]['p_0'] if t == 1 else model.p[g, t - 1]
        SD = max(gen_params[g]['P_min'], gen_params[g]['R_g'])
        return p_prev - model.p[g, t] <= gen_params[g]['R_g'] * model.u[g, t] + SD * (1 - model.u[g, t])
    m.con_ramp_down = pyo.Constraint(m.G, m.T, rule=ramp_down_rule)
    
    # Límites de recorte de demanda
    def recorte_horario_rule(model, t):
        return model.r[t] <= l_bar_h * d_t[t]
    m.con_recorte_horario = pyo.Constraint(m.T, rule=recorte_horario_rule, doc="Máximo 20% de corte horario")
    
    m.con_recorte_semanal = pyo.Constraint(
        expr=sum(m.r[t] for t in m.T) <= l_bar_s * demanda_total_semanal,
        doc="Máximo 5% de corte semanal"
    )
    
    def energy_balance_rule(model, t):
        return sum(model.p[g, t] for g in model.G) + model.g_red[t] == d_t[t] - model.r[t]
    m.con_energy_balance = pyo.Constraint(m.T, rule=energy_balance_rule)
    
    def reserve_rule(model, t):
        unused_gen = sum(gen_params[g]['P_max'] * model.u[g, t] - model.p[g, t] for g in model.G)
        unused_grid = G_bar_red - model.g_red[t]
        return unused_gen + unused_grid >= res_t[t]
    m.con_reserve = pyo.Constraint(m.T, rule=reserve_rule)
    
    def objective_rule(model):
        costo_variables = sum(gen_params[g]['c_var'] * model.p[g, t] for g in model.G for t in model.T)
        costo_no_load = sum(gen_params[g]['c_nl'] * model.u[g, t] for g in model.G for t in model.T)
        costo_arranque = sum(gen_params[g]['c_start'] * model.v[g, t] for g in model.G for t in model.T)
        costo_red = sum(lambda_t[t] * model.g_red[t] for t in model.T)
        costo_recorte = sum(c_shed * model.r[t] for t in model.T)
        return costo_variables + costo_no_load + costo_arranque + costo_red + costo_recorte
    m.obj = pyo.Objective(rule=objective_rule, sense=pyo.minimize)
    
    return m


def barrido_c_shed(datos_instancia, lista_c_shed=None, solver_name='appsi_highs'):
    if lista_c_shed is None:
        lista_c_shed = [
            0, 20000, 40000, 45000, 50000, 60000, 70000, 80000, 85000, 90000,
            100000, 110000, 120000, 130000, 140000, 150000, 160000, 170000,
            180000, 185000, 190000, 195000, 200000, 220000
        ]
        
    solver = pyo.SolverFactory(solver_name)
    resultados = []
    
    for c in lista_c_shed:
        m = construir_modelo_demanda(datos_instancia, c)
        solver.solve(m)
        
        r_tot = sum(pyo.value(m.r[t]) for t in m.T)
        horas_con_corte = sum(1 for t in m.T if pyo.value(m.r[t]) > 1e-3)
        costo_total = pyo.value(m.obj)
        costo_corte = c * r_tot
        costo_op_puro = costo_total - costo_corte
        g_red_tot = sum(pyo.value(m.g_red[t]) for t in m.T)
        
        resultados.append({
            'c_shed': c,
            'recorte_total_MWh': round(r_tot, 2),
            'horas_con_recorte': horas_con_corte,
            'costo_total_CLP': costo_total,
            'costo_operativo_puro_CLP': costo_op_puro,
            'costo_penalizacion_recorte_CLP': costo_corte,
            'importacion_red_MWh': round(g_red_tot, 2)
        })
        
    df_res = pd.DataFrame(resultados)
    
    df_zero = df_res[df_res['recorte_total_MWh'] < 1e-2]
    c_umbral = df_zero['c_shed'].min() if not df_zero.empty else None
    
    return df_res, c_umbral
