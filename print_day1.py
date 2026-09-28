from generar_parametros import generar_datos_instancia
from modelo_base import construir_modelo_base, resolver_modelo, extraer_resultados

datos = generar_datos_instancia(534)
m = construir_modelo_base(datos)
resolver_modelo(m)
res = extraer_resultados(m, datos)
df = res['df_hourly']
day1 = df[df['dia'] == 1]
for _, r in day1.iterrows():
    def fmt(val):
        return f"{val:.1f}".replace('.', ',')
    print(f"{int(r['t'])} & {int(r['demanda'])} & {fmt(r['p_Gas_Base_1'])} & {fmt(r['p_Gas_Base_2'])} & {fmt(r['p_Diesel_Med_1'])} & {fmt(r['p_Diesel_Med_2'])} & {fmt(r['p_Peaker'])} & {fmt(r['g_red'])} & {int(r['reserva_req'])} & {fmt(r['reserva_disponible'])} & {fmt(r['holgura_reserva'])} \\\\")
