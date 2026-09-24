import random
import pyomo.environ as pyo
from generar_parametros import generar_datos_instancia, obtener_parametros_generadores, obtener_parametros_sistema
from modelo_base import construir_modelo_base, resolver_modelo, extraer_resultados
from variacion_bateria import construir_modelo_bateria, extraer_resultados_bateria
from variacion_demanda import barrido_c_shed
from variacion_emisiones import barrido_F

sem = 534
datos = generar_datos_instancia(sem)
df = datos['df']
print(f'=== PARÁMETROS SEMILLA {sem} ===')
print(f"P_peak: {datos['P_peak']:.2f} MW")
print(f"Demanda: min={df['d_t'].min()} (t={df.loc[df['d_t'].idxmin(), 't']}), max={df['d_t'].max()} (t={df.loc[df['d_t'].idxmax(), 't']}), mean={df['d_t'].mean():.2f}, sum={df['d_t'].sum()} MWh")
print(f"Precio red: min={df['lambda_t'].min()}, max={df['lambda_t'].max()}, mean={df['lambda_t'].mean():.2f}")
print(f"Reserva: min={df['res_t'].min()}, max={df['res_t'].max()}, mean={df['res_t'].mean():.2f}")

# Base
m_base = construir_modelo_base(datos)
resolver_modelo(m_base)
res_base = extraer_resultados(m_base, datos)
print(f'\n=== CASO BASE SEMILLA {sem} ===')
print(f"Costo Total: {res_base['total_cost']:,.2f} CLP")
for k, v in res_base['costos_desglosados'].items():
    print(f"  {k}: {v:,.2f} CLP ({v/res_base['total_cost']*100:.2f}%)")
print('Unidades:')
for g, info in res_base['unidades'].items():
    print(f"  {g:12s}: Gen={info['gen_total_MWh']:8.1f} | FP={info['factor_planta']*100:5.1f}% | Horas={info['horas_encendida']:3d} | Starts={info['arranques']} | Emiss={info['emisiones_tCO2']:7.1f} tCO2")
print(f"Red: {res_base['red']['energia_total_MWh']} MWh en {res_base['red']['horas_uso']} horas, costo={res_base['red']['costo_total_CLP']:,.2f} CLP")
tot_emiss = sum(info['emisiones_tCO2'] for info in res_base['unidades'].values())
print(f'Emisiones totales semanales: {tot_emiss:.1f} tCO2')

# Emisiones diarias base
gen_params = obtener_parametros_generadores()
print('\nEmisiones Diarias Caso Base:')
for d in range(1, 8):
    hrs = range(24 * (d - 1) + 1, 24 * d + 1)
    e_d = sum(gen_params[g]['e_g'] * pyo.value(m_base.p[g, t]) for g in m_base.G for t in hrs)
    dem_d = sum(datos['d_t'][t] for t in hrs)
    print(f"  Día {d}: Demanda={dem_d} MWh, Emisiones={e_d:.1f} tCO2, Sobre 1500={e_d > 1500}")

# Bateria
m_bat = construir_modelo_bateria(datos)
resolver_modelo(m_bat)
res_bat = extraer_resultados_bateria(m_bat, datos)
ahorro = res_base['total_cost'] - res_bat['total_cost']
print(f'\n=== VARIACIÓN BATERÍA SEMILLA {sem} ===')
print(f"Costo Batería: {res_bat['total_cost']:,.2f} CLP")
print(f"Ahorro: {ahorro:,.2f} CLP ({ahorro/res_base['total_cost']*100:.2f}%)")
print(f"Carga: {res_bat['bateria']['energia_cargada_MWh']:.1f} MWh, Descarga: {res_bat['bateria']['energia_descargada_MWh']:.1f} MWh, Perdidas: {res_bat['bateria']['perdidas_eficiencia_MWh']:.1f} MWh")
print(f"Red con batería: {res_bat['red']['energia_total_MWh']} MWh")
print('Arranques con batería:')
for g, info in res_bat['unidades'].items():
    print(f"  {g:12s}: {info['arranques']} (vs {res_base['unidades'][g]['arranques']} base)")

# Demanda c_shed
print(f'\n=== VARIACIÓN RESPUESTA DEMANDA SEMILLA {sem} ===')
df_cshed, c_umbral = barrido_c_shed(datos)
print(f'Umbral c_shed identificado: {c_umbral:,d} CLP/MWh')
print(df_cshed[df_cshed['c_shed'].isin([0, 50000, 80000, 90000, 100000, 120000, 150000, 180000, 185000, 190000, 195000, 200000])][['c_shed', 'recorte_total_MWh', 'horas_con_recorte', 'costo_total_CLP']].to_string(index=False))

# Emisiones F
print(f'\n=== VARIACIÓN EMISIONES F SEMILLA {sem} ===')
df_F = barrido_F(datos)
print(df_F[['F_CLP', 'dias_sobre_umbral', 'costo_operativo_CLP', 'costo_total_CLP', 'emisiones_totales_semana_tCO2']].to_string(index=False))
