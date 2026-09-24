"""
variacion_bateria.py
Implementación de la Variación 2.a: Incorporación de un Sistema de Almacenamiento de Energía (Batería BESS).
Tarea Computacional 1 - ILN250 (2s26).
"""

import pyomo.environ as pyo
import pandas as pd
from generar_parametros import obtener_parametros_generadores, obtener_parametros_sistema


def construir_modelo_bateria(datos_instancia):
    """
    Construye y retorna el modelo ConcreteModel de Pyomo con la batería BESS incorporada.
    """
    gen_params = obtener_parametros_generadores()
    sys_params = obtener_parametros_sistema()
    
    T = list(range(1, sys_params['T'] + 1))
    G = list(gen_params.keys())
    
    d_t = datos_instancia['d_t']
    lambda_t = datos_instancia['lambda_t']
    res_t = datos_instancia['res_t']
    G_bar_red = sys_params['G_bar_red']
    
    # Parámetros Batería
    S_bar = sys_params['S_bar']         # 200 MWh
    B_bar_ch = sys_params['B_bar_ch']   # 60 MW
    B_bar_dis = sys_params['B_bar_dis'] # 60 MW
    eta_ch = sys_params['eta_ch']       # 0.95
    eta_dis = sys_params['eta_dis']     # 0.95
    S_0 = sys_params['S_0']             # 100 MWh
    
    m = pyo.ConcreteModel(name="Unit_Commitment_Bateria")
    
    m.T = pyo.Set(initialize=T)
    m.G = pyo.Set(initialize=G)
    
    # Variables de generación térmica y red
    m.u = pyo.Var(m.G, m.T, domain=pyo.Binary)
    m.v = pyo.Var(m.G, m.T, domain=pyo.NonNegativeReals, bounds=(0, 1))
    m.p = pyo.Var(m.G, m.T, domain=pyo.NonNegativeReals)
    m.g_red = pyo.Var(m.T, domain=pyo.NonNegativeReals, bounds=(0, G_bar_red))
    
    # Variables de batería
    m.p_ch = pyo.Var(m.T, domain=pyo.NonNegativeReals, bounds=(0, B_bar_ch), doc="Potencia de carga MW")
    m.p_dis = pyo.Var(m.T, domain=pyo.NonNegativeReals, bounds=(0, B_bar_dis), doc="Potencia de descarga MW")
    m.soc = pyo.Var(m.T, domain=pyo.NonNegativeReals, bounds=(0, S_bar), doc="Estado de carga MWh")
    
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
    
    # Balance de estado de carga (SOC)
    def soc_balance_rule(model, t):
        soc_prev = S_0 if t == 1 else model.soc[t - 1]
        return model.soc[t] == soc_prev + eta_ch * model.p_ch[t] - model.p_dis[t] / eta_dis
    m.con_soc_balance = pyo.Constraint(m.T, rule=soc_balance_rule, doc="Dinámica de estado de carga de la batería")
    
    # Exigencia de SOC final al menos igual al inicial
    m.con_soc_final = pyo.Constraint(expr=m.soc[sys_params['T']] >= S_0, doc="SOC final >= SOC inicial")
    
    # Balance de energía modificado
    def energy_balance_bat_rule(model, t):
        return sum(model.p[g, t] for g in model.G) + model.g_red[t] + model.p_dis[t] == d_t[t] + model.p_ch[t]
    m.con_energy_balance = pyo.Constraint(m.T, rule=energy_balance_bat_rule, doc="Balance modificado de energía con BESS")
    
    # Reserva operativa
    def reserve_bat_rule(model, t):
        unused_gen = sum(gen_params[g]['P_max'] * model.u[g, t] - model.p[g, t] for g in model.G)
        unused_grid = G_bar_red - model.g_red[t]
        return unused_gen + unused_grid >= res_t[t]
    m.con_reserve = pyo.Constraint(m.T, rule=reserve_bat_rule)
    
    # Función Objetivo
    def objective_rule(model):
        costo_variables = sum(gen_params[g]['c_var'] * model.p[g, t] for g in model.G for t in model.T)
        costo_no_load = sum(gen_params[g]['c_nl'] * model.u[g, t] for g in model.G for t in model.T)
        costo_arranque = sum(gen_params[g]['c_start'] * model.v[g, t] for g in model.G for t in model.T)
        costo_red = sum(lambda_t[t] * model.g_red[t] for t in model.T)
        return costo_variables + costo_no_load + costo_arranque + costo_red
    m.obj = pyo.Objective(rule=objective_rule, sense=pyo.minimize)
    
    return m


def extraer_resultados_bateria(modelo, datos_instancia):
    """Extrae resultados de la variación con batería."""
    gen_params = obtener_parametros_generadores()
    T = list(modelo.T)
    G = list(modelo.G)
    d_t = datos_instancia['d_t']
    lambda_t = datos_instancia['lambda_t']
    
    total_cost = pyo.value(modelo.obj)
    c_var_total = sum(gen_params[g]['c_var'] * pyo.value(modelo.p[g, t]) for g in G for t in T)
    c_nl_total = sum(gen_params[g]['c_nl'] * pyo.value(modelo.u[g, t]) for g in G for t in T)
    c_start_total = sum(gen_params[g]['c_start'] * pyo.value(modelo.v[g, t]) for g in G for t in T)
    c_red_total = sum(lambda_t[t] * pyo.value(modelo.g_red[t]) for t in T)
    
    unidades_stats = {}
    for g in G:
        gen_tot = sum(pyo.value(modelo.p[g, t]) for t in T)
        starts = sum(round(pyo.value(modelo.v[g, t])) for t in T)
        hours_on = sum(round(pyo.value(modelo.u[g, t])) for t in T)
        c_v = sum(gen_params[g]['c_var'] * pyo.value(modelo.p[g, t]) for t in T)
        c_n = sum(gen_params[g]['c_nl'] * pyo.value(modelo.u[g, t]) for t in T)
        c_s = sum(gen_params[g]['c_start'] * pyo.value(modelo.v[g, t]) for t in T)
        emiss = sum(gen_params[g]['e_g'] * pyo.value(modelo.p[g, t]) for t in T)
        unidades_stats[g] = {
            'gen_total_MWh': gen_tot,
            'factor_planta': gen_tot / (gen_params[g]['P_max'] * 168.0),
            'horas_encendida': hours_on,
            'arranques': starts,
            'costo_var_CLP': c_v,
            'costo_nl_CLP': c_n,
            'costo_start_CLP': c_s,
            'costo_total_CLP': c_v + c_n + c_s,
            'emisiones_tCO2': emiss
        }
        
    grid_total_MWh = sum(pyo.value(modelo.g_red[t]) for t in T)
    grid_hours_used = sum(1 for t in T if pyo.value(modelo.g_red[t]) > 1e-3)
    
    e_ch_total = sum(pyo.value(modelo.p_ch[t]) for t in T)
    e_dis_total = sum(pyo.value(modelo.p_dis[t]) for t in T)
    
    hourly_records = []
    for t in T:
        rec = {
            't': t,
            'dia': (t - 1) // 24 + 1,
            'hora': (t - 1) % 24,
            'demanda': d_t[t],
            'precio_red': lambda_t[t],
            'g_red': pyo.value(modelo.g_red[t]),
            'p_ch': pyo.value(modelo.p_ch[t]),
            'p_dis': pyo.value(modelo.p_dis[t]),
            'soc': pyo.value(modelo.soc[t])
        }
        for g in G:
            rec[f'p_{g}'] = pyo.value(modelo.p[g, t])
            rec[f'u_{g}'] = int(round(pyo.value(modelo.u[g, t])))
            rec[f'v_{g}'] = int(round(pyo.value(modelo.v[g, t])))
        hourly_records.append(rec)
        
    df_hourly = pd.DataFrame(hourly_records)
    
    return {
        'total_cost': total_cost,
        'costos_desglosados': {
            'variable': c_var_total,
            'no_load': c_nl_total,
            'arranque': c_start_total,
            'red': c_red_total
        },
        'unidades': unidades_stats,
        'red': {
            'energia_total_MWh': grid_total_MWh,
            'horas_uso': grid_hours_used,
            'costo_total_CLP': c_red_total
        },
        'bateria': {
            'energia_cargada_MWh': e_ch_total,
            'energia_descargada_MWh': e_dis_total,
            'perdidas_eficiencia_MWh': e_ch_total - e_dis_total,
            'soc_final_MWh': pyo.value(modelo.soc[T[-1]])
        },
        'df_hourly': df_hourly
    }
