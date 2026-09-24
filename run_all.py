"""
run_all.py
Script maestro que ejecuta la totalidad de los análisis para la Tarea Computacional 1 - ILN250 (2s26).
Resuelve el caso base y todas las variaciones para la SEMILLA OFICIAL DE GRUPO = 534 (392 + 142).
Genera figuras de alta calidad, tablas resumen e imprime detalladamente todos los resultados en consola.
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from generar_parametros import generar_datos_instancia, obtener_parametros_generadores, obtener_parametros_sistema
from modelo_base import construir_modelo_base, resolver_modelo, extraer_resultados
from variacion_bateria import construir_modelo_bateria, extraer_resultados_bateria
from variacion_demanda import barrido_c_shed, construir_modelo_demanda
from variacion_emisiones import barrido_F, construir_modelo_emisiones

# Configurar estilo visual de gráficos
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#cccccc'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.5


def asegurar_directorio(path):
    if not os.path.exists(path):
        os.makedirs(path)


def generar_graficos_pregunta_1a(datos_instancia, fig_dir, semilla):
    """Genera gráficos de demanda y precios para la pregunta 1.a."""
    df = datos_instancia['df']
    t = df['t']
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    
    # Subplot 1: Demanda horaria
    ax1.plot(t, df['d_t'], color='#1f77b4', lw=1.8, label='Demanda $d_t$ [MW]')
    ax1.axhline(df['d_t'].mean(), color='#1f77b4', linestyle=':', lw=1.5, label=f'Promedio ({df["d_t"].mean():.1f} MW)')
    ax1.axvline(120, color='red', linestyle='--', alpha=0.7, label='Fin Lun-Vie (t=120)')
    ax1.set_ylabel('Demanda [MW]', fontsize=11, fontweight='bold')
    ax1.set_title(f'Perfil Semanal de Demanda Horaria $d_t$ y Precio de Red $\\lambda_t$ (Semilla de Grupo {semilla})', fontsize=13, fontweight='bold')
    ax1.grid(True)
    ax1.legend(loc='upper right', framealpha=0.9)
    
    # Subplot 2: Precio de la Red
    ax2.plot(t, df['lambda_t'], color='#d62728', lw=1.5, label='Precio de Red $\\lambda_t$ [CLP/MWh]')
    ax2.axhline(df['lambda_t'].mean(), color='#d62728', linestyle=':', lw=1.5, label=f'Promedio ({df["lambda_t"].mean():,.0f} CLP/MWh)')
    ax2.axvline(120, color='red', linestyle='--', alpha=0.7)
    ax2.set_xlabel('Hora del horizonte temporal $t$ [h]', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Precio [CLP/MWh]', fontsize=11, fontweight='bold')
    ax2.grid(True)
    ax2.legend(loc='upper right', framealpha=0.9)
    
    # Etiquetas de días
    dias_nombres = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    for d in range(1, 8):
        ax1.axvline(24 * d, color='#888888', linestyle='-', alpha=0.3)
        ax2.axvline(24 * d, color='#888888', linestyle='-', alpha=0.3)
        ax1.text(24 * (d - 1) + 12, ax1.get_ylim()[1] * 0.95, dias_nombres[d - 1], ha='center', va='top', fontsize=9, bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))
        
    plt.tight_layout()
    ruta = os.path.join(fig_dir, f'fig_1a_demanda_precios_sem_{semilla}.png')
    plt.savefig(ruta, dpi=300)
    plt.close()
    print(f"Gráfico guardado: {ruta}")


def generar_graficos_despacho_base(res_base, fig_dir, semilla):
    """Genera gráfico de área apilada de despacho y reserva para el Caso Base (1.d)."""
    df = res_base['df_hourly']
    t = df['t']
    
    colores = {
        'Gas_Base_1': '#2ca02c',   # Verde oscuro
        'Gas_Base_2': '#8c564b',   # Marrón / Verde oliva
        'Diesel_Med_1': '#ff7f0e', # Naranja
        'Diesel_Med_2': '#bcbd22', # Amarillo verdoso
        'Peaker': '#9467bd',       # Morado
        'Red': '#d62728'           # Rojo
    }
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8), sharex=True, gridspec_kw={'height_ratios': [2.5, 1.2]})
    
    # 1. Despacho apilado
    y_stack = [
        df['p_Gas_Base_1'],
        df['p_Gas_Base_2'],
        df['p_Diesel_Med_1'],
        df['p_Diesel_Med_2'],
        df['p_Peaker'],
        df['g_red']
    ]
    etiquetas = ['Gas_Base_1', 'Gas_Base_2', 'Diesel_Med_1', 'Diesel_Med_2', 'Peaker', 'Importación Red']
    ax1.stackplot(t, y_stack, labels=etiquetas, colors=[colores['Gas_Base_1'], colores['Gas_Base_2'], colores['Diesel_Med_1'], colores['Diesel_Med_2'], colores['Peaker'], colores['Red']], alpha=0.85)
    ax1.plot(t, df['demanda'], color='black', lw=2.0, linestyle='--', label='Demanda $d_t$')
    ax1.set_ylabel('Potencia Despachada [MW]', fontsize=11, fontweight='bold')
    ax1.set_title(f'Despacho Económico y Compromiso de Unidades - Caso Base (Semilla de Grupo {semilla})', fontsize=13, fontweight='bold')
    ax1.legend(loc='upper right', ncol=3, framealpha=0.9)
    ax1.grid(True)
    
    # 2. Reserva operativa
    ax2.plot(t, df['reserva_req'], color='#1f77b4', lw=1.8, label='Reserva Requerida $Res_t$ [MW]')
    ax2.plot(t, df['reserva_disponible'], color='#2ca02c', lw=1.8, label='Reserva Disponible Total [MW]')
    ax2.fill_between(t, df['reserva_req'], df['reserva_disponible'], color='#2ca02c', alpha=0.2, label='Holgura de Reserva')
    ax2.set_xlabel('Hora del horizonte temporal $t$ [h]', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Reserva [MW]', fontsize=11, fontweight='bold')
    ax2.legend(loc='upper right', ncol=3, framealpha=0.9)
    ax2.grid(True)
    
    # Días separadores
    for d in range(1, 8):
        ax1.axvline(24 * d, color='#888888', linestyle=':', alpha=0.4)
        ax2.axvline(24 * d, color='#888888', linestyle=':', alpha=0.4)
        
    plt.tight_layout()
    ruta = os.path.join(fig_dir, f'fig_1d_despacho_base_sem_{semilla}.png')
    plt.savefig(ruta, dpi=300)
    plt.close()
    print(f"Gráfico guardado: {ruta}")


def generar_graficos_bateria(res_base, res_bat, fig_dir, semilla):
    """Genera gráfico comparativo y de operación de la batería (2.a)."""
    df_bat = res_bat['df_hourly']
    t = df_bat['t']
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1.2]})
    
    # 1. Operación de carga / descarga
    ax1.plot(t, df_bat['p_dis'], color='#2ca02c', lw=2.0, label='Descarga BESS $p_{dis,t}$ [MW] (Inyección)')
    ax1.plot(t, -df_bat['p_ch'], color='#d62728', lw=2.0, label='Carga BESS $p_{ch,t}$ [MW] (Consumo)')
    ax1.axhline(0, color='black', lw=1.0)
    ax1.set_ylabel('Potencia BESS [MW]', fontsize=11, fontweight='bold')
    ax1.set_title(f'Operación del Sistema de Almacenamiento (BESS) y Estado de Carga (Semilla de Grupo {semilla})', fontsize=13, fontweight='bold')
    ax1.legend(loc='upper right', framealpha=0.9)
    ax1.grid(True)
    
    # 2. SOC
    ax2.plot(t, df_bat['soc'], color='#1f77b4', lw=2.2, label='Estado de Carga $S_t$ [MWh]')
    ax2.axhline(100, color='#ff7f0e', linestyle='--', lw=1.5, label='SOC Inicial / Mínimo Final ($S_0=100$ MWh)')
    ax2.axhline(200, color='#333333', linestyle=':', lw=1.2, label='Capacidad Máxima ($\\bar{S}=200$ MWh)')
    ax2.set_xlabel('Hora del horizonte temporal $t$ [h]', fontsize=11, fontweight='bold')
    ax2.set_ylabel('SOC [MWh]', fontsize=11, fontweight='bold')
    ax2.set_ylim(-5, 215)
    ax2.legend(loc='upper right', framealpha=0.9)
    ax2.grid(True)
    
    for d in range(1, 8):
        ax1.axvline(24 * d, color='#888888', linestyle=':', alpha=0.4)
        ax2.axvline(24 * d, color='#888888', linestyle=':', alpha=0.4)
        
    plt.tight_layout()
    ruta = os.path.join(fig_dir, f'fig_2a_operacion_bateria_sem_{semilla}.png')
    plt.savefig(ruta, dpi=300)
    plt.close()
    print(f"Gráfico guardado: {ruta}")


def generar_grafico_curva_cshed(df_cshed, c_umbral, fig_dir, semilla):
    """Genera gráfico de demanda recortada vs c_shed (2.b)."""
    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    
    color1 = '#1f77b4'
    ax1.set_xlabel('Costo de Corte $c^{shed}$ [CLP/MWh]', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Energía Recortada Semanal [MWh]', color=color1, fontsize=11, fontweight='bold')
    ax1.plot(df_cshed['c_shed'], df_cshed['recorte_total_MWh'], marker='o', lw=2.2, color=color1, label='Energía Recortada [MWh]')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True)
    
    # Eje secundario para costo total
    ax2 = ax1.twinx()
    color2 = '#d62728'
    ax2.set_ylabel('Costo Total de Operación [Miles de Millones CLP]', color=color2, fontsize=11, fontweight='bold')
    ax2.plot(df_cshed['c_shed'], df_cshed['costo_total_CLP'] / 1e9, marker='s', lw=2.0, linestyle='--', color=color2, label='Costo Total [Mil Millones CLP]')
    ax2.tick_params(axis='y', labelcolor=color2)
    
    if c_umbral is not None:
        ax1.axvline(c_umbral, color='#2ca02c', linestyle='-.', lw=2.0, label=f'Umbral Económico ($c^{{shed}}={c_umbral:,d}$ CLP)')
        ax1.annotate(f'Umbral: {c_umbral:,d} CLP/MWh\n(Recorte = 0 MWh)',
                     xy=(c_umbral, 0), xytext=(c_umbral - 50000, max(df_cshed['recorte_total_MWh']) * 0.4),
                     arrowprops=dict(facecolor='#2ca02c', shrink=0.08, width=1.5, headwidth=8),
                     fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor='#e8f5e9', edgecolor='#2ca02c'))
        
    plt.title(f'Sensibilidad de la Demanda Interrumpible ante Variaciones de $c^{{shed}}$ (Semilla de Grupo {semilla})', fontsize=12, fontweight='bold')
    fig.tight_layout()
    ruta = os.path.join(fig_dir, f'fig_2b_demanda_curt_vs_cshed_sem_{semilla}.png')
    plt.savefig(ruta, dpi=300)
    plt.close()
    print(f"Gráfico guardado: {ruta}")


def generar_grafico_curva_F(df_F, fig_dir, semilla):
    """Genera gráfico de días sobre umbral vs penalización F (2.c)."""
    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    
    color1 = '#d62728'
    ax1.set_xlabel('Penalización Fija Diaria $F$ [CLP/día]', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Días Semanales Sobre Umbral (Emisiones > 1500 t$CO_2$)', color=color1, fontsize=11, fontweight='bold')
    ax1.plot(df_F['F_CLP'], df_F['dias_sobre_umbral'], marker='o', lw=2.2, color=color1, label='Días Sobre Umbral')
    ax1.set_ylim(-0.5, 7.5)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True)
    
    ax2 = ax1.twinx()
    color2 = '#1f77b4'
    ax2.set_ylabel('Costo Operativo Puro [Miles de Millones CLP]', color=color2, fontsize=11, fontweight='bold')
    ax2.plot(df_F['F_CLP'], df_F['costo_operativo_CLP'] / 1e9, marker='^', lw=2.0, linestyle='--', color=color2, label='Costo Operativo')
    ax2.tick_params(axis='y', labelcolor=color2)
    
    plt.title(f'Impacto de la Penalización $F$ en el Cumplimiento del Umbral Diario de Emisiones (Semilla de Grupo {semilla})', fontsize=12, fontweight='bold')
    fig.tight_layout()
    ruta = os.path.join(fig_dir, f'fig_2c_emisiones_vs_F_sem_{semilla}.png')
    plt.savefig(ruta, dpi=300)
    plt.close()
    print(f"Gráfico guardado: {ruta}")


def ejecutar_analisis_completo_para_semilla(semilla, fig_dir):
    """Ejecuta todos los modelos y cálculos para una semilla específica."""
    print(f"\n######################################################################")
    print(f"### INICIANDO EJECUCIÓN INTEGRAL PARA SEMILLA = {semilla} ###")
    print(f"######################################################################\n")
    
    # 1. Generación de parámetros
    datos = generar_datos_instancia(semilla)
    generar_graficos_pregunta_1a(datos, fig_dir, semilla)
    
    # 2. Caso Base (1.b, 1.c, 1.d)
    print("\n--- Resolviendo Caso Base (Pregunta 1) ---")
    m_base = construir_modelo_base(datos)
    res_base_solver = resolver_modelo(m_base)
    res_base = extraer_resultados(m_base, datos)
    generar_graficos_despacho_base(res_base, fig_dir, semilla)
    
    # 3. Variación 2.a: Batería
    print("\n--- Resolviendo Variación 2.a (Batería) ---")
    m_bat = construir_modelo_bateria(datos)
    resolver_modelo(m_bat)
    res_bat = extraer_resultados_bateria(m_bat, datos)
    generar_graficos_bateria(res_base, res_bat, fig_dir, semilla)
    
    # 4. Variación 2.b: Carga Interrumpible (Barrido de c_shed)
    print("\n--- Resolviendo Variación 2.b (Respuesta de Demanda - Barrido c_shed) ---")
    df_cshed, c_umbral = barrido_c_shed(datos)
    generar_grafico_curva_cshed(df_cshed, c_umbral, fig_dir, semilla)
    
    # 5. Variación 2.c: Penalización de Emisiones (Barrido de F)
    print("\n--- Resolviendo Variación 2.c (Penalización de Emisiones - Barrido F) ---")
    df_F = barrido_F(datos)
    generar_grafico_curva_F(df_F, fig_dir, semilla)
    
    # Guardar dataframes de resultados
    df_cshed.to_csv(os.path.join(fig_dir, f'tabla_cshed_sem_{semilla}.csv'), index=False)
    df_F.to_csv(os.path.join(fig_dir, f'tabla_F_sem_{semilla}.csv'), index=False)
    
    # IMPRESIÓN DETALLADA DE RESULTADOS (Exigencia FAQ: "se debe imprimir mediante print todo lo mostrado en el informe")
    print(f"\n======================================================================")
    print(f"RESUMEN EJECUTIVO DE RESULTADOS NUMÉRICOS - SEMILLA {semilla}")
    print(f"======================================================================")
    print(f"1. CASO BASE:")
    print(f"  - Costo Total de Operación: {res_base['total_cost']:,.2f} CLP")
    print(f"  - Desglose de Costos:")
    print(f"      * Combustible/Var:     {res_base['costos_desglosados']['variable']:,.2f} CLP ({(res_base['costos_desglosados']['variable']/res_base['total_cost'])*100:.2f}%)")
    print(f"      * No-Load (Fijo op):   {res_base['costos_desglosados']['no_load']:,.2f} CLP ({(res_base['costos_desglosados']['no_load']/res_base['total_cost'])*100:.2f}%)")
    print(f"      * Arranque (Start):    {res_base['costos_desglosados']['arranque']:,.2f} CLP ({(res_base['costos_desglosados']['arranque']/res_base['total_cost'])*100:.2f}%)")
    print(f"      * Importación Red:     {res_base['costos_desglosados']['red']:,.2f} CLP ({(res_base['costos_desglosados']['red']/res_base['total_cost'])*100:.2f}%)")
    print(f"  - Generación por Unidad y Factores de Planta:")
    for g, info in res_base['unidades'].items():
        print(f"      * {g:12s}: Gen={info['gen_total_MWh']:8.1f} MWh | FP={info['factor_planta']*100:5.1f}% | Horas={info['horas_encendida']:3d} h | Arranques={info['arranques']} | Emisiones={info['emisiones_tCO2']:7.1f} tCO2")
    print(f"  - Uso de la Red Externa: {res_base['red']['energia_total_MWh']:.1f} MWh en {res_base['red']['horas_uso']} horas.")
    
    print(f"\n2. VARIACIÓN 2.a (BATERÍA BESS):")
    ahorro_bat = res_base['total_cost'] - res_bat['total_cost']
    print(f"  - Costo Total con Batería: {res_bat['total_cost']:,.2f} CLP")
    print(f"  - Ahorro Económico:        {ahorro_bat:,.2f} CLP ({ahorro_bat/res_base['total_cost']*100:.2f}%)")
    print(f"  - Energía Cargada:         {res_bat['bateria']['energia_cargada_MWh']:.1f} MWh")
    print(f"  - Energía Descargada:      {res_bat['bateria']['energia_descargada_MWh']:.1f} MWh")
    print(f"  - Pérdidas por Ciclo:      {res_bat['bateria']['perdidas_eficiencia_MWh']:.1f} MWh")
    print(f"  - Importación Red con Bat: {res_bat['red']['energia_total_MWh']:.1f} MWh (vs {res_base['red']['energia_total_MWh']:.1f} MWh base)")
    print(f"  - Arranques por Unidad con Batería:")
    for g, info in res_bat['unidades'].items():
        base_starts = res_base['unidades'][g]['arranques']
        print(f"      * {g:12s}: {info['arranques']} arranques (vs {base_starts} en caso base)")

    print(f"\n3. VARIACIÓN 2.b (RESPUESTA DE DEMANDA):")
    print(f"  - Umbral económico identificado: {c_umbral:,d} CLP/MWh")
    print(f"  - A partir de este valor, el recorte se anula y la operación coincide con el caso base.")
    print(f"  - Muestra del barrido:")
    for _, row in df_cshed[df_cshed['c_shed'].isin([0, 50000, 80000, 90000, 100000, 120000, 150000, 180000, 185000, 190000, 195000, 200000])].iterrows():
        print(f"      * c_shed={int(row['c_shed']):7,d} | Recorte={row['recorte_total_MWh']:7.1f} MWh | Costo Total={row['costo_total_CLP']:15,.0f} CLP")

    print(f"\n4. VARIACIÓN 2.c (COSTO FIJO POR EMISIONES F):")
    print(f"  - Muestra del barrido de penalización F:")
    for _, row in df_F.iterrows():
        print(f"      * F={int(row['F_CLP']):11,d} CLP/día | Días sobre umbral={row['dias_sobre_umbral']} | Costo Op={row['costo_operativo_CLP']:14,.0f} | Emisiones Tot={row['emisiones_totales_semana_tCO2']:7.1f} tCO2")
        
    return {
        'datos': datos,
        'res_base': res_base,
        'res_bat': res_bat,
        'df_cshed': df_cshed,
        'c_umbral': c_umbral,
        'df_F': df_F
    }


def main():
    fig_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figuras')
    asegurar_directorio(fig_dir)
    
    # Semilla oficial del grupo = 534 (Suma de integrantes 392 + 142)
    semilla_grupo = 534
    ejecutar_analisis_completo_para_semilla(semilla_grupo, fig_dir)
        
    print("\n\n" + "#"*70)
    print(f"EJECUCIÓN COMPLETA EXITOSA PARA LA SEMILLA OFICIAL DE GRUPO = {semilla_grupo}")
    print("#"*70)


if __name__ == '__main__':
    main()
