"""
variacion_emisiones.py
Implementación de la Variación 2.c: Costo Fijo por Sobrepasar Umbral Diario de Emisiones (Formulación Big-M).
Tarea Computacional 1 - ILN250 (2s26).
"""

import pyomo.environ as pyo
import pandas as pd
from generar_parametros import obtener_parametros_generadores, obtener_parametros_sistema


def construir_modelo_emisiones(datos_instancia, F, M_big=3000.0):
    """
    Construye y retorna el modelo ConcreteModel de Pyomo con penalización Big-M por superar el umbral diario.
    """
    gen_params = obtener_parametros_generadores()
    sys_params = obtener_parametros_sistema()
    
    T = list(range(1, sys_params['T'] + 1))
    G = list(gen_params.keys())
    DIAS = list(range(1, 8))
    
    d_t = datos_instancia['d_t']
    lambda_t = datos_instancia['lambda_t']
    res_t = datos_instancia['res_t']
    G_bar_red = sys_params['G_bar_red']
    E_bar_day = sys_params['E_bar_day']  # 1500 tCO2
    
    m = pyo.ConcreteModel(name=f"Unit_Commitment_Emisiones_{F}")
    
    m.T = pyo.Set(initialize=T)
    m.G = pyo.Set(initialize=G)
    m.DIAS = pyo.Set(initialize=DIAS)
    
    m.u = pyo.Var(m.G, m.T, domain=pyo.Binary)
    m.v = pyo.Var(m.G, m.T, domain=pyo.NonNegativeReals, bounds=(0, 1))
    m.p = pyo.Var(m.G, m.T, domain=pyo.NonNegativeReals)
    m.g_red = pyo.Var(m.T, domain=pyo.NonNegativeReals, bounds=(0, G_bar_red))
    
    # Variable binaria indicadora de sobrepasar el umbral en el día d
    m.y_emiss = pyo.Var(m.DIAS, domain=pyo.Binary, doc="1 si el día d supera el umbral E_bar_day, 0 e.o.c.")
    
    # Restricciones térmicas
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
    
    def energy_balance_rule(model, t):
        return sum(model.p[g, t] for g in model.G) + model.g_red[t] == d_t[t]
    m.con_energy_balance = pyo.Constraint(m.T, rule=energy_balance_rule)
    
    def reserve_rule(model, t):
        unused_gen = sum(gen_params[g]['P_max'] * model.u[g, t] - model.p[g, t] for g in model.G)
        unused_grid = G_bar_red - model.g_red[t]
        return unused_gen + unused_grid >= res_t[t]
    m.con_reserve = pyo.Constraint(m.T, rule=reserve_rule)
    
    # Restricción Big-M de emisiones diarias
    def big_m_emissions_rule(model, d):
        horas_dia = range(24 * (d - 1) + 1, 24 * d + 1)
        emisiones_dia = sum(gen_params[g]['e_g'] * model.p[g, t] for g in model.G for t in horas_dia)
        return emisiones_dia - E_bar_day <= M_big * model.y_emiss[d]
    m.con_big_m_emiss = pyo.Constraint(m.DIAS, rule=big_m_emissions_rule, doc="Restricción Big-M umbral emisiones")
    
    # Función Objetivo: Costos base + suma(F * y_emiss_d)
    def objective_rule(model):
        costo_variables = sum(gen_params[g]['c_var'] * model.p[g, t] for g in model.G for t in model.T)
        costo_no_load = sum(gen_params[g]['c_nl'] * model.u[g, t] for g in model.G for t in model.T)
        costo_arranque = sum(gen_params[g]['c_start'] * model.v[g, t] for g in model.G for t in model.T)
        costo_red = sum(lambda_t[t] * model.g_red[t] for t in model.T)
        costo_penalidad_emisiones = sum(F * model.y_emiss[d] for d in model.DIAS)
        return costo_variables + costo_no_load + costo_arranque + costo_red + costo_penalidad_emisiones
    m.obj = pyo.Objective(rule=objective_rule, sense=pyo.minimize)
    
    return m


def barrido_F(datos_instancia, lista_F=None, solver_name='appsi_highs'):
    """
    Ejecuta un barrido sobre diferentes valores del costo fijo de penalización F.
    Devuelve DataFrame con el número de días sobre el umbral, costos operativos y emisiones.
    """
    if lista_F is None:
        lista_F = [
            0, 500000, 1000000, 2000000, 2500000, 3000000, 5000000, 10000000,
            25000000, 50000000, 75000000, 100000000, 120000000, 150000000, 200000000
        ]
        
    gen_params = obtener_parametros_generadores()
    solver = pyo.SolverFactory(solver_name)
    resultados = []
    
    for f_val in lista_F:
        m = construir_modelo_emisiones(datos_instancia, f_val)
        solver.solve(m)
        
        # Con F=0, y_emiss puede ser 0 o 1 indistintamente; evaluamos el exceso real
        dias_sobre_umbral = 0
        emisiones_por_dia = []
        for d in range(1, 8):
            hrs = range(24 * (d - 1) + 1, 24 * d + 1)
            e_d = sum(gen_params[g]['e_g'] * pyo.value(m.p[g, t]) for g in m.G for t in hrs)
            emisiones_por_dia.append(round(e_d, 2))
            if e_d > 1500.001:
                dias_sobre_umbral += 1
                
        costo_total = pyo.value(m.obj)
        # Costo de penalización efectivo
        costo_penalidad = f_val * dias_sobre_umbral
        costo_operativo = sum(
            sum(gen_params[g]['c_var'] * pyo.value(m.p[g, t]) + gen_params[g]['c_nl'] * pyo.value(m.u[g, t]) + gen_params[g]['c_start'] * pyo.value(m.v[g, t]) for g in m.G)
            + datos_instancia['lambda_t'][t] * pyo.value(m.g_red[t]) for t in m.T
        )
        g_red_tot = sum(pyo.value(m.g_red[t]) for t in m.T)
        
        resultados.append({
            'F_CLP': f_val,
            'dias_sobre_umbral': dias_sobre_umbral,
            'costo_total_CLP': costo_operativo + costo_penalidad,
            'costo_operativo_CLP': costo_operativo,
            'costo_penalidad_CLP': costo_penalidad,
            'importacion_red_MWh': round(g_red_tot, 2),
            'emisiones_dias': emisiones_por_dia,
            'emisiones_totales_semana_tCO2': round(sum(emisiones_por_dia), 2)
        })
        
    df_res = pd.DataFrame(resultados)
    return df_res
