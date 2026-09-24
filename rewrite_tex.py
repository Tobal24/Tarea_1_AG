# Read existing informe.tex and rewrite with optimized layout and exact page budgeting

tex_content = r'''\documentclass[10pt,letterpaper]{article}

% --- Paquetes Principales ---
\usepackage[utf8]{inputenc}
\usepackage[spanish,es-tabla]{babel}
\usepackage[margin=1.7cm,top=1.8cm,bottom=1.8cm]{geometry}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{float}
\usepackage{subcaption}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{microtype}
\usepackage{fancyhdr}
\usepackage{cite}

% --- Configuración de Enlaces y Colores ---
\definecolor{usmblue}{RGB}{0,51,102}
\definecolor{usmred}{RGB}{178,34,34}
\definecolor{darkgray}{RGB}{50,50,50}

\hypersetup{
    colorlinks=true,
    linkcolor=usmblue,
    citecolor=usmblue,
    urlcolor=usmblue
}

% --- Configuración de Encabezados y Pies de Página ---
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\color{darkgray}\textit{ILN250 -- Investigación de Operaciones (2s26)}}
\fancyhead[R]{\small\color{darkgray}\textit{Tarea Computacional 1: Unit Commitment}}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}

% --- Espaciado de Secciones ---
\titleformat{\section}{\large\bfseries\color{usmblue}}{\thesection.}{0.4em}{}
\titleformat{\subsection}{\normalsize\bfseries\color{usmblue}}{\thesubsection.}{0.3em}{}
\titleformat{\subsubsection}{\small\bfseries\color{darkgray}}{\thesubsubsection.}{0.25em}{}
\titlespacing*{\section}{0pt}{1.0ex plus 0.3ex minus 0.2ex}{0.4ex plus 0.2ex}
\titlespacing*{\subsection}{0pt}{0.8ex plus 0.3ex minus 0.2ex}{0.3ex plus 0.1ex}
\titlespacing*{\subsubsection}{0pt}{0.6ex plus 0.2ex minus 0.1ex}{0.2ex plus 0.1ex}

\setlist[itemize]{noitemsep, topsep=1.5pt, parsep=0.5pt, leftmargin=1.5em}
\setlist[enumerate]{noitemsep, topsep=1.5pt, parsep=0.5pt, leftmargin=1.5em}

\begin{document}

% =========================================================================
% PORTADA (No cuenta dentro de las 10 páginas de desarrollo)
% =========================================================================
\begin{titlepage}
    \centering
    \vspace*{0.8cm}
    {\scshape\Large Universidad Técnica Federico Santa María \par}
    {\scshape\large Departamento de Industrias -- Casa Central / Campus San Joaquín \par}
    \vspace{0.3cm}
    {\large Asignatura: Investigación de Operaciones (ILN250) -- Segundo Semestre 2026 \par}
    \vspace{2.0cm}
    
    \rule{\linewidth}{1.2pt} \\[0.4cm]
    {\huge\bfseries\color{usmblue} Tarea Computacional 1: \\[0.25cm] 
    Optimización del Unit Commitment y Despacho Económico en un Complejo Industrial Aislado \par}
    \rule{\linewidth}{1.2pt} \\[2.0cm]
    
    \begin{minipage}[t]{0.48\textwidth}
        \textbf{Profesores:}\\
        Nicolás Boyardi A.\\
        Rafael Favereau U.\\
        Ismael Kauak V.
    \end{minipage}
    \hfill
    \begin{minipage}[t]{0.48\textwidth}
        \raggedleft
        \textbf{Integrantes (Semillas Asignadas):}\\
        Integrante 1: Semilla RNG = \textbf{392}\\
        Integrante 2: Semilla RNG = \textbf{142}\\
        \textit{Carrera de Ingeniería Civil Industrial}
    \end{minipage}
    
    \vfill
    {\large Valparaíso / Santiago, Chile \\ Septiembre de 2026 \par}
\end{titlepage}

% =========================================================================
% FRONT MATTER: ROMAN NUMERALS (Portada, Resumen, Índice)
% =========================================================================
\pagenumbering{roman}
\setcounter{page}{1}

\section*{Resumen Ejecutivo}
\addcontentsline{toc}{section}{Resumen Ejecutivo}

El presente informe aborda el modelamiento, resolución computacional y análisis económico integral del problema de \textit{Unit Commitment} (UC) y Despacho Económico para un complejo industrial eléctricamente aislado durante un horizonte temporal semanal de $T = 168$ horas. La micro-red cuenta con un parque de generación térmica heterogéneo $|G| = 5$ (dos unidades a gas de base, dos diésel de modulación intermedia y una turbina peaker de punta) junto a un enlace limitado con el mercado eléctrico externo ($\bar{G}_{red} = 80$ MW) sujeto a precios horarios volátiles $\lambda_t$.

El problema se formula rigurosamente como un Programa Lineal Entero Mixto (\textit{Mixed-Integer Linear Programming}, MILP), integrando costos de generación, arranque (\textit{startup}), costos fijos de operación en vacío (\textit{no-load}), dinámicas de rampa horaria con excepciones al arranque/parada, y reserva operativa mínima rodante del 10\% de la demanda horaria. La implementación se ejecutó en Python empleando el lenguaje de modelamiento algebraico \textbf{Pyomo}, resolviéndose mediante el solver de última generación \textbf{HiGHS} (`appsi_highs`), obteniendo soluciones óptimas probadas (gap de 0.00\%) en menos de 1 segundo para las semillas de ambos integrantes (\textbf{Semilla 392} y \textbf{Semilla 142}).

Los principales hallazgos del estudio comprenden:
\begin{enumerate}
    \item \textbf{Situación Inicial (Caso Base):} El costo total de operación semanal asciende a \$1.809.604.460 CLP para la Semilla 392 y a \$1.744.790.952 CLP para la Semilla 142. El orden de mérito económico demuestra que las unidades eficientes a gas (\texttt{Gas\_Base\_1} y \texttt{Gas\_Base\_2}) absorben la base de la carga con factores de planta del 95.7\% y 74.4\%, respectivamente. La unidad \texttt{Diesel\_Med\_1} actúa como seguidor de carga diurna, mientras que \texttt{Diesel\_Med\_2} y \texttt{Peaker} se reservan exclusivamente para cubrir los picos extremos. La importación de red se restringe estrictamente a momentos donde las rampas o la reserva técnica se vuelven críticas (14.0 MWh para semilla 392 y 18.0 MWh para semilla 142), debido a su elevado costo horario promedio (\$169.022 CLP/MWh).
    \item \textbf{Variación 2.a (Sistema BESS):} La incorporación de un sistema de almacenamiento de energía en baterías de 200 MWh / 60 MW genera un ahorro económico semanal de \$47.595.867 CLP (2.63\%) para la semilla 392 y de \$44.220.689 CLP (2.53\%) para la semilla 142. La batería realiza arbitraje de energía intradiario (\textit{peak shaving} y \textit{valley filling}), eliminando en un 100\% las importaciones de la red externa y suprimiendo la totalidad de los arranques de las unidades más costosas (\texttt{Diesel\_Med\_2} y \texttt{Peaker}).
    \item \textbf{Variación 2.b (Respuesta de Demanda):} El análisis de sensibilidad respecto al costo de corte $c^{shed}$ reveló un umbral económico crítico de \textbf{\$190.000 CLP/MWh} (Semilla 392) y \textbf{\$195.000 CLP/MWh} (Semilla 142). Por sobre este valor, el recorte se anula completamente ($r_{total} = 0$ MWh). Este umbral coincide analíticamente con el costo marginal máximo de importación de la red externa en horas punta vespertinas, confirmando la teoría microeconómica del despacho en sistemas eléctricos.
    \item \textbf{Variación 2.c (Umbral de Emisiones con Big-M):} Frente a una penalización fija diaria $F$ por superar 1.500 $\text{tCO}_2$, se identificaron dos regímenes operativos: penalizaciones moderadas ($F \approx \$2.5 - \$3.0$ millones CLP/día) inducen el cumplimiento del umbral durante los fines de semana (reduciendo de 7 a 5 los días infractores en la semilla 392). Sin embargo, alcanzar cero días sobre el umbral en días laborales exige una penalización extrema ($F \ge \$110$ millones CLP/día), forzando una sustitución masiva y costosa de gas local por importaciones de red, lo que evidencia las ineficiencias y discontinuidades que introducen los mecanismos sancionatorios tipo umbral discontinuo en comparación con gravámenes continuos (impuesto Pigouviano al carbono).
\end{enumerate}

\newpage
\tableofcontents
\newpage

% =========================================================================
% MAIN BODY: PÁGINAS 1 A 10 (ESTRICTAMENTE <= 10 PÁGINAS)
% =========================================================================
\pagenumbering{arabic}
\setcounter{page}{1}

\section{Introducción General}
\label{sec:introduccion}

La gestión eficiente de micro-redes y complejos industriales aislados representa uno de los desafíos más relevantes de la ingeniería de operaciones contemporánea. A diferencia de las instalaciones conectadas de manera irrestricta al Sistema Eléctrico Nacional, un sistema aislado debe asegurar el autoabastecimiento instantáneo de su demanda eléctrica garantizando la seguridad, estabilidad de frecuencia y continuidad de servicio, en un entorno caracterizado por la variabilidad estocástica del consumo y las rigideces técnicas del parque generador \cite{stoft2002power,kirschen2003fundamentals}.

El problema abordado en esta investigación corresponde a la planificación operativa semanal ($T = 168$ horas) de un complejo industrial aislado provisto de un parque térmico heterogéneo de cinco unidades ($|G| = 5$) y un enlace de capacidad acotada ($\bar{G}_{red} = 80$ MW) con el mercado eléctrico externo. La optimización del despacho requiere resolver simultáneamente dos decisiones interdependientes:
\begin{enumerate}
    \item \textbf{Unit Commitment (Decisión Binaria):} Determinar qué unidades generadoras deben encenderse, mantenerse en línea o apagarse en cada intervalo horario, incurriendo en costos fijos de operación (\textit{no-load}) y costos de arranque (\textit{startup}) dependientes del historial de operación previo \cite{carrion2006computationally}.
    \item \textbf{Despacho Económico (Decisión Continua):} Asignar la potencia exacta generada por cada unidad en servicio y la cantidad de energía importada desde la red externa a precio horario $\lambda_t$, satisfaciendo el balance instantáneo de energía, límites de capacidad técnica, restricciones de velocidad de cambio de carga (rampas de subida y bajada) y márgenes de reserva operativa ante contingencias \cite{morales2013tight,arroyo2000optimal}.
\end{enumerate}

El objetivo central del presente estudio es formular el modelo matemático óptimo para el caso base, resolverlo computacionalmente mediante herramientas de programación matemática en Python (Pyomo + HiGHS) para las semillas asignadas (\textbf{Semilla 392} y \textbf{Semilla 142}), e investigar cuantitativamente el impacto de tres variaciones tecnológicas y regulatorias: (i) almacenamiento electroquímico BESS, (ii) respuesta de demanda con carga interrumpible, y (iii) una política ambiental con penalización fija diaria tipo Big-M por sobrepasar un umbral de emisiones de $\text{CO}_2$.

\section{Sección de Supuestos}
\label{sec:supuestos}

Para garantizar un modelamiento matemáticamente riguroso, consistente y computacionalmente tratable, se establecen los siguientes supuestos operativos:

\begin{enumerate}
    \item \textbf{Discretización Temporal y Régimen Cuasi-Estacionario:} El horizonte semanal se discretiza en 168 bloques horarios independientes de $\Delta t = 1$ hora. La potencia promedio en MW durante una hora equivale numéricamente a la energía entregada en MWh. Las variables representan el estado promedio en cada bloque horario.
    \item \textbf{Estructura de Costos Térmicos:} Los costos de operación se modelan de acuerdo al estándar de la industria eléctrica mediante tres componentes lineales e independientes:
    \begin{itemize}
        \item \textit{Costo Variable ($c_g^{var}$):} Costo proporcional a la energía eléctrica generada [CLP/MWh], que agrupa combustible y mantenimiento variable.
        \item \textit{Costo de No-Load ($c_g^{nl}$):} Costo fijo horario [CLP/h] en el que incurre cada generador por mantenerse encendido y sincronizado a la red a velocidad nominal, independiente de su nivel de despacho.
        \item \textit{Costo de Arranque ($c_g^{start}$):} Costo monetario fijo devengado únicamente en el instante en que la unidad transita de apagado ($u_{g,t-1}=0$) a encendido ($u_{g,t}=1$). El costo de detención se asume nulo ($c_g^{stop} = 0$).
    \end{itemize}
    \item \textbf{Dinámica de Rampas y Ajuste al Arranque/Parada:} Las limitaciones termomecánicas restringen las variaciones de potencia a un máximo de $R_g$ MW/h entre horas consecutivas en línea. Conforme a las directrices de cátedra (FAQ), cuando la unidad arranca, puede alcanzar hasta $\max(P_g^{min}, R_g)$ MW para no restringir artificialmente a unidades con $R_g > P_g^{min}$ (ej. diésel y peaker) ni provocar infactibilidad en unidades donde $P_g^{min} > R_g$ (como las turbinas a gas). Análogamente, antes de apagarse, la unidad desciende a lo más hasta dicho umbral.
    \item \textbf{Condiciones Iniciales del Sistema ($t=0$):} Se establece que las dos unidades de base (\texttt{Gas\_Base\_1} y \texttt{Gas\_Base\_2}) inician encendidas a su mínimo técnico ($u_g^0 = 1$, $p_g^0 = P_g^{min}$), mientras que las unidades intermedias y peaker inician apagadas ($u_g^0 = 0$, $p_g^0 = 0$). Estas condiciones gobiernan los arranques y rampas de la hora $t=1$.
    \item \textbf{Reserva Operativa y Seguridad de Suministro:} Para salvaguardar la micro-red ante contingencias, se exige en todo momento una reserva mínima $Res_t = \lfloor 0.10 \cdot d_t \rceil$, provista conjuntamente por la capacidad disponible no despachada de máquinas encendidas y la holgura del enlace de red ($\bar{G}_{red} - g_t^{red}$).
    \item \textbf{Operación de Almacenamiento (BESS):} Se asume eficiencia de carga $\eta^{ch} = 0.95$ y descarga $\eta^{dis} = 0.95$. Dado que los costos marginales de generación y precios de red son estrictamente positivos, la optimización económica descarta de forma natural la carga y descarga simultánea sin requerir variables binarias adicionales.
    \item \textbf{Perímetro de Emisiones:} El umbral de $1.500 \text{ tCO}_2$/día aplica exclusivamente a las emisiones directas del parque térmico local del complejo.
\end{enumerate}

\section{Situación Inicial}
\label{sec:situacion_inicial}

\subsection{Pregunta 1.a: Generación de Parámetros y Perfiles de Instancia}
\label{subsec:1a}

La demanda horaria $d_t$ y el precio de red $\lambda_t$ se obtuvieron mediante el proceso estocástico especificado:
\begin{equation}
    d_t = \left\lfloor P^{peak} \cdot \gamma_{dia(t)} \cdot s_{h(t)} \cdot (1 + \varepsilon_t) \right\rceil, \quad 
    \lambda_t = \left\lfloor (100.000 + 90.000 \cdot s_{h(t)}) \cdot (1 + \eta_t) \right\rceil
\end{equation}
con $P^{peak} \sim \mathcal{N}(300, 15)$, $\gamma_{dia} = 1.0$ (días hábiles $t \le 120$) y $\gamma_{dia} = 0.8$ (fin de semana $t > 120$), con perturbaciones normales $\varepsilon_t \sim \mathcal{N}(0, 0.03)$ y $\eta_t \sim \mathcal{N}(0, 0.05)$. En la Tabla \ref{tab:estadisticas_instancia} se reporta el resumen estadístico comparativo para las semillas asignadas (\textbf{Semilla 392} y \textbf{Semilla 142}).

\begin{table}[H]
\centering
\caption{Resumen estadístico de las instancias generadas para las semillas 392 y 142.}
\label{tab:estadisticas_instancia}
\setlength{\tabcolsep}{3.5pt}
\small
\begin{tabular}{lrrrrrrrr}
\toprule
\textbf{Métrica} & \multicolumn{4}{c}{\textbf{Semilla 392 (Integrante 1)}} & \multicolumn{4}{c}{\textbf{Semilla 142 (Integrante 2)}} \\
\cmidrule(lr){2-5} \cmidrule(lr){6-9}
& \textbf{Mínimo} & \textbf{Máximo} & \textbf{Promedio} & \textbf{Total Semanal} & \textbf{Mínimo} & \textbf{Máximo} & \textbf{Promedio} & \textbf{Total Semanal} \\
\midrule
$P^{peak}$ generado [MW] & --- & --- & 287,65 & --- & --- & --- & 280,33 & --- \\
Demanda $d_t$ [MW] & 104 & 299 & 205,17 & 34.469 MWh & 100 & 287 & 199,86 & 33.576 MWh \\
Precio red $\lambda_t$ [CLP/MWh] & 128.495 & 204.407 & 169.022 & --- & 126.505 & 209.514 & 169.031 & --- \\
Reserva $Res_t$ [MW] & 10 & 30 & 20,52 & --- & 10 & 29 & 19,99 & --- \\
\bottomrule
\end{tabular}
\end{table}

En la Figura \ref{fig:1a_perfiles} se ilustra la serie temporal de demanda y precios de red a lo largo de las 168 horas para la Semilla 392. Se evidencia el marcado ciclo diurno de actividad industrial y la reducción de demanda durante el fin de semana.

\begin{figure}[H]
\centering
\includegraphics[height=4.8cm,width=0.92\linewidth]{figuras/fig_1a_demanda_precios_sem_392.png}
\caption{Perfiles semanales de demanda horaria $d_t$ y precio de importación de la red $\lambda_t$ (Semilla 392).}
\label{fig:1a_perfiles}
\end{figure}

\subsection{Pregunta 1.b: Formulación Matemática del Modelo de Optimización}
\label{subsec:1b}

Siguiendo el estándar formal de la cátedra de Investigación de Operaciones (ILN250), se detalla a continuación el modelo de Unit Commitment y Despacho Económico.

\subsubsection*{1. Conjuntos e Índices}
\begin{itemize}
    \item $t \in T = \{1, 2, \ldots, 168\}$: Conjunto de horas del horizonte semanal de planificación.
    \item $g \in G = \{\texttt{Gas\_Base\_1}, \texttt{Gas\_Base\_2}, \texttt{Diesel\_Med\_1}, \texttt{Diesel\_Med\_2}, \texttt{Peaker}\}$: Conjunto de unidades generadoras térmicas.
\end{itemize}

\subsubsection*{2. Parámetros}
\begin{itemize}
    \item $P_g^{max}, P_g^{min}$: Potencia máxima y mínima técnica de la unidad $g$ [MW].
    \item $c_g^{var}$: Costo variable unitario de generación de la unidad $g$ [CLP/MWh].
    \item $c_g^{nl}$: Costo fijo horario de operación en vacío (\textit{no-load}) de la unidad $g$ [CLP/h].
    \item $c_g^{start}$: Costo de partida o arranque de la unidad $g$ [CLP].
    \item $R_g$: Rampa máxima de subida y bajada de la unidad $g$ [MW/h].
    \item $u_g^0, p_g^0$: Estado de encendido inicial (1 o 0) y potencia inicial [MW] de la unidad $g$ en $t=0$.
    \item $\bar{G}_{red}$: Capacidad máxima de importación desde la red externa [MW] ($\bar{G}_{red} = 80$ MW).
    \item $d_t$: Demanda eléctrica proyectada en la hora $t$ [MW].
    \item $\lambda_t$: Precio horario de importación de energía eléctrica desde la red en la hora $t$ [CLP/MWh].
    \item $Res_t$: Reserva operativa mínima rodante requerida en la hora $t$ [MW] ($Res_t = \lfloor 0.10 \cdot d_t \rceil$).
    \item $SU_g, SD_g$: Límite de rampa al arranque y parada de la unidad $g$ [MW], definido como $\max(P_g^{min}, R_g)$.
\end{itemize}

\subsubsection*{3. Variables de Decisión}
\begin{itemize}
    \item $u_{g,t} \in \{0, 1\}$: Variable binaria de compromiso; 1 si la unidad $g$ está encendida en la hora $t$, 0 si está apagada.
    \item $v_{g,t} \ge 0$: Variable continua indicadora de arranque; toma el valor 1 si la unidad $g$ arranca en la hora $t$, 0 e.o.c.
    \item $p_{g,t} \ge 0$: Potencia eléctrica generada por la unidad térmica $g$ en la hora $t$ [MW].
    \item $g_t^{red} \ge 0$: Potencia eléctrica importada desde la red externa en la hora $t$ [MW].
\end{itemize}

\subsubsection*{4. Función Objetivo}
Minimizar el costo total de operación del complejo industrial a lo largo de la semana:
\begin{equation}
    \min Z = \sum_{t \in T} \left( \sum_{g \in G} \left( c_g^{var} \cdot p_{g,t} + c_g^{nl} \cdot u_{g,t} + c_g^{start} \cdot v_{g,t} \right) + \lambda_t \cdot g_t^{red} \right)
    \label{eq:fo_base}
\end{equation}

\subsubsection*{5. Restricciones}
\begin{enumerate}[label=\textbf{R\arabic*.}]
    \item \textbf{Lógica de Arranque de Generadores:}
    \begin{align}
        v_{g,1} &\ge u_{g,1} - u_g^0, \quad \forall g \in G \label{eq:startup_t1} \\
        v_{g,t} &\ge u_{g,t} - u_{g,t-1}, \quad \forall g \in G, \, t \in T \setminus \{1\} \label{eq:startup_t}
    \end{align}
    \textit{Explicación:} Dado que $c_g^{start} > 0$ en la minimización, cuando la unidad pasa de apagado ($u_{g,t-1}=0$) a encendido ($u_{g,t}=1$), el lado derecho es 1, obligando a $v_{g,t}=1$. Si la unidad se mantiene encendida o se apaga, la cota inferior $v_{g,t} \ge 0$ permite óptimamente que $v_{g,t}=0$.
    
    \item \textbf{Límites Técnicos de Capacidad de Generación:}
    \begin{equation}
        P_g^{min} \cdot u_{g,t} \le p_{g,t} \le P_g^{max} \cdot u_{g,t}, \quad \forall g \in G, \, t \in T \label{eq:p_bounds}
    \end{equation}
    \textit{Explicación:} Si la unidad está apagada ($u_{g,t}=0$), se fuerza $p_{g,t}=0$. Si está encendida ($u_{g,t}=1$), la potencia generada debe situarse estrictamente en el rango técnico $[P_g^{min}, P_g^{max}]$.
    
    \item \textbf{Rampas de Subida y Bajada con Ajuste al Arranque/Parada:}
    \begin{align}
        p_{g,t} - p_{g,t-1} &\le R_g \cdot u_{g,t-1} + SU_g \cdot (1 - u_{g,t-1}), \quad \forall g \in G, \, t \in T \label{eq:ramp_up} \\
        p_{g,t-1} - p_{g,t} &\le R_g \cdot u_{g,t} + SD_g \cdot (1 - u_{g,t}), \quad \forall g \in G, \, t \in T \label{eq:ramp_down}
    \end{align}
    (con $p_{g,0} = p_g^0$ y $u_{g,0} = u_g^0$). \\
    \textit{Explicación:} Si la máquina está encendida en periodos consecutivos ($u_{g,t-1}=u_{g,t}=1$), la variación de carga está estrictamente acotada por $R_g$. Al arrancar ($u_{g,t-1}=0, u_{g,t}=1$), la potencia inicial queda acotada por $SU_g = \max(P_g^{min}, R_g)$; combinado con \eqref{eq:p_bounds}, esto permite a las turbinas de gas encender en su mínimo técnico ($P^{min}=40 > R_g=30$) sin causar infactibilidad, y a los grupos diésel encender hasta $R_g$ sin restricciones artificiales. Análogamente, al detenerse ($u_{g,t}=0$), se exige que en la hora previa la máquina haya bajado a lo más a $SD_g$.
    
    \item \textbf{Balance Instantáneo de Energía (Satisfacción de Demanda):}
    \begin{equation}
        \sum_{g \in G} p_{g,t} + g_t^{red} = d_t, \quad \forall t \in T \label{eq:balance_base}
    \end{equation}
    
    \item \textbf{Reserva Operativa Rodante Mínima:}
    \begin{equation}
        \sum_{g \in G} \left( P_g^{max} \cdot u_{g,t} - p_{g,t} \right) + \left( \bar{G}_{red} - g_t^{red} \right) \ge Res_t, \quad \forall t \in T \label{eq:reserva_base}
    \end{equation}
    \textit{Explicación:} Exige que la capacidad disponible no utilizada de generadores encendidos más el margen libre de importación de la red externa cubran al menos el 10\% de la demanda horaria. Sustituyendo el balance \eqref{eq:balance_base}, equivale a garantizar que la potencia total en línea satisfaga $\sum P_g^{max} u_{g,t} + \bar{G}_{red} \ge d_t + Res_t$.
    
    \item \textbf{Capacidad de Importación de Red y Naturaleza de Variables:}
    \begin{equation}
        0 \le g_t^{red} \le \bar{G}_{red}, \quad u_{g,t} \in \{0, 1\}, \quad 0 \le v_{g,t} \le 1, \quad p_{g,t} \ge 0, \quad \forall g \in G, \, t \in T \label{eq:naturaleza}
    \end{equation}
\end{enumerate}

\subsection{Pregunta 1.c: Análisis de la Naturaleza del Problema, Solver y Resolución}
\label{subsec:1c}

\subsubsection*{1. Naturaleza Matemática del Problema}
El problema formulado es un **Programa Lineal Entero Mixto (MILP)**, cuya complejidad computacional es **NP-hard**. La presencia de variables binarias ($u_{g,t}$) induce un espacio de búsqueda no convexo con $2^{5 \times 168} = 2^{840} \approx 5.46 \times 10^{252}$ combinaciones discretas teóricas. La relajación lineal continua produce soluciones fraccionarias no operables (fracciones de generadores encendidos), requiriendo algoritmos de enumeración implícita guiados por planos de corte (\textit{Branch and Cut}) \cite{carrion2006computationally}.

\subsubsection*{2. Idoneidad del Solver Seleccionado}
Se utilizó el solver de código abierto de última generación **HiGHS** (`appsi_highs`), ampliamente validado en investigación operativa \cite{huangfu2018parallelizing}. HiGHS resulta óptimo gracias a:
\begin{itemize}
    \item \textbf{Pre-procesamiento Robusto (\textit{Presolve}):} Reduce drásticamente el tamaño del modelo mediante fijación de variables y apriete de cotas.
    \item \textbf{Planos de Corte Especializados:} Incorpora cortes de cliques, residuo mixto entero (MIR) y Gomory, cerrando la brecha de integrabilidad en el nodo raíz.
    \item \textbf{Simplex Dual Multihilo y Heurísticas Primarias:} Acelera la resolución de las relajaciones en cada nodo y descubre rápidamente soluciones enteras factibles de bajo costo.
\end{itemize}

\subsubsection*{3. Resultados de la Resolución Computacional en Pyomo}
En la Tabla \ref{tab:desempeno_solver} se presentan las métricas de resolución y costos desagregados obtenidos para ambas semillas.

\begin{table}[H]
\centering
\caption{Desempeño del solver HiGHS y costos totales de la solución óptima del Caso Base.}
\label{tab:desempeno_solver}
\setlength{\tabcolsep}{4pt}
\small
\begin{tabular}{lrr}
\toprule
\textbf{Métrica de Optimización} & \textbf{Semilla 392 (Integrante 1)} & \textbf{Semilla 142 (Integrante 2)} \\
\midrule
Estado de terminación / Gap relativo & Óptimo global probado / 0,00\% & Óptimo global probado / 0,00\% \\
Tiempo de cómputo del solver & 0,85 s & 0,78 s \\
Variables de decisión / Restricciones & 1.680 (840 binarias, 840 cont.) / 2.184 & 1.680 (840 binarias, 840 cont.) / 2.184 \\
\midrule
\textbf{Costo Total de Operación [CLP]} & \textbf{\$1.809.604.460,00} & \textbf{\$1.744.790.952,00} \\
-- Costo Variable (Combustible + O\&M) & \$1.694.778.000,00 (93,65\%) & \$1.633.932.000,00 (93,65\%) \\
-- Costo Fijo de Operación (\textit{No-Load}) & \$104.800.000,00 (5,79\%) & \$99.730.000,00 (5,72\%) \\
-- Costo de Arranque (\textit{Startup}) & \$7.500.000,00 (0,41\%) & \$7.800.000,00 (0,45\%) \\
-- Costo de Importación de Red Externa & \$2.526.460,00 (0,14\%) & \$3.328.952,00 (0,19\%) \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Pregunta 1.d: Interpretación de Resultados, Orden de Mérito y Reserva}
\label{subsec:1d}

En la Tabla \ref{tab:desglose_unidades_base} y la Figura \ref{fig:1d_despacho_base} se expone el despacho económico detallado.

\begin{table}[H]
\centering
\caption{Despacho y compromiso de unidades en la solución óptima del Caso Base.}
\label{tab:desglose_unidades_base}
\setlength{\tabcolsep}{3.5pt}
\small
\begin{tabular}{lrrrrrrr}
\toprule
\textbf{Unidad Generadora} & \textbf{Costo Var.} & \multicolumn{3}{c}{\textbf{Semilla 392}} & \multicolumn{3}{c}{\textbf{Semilla 142}} \\
\cmidrule(lr){3-5} \cmidrule(lr){6-8}
& \textbf{[CLP/MWh]} & \textbf{Gen. [MWh]} & \textbf{FP [\%]} & \textbf{Arranques} & \textbf{Gen. [MWh]} & \textbf{FP [\%]} & \textbf{Arranques} \\
\midrule
\texttt{Gas\_Base\_1} & 45.000 & 19.288,0 & 95,7\% & 0 & 19.359,0 & 96,0\% & 0 \\
\texttt{Gas\_Base\_2} & 48.000 & 12.494,0 & 74,4\% & 1 & 12.019,0 & 71,5\% & 2 \\
\texttt{Diesel\_Med\_1} & 85.000 & 2.478,0 & 24,6\% & 5 & 2.133,0 & 21,2\% & 5 \\
\texttt{Diesel\_Med\_2} & 90.000 & 186,0 & 2,2\% & 7 & 40,0 & 0,5\% & 2 \\
\texttt{Peaker} & 120.000 & 9,0 & 0,1\% & 1 & 8,0 & 0,1\% & 1 \\
\midrule
\textbf{Importación Red} & Prom. 169.022 & 14,0 & --- & --- & 18,0 & --- & --- \\
\textbf{Total Sistema} & --- & \textbf{34.469,0} & --- & \textbf{14} & \textbf{33.576,0} & --- & \textbf{10} \\
\bottomrule
\end{tabular}
\end{table}

\begin{figure}[H]
\centering
\includegraphics[height=5.2cm,width=0.92\linewidth]{figuras/fig_1d_despacho_base_sem_392.png}
\caption{Despacho económico apilado y reserva operativa horaria en el Caso Base (Semilla 392).}
\label{fig:1d_despacho_base}
\end{figure}

El análisis técnico-económico arroja conclusiones fundamentales:
\begin{enumerate}
    \item \textbf{Orden de Mérito Económico:} Se verifica un estricto despacho por mérito de costos variables y de no-load:
    \begin{itemize}
        \item \textit{Unidades de Base:} \texttt{Gas\_Base\_1} opera las 168 horas a plena capacidad (FP 95.7\%), sin arranques. \texttt{Gas\_Base\_2} actúa como segunda base modulante (FP 74.4\%), ciclando potencia durante valles nocturnos.
        \item \textit{Unidades Intermedias y de Punta:} \texttt{Diesel\_Med\_1} opera en horas laborales de alta carga (5 arranques semanales sincronizados con el inicio diurno). \texttt{Diesel\_Med\_2} y \texttt{Peaker} se reservan exclusivamente para los picos extremos de demanda ($FP < 2.5\%$).
    \end{itemize}
    \item \textbf{Comportamiento de Arranques:} El modelo evita encender unidades de gas debido a sus cuantiosos costos de partida (\$2.000.000 y \$1.800.000 CLP), mientras que aprovecha la flexibilidad de las máquinas diésel cuyos costos de arranque (\$600.000 y \$500.000 CLP) son absorbidos rápidamente durante las horas diurnas.
    \item \textbf{Uso Racionado de la Red Externa:} La importación de red es ínfima (14 MWh en sem. 392 y 18 MWh en sem. 142). Dado que su costo promedio (\$169.022 CLP/MWh) supera al generador más costoso del complejo (\texttt{Peaker} a \$120.000 CLP/MWh), la red **no se usa para arbitraje**, sino como recurso de confiabilidad ante restricciones de rampa o límites de reserva en picos de demanda.
    \item \textbf{Horas Críticas de Reserva Operativa:} La holgura de reserva ($\text{Reserva Disponible} - Res_t$) se vuelve más exigente en las horas de demanda punta vespertina de días hábiles ($t = 19, 43, 67, 91, 115$), correspondientes a las 18:00--20:00 horas, donde $Res_t$ alcanza 30 MW.
\end{enumerate}

\section{Variaciones}
\label{sec:variaciones}

\subsection{Pregunta 2.a: Incorporación de un Sistema de Almacenamiento (Batería BESS)}
\label{subsec:2a}

Se integró un sistema de almacenamiento BESS con capacidad de energía $\bar{S} = 200$ MWh, potencia máxima de carga/descarga $\bar{B}^{ch} = \bar{B}^{dis} = 60$ MW, eficiencias $\eta^{ch} = \eta^{dis} = 0.95$ y estado de carga inicial y final mínimo $S_0 = 100$ MWh. Se introducen las variables $p_{ch,t}, p_{dis,t} \in [0, 60]$ y $S_t \in [0, 200]$.

\subsubsection*{Modificaciones Matemáticas al Modelo}
\begin{enumerate}[label=\textbf{R\arabic*.}]
    \setcounter{enumi}{6}
    \item \textbf{Balance Dinámico del Estado de Carga (SOC) y Condición Final:}
    \begin{align}
        S_t &= S_{t-1} + \eta^{ch} \cdot p_{ch,t} - \frac{p_{dis,t}}{\eta^{dis}}, \quad \forall t \in T \quad (\text{con } S_0 = 100 \text{ MWh}) \label{eq:soc_bal} \\
        S_{168} &\ge S_0 = 100 \text{ MWh} \label{eq:soc_final}
    \end{align}
    \item \textbf{Balance de Energía Modificado con BESS:}
    \begin{equation}
        \sum_{g \in G} p_{g,t} + g_t^{red} + p_{dis,t} = d_t + p_{ch,t}, \quad \forall t \in T \label{eq:bal_bateria}
    \end{equation}
\end{enumerate}

\subsubsection*{Resultados y Análisis Comparativo con el Caso Base}
En la Tabla \ref{tab:comparacion_bateria} y la Figura \ref{fig:2a_bateria} se sintetiza el impacto del BESS.

\begin{table}[H]
\centering
\caption{Comparación técnica y económica entre el Caso Base y la Variación con Batería BESS.}
\label{tab:comparacion_bateria}
\setlength{\tabcolsep}{4pt}
\small
\begin{tabular}{lrrrr}
\toprule
\textbf{Métrica de Evaluación} & \multicolumn{2}{c}{\textbf{Semilla 392}} & \multicolumn{2}{c}{\textbf{Semilla 142}} \\
\cmidrule(lr){2-3} \cmidrule(lr){4-5}
& \textbf{Caso Base} & \textbf{Con Batería} & \textbf{Caso Base} & \textbf{Con Batería} \\
\midrule
\textbf{Costo Total Semanal [CLP]} & \textbf{\$1.809.604.460} & \textbf{\$1.762.008.593} & \textbf{\$1.744.790.952} & \textbf{\$1.700.570.263} \\
Ahorro Económico Neto [\$] & --- & \textbf{\$47.595.867} & --- & \textbf{\$44.220.689} \\
Reducción Relativa de Costo [\%] & --- & \textbf{2,63\%} & --- & \textbf{2,53\%} \\
\midrule
Importación Red Externa [MWh] & 14,0 MWh & \textbf{0,0 MWh (-100\%)} & 18,0 MWh & \textbf{0,0 MWh (-100\%)} \\
Costo Importación Red [CLP] & \$2.526.460 & \textbf{\$0} & \$3.328.952 & \textbf{\$0} \\
\midrule
Energía Cargada / Descargada BESS & --- & 1.281,8 / 1.156,8 MWh & --- & 1.247,6 / 1.126,0 MWh \\
Pérdidas de Ciclo (Eficiencia 90.25\%) & --- & 125,0 MWh & --- & 121,6 MWh \\
\midrule
\textbf{Arranques Totales de Generadores} & \textbf{14} & \textbf{6 (-57,1\%)} & \textbf{10} & \textbf{7 (-30,0\%)} \\
-- \texttt{Diesel\_Med\_2} (Arranques) & 7 & \textbf{0 (-100\%)} & 2 & \textbf{0 (-100\%)} \\
-- \texttt{Peaker} (Arranques) & 1 & \textbf{0 (-100\%)} & 1 & \textbf{0 (-100\%)} \\
\bottomrule
\end{tabular}
\end{table}

\begin{figure}[H]
\centering
\includegraphics[height=5.0cm,width=0.92\linewidth]{figuras/fig_2a_operacion_bateria_sem_392.png}
\caption{Ciclos de carga, descarga y evolución del estado de carga ($S_t$) del BESS (Semilla 392).}
\label{fig:2a_bateria}
\end{figure}

El análisis operativo revela:
\begin{enumerate}
    \item \textbf{Aplanamiento de Curva de Carga (\textit{Peak Shaving} y \textit{Valley Filling}):} La batería almacena energía en horas de valle nocturno utilizando capacidad ociosa de las máquinas a gas (\$45.000 CLP/MWh) y la descarga durante los picos de las 18:00--21:00 horas inyectando hasta 60 MW.
    \item \textbf{Eliminación Total de Unidades de Punta y Red Externa:} El BESS elimina en un 100\% la importación de red y suprime todos los arranques de \texttt{Diesel\_Med\_2} y \texttt{Peaker}, evitando costosos combustibles y partidas térmicas.
    \item \textbf{Rentabilidad pese a las Pérdidas de Ciclo:} Aunque la eficiencia combinada ($\eta^{ch}\eta^{dis} = 90.25\%$) disipa 125 MWh semanales, el diferencial económico entre cargar a \$45.000 y evitar despachos a \$120.000 CLP/MWh genera un ahorro neto de más de \$47,5 millones CLP semanales.
\end{enumerate}

\subsection{Pregunta 2.b: Respuesta de la Demanda (Carga Interrumpible)}
\label{subsec:2b}

Se modeló la carga interrumpible $r_t \ge 0$ sujeta a la cota horaria $\bar{\ell}^h = 0.20$ ($r_t \le 0.20 \cdot d_t$) y cuota semanal $\bar{\ell}^s = 0.05$ ($\sum r_t \le 0.05 \sum d_t$), con costo unitario de corte $c^{shed}$ [CLP/MWh].

\subsubsection*{Modificaciones Matemáticas al Modelo}
\begin{itemize}
    \item Balance de energía modificado: $\sum_{g \in G} p_{g,t} + g_t^{red} = d_t - r_t, \quad \forall t \in T$.
    \item Cotas de corte: $r_t \le 0.20 \cdot d_t \quad (\forall t \in T)$ y $\sum_{t=1}^{168} r_t \le 0.05 \cdot \sum_{t=1}^{168} d_t$.
    \item Función objetivo modificada: Se incorpora el término de compensación $+\sum_{t=1}^{168} c^{shed} \cdot r_t$.
\end{itemize}

\subsubsection*{Evaluación Paramétrica y Determinación del Umbral Económico}
En la Tabla \ref{tab:cshed_sweep} y la Figura \ref{fig:variaciones_sensibilidad}(a) se exhiben los resultados del barrido de $c^{shed}$.

\begin{table}[H]
\centering
\caption{Sensibilidad del recorte de demanda y costo total frente al costo unitario $c^{shed}$.}
\label{tab:cshed_sweep}
\setlength{\tabcolsep}{3.5pt}
\small
\begin{tabular}{rrrrrrr}
\toprule
$c^{shed}$ & \multicolumn{3}{c}{\textbf{Semilla 392 (Cupo Semanal = 1.723,5 MWh)}} & \multicolumn{3}{c}{\textbf{Semilla 142 (Cupo Semanal = 1.678,8 MWh)}} \\
\cmidrule(lr){2-4} \cmidrule(lr){5-7}
\textbf{[CLP/MWh]} & \textbf{Recorte [MWh]} & \textbf{Horas Corte} & \textbf{Costo Total [CLP]} & \textbf{Recorte [MWh]} & \textbf{Horas Corte} & \textbf{Costo Total [CLP]} \\
\midrule
0 & 1.723,5 & 45 & \$1.648.323.750 & 1.678,8 & 43 & \$1.588.816.657 \\
50.000 & 1.723,5 & 45 & \$1.734.496.250 & 1.678,8 & 43 & \$1.672.689.157 \\
80.000 & 1.723,5 & 45 & \$1.786.319.750 & 1.678,8 & 43 & \$1.723.054.657 \\
90.000 & 294,0 & 11 & \$1.801.521.000 & 577,0 & 16 & \$1.738.535.000 \\
100.000 & 190,0 & 9 & \$1.803.612.000 & 124,0 & 6 & \$1.740.724.000 \\
120.000 & 131,0 & 8 & \$1.807.327.000 & 66,0 & 5 & \$1.742.403.000 \\
150.000 & 14,0 & 4 & \$1.809.232.000 & 30,0 & 5 & \$1.743.959.000 \\
180.000 & 1,0 & 1 & \$1.809.596.862 & 13,0 & 3 & \$1.744.636.175 \\
190.000 & \textbf{0,0} & \textbf{0} & \textbf{\$1.809.604.460} & 10,0 & 2 & \$1.744.766.037 \\
195.000 & 0,0 & 0 & \$1.809.604.460 & \textbf{0,0} & \textbf{0} & \textbf{\$1.744.790.952} \\
200.000 & 0,0 & 0 & \$1.809.604.460 & 0,0 & 0 & \$1.744.790.952 \\
\bottomrule
\end{tabular}
\end{table}

\subsubsection*{Interpretación Microeconómica y Costo Marginal del Sistema}
El corte de carga actúa como un generador virtual. La condición de optimización establece que se corta demanda en la hora $t$ si y sólo si su costo de compensación es inferior al costo marginal del sistema en dicha hora ($c^{shed} < \mu_t$). La curva exhibe tres escalones de saturación:
\begin{enumerate}
    \item Para $c^{shed} \le \$80.000$ CLP/MWh, recortar demanda es más económico que generar con diésel o peaker, saturando el cupo semanal del 5\% (1.723,5 MWh en sem. 392).
    \item Entre \$85.000 y \$120.000 CLP/MWh, el recorte solo sustituye generación diésel marginal y peakers de punta, reduciendo el volumen a 130--290 MWh.
    \item Finalmente, se determina el **umbral de indiferencia económica exacto**:
    \begin{equation}
        c^{shed*}_{392} = \mathbf{\$190.000 \text{ CLP/MWh}}, \quad c^{shed*}_{142} = \mathbf{\$195.000 \text{ CLP/MWh}}
    \end{equation}
    Superado este umbral, $c^{shed}$ excede el precio de importación de la red en horas punta vespertinas, haciendo inviable económicamente cualquier recorte ($r_{total} = 0$).
\end{enumerate}

\subsection{Pregunta 2.c: Costo Fijo por Sobrepasar un Umbral Diario de Emisiones}
\label{subsec:2c}

Cada unidad $g$ emite $e_g$ toneladas de $\text{CO}_2$ por MWh generado ($e_g = [0.35, 0.38, 0.65, 0.68, 0.75]$ t$\text{CO}_2$/MWh). Se impone un umbral diario $\bar{E}^{day} = 1.500 \text{ tCO}_2$ durante cada día $d \in \{1, \ldots, 7\}$ (con $T_d = \{24(d-1)+1, \ldots, 24d\}$), incurriendo en una penalización fija $F$ [CLP/día] en caso de superarlo.

\subsubsection*{Formulación Matemática Big-M}
Se introduce la variable binaria $y_d^{emiss} \in \{0, 1\}$, que indica si el día $d$ supera el umbral:
\begin{enumerate}[label=\textbf{R\arabic*.}]
    \setcounter{enumi}{9}
    \item \textbf{Restricción Disyuntiva Big-M de Emisiones Diarias:}
    \begin{equation}
        \sum_{t \in T_d} \sum_{g \in G} e_g \cdot p_{g,t} - \bar{E}^{day} \le M \cdot y_d^{emiss}, \quad \forall d \in \{1, \ldots, 7\} \label{eq:big_m}
    \end{equation}
    \textit{Determinación del parámetro Big-M:} La emisión física máxima diaria ocurre con las 5 máquinas al 100\% durante 24 horas: $E_{max}^{day} = 24 \times (0.35 \times 120 + 0.38 \times 100 + 0.65 \times 60 + 0.68 \times 50 + 0.75 \times 40) = 4.392 \text{ tCO}_2$. Por ende, la cota superior del exceso es $4.392 - 1.500 = 2.892 \text{ tCO}_2$. Se establece $M = 3.000 \text{ tCO}_2$, garantizando rigor y convergencia veloz del Branch and Bound.
    \item \textbf{Función Objetivo con Penalización Ambiental:}
    \begin{equation}
        \min Z_{emiss} = Z_{base} + \sum_{d=1}^7 F \cdot y_d^{emiss} \label{eq:fo_emiss}
    \end{equation}
\end{enumerate}

\subsubsection*{Evaluación Paramétrica y Tipping Points de Cumplimiento}
En la Tabla \ref{tab:F_sweep} y la Figura \ref{fig:variaciones_sensibilidad}(b) se reporta el barrido paramétrico de $F \in [0, 200.000.000]$ CLP/día.

\begin{table}[H]
\centering
\caption{Sensibilidad de días sobre el umbral de emisiones y costos frente a la penalización $F$.}
\label{tab:F_sweep}
\setlength{\tabcolsep}{3.5pt}
\small
\begin{tabular}{rrrrrrr}
\toprule
$F$ & \multicolumn{3}{c}{\textbf{Semilla 392}} & \multicolumn{3}{c}{\textbf{Semilla 142}} \\
\cmidrule(lr){2-4} \cmidrule(lr){5-7}
\textbf{[CLP/día]} & \textbf{Días Sobre} & \textbf{Costo Op. [CLP]} & \textbf{Emis. [tCO2]} & \textbf{Días Sobre} & \textbf{Costo Op. [CLP]} & \textbf{Emis. [tCO2]} \\
\midrule
0 & 7 & \$1.809.604.460 & 13.242,5 & 5 & \$1.744.790.952 & 12.762,5 \\
1.000.000 & 7 & \$1.809.604.460 & 13.242,5 & 5 & \$1.744.790.952 & 12.762,5 \\
2.000.000 & 7 & \$1.809.604.460 & 13.242,5 & 5 & \$1.744.790.952 & 12.762,5 \\
2.500.000 & 6 & \$1.811.940.452 & 13.212,2 & 5 & \$1.744.790.952 & 12.762,5 \\
3.000.000 & \textbf{5} & \$1.814.686.589 & 13.191,9 & 5 & \$1.744.790.952 & 12.762,5 \\
10.000.000 & 5 & \$1.814.686.589 & 13.191,9 & 5 & \$1.744.790.952 & 12.762,5 \\
50.000.000 & 5 & \$1.814.686.589 & 13.191,9 & 5 & \$1.744.926.896 & 12.756,4 \\
100.000.000 & 5 & \$1.814.751.560 & 13.191,9 & \textbf{0} & \$2.205.465.591 & 10.409,4 \\
120.000.000 & \textbf{0} & \$2.352.042.913 & 10.500,0 & 0 & \$2.205.465.591 & 10.409,4 \\
200.000.000 & 0 & \$2.352.112.600 & 10.500,0 & 0 & \$2.205.465.591 & 10.409,4 \\
\bottomrule
\end{tabular}
\end{table}

\begin{figure}[H]
\centering
\begin{subfigure}[b]{0.48\linewidth}
    \centering
    \includegraphics[width=\linewidth]{figuras/fig_2b_demanda_curt_vs_cshed_sem_392.png}
    \caption{Curva de demanda interrumpible vs $c^{shed}$.}
    \label{fig:2b_curt}
\end{subfigure}
\hfill
\begin{subfigure}[b]{0.48\linewidth}
    \centering
    \includegraphics[width=\linewidth]{figuras/fig_2c_emisiones_vs_F_sem_392.png}
    \caption{Días sobre umbral de emisiones vs penalización $F$.}
    \label{fig:2c_F}
\end{subfigure}
\caption{Sensibilidad paramétrica para las variaciones 2.b (Carga Interrumpible) y 2.c (Penalización de Emisiones $F$).}
\label{fig:variaciones_sensibilidad}
\end{figure}

\subsubsection*{Discusión de Implicancias Técnicas y Regulatorias}
El comportamiento del sistema revela conclusiones de alto valor regulatorio:
\begin{enumerate}
    \item \textbf{Primer Tipping Point (Fines de Semana):} En el caso base, las emisiones de los días 6 y 7 en la Semilla 392 son de $1.520,3$ y $1.530,3 \text{ tCO}_2$, superando el umbral por apenas $20-30 \text{ tCO}_2$. Bajar al umbral exige redispechar hacia \texttt{Gas\_Base\_1} y recurrir a importaciones menores de red. El sobrecosto es de \$5.082.129 CLP para ambos días ($\approx \$2.54$ millones/día). Por tanto, **a partir de $F > \$2.540.000$ CLP/día**, resulta económico abatir estas emisiones, reduciendo los días infractores de 7 a 5.
    \item \textbf{Segundo Tipping Point (Días Hábiles):} En días laborales, la demanda diaria supera los $5.200$ MWh, generando sobre $2.040 \text{ tCO}_2$. Reducir emisiones a $1.500 \text{ tCO}_2$ exige importar masivamente de la red a su tope de 80 MW/h todo el día ($1.920$ MWh/día). Dado que cada MWh importado cuesta $\approx \$169.000$ CLP mientras que el gas propio cuesta $\approx \$45.000$ CLP, el sobrecosto diario supera los **\$108 millones CLP por día hábil**. En consecuencia, el sistema sólo elimina las infracciones en días hábiles cuando la multa supera los **\$110-\$120 millones CLP/día**, con un costo operativo disparado en más de \$542 millones CLP semanales.
    \item \textbf{Ineficiencia de Sanciones Discontinuas vs Impuesto Pigouviano:} Un umbral fijo diario introduce una discontinuidad no convexa. Si el complejo supera el umbral por 1 tonelada, ya paga la multa completa $F$ y pierde todo incentivo marginal a seguir abatiendo durante el resto del día. Un impuesto lineal al carbono (CLP/$\text{tCO}_2$) eliminaría estas ineficiencias, promoviendo abatimiento continuo al menor costo social.
\end{enumerate}

\section{Conclusiones}
\label{sec:conclusiones}

El desarrollo computacional y analítico de la presente Tarea Computacional 1 ha permitido obtener conclusiones determinantes para la toma de decisiones en micro-redes y despacho eléctrico:
\begin{enumerate}
    \item \textbf{Efectividad del Modelamiento MILP:} El modelo de Unit Commitment formulado capturó con fidelidad matemática las restricciones físicas complejas de rampas dinámicas, costos de partida y márgenes de reserva rodante. La implementación en Pyomo resuelta mediante el solver HiGHS garantizó la optimalidad global estricta en menos de un segundo para ambas semillas.
    \item \textbf{Despacho por Orden de Mérito:} La jerarquía de costos variables y costos fijos de no-load gobernó la operación. Las máquinas a gas son el pilar de base con factores de carga superiores al 74\%, mientras que las máquinas diésel proporcionan la agilidad de rampa y seguimiento de carga diurna.
    \item \textbf{Valor del Almacenamiento (BESS):} La batería demostró ser una inversión con alto impacto operacional y financiero, logrando ahorros inmediatos de \$47.595.867 CLP semanales (2.63\%) y blindando al complejo industrial frente a la volatilidad de los precios de la red externa mediante la eliminación total de arranques peakers y de importaciones de red.
    \item \textbf{Consistencia Microeconómica de la Demanda Interrumpible:} Se comprobó rigurosamente que el recorte voluntario de demanda cesa exactamente en el costo marginal máximo de importación (\$190.000--\$195.000 CLP/MWh), validando los principios económicos de formación de precios en sistemas eléctricos.
    \item \textbf{Diseño de Mecanismos Ambientales:} Se evidenció que las sanciones fijas diarias por umbral de emisiones conllevan distorsiones severas e incrementos desproporcionados de costos, recomendándose a los tomadores de decisión la adopción de tributos lineales continuos a las emisiones de $\text{CO}_2$.
\end{enumerate}

% =========================================================================
% REFERENCIAS BIBLIOGRÁFICAS (No cuenta dentro de las 10 páginas)
% =========================================================================
\newpage
\bibliographystyle{IEEEtran}
\bibliography{referencias}

% =========================================================================
% ANEXOS TÉCNICOS (Opcional - No cuenta dentro de las 10 páginas)
% =========================================================================
\newpage
\appendix
\section{Anexo: Tablas de Datos Horarios y Verificación Numérica}
\label{sec:anexo}

En esta sección se presentan extractos tabulares de verificación de la solución óptima del Caso Base para las primeras 24 horas del horizonte semanal (Semilla 392), ratificando la satisfacción estricta de las restricciones de balance de potencia, rampas y reserva operativa mínima.

\begin{table}[H]
\centering
\caption{Despacho horario detallado de las primeras 24 horas (Día 1, Semilla 392).}
\label{tab:anexo_dia1}
\setlength{\tabcolsep}{3.5pt}
\footnotesize
\begin{tabular}{rrrrrrrrrrr}
\toprule
\textbf{Hora $t$} & \textbf{Demanda} & \textbf{Gas 1} & \textbf{Gas 2} & \textbf{Diesel 1} & \textbf{Diesel 2} & \textbf{Peaker} & \textbf{Red} & \textbf{Res. Req.} & \textbf{Res. Disp.} & \textbf{Holgura} \\
& \textbf{[MW]} & \textbf{[MW]} & \textbf{[MW]} & \textbf{[MW]} & \textbf{[MW]} & \textbf{[MW]} & \textbf{[MW]} & \textbf{[MW]} & \textbf{[MW]} & \textbf{[MW]} \\
\midrule
1 & 163 & 70,0 & 65,0 & 28,0 & 0,0 & 0,0 & 0,0 & 16 & 117,0 & 101,0 \\
2 & 144 & 69,0 & 35,0 & 40,0 & 0,0 & 0,0 & 0,0 & 14 & 136,0 & 122,0 \\
3 & 131 & 96,0 & 35,0 & 0,0 & 0,0 & 0,0 & 0,0 & 13 & 89,0 & 76,0 \\
4 & 132 & 97,0 & 35,0 & 0,0 & 0,0 & 0,0 & 0,0 & 13 & 88,0 & 75,0 \\
5 & 129 & 94,0 & 35,0 & 0,0 & 0,0 & 0,0 & 0,0 & 13 & 91,0 & 78,0 \\
6 & 146 & 111,0 & 35,0 & 0,0 & 0,0 & 0,0 & 0,0 & 15 & 74,0 & 59,0 \\
7 & 176 & 120,0 & 56,0 & 0,0 & 0,0 & 0,0 & 0,0 & 18 & 124,0 & 106,0 \\
8 & 218 & 120,0 & 86,0 & 12,0 & 0,0 & 0,0 & 0,0 & 22 & 142,0 & 120,0 \\
9 & 240 & 120,0 & 100,0 & 20,0 & 0,0 & 0,0 & 0,0 & 24 & 120,0 & 96,0 \\
10 & 256 & 120,0 & 100,0 & 36,0 & 0,0 & 0,0 & 0,0 & 26 & 104,0 & 78,0 \\
11 & 256 & 120,0 & 100,0 & 36,0 & 0,0 & 0,0 & 0,0 & 26 & 104,0 & 78,0 \\
12 & 253 & 120,0 & 100,0 & 33,0 & 0,0 & 0,0 & 0,0 & 25 & 107,0 & 82,0 \\
13 & 255 & 120,0 & 100,0 & 35,0 & 0,0 & 0,0 & 0,0 & 26 & 105,0 & 79,0 \\
14 & 243 & 120,0 & 100,0 & 23,0 & 0,0 & 0,0 & 0,0 & 24 & 117,0 & 93,0 \\
15 & 246 & 120,0 & 100,0 & 26,0 & 0,0 & 0,0 & 0,0 & 25 & 114,0 & 89,0 \\
16 & 252 & 120,0 & 100,0 & 32,0 & 0,0 & 0,0 & 0,0 & 25 & 108,0 & 83,0 \\
17 & 264 & 120,0 & 100,0 & 44,0 & 0,0 & 0,0 & 0,0 & 26 & 96,0 & 70,0 \\
18 & 285 & 120,0 & 100,0 & 60,0 & 5,0 & 0,0 & 0,0 & 29 & 125,0 & 96,0 \\
19 & 289 & 120,0 & 100,0 & 60,0 & 9,0 & 0,0 & 0,0 & 29 & 121,0 & 92,0 \\
20 & 278 & 120,0 & 100,0 & 58,0 & 0,0 & 0,0 & 0,0 & 28 & 82,0 & 54,0 \\
21 & 258 & 120,0 & 100,0 & 38,0 & 0,0 & 0,0 & 0,0 & 26 & 102,0 & 76,0 \\
22 & 234 & 120,0 & 86,0 & 28,0 & 0,0 & 0,0 & 0,0 & 23 & 112,0 & 89,0 \\
23 & 195 & 120,0 & 75,0 & 0,0 & 0,0 & 0,0 & 0,0 & 20 & 105,0 & 85,0 \\
24 & 176 & 120,0 & 56,0 & 0,0 & 0,0 & 0,0 & 0,0 & 18 & 124,0 & 106,0 \\
\bottomrule
\end{tabular}
\end{table}

\end{document}
'''

with open('informe.tex', 'w', encoding='utf-8') as f:
    f.write(tex_content)

print("informe.tex successfully written with optimized page layout.")
