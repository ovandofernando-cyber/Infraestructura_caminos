const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, AlignmentType, BorderStyle, WidthType, ShadingType,
        LevelFormat, Footer, PageNumber } = require('docx');
const D = '/home/user/infraestructura_caminos/26_royalties_conservacion_vial/';
const NAVY = '1F3B57', GREEN = '2C6E49', GRAY = '555555', FONT = 'Calibri';
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
const P = (t, o = {}) => new Paragraph({ children: runs(t, { size: 21, ...(o.run || {}) }), spacing: { after: 100 }, ...(o.par || {}) });
const H1 = t => new Paragraph({ children: [new TextRun({ text: t, bold: true, size: 28, color: NAVY, font: FONT })], spacing: { before: 280, after: 120 }, keepNext: true });
const H2 = t => new Paragraph({ children: [new TextRun({ text: t, bold: true, size: 23, color: GREEN, font: FONT })], spacing: { before: 180, after: 80 }, keepNext: true });
const B = (t, lvl = 0) => new Paragraph({ children: runs(t, { size: 21 }), numbering: { reference: 'bul', level: lvl }, spacing: { after: 60 } });
let LISTA = 1;
const N = (t) => new Paragraph({ children: runs(t, { size: 21 }), numbering: { reference: 'num', level: 0, instance: LISTA }, spacing: { after: 60 } });
const F = t => new Paragraph({ children: runs(t, { size: 17, italics: true, color: GRAY }), spacing: { before: 60, after: 120 } });
const ART = t => new Paragraph({ children: runs(t, { size: 20 }), spacing: { after: 100 }, indent: { left: 360, right: 360 },
  shading: { type: ShadingType.CLEAR, color: 'auto', fill: 'F3F6F9' } });
function tabla(cab, filas, anchos, opts = {}) {
  const tot = anchos.reduce((a, b) => a + b, 0);
  const borde = { style: BorderStyle.SINGLE, size: 4, color: 'D0D5DB' };
  const bordes = { top: borde, bottom: borde, left: borde, right: borde };
  const celda = (t, i, head, zebra, bold) => new TableCell({ width: { size: anchos[i], type: WidthType.DXA }, borders: bordes,
    shading: { type: ShadingType.CLEAR, color: 'auto', fill: head ? NAVY : (zebra ? 'F4F6F8' : 'FFFFFF') },
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    children: [new Paragraph({ children: runs(String(t), { size: 18, bold: head || bold, color: head ? 'FFFFFF' : '222222' }) })] });
  const rows = [new TableRow({ tableHeader: true, children: cab.map((c, i) => celda(c, i, true, false)) })];
  filas.forEach((f, j) => rows.push(new TableRow({ cantSplit: true, children: f.map((c, i) => celda(c, i, false, j % 2 === 1, (opts.bold || []).includes(j))) })));
  return new Table({ width: { size: tot, type: WidthType.DXA }, columnWidths: anchos, rows });
}
const W = 9360;
const c = [];
c.push(new Paragraph({ children: [new TextRun({ text: 'Royalties para conservar los caminos vecinales', bold: true, size: 36, color: NAVY, font: FONT })], spacing: { after: 60 } }));
c.push(P('Propuesta para operativizar el financiamiento sostenible del plan de mantenimiento · Equipo 3 · Anexo a la presentación "Plan de mantenimiento sostenible de caminos rurales" · noviembre de 2026', { run: { size: 19, color: GRAY } }));

c.push(H1('1. La propuesta en una página'));
c.push(P('**Qué:**'));
c.push(B('Cada gobernación y cada municipio de los departamentos con caminos vecinales intervenidos destina el **5 % de sus royalties** a un **Fondo Departamental de Conservación de Caminos Vecinales**. Ese 5 % sale del 80 % que la ley ya les obliga a invertir en gastos de capital.'));
c.push(B('El **MOPC pone una contrapartida igual**.'));
c.push(B('El fondo paga el mantenimiento por niveles de servicio **contra la certificación del estado de cada tramo**.'));
c.push(P('**Cuánto:**'));
c.push(B('En San Pedro, Caaguazú, Caazapá y Canindeyú, el 5 % de los royalties de municipios y gobernaciones suma unos **Gs 11.600 millones por año (USD 1,5 millones)**.'));
c.push(B('Con la contrapartida del MOPC, el fondo llega a **USD 3,1 millones por año**.'));
c.push(B('Eso cubre los **301,8 km del plan** (USD 1,36 millones por año) y alcanza para mantener **unos 380 km más** de la red vecinal mejorada de esos departamentos.'));
c.push(P('**Cómo se llega, en dos etapas:**'));
c.push(B('**2027, sin cambiar la ley:** convenios entre el MOPC, la gobernación y los municipios, y ordenanzas que aprueban el aporte. Alcanza con un **2,2 %** de los royalties para financiar el piloto.'));
c.push(B('**Desde 2028, con ley:** se incorpora un artículo 5° bis a la Ley 3984/2010. El aporte pasa a ser **obligatorio y se deposita en origen**: el Ministerio de Economía y Finanzas lo transfiere directamente al fondo, sin pasar por la caja municipal.'));
c.push(P('**Por qué hace falta la ley:**'));
c.push(B('Los esquemas voluntarios ya existieron. Las Agencias de Gestión Vial de Itapúa y Alto Paraná recibieron aportes municipales de entre 10 % y 45 % del costo, pero **se cortaron en 2020 al terminar el préstamo**.'));
c.push(B('Lo que vive de convenios y préstamos se termina con ellos. Una regla en la ley que ya reparte los royalties, con depósito automático, es lo que hace sostenible el mantenimiento.'));

c.push(H1('2. Qué permite hoy la ley'));
c.push(P('Verificado en los textos oficiales de la Biblioteca y Archivo del Congreso Nacional (BACN), el 14 de noviembre de 2026.'));
c.push(tabla(['Norma', 'Qué dice', 'Qué implica para la propuesta'], [
  ['Ley 3984/2010, art. 1', 'Reparte royalties y compensaciones: 50 % a la administración central; 5 % a las gobernaciones "afectadas"; 5 % a las "no afectadas"; 15 % a los municipios "afectados"; 25 % a los "no afectados"', 'La mitad de los royalties ya va a gobiernos subnacionales. Es la fuente natural para mantener la red local'],
  ['Ley 3984/2010, art. 2 (texto de la Ley 5831/2016)', 'Entre municipios: 50 % en partes iguales y 50 % según la población. Canindeyú es departamento "afectado"; en Caazapá son "afectados" los municipios de Caazapá, Yuty y Fulgencio Yegros', 'El reparto no tiene en cuenta los km de caminos. Un fondo departamental repartido por km lo corrige'],
  ['Ley 3984/2010, art. 4 (texto de la Ley 4891/2012)', 'El Ministerio transfiere dentro de los 15 días, "una vez cumplidos los requisitos exigidos en la presente Ley"', 'Las transferencias ya están condicionadas: se puede agregar un requisito o un depósito en origen'],
  ['Ley 4891/2012, arts. 2 y 3', 'Requisitos: balance, informes de resultados, rendiciones cuatrimestrales a la Contraloría y no tener deuda tributaria. Si no se cumplen, "el Tesoro Nacional no transferirá recurso alguno hasta tanto dure el incumplimiento"', 'La sanción ya existe y funciona. Basta con sumar el aporte al fondo como un requisito más'],
  ['Ley 3984/2010, art. 5', 'Gobernaciones: al menos el 80 % a gastos de capital. Municipalidades: 80 % a gastos de capital, 10 % a desarrollo sustentable y 10 % a gastos corrientes vinculados a los de capital. Controla la Contraloría al cierre del ejercicio', 'Hoy los royalties **pueden** usarse en caminos, pero no están **obligados**. El 5 % propuesto cabe dentro del 80 % de capital'],
  ['Ley 6528/2020', 'Modificó el art. 5 solo para 2020 (víveres y gastos corrientes)', 'El Congreso ya cambió el destino de los royalties cuando hubo una prioridad'],
  ['Ley 3966/2010 Orgánica Municipal, art. 12.2.d', 'Es función municipal "la construcción, equipamiento y mantenimiento de los caminos vecinales rurales y otras vías de comunicación que no estén a cargo de otros organismos públicos"', 'Mantener caminos vecinales es competencia municipal. Los tramos del MOPC requieren un convenio'],
  ['Ley 3966/2010, arts. 16 a 18', 'Competencias nacionales delegadas por convenio aprobado por la Junta Municipal, con alcance, control y recursos; convenios intergubernamentales con su financiación', 'Base legal de la etapa 1, sin cambiar la ley'],
  ['Ley 426/1994 Carta Orgánica Departamental, arts. 16.b, 16.h y 45.a', 'La gobernación coordina con los municipios y organiza servicios comunes, como obras públicas que afectan a más de un municipio. Sus planes de inversión incluyen "la construcción de caminos rurales"', 'La gobernación es el nivel natural para administrar un fondo que cubre tramos de varios distritos'],
  ['Ley 4758/2012 (FONACIDE), art. 4', 'Obliga a gobernaciones y municipios a destinar al menos el 50 % a infraestructura educativa ("construcción, remodelación, mantenimiento y equipamiento") y el 30 % a almuerzo escolar', '**Precedente:** una ley nacional ya fija destinos obligatorios para recursos de Itaipú transferidos a gobiernos locales'],
  ['Práctica del MOPC en la DNCP', 'Los contratos de "mantenimiento de caminos rurales por niveles de servicio" (2015, 2016, 2018 y 2022) se registran en la categoría Obras', 'El mantenimiento por niveles de servicio puede imputarse a gasto de capital'],
], [2100, 3900, 3360]));

c.push(H1('3. Cuánto hace falta y cuánto hay'));
c.push(P('**Royalties 2025.** Los de los municipios son la liquidación del MEF. Los de las gobernaciones se estiman con las proporciones del artículo 1 de la Ley 3984/2010, porque no tenemos la planilla.'));
c.push(P('**Costos.** Se usan USD 4.500 por km y año, el costo del plan del equipo, y Gs 7.566 por dólar.'));
c.push(tabla(['Departamento', 'Royalties municipios (miles de millones de Gs)', 'Royalties gobernación (estimado)', '5 % de ambos (miles de millones de Gs)', 'Km del plan (9 tramos)', 'Km vecinales mejorados', 'Km que cubre el 5 % + MOPC 1:1'], [
  ['San Pedro', '53,1', '9,1', '3,1', '104,9', '301', '183'],
  ['Caaguazú', '57,3', '9,1', '3,3', '86,4', '533', '195'],
  ['Caazapá', '28,9', '9,1', '1,9', '75,4', '100', '112'],
  ['Canindeyú', '43,0', '21,9', '3,2', '35,0', '211', '191'],
  ['**Total**', '**182,3**', '**49,3**', '**11,6**', '**301,8**', '**1.145**', '**681**'],
], [1500, 1400, 1300, 1400, 1200, 1200, 1360]));
c.push(esp());
c.push(tabla(['Qué se financia', 'Costo anual', 'Sin contrapartida del MOPC: % de los royalties', 'Con contrapartida 1:1: % de los royalties'], [
  ['Plan del equipo: 301,8 km a USD 4.500/km', 'Gs 10.300 millones (USD 1,36 M)', '4,4 %', '**2,2 %**'],
  ['Plan del equipo a USD 2.600/km (costo del MOPC para el BID)', 'Gs 5.900 millones', '2,6 %', '1,3 %'],
  ['Toda la red vecinal mejorada de los 4 dptos. (1.145 km) a USD 4.500/km', 'Gs 39.000 millones', '16,8 %', '8,4 %'],
  ['Toda la red mejorada a USD 2.600/km', 'Gs 22.500 millones', '9,7 %', '**4,9 %**'],
], [3800, 2000, 1800, 1760]));
c.push(F('Porcentajes sobre los royalties 2025 de municipios y gobernaciones de los 4 departamentos (Gs 231.600 millones). Fuentes: MEF, liquidación de royalties a municipalidades 2025; MOPC, inventario vial (dic. 2025); cálculos del equipo (script roy_01).'));
c.push(P('**Tres lecturas:**'));
c.push(N('**Con un 5 % alcanza para el plan y sobra para crecer.** Con la contrapartida del MOPC, el fondo cubre los 301,8 km y unos 380 km más.'));
c.push(N('**Hay que juntar a nivel departamental, no distrito por distrito.** Los 19 distritos que atraviesan los 9 tramos reciben Gs 45.200 millones de royalties: el plan les costaría el 23 % si lo pagaran solos. Además, los distritos más pobres tienen más km de caminos y menos royalties.'));
c.push(N('**Caazapá necesita más apoyo del MOPC.** Su 5 % cubre 56 km frente a 75 km de tramos. La contrapartida del MOPC debe poder ser mayor donde el aporte local no alcanza.'));

c.push(H1('4. El mecanismo: Fondo Departamental de Conservación de Caminos Vecinales'));
c.push(tabla(['Elemento', 'Diseño propuesto'], [
  ['Entradas', '5 % de los royalties de la gobernación y de cada municipio del departamento (depositado en origen por el MEF desde 2028). Contrapartida del MOPC desde sus programas de conservación (2-002-09 y 2-002-12): 1:1, y hasta 2:1 en los departamentos donde el aporte local no cubre los km a mantener. Aportes de programas BID y CAF cuando existan'],
  ['Cuenta', 'Cuenta especial en el Banco Nacional de Fomento a nombre del fondo, administrada por la gobernación. Los saldos no se pierden al cierre del ejercicio. El 10 % queda como reserva para emergencias por lluvias'],
  ['Gobierno', 'Comité Departamental de Conservación Vial: preside el gobernador; lo integran dos intendentes elegidos por los municipios del departamento y el jefe del distrito de conservación del MOPC, que es la secretaría técnica. Un representante de los usuarios participa con voz'],
  ['Qué financia', 'Mantenimiento rutinario y periódico de caminos vecinales mejorados del inventario del MOPC. Primero, los tramos rehabilitados con préstamos en los últimos 10 años. **No** financia personal permanente, obras nuevas ni calles urbanas'],
  ['Cómo se asigna', 'Según los km mejorados de cada distrito certificados por el MOPC, no según los royalties de cada municipio'],
  ['Cómo se paga', 'Contratos por niveles de servicio (DNCP, categoría Obras) con asociaciones de conservación vial, microempresas o empresas locales. Pago mensual contra el certificado del distrito de conservación, con verificación por muestreo y fotos georreferenciadas'],
  ['Transparencia', 'Publicación mensual de km certificados, pagos y estado de cada tramo. Informe cuatrimestral del MEF y del MOPC al Congreso y a la Contraloría, como ya prevé el art. 3 de la Ley 4891/2012'],
  ['Si no se cumple', 'Con el depósito en origen, el aporte no depende de la voluntad de cada año. Si una gobernación o municipio desvía el fondo, se aplica la retención de transferencias del art. 3 de la Ley 4891/2012'],
], [2000, 7360]));
c.push(H2('El dinero, paso a paso'));
LISTA = 2;
c.push(N('Itaipú y Yacyretá pagan royalties y compensaciones al Tesoro.'));
c.push(N('El MEF calcula la parte de cada gobernación y municipio (arts. 1 y 2 de la Ley 3984) y deposita **el 95 % en sus cuentas y el 5 % en el fondo de su departamento**, dentro de los mismos 15 días.'));
c.push(N('El MOPC transfiere su contrapartida al fondo cada trimestre, según los km certificados.'));
c.push(N('El comité aprueba el plan anual de tramos y contrata por niveles de servicio.'));
c.push(N('El distrito de conservación certifica cada mes el estado de cada tramo, y el fondo paga solo los km certificados.'));
c.push(N('Todo se publica, y la Contraloría controla al cierre del ejercicio.'));

c.push(H1('5. Ruta en dos etapas'));
c.push(tabla(['Cuándo', 'Qué', 'Instrumento', 'Quién'], [
  ['Dic. 2026 a mar. 2027', 'Convenio marco para el piloto en los 4 departamentos', 'Convenio intergubernamental (Ley 3966, arts. 16 a 18; Ley 426, art. 16)', 'Ministro del MOPC, 4 gobernadores, intendentes de los distritos de los tramos'],
  ['Feb. a abr. 2027', 'Aprobar el aporte (al menos 2,2 % de los royalties) y el convenio', 'Ordenanzas de las Juntas Municipales y Departamentales; ampliación o reprogramación del presupuesto 2027', 'Juntas Municipales y Departamentales'],
  ['Mar. a abr. 2027', 'Contrapartida del MOPC para 2027', 'Reprogramación presupuestaria de los programas de conservación', 'MOPC y MEF'],
  ['Abr. 2027', 'Abrir el fondo y lanzar los primeros contratos por niveles de servicio', 'Cuenta en el BNF; resolución del comité; llamado en la DNCP', 'Gobernaciones, MOPC'],
  ['Jun. 2027', 'Presentar el proyecto de ley (art. 5° bis de la Ley 3984)', 'Proyecto del Poder Ejecutivo (MOPC y MEF) o de legisladores de los departamentos', 'Poder Ejecutivo y Congreso'],
  ['Puente', 'Si la ley se demora: un artículo en la Ley de Presupuesto 2028 con la misma regla para ese año', 'Disposición de la Ley del Presupuesto General de la Nación', 'MEF y Congreso'],
  ['Ene. 2028', 'Entra en vigencia la asignación obligatoria con depósito en origen; reglamentación en 90 días', 'Ley y decreto reglamentario', 'MEF, MOPC'],
], [1500, 2900, 2800, 2160]));

c.push(H1('6. Borrador de articulado (para revisión de la asesoría jurídica)'));
c.push(P('~Proyecto de ley que incorpora los artículos 5° bis y 5° ter a la Ley N° 3984/2010 y crea los Fondos Departamentales de Conservación de Caminos Vecinales.~'));
c.push(ART('**Artículo 1°.-** Incorpórase a la Ley N° 3984/2010 el siguiente artículo: **"Art. 5° bis.-** Del porcentaje que las gobernaciones y municipalidades deben destinar a gastos de capital conforme al artículo 5°, como mínimo el cinco por ciento (5 %) de los ingresos percibidos en virtud de la presente ley será destinado a la conservación rutinaria y periódica de los caminos vecinales mejorados del departamento. El Ministerio de Economía y Finanzas depositará dicho porcentaje, en el mismo plazo previsto en el artículo 4°, en la cuenta del Fondo Departamental de Conservación de Caminos Vecinales del departamento correspondiente."'));
c.push(ART('**Artículo 2°.-** Incorpórase a la Ley N° 3984/2010 el siguiente artículo: **"Art. 5° ter.-** Créase en cada departamento el Fondo Departamental de Conservación de Caminos Vecinales, administrado por la gobernación y gobernado por un comité integrado por el gobernador, que lo presidirá, dos intendentes elegidos por los municipios del departamento y el jefe del distrito de conservación del Ministerio de Obras Públicas y Comunicaciones, que ejercerá la secretaría técnica. Los recursos del fondo: a) se asignarán según los kilómetros de caminos vecinales mejorados certificados por el Ministerio de Obras Públicas y Comunicaciones; b) se aplicarán mediante contratos de conservación por niveles de servicio, cuyo pago estará sujeto a la certificación mensual del estado de cada tramo; c) no podrán destinarse a gastos de personal ni a obras nuevas; d) no caducarán al cierre del ejercicio fiscal. El Ministerio de Obras Públicas y Comunicaciones aportará al fondo una contrapartida no menor al monto depositado conforme al artículo 5° bis, en la forma que establezca la reglamentación."'));
c.push(ART('**Artículo 3°.-** El Ministerio de Economía y Finanzas y el Ministerio de Obras Públicas y Comunicaciones publicarán cada mes los kilómetros certificados, los pagos realizados y el estado de cada tramo, e informarán cuatrimestralmente al Congreso Nacional y a la Contraloría General de la República. El incumplimiento de lo dispuesto en los artículos 5° bis y 5° ter estará sujeto a lo previsto en el artículo 3° de la Ley N° 4891/2012.'));
c.push(ART('**Artículo 4°.-** La presente ley regirá a partir del ejercicio fiscal siguiente al de su promulgación. El Poder Ejecutivo la reglamentará dentro de los noventa días.'));
c.push(F('Puntos a definir con la asesoría jurídica: (1) el nombre vigente del ministerio de finanzas en el texto de la ley; (2) si el 5 % aplica también a la porción de los municipios "afectados"; (3) cómo se trata a Asunción, que no tiene caminos vecinales; (4) la fórmula de contrapartida mayor para los departamentos con poco aporte local.'));

c.push(H1('7. Riesgos y cómo responderlos'));
c.push(tabla(['Riesgo', 'Respuesta'], [
  ['Intendentes y gobernadores no quieren perder libre disponibilidad', 'El 5 % sale del 80 % que ya deben invertir en capital y se invierte en su propio departamento. Con la contrapartida del MOPC, cada guaraní local se duplica, y el mantenimiento es visible para sus votantes'],
  ['Objeción de autonomía municipal', 'La ley de royalties ya fija destinos (art. 5), y el FONACIDE obliga a usar al menos el 50 % en infraestructura educativa. Hay precedente de asignaciones obligatorias'],
  ['Desigualdad entre departamentos', 'Reparto por km, no por royalties. Contrapartida del MOPC de hasta 2:1 donde el aporte local no alcanza (por ejemplo, Caazapá)'],
  ['Los royalties varían (tipo de cambio, revisión del Anexo C de Itaipú)', 'Reserva del 10 % y compromisos plurianuales limitados al 80 % de lo recaudado el año anterior'],
  ['Uso político de los contratos', 'Contratación por la DNCP, criterios técnicos para elegir tramos, pago solo contra certificado y publicación mensual'],
  ['El MOPC no tiene capacidad de certificar a tiempo', 'Certificación con app y fotos georreferenciadas, verificación por muestreo y fortalecimiento de los distritos de conservación con parte de la contrapartida'],
  ['¿Es gasto de capital o corriente?', 'Contratar la conservación por niveles de servicio como obra, como ya hace el MOPC en la DNCP'],
], [3000, 6360]));

c.push(H1('8. Cómo llevarlo a la presentación'));
c.push(P('**Diapositiva 6, "Respuesta de diseño" (texto sugerido):** "Un Fondo Departamental de Conservación de Caminos Vecinales con el 5 % de los royalties de gobernaciones y municipios, depositado en origen por el MEF, más una contrapartida igual del MOPC. Paga contra la certificación del estado de cada tramo. 2027: convenios y ordenanzas (2,2 % de los royalties alcanza para el piloto). 2028: art. 5° bis de la Ley 3984/2010."'));
c.push(P('**Diapositiva 10, "Nuestro pedido" (cuarto punto sugerido):** "Enviar al Congreso el proyecto de ley que destina el 5 % de los royalties departamentales y municipales a la conservación de caminos vecinales, con depósito en origen."'));
c.push(P('**Diapositiva 3, canal 1:** la frase "el mantenimiento vive y muere con cada préstamo" queda respondida: la propuesta cambia la fuente de financiamiento de los préstamos a una regla de ley.'));

c.push(H1('Fuentes'));
['Ley N° 3984/2010 y sus modificaciones: Ley N° 4891/2012 (art. 4 y requisitos para la transferencia), Ley N° 5831/2016 (art. 2) y Ley N° 6528/2020 (art. 5, transitoria). BACN, bacn.gov.py, consultado el 14/11/2026.',
 'Ley N° 3966/2010 Orgánica Municipal, arts. 12, 16 y 18. Ley N° 426/1994 Carta Orgánica del Gobierno Departamental, arts. 16 y 45. Ley N° 4758/2012 (FONACIDE), arts. 4 y 5. BACN.',
 'MEF, liquidación de royalties a municipalidades 2025. MOPC, inventario vial (dic. 2025). DNCP, datos abiertos de contrataciones (categoría de los contratos de mantenimiento por niveles de servicio).',
 'Equipo 3, presentación "Plan de mantenimiento sostenible de caminos rurales" (9 tramos PR-L1084, 301,8 km, USD 4.500 por km y año; antecedente de las Agencias de Gestión Vial según la evaluación ex post de JICA PG-P16).',
 'Repositorio Infraestructura_caminos: 22_propuesta_mantenimiento (reparto de royalties y distritos más pobres) y 26_royalties_conservacion_vial (cálculos de este anexo).'].forEach(t => c.push(B(t)));

function esp() { return new Paragraph({ children: [], spacing: { after: 80 } }); }
const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 21 } } } },
  numbering: { config: [
    { reference: 'bul', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 240 } } } }] },
    { reference: 'num', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 300 } } } }] }] },
  sections: [{ properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1080, bottom: 1080, left: 1440, right: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ children: [PageNumber.CURRENT], size: 16, color: GRAY, font: FONT })] })] }) },
    children: c }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(D + 'Propuesta_royalties_conservacion_vial.docx', b); console.log('ok'); });
