"""
generar_parametros.py
Módulo de generación de parámetros para la Tarea Computacional 1 - ILN250 (2s26).
Genera perfiles de demanda horaria, precios de la red externa y requerimientos de reserva.
Soporta las semillas especificadas (por defecto 392 y 142).
"""

import random
import numpy as np
import pandas as pd


def obtener_perfil_normalizado():
    """Retorna el perfil diario normalizado s_h para h = 0, ..., 23."""
    return [
        0.55, 0.50, 0.47, 0.45, 0.46, 0.52, 0.62, 0.75, 0.85, 0.88, 0.90, 0.89,
        0.86, 0.85, 0.86, 0.88, 0.92, 0.97, 1.00, 0.98, 0.90, 0.80, 0.70, 0.60
    ]


def obtener_parametros_generadores():
    """
    Retorna el diccionario con los parámetros técnicos y económicos fijos
    de las 5 unidades de generación térmica (Tabla 1 del enunciado).
    """
    return {
        'Gas_Base_1': {
            'P_max': 120.0, 'P_min': 40.0,
            'c_var': 45000.0, 'c_start': 2000000.0, 'c_nl': 300000.0,
            'R_g': 30.0, 'e_g': 0.35,
            'u_0': 1, 'p_0': 40.0
        },
        'Gas_Base_2': {
            'P_max': 100.0, 'P_min': 35.0,
            'c_var': 48000.0, 'c_start': 1800000.0, 'c_nl': 260000.0,
            'R_g': 30.0, 'e_g': 0.38,
            'u_0': 1, 'p_0': 35.0
        },
        'Diesel_Med_1': {
            'P_max': 60.0, 'P_min': 15.0,
            'c_var': 85000.0, 'c_start': 600000.0, 'c_nl': 120000.0,
            'R_g': 40.0, 'e_g': 0.65,
            'u_0': 0, 'p_0': 0.0
        },
        'Diesel_Med_2': {
            'P_max': 50.0, 'P_min': 12.0,
            'c_var': 90000.0, 'c_start': 500000.0, 'c_nl': 100000.0,
            'R_g': 40.0, 'e_g': 0.68,
            'u_0': 0, 'p_0': 0.0
        },
        'Peaker': {
            'P_max': 40.0, 'P_min': 8.0,
            'c_var': 120000.0, 'c_start': 200000.0, 'c_nl': 50000.0,
            'R_g': 40.0, 'e_g': 0.75,
            'u_0': 0, 'p_0': 0.0
        }
    }


def obtener_parametros_sistema():
    """Retorna parámetros globales del sistema y variaciones (Tabla 2)."""
    return {
        'T': 168,
        'G_bar_red': 80.0,      # MW capacidad máxima importación red
        'phi_reserva': 0.10,    # Fracción de reserva operativa
        # Batería (2.a)
        'S_bar': 200.0,         # Capacidad de energía en MWh
        'B_bar_ch': 60.0,       # Potencia máx de carga MW
        'B_bar_dis': 60.0,      # Potencia máx de descarga MW
        'eta_ch': 0.95,         # Eficiencia de carga
        'eta_dis': 0.95,        # Eficiencia de descarga
        'S_0': 100.0,           # Estado de carga inicial MWh
        # Respuesta de Demanda (2.b)
        'l_bar_h': 0.20,        # Fracción horaria máxima recortable
        'l_bar_s': 0.05,        # Fracción semanal máxima recortable
        # Emisiones (2.c)
        'E_bar_day': 1500.0     # Umbral diario de emisiones tCO2
    }


def generar_datos_instancia(semilla):
    """
    Genera la serie temporal de 168 horas para demanda dt, precio de red lambda_t
    y reserva mínima requerida Res_t en base a la semilla indicada.
    """
    random.seed(semilla)
    s_h = obtener_perfil_normalizado()
    P_peak = random.gauss(300.0, 0.05 * 300.0)  # P_peak ~ N(300, 15)
    
    registros = []
    for t in range(1, 169):
        dia = (t - 1) // 24 + 1
        hora = (t - 1) % 24
        gamma_dia = 1.0 if t <= 120 else 0.8
        
        eps_t = random.gauss(0.0, 0.03)
        dt = int(round(P_peak * gamma_dia * s_h[hora] * (1.0 + eps_t)))
        
        eta_t = random.gauss(0.0, 0.05)
        lambda_t = int(round((100000.0 + 90000.0 * s_h[hora]) * (1.0 + eta_t)))
        
        res_t = int(round(0.10 * dt))
        
        registros.append({
            't': t,
            'dia': dia,
            'hora': hora,
            'gamma_dia': gamma_dia,
            's_h': s_h[hora],
            'eps_t': eps_t,
            'd_t': dt,
            'eta_t': eta_t,
            'lambda_t': lambda_t,
            'res_t': res_t
        })
        
    df = pd.DataFrame(registros)
    return {
        'semilla': semilla,
        'P_peak': P_peak,
        'df': df,
        'd_t': df.set_index('t')['d_t'].to_dict(),
        'lambda_t': df.set_index('t')['lambda_t'].to_dict(),
        'res_t': df.set_index('t')['res_t'].to_dict()
    }


if __name__ == '__main__':
    for sem in [392, 142]:
        inst = generar_datos_instancia(sem)
        df = inst['df']
        print(f"\n=======================================================")
        print(f"ESTADÍSTICAS GENERADAS PARA SEMILLA = {sem}")
        print(f"=======================================================")
        print(f"Potencia Peak generada (P_peak): {inst['P_peak']:.2f} MW")
        print(f"Demanda horaria (MW):")
        print(f"  Mínimo:  {df['d_t'].min()} MW (t={df.loc[df['d_t'].idxmin(), 't']})")
        print(f"  Máximo:  {df['d_t'].max()} MW (t={df.loc[df['d_t'].idxmax(), 't']})")
        print(f"  Promedio:{df['d_t'].mean():.2f} MW")
        print(f"  Total Semanal: {df['d_t'].sum()} MWh")
        print(f"Precio de Red lambda_t (CLP/MWh):")
        print(f"  Mínimo:  {df['lambda_t'].min():,d} CLP/MWh")
        print(f"  Máximo:  {df['lambda_t'].max():,d} CLP/MWh")
        print(f"  Promedio:{df['lambda_t'].mean():,.2f} CLP/MWh")
        print(f"Reserva Operativa Res_t (MW):")
        print(f"  Mínimo:  {df['res_t'].min()} MW")
        print(f"  Máximo:  {df['res_t'].max()} MW")
        print(f"  Promedio:{df['res_t'].mean():.2f} MW")
