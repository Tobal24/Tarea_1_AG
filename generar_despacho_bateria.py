"""
generar_despacho_bateria.py
Genera el gráfico de despacho económico apilado y reserva operativa para la Variación 2.a (Batería).
Estructura idéntica a la Figura 2 (1.d) del caso base para permitir comparación directa.
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from generar_parametros import (
    generar_datos_instancia,
    obtener_parametros_generadores,
    obtener_parametros_sistema
)
from variacion_bateria import construir_modelo_bateria, extraer_resultados_bateria
from modelo_base import resolver_modelo

# Estilo gráfico consistente
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#cccccc'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.5


def generar_grafico_despacho_bateria(semilla=534, guardar_csv=True):
    fig_dir = 'figuras'
    os.makedirs(fig_dir, exist_ok=True)
    
    # 1. Obtener datos y resolver modelo
    datos = generar_datos_instancia(semilla)
    gen_params = obtener_parametros_generadores()
    sys_params = obtener_parametros_sistema()
    
    m_bat = construir_modelo_bateria(datos)
    resolver_modelo(m_bat)
    res_bat = extraer_resultados_bateria(m_bat, datos)
    df = res_bat['df_hourly']
    
    # 2. Calcular reserva requerida y disponible
    res_req = [datos['res_t'][t] for t in df['t']]
    res_disp = []
    for _, row in df.iterrows():
        cap_online = sum(gen_params[g]['P_max'] * row[f'u_{g}'] for g in gen_params)
        gen_actual = sum(row[f'p_{g}'] for g in gen_params)
        disp = (cap_online - gen_actual) + (sys_params['G_bar_red'] - row['g_red'])
        res_disp.append(disp)
        
    df['reserva_req'] = res_req
    df['reserva_disponible'] = res_disp
    
    if guardar_csv:
        csv_path = os.path.join(fig_dir, f'despacho_horario_bateria_sem_{semilla}.csv')
        df.to_csv(csv_path, index=False)
        print(f"Datos horarios guardados en: {csv_path}")

    # 3. Gráfico comparativo
    t = df['t']
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8), sharex=True, gridspec_kw={'height_ratios': [2.5, 1.2]})
    
    # Colores coherentes con el caso base
    colores = {
        'Gas_Base_1': '#2ca02c',    # Verde
        'Gas_Base_2': '#8c564b',    # Marrón / Oliva
        'Diesel_Med_1': '#ff7f0e',  # Naranja
        'Diesel_Med_2': '#bcbd22',  # Amarillo verdoso
        'Peaker': '#9467bd',        # Morado
        'Red': '#d62728',           # Rojo
        'Bateria_Diss': '#17becf'       # Turquesa / Cian
    }
    
    y_stack = [
        df['p_Gas_Base_1'],
        df['p_Gas_Base_2'],
        df['p_Diesel_Med_1'],
        df['p_Diesel_Med_2'],
        df['p_Peaker'],
        df['g_red'],
        df['p_dis']
    ]
    etiquetas = [
        'Gas_Base_1',
        'Gas_Base_2',
        'Diesel_Med_1',
        'Diesel_Med_2',
        'Peaker',
        'Importación Red',
        r'Descarga Batería $p_{dis,t}$'
    ]
    colors_list = [
        colores['Gas_Base_1'],
        colores['Gas_Base_2'],
        colores['Diesel_Med_1'],
        colores['Diesel_Med_2'],
        colores['Peaker'],
        colores['Red'],
        colores['Bateria_Diss']
    ]
    
    # Subplot 1: Despacho Apilado
    ax1.stackplot(t, y_stack, labels=etiquetas, colors=colors_list, alpha=0.85)
    ax1.plot(t, df['demanda'], color='black', lw=2.0, linestyle='--', label=r'Demanda Fábrica $d_t$')
    ax1.plot(t, df['demanda'] + df['p_ch'], color='#003366', lw=1.5, linestyle=':', label=r'Demanda Total + Carga ($d_t + p_{ch,t}$)')
    
    ax1.set_ylabel('Potencia Despachada [MW]', fontsize=11, fontweight='bold')
    ax1.set_title(f'Despacho Económico y Compromiso con Sistema de Almacenamiento - Variación 2.a (Semilla {semilla})', fontsize=13, fontweight='bold')
    ax1.legend(loc='upper right', ncol=4, framealpha=0.9, fontsize=9)
    ax1.grid(True)
    
    # Subplot 2: Reserva Operativa
    ax2.plot(t, df['reserva_req'], color='#1f77b4', lw=1.8, label=r'Reserva Requerida $Res_t$ [MW]')
    ax2.plot(t, df['reserva_disponible'], color='#2ca02c', lw=1.8, label=r'Reserva Disponible Total [MW]')
    ax2.fill_between(t, df['reserva_req'], df['reserva_disponible'], color='#2ca02c', alpha=0.2, label='Holgura de Reserva')
    ax2.set_xlabel('Hora del horizonte temporal $t$ [h]', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Reserva [MW]', fontsize=11, fontweight='bold')
    ax2.legend(loc='upper right', ncol=3, framealpha=0.9)
    ax2.grid(True)
    
    # Separadores de días
    for d in range(1, 8):
        ax1.axvline(24 * d, color='#888888', linestyle=':', alpha=0.4)
        ax2.axvline(24 * d, color='#888888', linestyle=':', alpha=0.4)
        
    plt.tight_layout()
    ruta = os.path.join(fig_dir, f'fig_2a_despacho_bateria_sem_{semilla}.png')
    plt.savefig(ruta, dpi=300)
    plt.close()
    print(f"Gráfico guardado en: {ruta}")


if __name__ == '__main__':
    generar_grafico_despacho_bateria(534)
