import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from generar_parametros import generar_datos_instancia, obtener_parametros_generadores, obtener_parametros_sistema
from modelo_base import construir_modelo_base, resolver_modelo, extraer_resultados
from variacion_bateria import construir_modelo_bateria, extraer_resultados_bateria
from variacion_demanda import barrido_c_shed, construir_modelo_demanda
from variacion_emisiones import barrido_F, construir_modelo_emisiones

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#cccccc'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.5


def asegurar_directorio(path):
    if not os.path.exists(path):
        os.makedirs(path)



def ejecutar_analisis_completo_para_semilla(semilla, fig_dir):
    """Ejecuta todos los modelos y cálculos para una semilla específica."""
    print(f"\n######################################################################")
    print(f"### INICIANDO EJECUCIÓN INTEGRAL PARA SEMILLA = {semilla} ###")
    print(f"######################################################################\n")
    
    # 1. Generación de parámetros
    datos = generar_datos_instancia(semilla)
    
    # 2. Caso Base (1.b, 1.c, 1.d)
    print("\n--- Resolviendo Caso Base (Pregunta 1) ---")
    m_base = construir_modelo_base(datos)
    res_base_solver = resolver_modelo(m_base)
    res_base = extraer_resultados(m_base, datos)
    
    # 3. Variación 2.a: Batería
    print("\n--- Resolviendo Variación 2.a (Batería) ---")
    m_bat = construir_modelo_bateria(datos)
    resolver_modelo(m_bat)
    res_bat = extraer_resultados_bateria(m_bat, datos)
    
    # 4. Variación 2.b: Carga Interrumpible (Barrido de c_shed)
    print("\n--- Resolviendo Variación 2.b (Respuesta de Demanda - Barrido c_shed) ---")
    df_cshed, c_umbral = barrido_c_shed(datos)
    
    # 5. Variación 2.c: Penalización de Emisiones (Barrido de F)
    print("\n--- Resolviendo Variación 2.c (Penalización de Emisiones - Barrido F) ---")
    df_F = barrido_F(datos)
    
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
    
    print(f"\n2. VARIACIÓN 2.a (BATERÍA):")
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
    
    semilla_grupo = 534
    ejecutar_analisis_completo_para_semilla(semilla_grupo, fig_dir)
        
    print("\n\n" + "#"*70)
    print(f"EJECUCIÓN COMPLETA EXITOSA PARA LA SEMILLA OFICIAL DE GRUPO = {semilla_grupo}")
    print("#"*70)


if __name__ == '__main__':
    main()
