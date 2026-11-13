const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun, AlignmentType, BorderStyle,
        WidthType, ShadingType, LevelFormat, PageOrientation, PageBreak } = require('docx');
const D = '/home/user/infraestructura_caminos/24_entregable_mantenimiento/';
const NAVY = '17375E', RED = 'C8102E', GRAY = '555555', FONT = 'Calibri';
const W = 14400; // ancho útil (Letter apaisado 15840 - márgenes 2*720)

// --- texto con negritas: "**...**" y cursivas "_..._"
function runs(t, o = {}) {
  const out = []; const re = /(\*\*[^*]+\*\*|~[^~]+~)/g; let last = 0, m;
  while ((m = re.exec(t)) !== null) {
    if (m.index > last) out.push(new TextRun({ text: t.slice(last, m.index), font: FONT, ...o }));
    const s = m[0];
    if (s.startsWith('**')) out.push(new TextRun({ text: s.slice(2, -2), font: FONT, ...o, bold: true }));
    else out.push(new TextRun({ text: s.slice(1, -1), font: FONT, ...o, italics: true }));
    last = re.lastIndex;
  }
  if (last < t.length) out.push(new TextRun({ text: t.slice(last), font: FONT, ...o }));
  return out;
}
const P = (t, o = {}) => new Paragraph({ children: runs(t, { size: 20, ...(o.run || {}) }), spacing: { after: 80 }, ...(o.par || {}) });
const titulo = t => new Paragraph({ children: [new TextRun({ text: t, bold: true, size: 30, color: NAVY, font: FONT })],
  pageBreakBefore: /^(Diapositiva|Nota para el equipo)/.test(t), spacing: { before: 120, after: 120 }, border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: RED, space: 4 } }, keepNext: true });
const titular = t => new Paragraph({ children: [new TextRun({ text: t, bold: true, size: 22, color: RED, font: FONT })], spacing: { after: 100 }, keepNext: true });
const sub = t => new Paragraph({ children: [new TextRun({ text: t, bold: true, size: 20, color: '222222', font: FONT })], spacing: { before: 100, after: 60 }, keepNext: true });
const bullet = (t, lvl = 0) => new Paragraph({ children: runs(t, { size: 19 }), numbering: { reference: 'bul', level: lvl }, spacing: { after: 40 } });
const fuente = t => new Paragraph({ children: runs(t, { size: 17, italics: true, color: GRAY }), spacing: { before: 80, after: 80 } });
const nota = t => new Paragraph({ children: runs('**Nota / por qué:** ' + t, { size: 18 }), spacing: { before: 160, after: 120 },
  shading: { type: ShadingType.CLEAR, color: 'auto', fill: 'FFF6DC' }, indent: { left: 120, right: 120 },
  border: { left: { style: BorderStyle.SINGLE, size: 24, color: 'E0A800', space: 8 } } });
const salto = () => new Paragraph({ children: [new PageBreak()] });
function img(file, w, h) {
  return new Paragraph({ children: [new ImageRun({ type: 'png', data: fs.readFileSync(D + file), transformation: { width: w, height: h } })], spacing: { after: 60 } });
}
function tabla(cab, filas, anchos, opts = {}) {
  const tot = anchos.reduce((a, b) => a + b, 0);
  const borde = { style: BorderStyle.SINGLE, size: 4, color: 'D9D9D9' };
  const bordes = { top: borde, bottom: borde, left: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, right: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' } };
  const celda = (t, i, head, zebra, bold) => new TableCell({ width: { size: anchos[i], type: WidthType.DXA }, borders: bordes,
    shading: { type: ShadingType.CLEAR, color: 'auto', fill: head ? NAVY : (zebra ? 'F4F6FA' : 'FFFFFF') },
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    children: [new Paragraph({ children: runs(String(t), { size: head ? 17 : 17, bold: head || bold, color: head ? 'FFFFFF' : '222222' }) })] });
  const rows = [new TableRow({ tableHeader: true, children: cab.map((c, i) => celda(c, i, true, false)) })];
  filas.forEach((f, j) => rows.push(new TableRow({ children: f.map((c, i) => celda(c, i, false, j % 2 === 1, (opts.boldRows || []).includes(j))) })));
  return new Table({ width: { size: tot, type: WidthType.DXA }, columnWidths: anchos, rows });
}
const esp = () => new Paragraph({ children: [], spacing: { after: 60 } });

const c = [];
// ---------------- Portada / nota ----------------
c.push(new Paragraph({ children: [new TextRun({ text: 'Entregable: mantener los caminos vecinales que ya construimos', bold: true, size: 34, color: NAVY, font: FONT })],
  spacing: { after: 60 }, border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: RED, space: 4 } } }));
c.push(P('Hackatón de Políticas Públicas BECAL 2026: contenido para la presentación, basado en el memorando al Ministro del MOPC (12/11/2026)', { run: { size: 18, color: GRAY } }));
c.push(titulo('Nota sobre qué hicimos y por qué (no es una diapositiva; explica cómo armamos este documento)'));
c.push(P('Seguimos los cuatro pasos del Documento del Desafío (documentar, diagnosticar, diseñar y presentar la propuesta con costos) y la estructura de diapositivas del ejemplo del Eje 3.'));
c.push(bullet('**Datos.** Censo 2022 (población rural); inventario vial del MOPC (dic. 2025); EPHC 2023-2025 (ponderada); adjudicaciones del MOPC en la DNCP (datos abiertos OCDS, 2018-2025); planilla del MOPC con los 11 tramos rehabilitados con el BID (PR-L1084 y PR-L1092); escuelas y puestos de salud del geoportal del INE; población WorldPop 2020; royalties liquidados por el MEF en 2025. Los scripts ent_01, ent_02 y man_01 del repositorio Infraestructura_caminos (carpetas 22 y 24) vuelven a calcular cada cifra.'));
c.push(bullet('**Primero, validar el memorando.** (1) "1,1 millones de personas rurales, 60,6 %": **confirmado** (1.111.887 en el Censo 2022). (2) "Más de 330 km y USD 46 millones": la planilla suma **333,9 km y Gs 276.288 millones**. Son USD 46 millones al tipo de cambio de cuando se firmaron los contratos (unos Gs 6.000 por dólar), pero **USD 36,5 millones al de 2025**; conviene decir "Gs 276 mil millones". (3) "Reconstruir cuesta tres veces o más": **confirmado**, el Banco Mundial dice de 3 a 5 veces (Harral y Faiz, 1988). (4) CAF (2024): **confirmado** textualmente.'));
c.push(bullet('**Definiciones.** ~Mantenimiento rutinario~: limpieza de cunetas y alcantarillas, control de vegetación y reparaciones menores, todo el año. ~Periódico~: perfilado y reposición de ripio cada pocos años. ~Por niveles de servicio~: se paga contra el estado certificado del camino, no por tarea hecha. ~Caminos intervenidos~: los 11 tramos de la planilla.'));
c.push(bullet('**Por qué esta intervención.** El mantenimiento cumple dos objetivos a la vez: **sostiene los beneficios ya logrados** por los caminos rehabilitados y **reduce el gasto del MOPC**, porque mantener cuesta mucho menos que rehabilitar o reconstruir cuando pasa mucho tiempo. Según el BID, en estos tramos los días transitables pasaron del 75 % al 100 %, el costo de operar un vehículo bajó un 25 % y el tiempo de viaje un 40 %. Hoy nada protege esos logros: menos de Gs 1 de cada Gs 100 fue a mantenimiento, y la CAF califica el mantenimiento del MOPC como "fundamentalmente reactivo". Proponemos el modelo que el MOPC ya usó (contratos por niveles de servicio y convenios con gobiernos locales), con financiamiento estable y datos para evaluarlo.'));
c.push(bullet('**Fuentes externas.** Harral y Faiz (1988), Gertler et al. (2024), Escobal y Ponce (2002), Adukia, Asher y Novosad (2020), Asher y Novosad (2020), el informe de terminación del BID PR-L1084, el informe de cierre del Banco Mundial P082026 (2016) y la evaluación ex post de la CAF (2024).'));

// ---------------- Diapositiva 0 ----------------
c.push(titulo('Diapositiva 0: Equipo'));
c.push(P('**Equipo [Nombre]: "Caminos que Duran"**'));
c.push(P('Eje [completar]: brechas de infraestructura y acceso rural'));
c.push(P('Patrocinador: Ministerio de Obras Públicas y Comunicaciones (MOPC), Dirección de Caminos Vecinales, con las gobernaciones y municipios de San Pedro, Cordillera, Caaguazú, Caazapá, Itapúa y Canindeyú'));
c.push(tabla(['Integrante', 'Institución'], [['[Nombre 1]', '[Institución]'], ['[Nombre 2]', '[Institución]'], ['[Nombre 3]', '[Institución]'], ['[Nombre 4]', '[Institución]']], [7200, 7200]));

// ---------------- Diapositiva 1 ----------------
c.push(titulo('Diapositiva 1: El problema en una cifra'));
c.push(titular('Por cada Gs 100 que el MOPC adjudicó en obras de caminos vecinales y departamentales entre 2018 y 2025, menos de Gs 1 fue a contratos de mantenimiento'));
c.push(bullet('**Gs 5.863 mil millones** en obras frente a **Gs 34 mil millones (0,6 %)** en contratos de mantenimiento de caminos rurales.'));
c.push(bullet('Los **11 tramos rehabilitados con el BID** en los 6 departamentos suman **334 km y Gs 276 mil millones** (USD 36,5 millones de 2025) y no tienen un plan de mantenimiento financiado. Se recibieron entre 2020 y 2026.'));
c.push(bullet('Según la CAF (2024), el MOPC "no cuenta con recursos específicos para el mantenimiento" y este es "fundamentalmente reactivo".'));
c.push(bullet('**Lo que está en riesgo:** con estas obras los días transitables pasaron del 75 % al 100 %, el costo de operar un vehículo bajó un 25 %, el tiempo de viaje un 40 %, y el tránsito diario subió de 156 a 320 vehículos (BID, PR-L1084). Sin mantenimiento, esos logros se pierden de a poco.'));
c.push(bullet('**Lo que cuesta no mantener:** rehabilitar cuesta **de 3 a 5 veces** lo que habría costado mantener a tiempo (Banco Mundial). Con lo que costó rehabilitar 1 km de estos tramos (USD 109.400) se mantienen **42 km durante un año**.'));
c.push(fuente('Definición: contratos de mantenimiento = llamados del MOPC de "mantenimiento de caminos rurales por niveles de servicio" (2018 y 2022). No incluye el mantenimiento que hacen con sus propias máquinas los distritos de conservación, que no se publica.'));
c.push(fuente('Fuentes: DNCP, datos abiertos de contrataciones del MOPC 2018-2025 (clasificación del equipo); MOPC, planilla de tramos PR-L1084 y PR-L1092; BID, informe de terminación PR-L1084; CAF (2024); Harral y Faiz (1988).'));
c.push(nota('Una cifra (0,6 %), una comparación (obras frente a mantenimiento) y una pista sobre la causa (no hay financiamiento específico). También mostramos las dos cosas que se pierden sin mantenimiento: los beneficios ya logrados y el dinero de una nueva rehabilitación.'));

// ---------------- Diapositiva 2 ----------------
c.push(titulo('Diapositiva 2: Quiénes están afectados'));
c.push(titular('1,1 millones de personas rurales dependen de 27.800 km de caminos vecinales, el 94 % de tierra; en el campo se consulta menos a un profesional de salud y se asiste menos a la escuela'));
c.push(img('graf_quienes_afectados.png', 900, 322));
c.push(bullet('**Población:** 1.111.887 personas rurales en los 6 departamentos (60,6 %). Caazapá (76 %) y San Pedro (75 %) son los más rurales.'));
c.push(bullet('**Red:** 27.815 km de caminos vecinales, el **94 % de tierra**. Solo 1.793 km tienen ripio, empedrado o asfalto.'));
c.push(bullet('**Salud:** entre las personas que estuvieron enfermas, el **63 %** de las rurales consultó a un profesional, frente al **69 %** de las urbanas. Las brechas mayores están en Itapúa (9 puntos), Caazapá (9) y Caaguazú (8). El 77 % de los rurales que consultan se atiende en el Ministerio de Salud, frente al 62 % de los urbanos.'));
c.push(bullet('**Educación:** asiste a la escuela el **87,6 %** de los adolescentes rurales de 12 a 17 años, frente al **93,9 %** de los urbanos.'));
c.push(bullet('**Los 11 tramos:** unas **92.000 personas, 262 escuelas y 46 puestos de salud** a menos de 5 km (59.600 personas y 114 escuelas a menos de 2 km). El tramo PY13-Tarumai-San Joaquín (Caaguazú) es el que más personas sirve: 25.600.'));
c.push(fuente('Fuentes: INE, Censo 2022; MOPC, inventario vial (dic. 2025); INE, EPHC 2023-2025, ponderada (13.645 personas rurales y 7.510 urbanas enfermas o accidentadas en los últimos 90 días); geoportal del INE; WorldPop 2020 (población 2020); trazado aproximado de los tramos.'));
c.push(nota('El Documento del Desafío pide al menos un gráfico desagregado por grupo. El de la izquierda muestra la brecha rural en cada departamento; el de la derecha define la población objetivo: quiénes usan los caminos que proponemos mantener. Son brechas descriptivas: no prueban que se deban al camino.'));

// ---------------- Diapositiva 3 ----------------
c.push(titulo('Diapositiva 3: Por qué ocurre'));
c.push(titular('Tres canales, del más fuerte al más débil'));
c.push(img('graf_obras_vs_mantenimiento.png', 640, 301));
c.push(sub('1. No hay financiamiento específico para mantener (la restricción principal)'));
c.push(bullet('El 0,6 % de lo adjudicado fue a mantenimiento. Los contratos por niveles de servicio fueron esporádicos (2012, 2016, 2018 y 2022), por "áreas geográficas" y sin continuidad.'));
c.push(bullet('La CAF: "no existen mecanismos predeterminados" para asignar ingresos al mantenimiento vial, y el compromiso de incluir sus obras en el Programa de Conservación Vial cubrió menos de los 5 años acordados.'));
c.push(sub('2. No hay información para planificar'));
c.push(bullet('El MOPC informa "13.416 km mantenidos por los distritos de conservación" con **la misma cifra en sus balances de 2020, 2024 y 2025**: es una meta, no una medición. No hay registro público de km mantenidos por distrito ni del estado de cada tramo.'));
c.push(bullet('En el proyecto de mantenimiento del Banco Mundial (2007-2016), el indicador de km mantenidos se eliminó porque solo se informaban 101 de unos 1.000 km.'));
c.push(sub('3. Capacidad local débil para ejecutar'));
c.push(bullet('En 13 años, 65 de los 121 municipios de los 6 departamentos adjudicaron algún contrato de mantenimiento de caminos (272 contratos, Gs 40 mil millones en total).'));
c.push(bullet('El piloto de microempresas de mantenimiento del Banco Mundial llegó a **6 de las 10** previstas (26 % de mujeres). Los distritos más pobres tienen **60 % más km** de caminos vecinales y **la mitad de royalties** que los menos pobres.'));
c.push(fuente('Fuentes: DNCP (adjudicaciones MOPC y municipales); MOPC, Balance Anual de Gestión Pública 2020, 2024 y 2025; CAF (2024); Banco Mundial, informe de cierre P082026 (2016); MEF, royalties 2025; INE, Censo 2022 (NBI).'));
c.push(nota('Cada canal tiene un dato de nuestra base y una fuente externa. El canal 1 explica por qué hace falta un financiamiento estable, el 2 por qué hace falta medir y el 3 por qué conviene ejecutar con gobiernos y asociaciones locales con apoyo del MOPC. Son patrones descriptivos.'));

// ---------------- Diapositiva 4 ----------------
c.push(titulo('Diapositiva 4: Nuestra propuesta'));
c.push(titular('"Caminos que Duran": mantener los 334 km rehabilitados para sostener sus beneficios y gastar menos que en volver a rehabilitarlos'));
c.push(P('**En una oración:** durante 3 años, el MOPC contrata el mantenimiento rutinario y periódico menor de los 11 tramos vecinales rehabilitados con el BID (334 km en San Pedro, Cordillera, Caaguazú, Caazapá, Itapúa y Canindeyú). Lo hace mediante convenios con las gobernaciones y los municipios, que contratan asociaciones de conservación vial locales pagadas cada mes contra la certificación del estado del camino. Desde el año 4, lo financia un fondo departamental con una parte de los royalties municipales.'));
c.push(sub('Teoría del cambio'));
c.push(tabla(['Insumos', 'Actividades', 'Productos', 'Resultados'], [
  ['USD 2,95 millones en 3 años (mantenimiento a USD 2.600 por km y año)', 'Relevar el estado de los 334 km y dividirlos en unos 30 subtramos; convenios con 6 gobernaciones y municipios', '334 km bajo contrato por niveles de servicio', 'Caminos transitables todo el año: más días con paso y menos rugosidad (canal 1)'],
  ['Supervisión de los distritos de conservación del MOPC y verificación independiente', 'Pago mensual contra certificado; medición con app de rugosidad y monitores comunitarios', 'Informe público mensual del estado de cada subtramo', 'Un plan plurianual basado en datos (canal 2)'],
  ['Apoyo técnico para conformar asociaciones (experiencia del PR-L1092, con inclusión de mujeres)', 'Conformar y capacitar 11 asociaciones de conservación; herramientas y equipos menores', '11 asociaciones operando, con mujeres en las cuadrillas', 'Capacidad local para mantener; menos reparaciones de emergencia (canal 3)'],
], [3600, 3600, 3600, 3600]));
c.push(P('**Impacto esperado:** (1) se sostienen los beneficios ya logrados: caminos transitables todo el año, menor costo de operar un vehículo y viajes más cortos a escuelas, puestos de salud y mercados; (2) el MOPC gasta menos, porque evita rehabilitar cada pocos años y protege una inversión de Gs 276 mil millones.', { par: { spacing: { before: 100, after: 80 } } }));
c.push(P('**Zona piloto:** los 11 tramos, con 92.000 personas, 262 escuelas y 46 puestos de salud a menos de 5 km. Se eligen porque ya fueron rehabilitados (hay una inversión que proteger), tienen datos de obra y fechas de recepción, y están en los departamentos del memorando.'));
c.push(P('**Supuesto clave:** el deterioro se debe a la falta de mantenimiento, no a defectos de construcción ni a camiones con exceso de carga. Si se mantiene el camino, sigue transitable y dura más.'));
c.push(fuente('Fuentes: MOPC, planilla de tramos PR-L1084 y PR-L1092; costo de mantenimiento: plan del MOPC para el BID (PR-L1092, EEO 7).'));
c.push(nota('La intervención responde uno a uno a los tres canales: financiamiento (contrato estable y luego fondo de royalties), información (certificación y reporte mensual) y capacidad local (asociaciones con apoyo del MOPC). Coincide con la recomendación del memorando.'));

// ---------------- Diapositiva 5 ----------------
c.push(titulo('Diapositiva 5: Qué dice la evidencia'));
c.push(titular('Mantener cuesta menos que reconstruir, y los caminos en buen estado se asocian a más empleo y escolaridad; pero en Paraguay todavía no se midió el efecto del mantenimiento'));
c.push(tabla(['Programa (país)', 'Diseño', 'Efecto', 'Costo'], [
  ['**Deterioro de caminos** (países en desarrollo), Harral y Faiz (1988), Banco Mundial', 'Estudio de política con datos de varios países', 'Restaurar caminos deteriorados cuesta **3 a 5 veces** más que haberlos mantenido a tiempo', '—'],
  ['**Mantenimiento de carreteras** (Indonesia), Gertler, Gonzalez-Navarro, Gracner y Rothenberg (2024)', 'Variables instrumentales (presupuesto vial en dos etapas)', 'Mejor estado del camino: más empleo manufacturero y más ingreso laboral; precios de alimentos perecederos más bajos', 'Beneficio-costo del mantenimiento: **1,8 a 2,3** (según la versión)'],
  ['**Caminos rurales rehabilitados** (Perú, PROVÍAS Rural), Escobal y Ponce (2002)', 'Emparejamiento por puntaje de propensión', 'Más ingreso salarial no agrícola. Los hogares ahorraron el ingreso extra porque veían la mejora como **transitoria**: el mantenimiento debe estar garantizado', '—'],
  ['**PMGSY** (India), Adukia, Asher y Novosad (2020)', 'Regresión discontinua (umbral de población)', 'Más matrícula en la secundaria básica y mejores resultados en exámenes', '—'],
  ['**PR-L1084** (Paraguay; incluye 9 de los 11 tramos), BID, informe de terminación', 'Antes y después (no causal)', 'Días transitables del **75 % al 100 %**; costo de operación vehicular **−25 %**; tiempo de viaje **−40 %**; tránsito diario de 156 a 320 vehículos; 10.700 usuarios por día', 'Rehabilitación: unos USD 109.000 por km en los 11 tramos'],
], [3900, 2900, 4900, 2700]));
c.push(P('**Qué no funcionó:** en India, los caminos nuevos sacaron trabajadores de la agricultura pero cambiaron poco las empresas y el consumo de las aldeas (Asher y Novosad, 2020). En Paraguay, el piloto de microempresas del Banco Mundial llegó a 6 de 10 y perdió su indicador de km mantenidos por falta de datos. **Qué no sabemos todavía:** en nuestros análisis de diferencias en diferencias, los 11 tramos no muestran efectos detectables en sus primeros 2 a 4 años en la luz nocturna de las comunidades cercanas ni en la consulta de salud y la asistencia escolar de sus departamentos. Tampoco encontramos que los contratos municipales de mantenimiento mejoraran el NBI. Por eso no prometemos efectos en la pobreza: el plan sostiene los beneficios directos documentados, y la evaluación medirá el resto.', { par: { spacing: { before: 120, after: 80 } } }));
c.push(P('**Por qué el nuestro debería funcionar en Paraguay:** usa un modelo que el MOPC ya contrató (niveles de servicio 2012-2022 y convenios con gobiernos locales), paga contra resultados que se pueden verificar y se concentra en tramos recién rehabilitados, donde el ahorro por evitar rehabilitaciones es mayor.'));
c.push(nota('El Documento del Desafío pide al menos tres fuentes externas, incluida al menos una evaluación de impacto. Usamos tres con diseños causales distintos (variables instrumentales, emparejamiento y regresión discontinua), un estudio de costos del Banco Mundial y la experiencia paraguaya, y decimos dónde fallaron programas parecidos.'));

// ---------------- Diapositiva 6 ----------------
c.push(titulo('Diapositiva 6: La propuesta al Fondo'));
c.push(titular('USD 2,95 millones en 3 años para mantener 334 km: cada dólar evita USD 2,8 en rehabilitaciones y sostiene otros USD 0,9 de beneficios para los usuarios (escenario base)'));
c.push(sub('Presupuesto y cobertura'));
c.push(tabla(['', 'Año 1', 'Año 2', 'Año 3', 'Total'], [
  ['Km mantenidos (año 1: la mitad de los subtramos, por sorteo)', '167', '334', '334', '835 km-año'],
  ['Costo (millones de USD), con supervisión (10 %), relevamiento, asociaciones, evaluación y 6 % de administración', '0,80', '1,08', '1,08', '**2,95**'],
], [5600, 2200, 2200, 2200, 2200]));
c.push(sub('Resultados y relación costo-resultado (por km y para los 334 km)'));
c.push(tabla(['Escenario', 'Supuestos (rehabilitar; vida sin mantenimiento; tránsito; ahorro)', 'Rehabilitación evitada (USD/km/año)', 'Beneficio de los usuarios sostenido (USD/km/año)', 'Costo del programa (USD/km/año)', 'Beneficio neto, 334 km (M USD/año)', 'Beneficio-costo: solo fiscal / con usuarios'], [
  ['Bajo', 'USD 70.000/km; dura 8 años; 156 veh./día; USD 0,05/veh-km', '3.800', '1.400', '3.200', '0,7', '1,2 / 1,6'],
  ['**Base**', '**USD 70.000/km; dura 5 años; 320 veh./día; USD 0,05/veh-km**', '**9.100**', '**2.900**', '**3.200**', '**3,0**', '**2,8 / 3,7**'],
  ['Alto', 'USD 109.400/km (costo real); 5 años; 320 veh./día; USD 0,10/veh-km', '14.300', '5.800', '3.200', '5,6', '4,4 / 6,2'],
], [1100, 4700, 1700, 1900, 1500, 1600, 1900]));
c.push(img('graf_mantener_vs_reconstruir.png', 460, 161));
c.push(bullet('**¿Comparado con qué?** Seguir como hoy (rehabilitar cada 5 años) cuesta unos **USD 19.400 por km y año** equivalentes; con el plan, unos **USD 13.500**.'));
c.push(bullet('**Beneficios contados:** (1) para el MOPC, la rehabilitación evitada, como costo anual equivalente (tasa del 12 % y vida de 15 años con mantenimiento); (2) para los usuarios, el menor costo de operar un vehículo que se sostiene. Sin mantenimiento, ese ahorro se perdería de a poco hasta la rehabilitación: en promedio, la mitad. **No contados:** el tiempo de viaje (−40 %), los días con paso y el acceso a escuelas y salud. Por eso la estimación es conservadora.'));
c.push(bullet('**Después del año 3:** el plan cuesta unos USD 1,08 millones por año (**Gs 8,1 mil millones**), el **2,4 %** de los royalties que recibieron en 2025 los municipios de los 6 departamentos (Gs 344,6 mil millones). Con el 10 % se mantendría toda su red vecinal mejorada (1.793 km). Proponemos un **fondo departamental repartido según los km**, no municipio por municipio, porque los distritos más pobres tienen más caminos y menos royalties. Hacerlo obligatorio requiere modificar la Ley 3984/2010. Si la evaluación no muestra mejoras, el fondo no se amplía.'));
c.push(fuente('Gs 7.566 = USD 1 (promedio 2025, BCP). Costos: MOPC (EEO 7), Banco Mundial (ICR 2016) y planilla de tramos; supervisión, relevamiento, asociaciones y evaluación son supuestos del equipo.'));
c.push(nota('La cifra clave para el Comité es la relación beneficio-costo, con sus dos partes: lo que el MOPC deja de gastar y lo que los usuarios dejan de perder. La mostramos para los escenarios bajo, base y alto, frente a la alternativa de seguir como hoy. Solo con el ahorro fiscal, el escenario bajo apenas cubre su costo; con los beneficios de los usuarios, lo supera.'));

// ---------------- Diapositiva 7 ----------------
c.push(titulo('Diapositiva 7: Cómo se implementa'));
c.push(titular('El MOPC lidera, las gobernaciones y municipios coejecutan con asociaciones locales, y el MEF y el Congreso aseguran el financiamiento'));
c.push(bullet('**Institución líder:** MOPC, Dirección de Caminos Vecinales, con los distritos de conservación de los 6 departamentos (supervisión y certificación del estado de los caminos).'));
c.push(bullet('**Socios:** las 6 gobernaciones y los municipios de los tramos, mediante convenios con Agencias de Gestión Vial o Asociaciones de Conservación Vial; el BID (experiencia del PR-L1092 y su plan de género); el MEC y el Ministerio de Salud (datos de asistencia y de consultas por establecimiento para la evaluación).'));
c.push(bullet('**Quién debe autorizarlo:** el Ministro del MOPC (resolución que aprueba el plan); el MEF (programa en el Presupuesto 2027); las juntas departamentales y municipales (convenios y aporte de royalties); el Congreso, para destinar royalties de forma permanente (Ley 3984/2010); y las reglas de la DNCP para contratar asociaciones locales.'));
c.push(bullet('**La capacidad estatal que más probablemente lo limite:** supervisar y certificar cada mes el estado de 334 km y pagar a tiempo a las asociaciones. En segundo lugar, formar asociaciones locales que duren: el piloto del Banco Mundial llegó a 6 de 10 microempresas.'));
c.push(bullet('**Mitigaciones:** empezar con la mitad de los subtramos; verificar con app de rugosidad y monitores comunitarios; pago mensual automático contra certificado; apoyo técnico del MOPC y del BID para conformar las asociaciones.'));
c.push(sub('Primer paso a 90 días'));
c.push(tabla(['Días', 'Acción'], [
  ['1-30', 'Resolución ministerial que aprueba el plan; relevamiento del estado de los 11 tramos y división en unos 30 subtramos; costeo por subtramo'],
  ['31-60', 'Firmar convenios con gobernaciones y municipios; modelo de contrato por niveles de servicio; línea de base (estado, tiempos de viaje, escuelas y puestos cercanos)'],
  ['61-90', 'Sorteo público de los subtramos que entran en el año 1; firmar los primeros contratos; comenzar el mantenimiento en la mitad de los subtramos'],
], [2400, 12000]));
c.push(fuente('Fuentes: memorando al Ministro del MOPC (12/11/2026); CAF (2024); MOPC, Balance Anual de Gestión 2025; Ley 3984/2010.'));
c.push(nota('Una institución líder realista, autorizaciones con nombre, una capacidad limitante identificada con honestidad y un primer paso a 90 días que se puede verificar. Los primeros 30 días coinciden con lo que pide el memorando.'));

// ---------------- Diapositiva 8 ----------------
c.push(titulo('Diapositiva 8: Cómo sabremos si funcionó'));
c.push(titular('Un sorteo escalonado por subtramos pone a prueba si el mantenimiento mantiene los caminos abiertos y acorta los viajes'));
c.push(bullet('**Diseño:** el presupuesto y la capacidad de supervisión no alcanzan para empezar en todos los tramos a la vez, así que el orden se decide por sorteo público. Los 334 km se dividen en unos 30 subtramos de 8 a 12 km entre comunidades; dentro de cada tramo, la mitad entra en el mes 1 y la otra mitad en el mes 13.'));
c.push(bullet('**Grupo A:** mantenimiento desde el mes 1.', 1));
c.push(bullet('**Grupo B (lista de espera):** mantenimiento desde el mes 13. Nadie queda sin mantenimiento.', 1));
c.push(bullet('A los 12 meses se comparan A y B: es un experimento, el método más fuerte del curso.', 1));
c.push(bullet('**Resultado principal:** días con paso al año y rugosidad (IRI) de cada subtramo, medidos cada mes con una app de celular y verificados por el distrito de conservación. Es barato, objetivo y no depende de encuestas.'));
c.push(bullet('**Resultados secundarios:** tiempo de viaje a la escuela y al puesto de salud más cercanos; asistencia en las escuelas a menos de 5 km (registros del MEC); consultas en los puestos cercanos (registros de la DIGIES); tránsito; costo certificado por km; empleo y participación de mujeres en las asociaciones.'));
c.push(bullet('**Principales riesgos:**'));
c.push(bullet('Un subtramo en mal estado corta todo el camino. Mitigación: el resultado principal se mide en el propio subtramo y el acceso a servicios, a nivel de tramo.', 1));
c.push(bullet('Lluvias extremas. Mitigación: A y B se comparan en el mismo período y en el mismo tramo.', 1));
c.push(bullet('Asociaciones que no cumplen. Mitigación: pago contra certificado y reemplazo.', 1));
c.push(bullet('Pocos subtramos (unos 30): alcanza para detectar efectos grandes en el estado del camino, no efectos chicos en asistencia escolar.', 1));
c.push(bullet('**Qué nos haría cambiar de rumbo:**'));
c.push(bullet('Al mes 6, menos del 80 % de los subtramos del grupo A cumple el nivel de servicio: revisar contratos y supervisión.', 1));
c.push(bullet('A los 12 meses, los subtramos del grupo A no tienen al menos 30 días con paso más que los del B: no ampliar el fondo de royalties.', 1));
c.push(bullet('El costo certificado supera USD 3.800 por km y año: renegociar o cambiar de modalidad.', 1));
c.push(fuente('Referencia: Gertler, P. et al. (2017), La evaluación de impacto en la práctica, 2.ª ed., sobre la asignación aleatoria cuando hay más candidatos que capacidad.'));
c.push(nota('El sorteo escalonado responde a la segunda mitad de la pregunta del memorando, cómo impacta en las condiciones de vida, que con los datos actuales no se puede medir. Además genera el registro de mantenimiento que hoy no existe.'));

// ---------------- Limitaciones y fuentes ----------------
c.push(titulo('Nota para el equipo: limitaciones (tenerlas listas para las preguntas)'));
c.push(bullet('**Descriptivo frente a causal.** Las brechas rural/urbano son asociaciones. Nuestros análisis de diferencias en diferencias no detectaron efectos de las obras ni de los contratos municipales de mantenimiento en pobreza, NBI o salud. Los efectos esperados vienen de evaluaciones de otros países.'));
c.push(bullet('**Cifra del memorando.** USD 46 millones usa el tipo de cambio de los contratos; al de 2025 son USD 36,5 millones. Mejor decir Gs 276 mil millones.'));
c.push(bullet('**Costos unitarios.** USD 2.600 por km y año viene del plan del MOPC para el BID (2014), sin actualizar. Supervisión, relevamiento, asociaciones y evaluación son supuestos del equipo para verificar con la Dirección de Caminos Vecinales.'));
c.push(bullet('**Vida útil sin mantenimiento** (5 u 8 años): es un supuesto y el parámetro que más pesa.'));
c.push(bullet('**Beneficios de los usuarios.** Vienen del informe del BID (antes y después, no causal). El ahorro por vehículo-km (USD 0,05 a 0,10) y la pérdida gradual sin mantenimiento (en promedio, la mitad) son supuestos del equipo. Nuestros análisis de impacto no detectan efectos en pobreza, salud o educación en los primeros años: no los prometemos.'));
c.push(bullet('**Tramos y población.** El trazado es una línea recta entre extremos, más corta que el camino real. La población cercana sale de WorldPop 2020.'));
c.push(bullet('**DNCP.** Son montos adjudicados, no ejecutados. El mantenimiento por administración no aparece. En 2023-2025 hay pocas adjudicaciones registradas.'));
c.push(bullet('**Royalties.** Se usan los de 2025, más bajos que los de 2024.'));
c.push(titulo('Fuentes'));
c.push(sub('Datos'));
[
  'INE, Censo Nacional de Población y Viviendas 2022; Encuesta Permanente de Hogares Continua 2023-2025 (microdatos, revisión 2025); geoportal (locales educativos y puestos de salud).',
  'MOPC, inventario vial por red y superficie (corte dic. 2025); planilla de tramos intervenidos BID PR-L1084 y PR-L1092; Balance Anual de Gestión Pública 2020, 2024 y 2025.',
  'DNCP, datos abiertos de contrataciones (OCDS), adjudicaciones 2012-2025.',
  'MEF, liquidación de royalties a municipalidades 2025.',
  'WorldPop (2020), población por píxel, Paraguay. Banco Central del Paraguay, tipo de cambio de referencia, promedio 2025.',
].forEach(t => c.push(bullet(t)));
c.push(sub('Evidencia'));
[
  'Harral, C. y Faiz, A. (1988). ~Road Deterioration in Developing Countries: Causes and Remedies.~ Banco Mundial.',
  'Gertler, P., Gonzalez-Navarro, M., Gracner, T. y Rothenberg, A. (2024). "Road Maintenance and Local Economic Development: Evidence from Indonesia\'s Highways." ~Journal of Urban Economics~ (NBER WP 30454).',
  'Escobal, J. y Ponce, C. (2002). "El beneficio de los caminos rurales: ampliando oportunidades de ingreso para los pobres." GRADE, Documento de Trabajo 40.',
  'Adukia, A., Asher, S. y Novosad, P. (2020). "Educational Investment Responses to Economic Opportunity: Evidence from Indian Road Construction." ~AEJ: Applied Economics~ 12(1).',
  'Asher, S. y Novosad, P. (2020). "Rural Roads and Local Economic Development." ~American Economic Review~ 110(3).',
  'BID, PR-L1084, Informe de terminación de proyecto. Banco Mundial (2016), P082026, Informe de cierre. CAF (2024), Evaluación ex post CFA008711.',
  'Gertler, P. et al. (2017). ~La evaluación de impacto en la práctica~, 2.ª ed. BID y Banco Mundial.',
].forEach(t => c.push(bullet(t)));
c.push(sub('Contexto de Paraguay'));
['Ley 3984/2010, distribución de royalties a gobiernos departamentales y municipales (y modificación transitoria, Ley 6528).', 'Memorando al Ministro del MOPC, 12/11/2026.'].forEach(t => c.push(bullet(t)));

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 20 } } } },
  numbering: { config: [{ reference: 'bul', levels: [
    { level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 220 } } } },
    { level: 1, format: LevelFormat.BULLET, text: '◦', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 760, hanging: 220 } } } }] }] },
  sections: [{ properties: { page: { size: { width: 12240, height: 15840, orientation: PageOrientation.LANDSCAPE }, margin: { top: 720, bottom: 720, left: 720, right: 720 } } }, children: c }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(D + 'Entregable_track3_mantenimiento_caminos_vecinales.docx', b); console.log('ok'); });
