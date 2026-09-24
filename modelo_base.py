"""
modelo_base.py
Implementación en Pyomo del Modelo de Unit Commitment y Despacho Económico (Situación Inicial 1.b, 1.c, 1.d).
Tarea Computacional 1 - ILN250 (2s26).
"""

import pyomo.environ as pyo
import pandas as pd
from generar_parametros import obtener_parametros_generadores, obtener_parametros_sistema, generar_datos_instancia


def construir_modelo_base(datos_instancia):
    """
    Construye y retorna el modelo ConcreteModel de Pyomo para el caso base.
    """
    gen_params = obtener_parametros_generadores()
    sys_params = obtener_parametros_sistema()
    
    T = list(range(1, sys_params['T'] + 1))
    G = list(gen_params.keys())
    
    d_t = datos_instancia['d_t']
    lambda_t = datos_instancia['lambda_t']
    res_t = datos_instancia['res_t']
    G_bar_red = sys_params['G_bar_red']
    
    m = pyo.ConcreteModel(name="Unit_Commitment_Base")
    
    # Conjuntos
    m.T = pyo.Set(initialize=T, doc="Horizonte temporal en horas (1..168)")
    m.G = pyo.Set(initialize=G, doc="Conjunto de unidades generadoras térmicas")
    
    # Variables de decisión
    m.u = pyo.Var(m.G, m.T, domain=pyo.Binary, doc="Estado de encendido (1) o apagado (0)")
    m.v = pyo.Var(m.G, m.T, domain=pyo.NonNegativeReals, bounds=(0, 1), doc="Variable de arranque")
    m.p = pyo.Var(m.G, m.T, domain=pyo.NonNegativeReals, doc="Potencia generada en MW")
    m.g_red = pyo.Var(m.T, domain=pyo.NonNegativeReals, bounds=(0, G_bar_red), doc="Potencia importada de la red en MW")
    
    # Restricciones
    # 1. Lógica de arranque
    def startup_rule(model, g, t):
        u_prev = gen_params[g]['u_0'] if t == 1 else model.u[g, t - 1]
        return model.v[g, t] >= model.u[g, t] - u_prev
    m.con_startup = pyo.Constraint(m.G, m.T, rule=startup_rule, doc="Activación de costo de arranque")
    
    # 2. Límites técnicos de potencia
    def p_min_rule(model, g, t):
        return model.p[g, t] >= gen_params[g]['P_min'] * model.u[g, t]
    m.con_pmin = pyo.Constraint(m.G, m.T, rule=p_min_rule, doc="Límite de potencia mínima técnica")
    
    def p_max_rule(model, g, t):
        return model.p[g, t] <= gen_params[g]['P_max'] * model.u[g, t]
    m.con_pmax = pyo.Constraint(m.G, m.T, rule=p_max_rule, doc="Límite de potencia máxima técnica")
    
    # 3. Rampas de subida y bajada (con ajuste al arranque/parada)
    def ramp_up_rule(model, g, t):
        p_prev = gen_params[g]['p_0'] if t == 1 else model.p[g, t - 1]
        u_prev = gen_params[g]['u_0'] if t == 1 else model.u[g, t - 1]
        SU = max(gen_params[g]['P_min'], gen_params[g]['R_g'])
        return model.p[g, t] - p_prev <= gen_params[g]['R_g'] * u_prev + SU * (1 - u_prev)
    m.con_ramp_up = pyo.Constraint(m.G, m.T, rule=ramp_up_rule, doc="Rampa máxima de subida")
    
    def ramp_down_rule(model, g, t):
        p_prev = gen_params[g]['p_0'] if t == 1 else model.p[g, t - 1]
        SD = max(gen_params[g]['P_min'], gen_params[g]['R_g'])
        return p_prev - model.p[g, t] <= gen_params[g]['R_g'] * model.u[g, t] + SD * (1 - model.u[g, t])
    m.con_ramp_down = pyo.Constraint(m.G, m.T, rule=ramp_down_rule, doc="Rampa máxima de bajada")
    
    # 4. Balance de energía (cubrimiento de demanda horaria)
    def energy_balance_rule(model, t):
        return sum(model.p[g, t] for g in model.G) + model.g_red[t] == d_t[t]
    m.con_energy_balance = pyo.Constraint(m.T, rule=energy_balance_rule, doc="Balance instantáneo de energía")
    
    # 5. Reserva operativa mínima
    def reserve_rule(model, t):
        # Capacidad disponible no utilizada de unidades encendidas + importación no utilizada
        unused_gen = sum(gen_params[g]['P_max'] * model.u[g, t] - model.p[g, t] for g in model.G)
        unused_grid = G_bar_red - model.g_red[t]
        return unused_gen + unused_grid >= res_t[t]
    m.con_reserve = pyo.Constraint(m.T, rule=reserve_rule, doc="Requisito de reserva rodante/operativa")
    
    # Función Objetivo: Minimizar costo total de operación semanal
    def objective_rule(model):
        costo_variables = sum(gen_params[g]['c_var'] * model.p[g, t] for g in model.G for t in model.T)
        costo_no_load = sum(gen_params[g]['c_nl'] * model.u[g, t] for g in model.G for t in model.T)
        costo_arranque = sum(gen_params[g]['c_start'] * model.v[g, t] for g in model.G for t in model.T)
        costo_red = sum(lambda_t[t] * model.g_red[t] for t in model.T)
        return costo_variables + costo_no_load + costo_arranque + costo_red
    m.obj = pyo.Objective(rule=objective_rule, sense=pyo.minimize, doc="Costo total de operación [CLP]")
    
    return m


def resolver_modelo(modelo, solver_name='appsi_highs'):
    """Resuelve el modelo y devuelve resultados estructurados."""
    solver = pyo.SolverFactory(solver_name)
    results = solver.solve(modelo)
    return results


def extraer_resultados(modelo, datos_instancia):
    """Extrae métricas detalladas, series de tiempo y tablas resumen."""
    gen_params = obtener_parametros_generadores()
    T = list(modelo.T)
    G = list(modelo.G)
    
    d_t = datos_instancia['d_t']
    lambda_t = datos_instancia['lambda_t']
    res_t = datos_instancia['res_t']
    
    total_cost = pyo.value(modelo.obj)
    
    # Costos desagregados
    c_var_total = sum(gen_params[g]['c_var'] * pyo.value(modelo.p[g, t]) for g in G for t in T)
    c_nl_total = sum(gen_params[g]['c_nl'] * pyo.value(modelo.u[g, t]) for g in G for t in T)
    c_start_total = sum(gen_params[g]['c_start'] * pyo.value(modelo.v[g, t]) for g in G for t in T)
    c_red_total = sum(lambda_t[t] * pyo.value(modelo.g_red[t]) for t in T)
    
    # Generación y arranques por unidad
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
    
    # Serie horaria completa
    hourly_records = []
    for t in T:
        rec = {
            't': t,
            'dia': (t - 1) // 24 + 1,
            'hora': (t - 1) % 24,
            'demanda': d_t[t],
            'precio_red': lambda_t[t],
            'reserva_req': res_t[t],
            'g_red': pyo.value(modelo.g_red[t])
        }
        cap_online = 0.0
        for g in G:
            rec[f'p_{g}'] = pyo.value(modelo.p[g, t])
            rec[f'u_{g}'] = int(round(pyo.value(modelo.u[g, t])))
            rec[f'v_{g}'] = int(round(pyo.value(modelo.v[g, t])))
            if rec[f'u_{g}'] == 1:
                cap_online += gen_params[g]['P_max']
        
        # Reserva disponible total
        reserva_disp = (cap_online - sum(rec[f'p_{g}'] for g in G)) + (80.0 - rec['g_red'])
        rec['reserva_disponible'] = reserva_disp
        rec['holgura_reserva'] = reserva_disp - res_t[t]
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
        'df_hourly': df_hourly
    }
