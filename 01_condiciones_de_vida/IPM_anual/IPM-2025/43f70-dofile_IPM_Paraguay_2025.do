
/*==============================================================================
                 INSTITUTO NACIONAL DE ESTADÃSTICA (INE)
            SINTAXIS DE ÍNDICE DE POBREZA MULTIDIMENSIONAL (IPM)
                 Año 2025, base anual factor proyección 2025
================================================================================*/
    clear all
    pause on
    clear matrix
    clear mata
    set more off	
/*==============================================================================
						        0. Directory setup                                  
================================================================================*/
    global dir     "C:\GGaleano\IPM\IPM 2025\"    
    global results  "$dir\resultados"
    global data     "$dir\bases"
// Se debe descargar las bases de datos y dejarlas en una
// sola carpeta, en este caso se trabaja el año 2025 base anual.

/*==============================================================================
                          Primero se trabaja en la base REG01
                                 Base de viviendas
=================================================================================*/
use "$data\reg01_anual_2025.dta", clear
// pasa todos los nombres a minuscula, para mayusc. upper
rename *, lower  

// Se crea la variable que identifica a los hogares
gen str3 upms="0000"+string(upm) if upm<10
replace upms="000"+string(upm) if upm>9 & upm<100
replace upms="00"+string(upm) if upm>99 & upm<1000
replace upms="0"+string(upm) if upm>999 & upm<10000
replace upms=string(upm) if upm>9999 & upm!=.

gen str3 nvivis="00"+string(nvivi) if nvivi<10
replace nvivis="0"+string(nvivi) if nvivi>9 & nvivi<100
replace nvivis=string(nvivi) if nvivi>99 & nvivi!=.

gen str1 nhogas=string(nhoga)
egen hhid= concat(upms nvivis nhogas), punc("_")
sort hhid
drop upms nvivis nhogas

sort hhid
order upm nvivi nhoga hhid,  first

save "$results\R01_20_2.dta", replace

/*==============================================================================
                         Ahora se trabaja en la base REG02
                                  Base de población
================================================================================*/
use "$data\reg02_anual_2025.dta", clear
keep if p03<11
rename *, lower  /*upper*/

// Se crea la variable que identifica al hogar
gen str3 upms="0000"+string(upm) if upm<10
replace upms="000"+string(upm) if upm>9 & upm<100
replace upms="00"+string(upm) if upm>99 & upm<1000
replace upms="0"+string(upm) if upm>999 & upm<10000
replace upms=string(upm) if upm>9999 & upm!=.

gen str3 nvivis="00"+string(nvivi) if nvivi<10
replace nvivis="0"+string(nvivi) if nvivi>9 & nvivi<100
replace nvivis=string(nvivi) if nvivi>99 & nvivi!=.
gen str1 nhogas=string(nhoga)
egen hhid = concat(upms nvivis nhogas), punc("_")
sort hhid

drop upms nvivis nhogas

sort hhid
order upm nvivi nhoga hhid, first

save "$results\R02_20_2.dta", replace

/*==============================================================================
                        Se trabaja en la base INGREFAM
                          Ingresos a nivel de hogar
================================================================================*/
use "$data\ingrefam_anual_2025.dta", clear
rename *, lower

// Se crea la variable que identifica al hogar
gen str3 upms="0000"+string(upm) if upm<10
replace upms="000"+string(upm) if upm>9 & upm<100
replace upms="00"+string(upm) if upm>99 & upm<1000
replace upms="0"+string(upm) if upm>999 & upm<10000
replace upms=string(upm) if upm>9999 & upm!=.

gen str3 nvivis="00"+string(nvivi) if nvivi<10
replace nvivis="0"+string(nvivi) if nvivi>9 & nvivi<100
replace nvivis=string(nvivi) if nvivi>99 & nvivi!=.
gen str1 nhogas=string(nhoga)
egen hhid = concat(upms nvivis nhogas), punc("_")
sort hhid
drop upms nvivis nhogas

keep hhid upm nvivi nhoga totpers facpob linpobto linpobex pobrezai pobnopoi
sort hhid

save "$results\ingre_20_2.dta", replace

/*==============================================================================
                           Se une las tres bases
================================================================================*/
// Se pega todas las variables de r01 a ingrefam por hhid
use "$results\R01_20_2.dta", clear
merge 1:1 hhid using "$results\ingre_20_2.dta", nogen
// Se pega todas las var de r02 a ingrefam 
merge 1:m hhid using "$results\R02_20_2.dta", nogen   

sort hhid
order upm nvivi nhoga hhid, first
label var hhid "identificador hogar"

save "$results\MPI_EPH2025_2.dta", replace

/*==============================================================================
              Preparar los identificadores por cada dimensión
================================================================================*/

set dp comma

/*==============================================================================
                               I. EDUCACIÓN 
================================================================================*/

use "$results\MPI_EPH2025_2.dta", clear

/*==============================================================================
                  1. Asistencia escolar de personas de 6 a 17 años de edad
================================================================================
Se considera privado aquel hogar con al menos una persona de 6 a 17 años de 
edad no matriculada en escolarización obligatoria.                              */

desc añoest p02 ed08 ed03 // Para describir las variables

rename añoest anios_estudios
rename p02 edad
gen actualmente_escuela=(ed08<19) if ed08!=.
replace actualmente_escuela=0 if ed03==6


gen edad_escolar= (edad>=6 & edad<=17)
tab edad_es
bysort hhid: egen hh_edad_escolar=max(edad_escolar) //Para identifacar a los hogar con miembros en edad escolar
tab hh_edad_escolar, m 

gen ni_noasis= (actualmente_escuela==0) if edad_escolar==1 
tab ni_no if edad_escolar==1, m  // Asistencia escolar de niños en edad escolar

// Se genera una nueva variable llevando a nivel de hogar la privación, porque 
// el problema afecta a los demás integrantes del hogar.

bysort hhid: egen hh_d_ni_noasis= max(ni_noasis)
tab hh_d_ni_noasis, m

// Se cera los hogares donde no hay chicos de 6 a 17
replace hh_d_ni_noasis=0 if hh_edad_escolar==0
tab hh_d_ni_noasis, m
tab hh_d_ni_noasis [iw=factor], m   

label var hh_d_ni_noasis "Inasistencia escolar de personas de 6 a 17 años de edad"

/*==============================================================================
                                2. Escolarización atrasada
================================================================================
Se considera con privación aquel hogar con al menos una persona de entre 8 a 19
años de edad, asistiendo actualmente a una institución educativa o participa de 
un programa de enseñanza, con retraso de 2 o mâs años según la edad normativa 
para cada nivel escolar.
Ejemplo: con 19 años de edad una persona puede estar en el 3ro de la media, lo 
que indica que solo tiene 11 años de estudio.                                      */

gen miembros_elig=((edad>=8 & edad<=19) & (actualmente_escuela==1 & anios_estudios<=12)) 
bysort hhid: egen hh_miembros_elig=sum(miembros_elig), m 
tab hh_miembros_elig, m

// Contador de miembros de 8 a 19 años
replace hh_miembros_elig=(hh_miembros_elig>0)
tab hh_miembros_elig

gen escolarizacion_retardada=((edad-anios_estudios)>=8) if edad!=. & anios_estudios!=. & ///
miembros_elig==1

// Se genera una nueva variable llevando a nivel de hogar la carencia, es 
// decir: si hay un rezagado en el hogar, se extiende a todos sus miembros
bysort hhid: egen hh_d_esc_retardada=max(escolarizacion_retardada) 
replace hh_d_esc_retardada = 0 if hh_miembros_elig==0
tab hh_d_esc_retardada, m
tab hh_d_esc_retardada[iw=factor], m   
label var hh_d_esc_retardada "Escolarización atrasada"

/*==============================================================================
                     3. Año de estudio logrado y analfabetismo
================================================================================
El hogar se halla privado si ningún miembro del hogar ha alcanzado los niveles 
mínimos de escolaridad requeridos según se detalla:
- A los nacidos en el año 1996 hasta el año de la encuesta, se les exige 12 años 
  de estudio.
- A los nacidos entre 1988 y 1995, se les exige 9 años de estudio.
- A los nacidos antes de 1988, se les exige 6 años de estudio.
- Para las personas entre 50 y 65 años de edad se indaga si es analfabeta, 
  es decir, si sabe leer y escribir.                                          */

// Año de la base 2024
gen logro= (anios_estudio<12) if edad>=18 & edad<=29 & anios_estudio!=99 & anios_estudio!=.
tab logro,m  // 18 a 28 años, para el 2, le pedimos 12 años.

replace logro= (anios_estudio<9) if edad>=30 & edad<=37 & anios_estudio!=99 & anios_estudio!=. 
tab logro,m  // 25 a 36 años, para el 2024, le pedimos 9 años.

replace logro= (anios_estudio<6) if edad>=38 & edad<=58 & anios_estudio!=99 & anios_estudio!=.
tab logro, m  // 37 a 49 años, para el 2024, le pedimos 6 años.

rename ed02 leer_escribir
replace logro= (leer_escribir>=2 & leer_escribir<=6) if edad>=59 & edad <75 & leer_escribir!=9 & leer_escribir!=.
tab logro,m

sort hhid
bysort hhid: egen hh_d_logro_min=min(logro)
tab hh_d_logro_min, m

replace hh_d_logro_min=0 if hh_d_logro_min==. 
tab hh_d_logro_min [iw=factor],m  
label var hh_d_logro_min "Educación obligatoria incompleta y analfabetismo"


// Resumen
tab hh_d_ni_noasis [iw=factor], m   // 3,22 Inasistencia escolar de personas de 6 a 17 años de edad
tab hh_d_esc_retardada[iw=factor], m // 5,80 Escolarización atrasada
tab hh_d_logro_min[iw=factor],m      // 8,77 Educación obligatoria incompleta y analfabetismo

save "$results\MPI_EPH2025_3.dta", replace

/*======================================================================================
                       II. TABAJO Y SEGURIDAD SOCIAL
========================================================================================

========================================================================================
                                 1. Desocupación
========================================================================================
Se consideran con privación aquellos hogares en los que al menos un miembro del
hogar, cuya edad se halla comprendida entre 18 y 64 años se halla desocupado          */

gen pob_18_64 = (edad>=18 & edad <=64) 
bysort hhid: egen hh_pob_18_64 = sum(pob_18_64), m  
tab hh_pob_18_64, m
replace hh_pob_18_64= (hh_pob_18_64>0)
tab hh_pob_18_64, m

gen dy=(peaa==2) if peaa!=. & pob_18_64==1
tab dy
bysort hhid: egen hh_d_destotalmax =max(dy)

// Se sera los hogares donde no hay población de interés
replace hh_d_destotalmax=0 if hh_pob_18_64==0

tab hh_d_destotalmax, m
tab hh_d_destotalmax [iw=factor], m  // 11,34  Desocupacion

label var hh_d_destotalmax "Desocupacion"

/*======================================================================================
                 2. Subocupación por insuficiencia de tiempo
========================================================================================
Se consideran con privación aquellos hogares en los que al menos un miembro del
hogar, cuya edad se halla comprendida entre 18 y 64 años y está desocubocupado 
por insuficiencia de tiempo, con un total de horas inferior a 40.             */
desc horabco d01 d03 peaa
gen subocvi40=(horabco<40 & ((d01==1) | ((d01==9) & (d03>=1 & d03<=3))))
tab subocvi40[iw=factor], m  // El umbral de 40 horas, fue consensurado con el Comité

gen dl=(subocvi40==1) if peaa!=. & pob_18_64==1
tab dl, m

bysort hhid: egen hh_d_subocup_max=max(dl)

// Se cera los hogares donde no hay pob de interes.
replace hh_d_subocup_max=0 if hh_pob_18_64==0
label var hh_d_subocup_max "Subocupación por insuficiencia de tiempo"

tab hh_d_subocup_max, m
tab hh_d_subocup_max [w=factor], m 


/*=====================================================================================
                   3. Trabajo infantil de niños de 10 a 17 años de edad.
=======================================================================================
Ninos de 10 a 13 años
Se consideran hogares privados en este indicador aquellos con algún miembro de 
10 a 13 años de edad ocupado que realiza cualquier actividad dentro del 
territorio nacional por lo menos una hora.                                    */

gen pob10_13 = (edad>=10 & edad<=13)
tab pob10_13, m

gen ni_10_13= (peaa==1) if pob10_13==1 & peaa!=. 
tab ni_10_13

/* Niños de 14 a 15 años
Se consideran hogares privados en este indicador aquellos con algún miembro
de 14 a 15 años de edad ocupado que realiza cualquier actividad dentro del 
territorio nacional en una cantidad de horas mayor a 24 durante los últimos 
siete días de la semana.                                                  */

gen pob14_15 = (edad>=14 & edad<=15)
tab pob14_15
gen ni_14_15 = (peaa==1 & horabco >24) if pob14_15==1
tab ni_14_15

/* Niños de 16 a 17 años
Se consideran hogares privados en este indicador aquellos con algún miembro
de 16 a 17 años de edad ocupado que realiza cualquier actividad dentro del 
territorio nacional en una cantidad de horas mayor a 36 durante los últimos 
siete días de la semana.                                                      */

gen pob16_17 = (edad>=16 & edad<=17)
tab pob16_17
gen ni_16_17 = (peaa==1 & horabco>36) if pob16_17==1
tab ni_16_17

gen pob10_17 = (edad>=10 & edad<=17)
bysort hhid: egen hh_pob10_17= max(pob10_17)
gen nino_ocup= (ni_10_13==1 | ni_14_15==1 | ni_16_17==1 ) if pob10_17==1
tab nino_ocup

bysort hhid: egen hh_d_10a17_ocup= max(nino_ocup)
tab hh_d_10a17_ocup
tab hh_d_10a17_ocup, m

// Los hogares donde no hay chicos quedan como no privados
replace hh_d_10a17_ocup=0 if hh_pob10_17==0 
tab hh_d_10a17_ocup [w=factor], m  

label var hh_d_10a17_ocup "Trabajo de personas de 10 a 17 años de edad"

/*======================================================================================
                    4. Falta de aporte a caja jubilatoria
========================================================================================
Se consideran privados aquellos hogares con al menos una persona cuya edad 
estéentre 18 y 64 años. que este ocupada y que no contribuya a alguna caja 
jubilatoria.                                                                  */
desc b10 c07
gen pob=(peaa==1) if (edad>=18 & edad <=64)
gen aporte=(b10==1|c07==1) if pob==1 

tab pob
tab aporte

gen no_afiliados=(aporte==0)
tab no_afiliados, m

bysort hhid: egen hh_d_no_afil=max(no_afiliados)

tab hh_d_no_afil [w=factor],m   
label var hh_d_no_afil "Falta de aporte a caja jubilatoria"

/*======================================================================================
                     5. Jubilación y pensión
========================================================================================
El hogar se halla privado en este indicador si algún miembro de 65 años o más 
de edad no recibe pensión contributiva y no recibe pensión no contributiva 
(Adultos mayores y Tekoporâ).                                                 */

des e01hde e01kde e01ide

// Jubilación 
gen p_cont= (e01hde==0) if edad>=65 
gen p_no_cont= (e01ide==0 & e01kde==0) if edad>=65

tab p_cont
tab p_no_cont

// Población sin jubliación, ni adulto mayor ni tekoporâ
gen w=(p_cont==1 & p_no_cont==1) if edad>=65
tab w, m

bysort hhid: egen hh_d_jubi_pens =max(w) 
tab hh_d_jubi_pens,	m

gen pob65ymas=(edad>=65)
tab pob65ymas, m
bysort hhid: egen hh_pob65ymas= max(pob65ymas)
tab hh_pob65ymas,m

// Ceramos los hogares donde no hay pob de 65 y mas años de edad
replace hh_d_jubi_pens=0 if hh_pob65ymas==0
tab hh_d_jubi_pens [w=factor], m  
label var hh_d_jubi_pens "Falta de acceso a jubilacion o pension"

// Resumen 
tab hh_d_destotalmax [w=factor] // 9,23  desocupados.
tab hh_d_subocup_max [w=factor] // 9,41 Subocupada por insuficiencia de tiempo de trabajo.
tab hh_d_10a17_ocup [w=factor]  // 3,25 Con trabajo infantil.
tab hh_d_no_afil [w=factor]     // 77,35 Sin aporte a una caja de jubilación.   
tab hh_d_jubi_pens [w=factor]   // 9,21 Sin pensión ni jubilación  

save "$results\MPI_EPH2025_4.dta", replace

/*======================================================================================
                         III. VIVIENDA Y SERVICIOS
========================================================================================

========================================================================================
                        1. Materialidad de la vivienda
========================================================================================
Se considera con privación aquellos hogares que presente al menos una de las 
siguientes características en la vivienda:
-Pared: hogar con pared de estaqueo, adobe, tronco de palma, cartón, hule, 
 madera de embalaje, no tiene pared, otro.
-Piso: hogar con piso de tierra. 
-Techo: hogar con techo de paja, tronco de palma, cartón, hule, madera de 
 embalaje, otro.                                                              */
 
sort hhid

gen hh_d_pared=(v03==1|v03==2|v03==6|v03==7|v03==8|v03==9)
replace hh_d_pared=. if v03==99
tab hh_d_pared
tab hh_d_pared [w=factor], m

gen hh_d_piso=(v04==1)
replace hh_d_piso=. if v04==99
tab hh_d_piso
tab hh_d_piso[w=factor], m

gen hh_d_techo=(v05==2|v05==7|v05==8|v05==9)
replace hh_d_techo=. if v05==99
tab hh_d_techo
tab hh_d_techo [w=factor], m

gen hh_d_materialidad=(hh_d_pared==1|hh_d_piso==1|hh_d_techo==1)
replace hh_d_materialidad =. if (hh_d_pared==. & hh_d_piso==. & hh_d_techo==.)
tab hh_d_materialidad [w=factor], m  
label var hh_d_materialidad "Materiales inadecuados de la vivienda"

/*=======================================================================================
                                   2. Hacinamiento
/========================================================================================
Se consideran con privación aquellos hogares con más de tres personas por 
dormitorio.
Hogares con más de 3 personas por dormitorio.                                 */

tab v02b
replace v02b = 1 if v02b==0
tab v02b

gen per_dormitorio=(totpers/v02b)

gen hh_d_hacinamiento = .
replace hh_d_hacinamiento = 1 if per_dormitorio >3 & per_dormitorio !=.
replace hh_d_hacinamiento = 0 if per_dormitorio <=3
tab hh_d_hacinamiento, m
tab hh_d_hacinamiento [w=factor], m 
label var hh_d_hacinamiento "Hacinamiento"

/*======================================================================================
                          3. Malas prácticas de eliminación de basura
========================================================================================
El hogar es privado si elimina la basura a traves de la quema, o tirar en hoyo, 
patio, baldio zanja o calle, en la chacra, o en arroyo, rio o laguna u otro
(lleva al parque, motocarro lleva, entierra, le da a otra persona).           */

gen hh_d_sin_disp_basura= (v15==1|v15==4|v15==5|v15==7|v15==8|v15==9)
replace hh_d_sin_disp_basura = . if v15==99
tab hh_d_sin_disp_basura, m
tab hh_d_sin_disp_basura [w=factor] eliminacion de basura
label var hh_d_sin_disp_basura "Practicas inadecuadas o falta de servicios para eliminacion de basura"

// Resumen
tab hh_d_materialidad [w=factor], m     // 3,67 Con carencia en materiales de la viv.
tab hh_d_hacinamiento [w=factor], m     // 7,86 Hacinamiento
tab hh_d_sin_disp_basura [w=factor], m  // 31,39 Practicas inadecuadas o falta de servicios para eliminacion de basura

/*======================================================================================
                             IV. SALUD Y AMBIENTE
========================================================================================
1. Acceso a atención médica

Definición de la privación:
- Hogares con algun miembro que no obtuvo acceso a atencion medica cuando estuvo 
  enfermo o accidentado (en los últimos tres meses).
- Porque: No habia atencion cercana, la atención es mala, las consultas son 
  caras, se automedico.
- Tambien se tiene en cuenta como privado al hogar en la que al menos una 
  persona ha consultado a: partera empirica (chae) farmaceutico/a,
  curandero/a, familiar o vecino, otro.                                       */

gen sin_atencion_med =((s03==1|s03==2)&(s05==2|s05==3|s05==4|s05==5 |s05==8)|(s04==1 & /*
                    */(s06==3|s06==6|s06==7|s06==8|s06==9))) if (s03!=9 & s03!=.)
bysort hhid: egen hh_d_sin_atencion_med = max(sin_atencion_med)

tab hh_d_sin_atencion_med, m
tab hh_d_sin_atencion_med [w=factor], m  
label var hh_d_sin_atencion_med "Personas enfermas o accidentadas sin acceso a atencion medica profesional"

/*=======================================================================================
                             2.Agua mejorada
=========================================================================================
Definición de la privación:
- Hogares que no tengan acceso al agua a traves de: ESSAP, SENASA, 
- Junta de Saneamiento, Red Comunitaria, Red o prestador privado, pozo artesiano.         */

gen hh_d_agua_mejorada = (v06!=1 & v06!=2 & v06!=3 & v06!=4 & v06!=5)
replace hh_d_agua_mejorada=. if v06==99
tab hh_d_agua_mejorada, m
tab hh_d_agua_mejorada[w=factor] 
label var hh_d_agua_mejorada "Falta de acceso a agua mejorada"

/*=====================================================================================
                             3. Saneamiento mejorado
=======================================================================================

Definición de la privación:
- El hogar que no tenga baño o si tiene y no esta conectado a la red de cloaca 
  de alcantarillado o no tenga
- Cámara séptica y pozo ciego.                                                             */

gen hh_d_san_mejorado = (v12==6 |(v13!=1 & v13!=2 & v13!=3))
replace hh_d_san_mejorado = . if v13==9
tab hh_d_san_mejorado
tab hh_d_san_mejorado [w=factor], m 
label var hh_d_san_mejorado "Falta de saneamiento mejorado"
browse if  hh_d_san_mejorado==. //Para observar los valores perdidos
/*=====================================================================================
                             4. Combustible de cocina
=======================================================================================
Definición del indicador:
- Hogares que cocinan con carbon o lena.                                                    */

gen hh_d_combustible = (v14b==1 | v14b==3)
replace hh_d_combustible = . if v14b==9
tab hh_d_combustible
tab hh_d_combustible [w=factor], m  
label var hh_d_combustible "Uso de carbón o leña para cocinar"
br if  hh_d_combustible==. //Para observar valores perdidos

// Resumen:
tab hh_d_sin_atencion_med [w=factor], m // 26,27 en acceso en la atención médica.
tab hh_d_agua_mejorada[w=factor],m      // 8,76  con déficit en acceso agua mejorada.
tab hh_d_san_mejorado [w=factor], m     // 6,53 con déficit en acceso a saneamiento mejorado.
tab hh_d_combustible [w=factor],m       // 16,25 con déficit en acceso a combustión adecuada.

save "$results\MPI_EPH2024_5.dta", replace

desc hh_d_*
count

save "$results\indicadores_I.dta", replace
set dp comma, perm

/*=======================================================================================
                                 MUESTRA RELEVANTE
=========================================================================================
Se contruye una variable filtro que identifica las observaciones con información
en todos los indicadores                                                                         */

gen sample = (hh_d_ni_noasis!=. & hh_d_esc_retardada!=. & hh_d_logro_min!=. & /*
*/ hh_d_destotalmax!=. & hh_d_subocup_max!=. & hh_d_10a17_ocup!=. & hh_d_no_afil!=. & /*
*/ hh_d_jubi_pens!=. & hh_d_materialidad!=. & hh_d_hacinamiento!=. & hh_d_sin_disp_basura!=. & /*
*/ hh_d_sin_atencion_med!=. &  hh_d_agua_mejorada!=. &  hh_d_san_mejorado!=. & hh_d_combustible!=.)

sum hh_d_ni_noasis hh_d_esc_retardada hh_d_logro_min [aw=factor] if sample==1
sum hh_d_destotalmax hh_d_subocup_max hh_d_10a17_ocup hh_d_no_afil hh_d_jubi_pens [aw=factor] if sample==1
sum hh_d_materialidad hh_d_hacinamiento hh_d_sin_disp_basura [aw=factor] if sample==1
sum hh_d_sin_atencion_med hh_d_agua_mejorada hh_d_san_mejorado hh_d_combustible [aw=factor] if sample==1

/* 1. Valores perdidos

 Analisis final para mirar el n° total de valores perdidos que existe en cada indicador.  
 Las variables no deben tener un alto porcentaje de valores perdidos en esta etapa.
 Es posible que el comando no este instalado: escribir "findit mdesc" en la ventana de comandos                 
findit mdesc     */
mdesc hh_d_ni_noasis hh_d_esc_retardada hh_d_logro_min 
mdesc hh_d_destotalmax hh_d_subocup_max hh_d_10a17_ocup hh_d_no_afil hh_d_jubi_pens
mdesc hh_d_materialidad hh_d_hacinamiento hh_d_sin_disp_basura
mdesc hh_d_sin_atencion_med hh_d_agua_mejorada hh_d_san_mejorado hh_d_combustible  

/*=======================================================================================
                       Análisis de los indicadores de IPM
=========================================================================================
Ver do file coeficiente P y Cramer
3. Cramer's V                                                                                   	
Dejamos solo esas observaciones con información en todos los indicadores 
relevantes y que son de miembros del hogar.                                                                               */

keep if sample==1 
count
save "$results\indicadores_II.dta", replace


/*=======================================================================================
                            1: Construyendo el Indice                                   
========================================================================================*/

set dp comma, perm

rename hh_d_sin_atencion_med hh_d_sin_salud
label var hh_d_sin_salud "Personas enfermas o accidentadas sin acceso a atencion medica profesional"
rename hh_d_sin_disp_basura hh_d_sin_basur
label var hh_d_sin_basur "Practicas inadecuadas o falta de servicios para eliminacion de basura"
rename hh_d_agua_mejorada hh_d_agua_mejor
label var hh_d_agua_mejor "Falta de acceso a agua mejorada"
rename hh_d_san_mejorado hh_d_san_mejor
label var hh_d_san_mejor "Falta de saneamiento mejorado"
rename hh_d_combustible hh_d_combus
label var hh_d_combus "Uso de carbón o leña para cocinar"


format %14.0g hh_d_*

gen pobre_extremo=(pobrezai==1)
gen pobre_no_extremo=(pobrezai<=2)

set more off
global ed = "hh_d_ni_noasis hh_d_esc_retardada hh_d_logro_min"
global em = "hh_d_destotalmax hh_d_subocup_max hh_d_10a17_ocup hh_d_no_afil hh_d_jubi_pens"
global vi = "hh_d_materialidad hh_d_hacinamiento hh_d_sin_basur"
global sa = "hh_d_sin_salud hh_d_agua_mejor hh_d_san_mejor hh_d_combus"
             
sort hhid

*========================================================================================
// Llevamos a nivel hogar la base, desde aqui ponderar todo por facpob.

collapse (mean) $ed $em $vi  $sa factor facpob upm nvivi nhoga dpto area pobrezai pobnopoi, by(hhid)

label var upm "Unidad primaria de muestreo"
label var nvivi "Identificación de la vivienda"
label var nhoga "Identificación del hogar"
label var nhoga "Identificación del hogar"
label var pobrezai "Estatus de pobreza monetario"
label var pobnopoi "Condición de pobreza monetario"
label var factor "Factor de expansion"
label var facpob "Factor de expansión de población.(factor*totpers)"
label var area "Area de Residencia"

// Se genera la var estratos geograficos, "variable de estratificación geográfica de la muestra"

// Asunción
gen estgeo=1 if dpto==0 & area==1

// Concepcion
replace estgeo=11 if dpto==1 & area==1
replace estgeo=16 if dpto==1 & area==6
// San Pedro
replace estgeo=21 if dpto==2 & area==1
replace estgeo=26 if dpto==2 & area==6
// Cordillera
replace estgeo=31 if dpto==3 & area==1
replace estgeo=36 if dpto==3 & area==6
// Guaira
replace estgeo=41 if dpto==4 & area==1
replace estgeo=46 if dpto==4 & area==6
// Caaguazú
replace estgeo=51 if dpto==5 & area==1
replace estgeo=56 if dpto==5 & area==6
// Caazapá
replace estgeo=61 if dpto==6 & area==1
replace estgeo=66 if dpto==6 & area==6
// Itapúa
replace estgeo=71 if dpto==7 & area==1
replace estgeo=76 if dpto==7 & area==6
// Misiones
replace estgeo=81 if dpto==8 & area==1
replace estgeo=86 if dpto==8 & area==6
// Paraguari
replace estgeo=91 if dpto==9 & area==1
replace estgeo=96 if dpto==9 & area==6
// Alto paraná
replace estgeo=101 if dpto==10 & area==1
replace estgeo=106 if dpto==10 & area==6
// Central
replace estgeo=111 if dpto==11 & area==1
replace estgeo=116 if dpto==11 & area==6
// Ñeembucú
replace estgeo=121 if dpto==12 & area==1
replace estgeo=126 if dpto==12 & area==6
// Amambay
replace estgeo=131 if dpto==13 & area==1
replace estgeo=136 if dpto==13 & area==6
// Canindeyu
replace estgeo=141 if dpto==14 & area==1
replace estgeo=146 if dpto==14 & area==6
// Presidente Hayes
replace estgeo=151 if dpto==15 & area==1
replace estgeo=156 if dpto==15 & area==6

label define estgeo 1 "Asuncion" 11 "Concepcion urbano" 16 "Concepcion rural" 21 "San Pedro urbano" /*
*/ 26 "San Pedro rural" 31 "Cordillera urbano" 36 "Cordillera rural" 41 "Guaira urbano" 46 "Guaira rural" /*
*/ 51 "Caaguazu urbano" 56 "Caaguazu rural" 61 "Caazapa urbano" 66 "Caazapa rural" 71 "Itapua urbana" /*
*/ 76 "Itapua rural" 81 "Misiones urbano" 86 "Misiones rural" 91 "Paraguari urbano" 96 "Paraguari rural" /*
*/ 101 "Alto Parana urbano" 106 "Alto Parana rural" 111 "Central urbano" 116 "Central rural"  /*
*/ 121 "Ñeembucú urbano" 126 "Ñeembucú rural" 131 "Amambay urbano" 136 "Amambay rural" 141 "Canindeyu urbano" /*
*/ 146 "Canindeyu rural" 151 "Presidente Hayes urbano" 156 "Presidente Hayes rural", replace
label val estgeo estgeo
label var estgeo "estrato geografico"
tab estgeo, m

label values dpto dpto  
tab dpto

label def dpto 0"Asuncion" 1"Concepcion" 2"San pedro" 3"Cordillera" 4"Guaira" /*
*/5"Caaguazu" 6"Caazapa" 7"Itapua" 8"Misiones" 9"ParaguarÃ­" 10"Alto Parana" /*
*/11"Central" 12"Neembucu" 13"Amambay" 14"Canindeyu" 15"Pdte Hayes" 20 "Resto", replace
label val dpto dpto
tab dpto, m
label var dpto "Departamento"

svyset upm [w=facpob], strata(estgeo)

/*=======================================================================================
                                  ASIGNANDO LOS PESOS
                   SE GENERAN VARIABLES CON LOS PESOS PARA CADA INDICADOR
=========================================================================================
Definir el vector 'w' de pesos
Cambiar de acuerdo a su especificion. Recuerde que la suma de pesos debe ser igual
a 1 o 100%

// ed = 1/12
// em = 1/20
// vi = 1/12
// sa = 1/16                                                                      */


	foreach var in $ed $vi {	
	
	gen	w_`var' = 1/12    // educación y vivienda tiene 3 indicadores, razon por la que se parte 1/4 entre 3 indic 
	lab var w_`var' "Peso `var'"
	}
//

foreach var in $em {	
	
	gen	w_`var' = 1/20       // para empleo el peso es 1/20, tienen 5 indicadores c/u 
	lab var w_`var' "Peso `var'"
	}

//
	foreach var in $sa {	
	
	gen	w_`var' = 1/16    // Salud el peso es 1/16 tiene 4 indicadores, razon por la que se parte 1/4 entre 4 indicadores
	lab var w_`var' "Peso `var'"
	}


/*======================================================================================
                                  MATRIZ DE PRIVACION PONDERADA
========================================================================================
 Los siguientes comandos multiplican la matriz de privacion por el peso de cada 
 indicador.                                                             */

foreach var in $ed $sa $em $vi {	

	gen	g0_w_`var' = `var' * w_`var'
	lab var g0_w_`var' "Privacion ponderada de `var'"
	}


format %18.0g g0_w_*

/*======================================================================================
                                         VECTOR DE CONTEO
========================================================================================*/

// Generar el vector de conteo de la suma de privaciones ponderadas, 'c'
 
egen c_vector = rowtotal(g0_w_*)  // cantidad de privaciones ponderada que tiene cada individuo
lab var c_vector "Vector de conteo"
tab	c_vector [aw = facpob], m

/*======================================================================================= 
                                    IDENTIFICACION 
========================================================================================*/
set more off

// Utilizando diferentes cortes de pobreza (i.e. diferentes k)

forvalue k = 1(1)100 {     //valores de k aumentados de 1 en 1

	gen	multid_poor_`k' = (c_vector >= `k'/100)
	lab var multid_poor_`k' "Identificacion de pobre con k=`k'%"
	}


/*======================================================================================
                             VECTOR DE CONTEO CENSURADO
========================================================================================
Generar el vector censurado de la suma de privaciones individuales ponderadas, 'c(k)'
Proporcionar un valor de cero si la persona no es pobre            */

forvalue k = 1(1)100 {

	gen	cens_c_vector_`k' = c_vector
	replace cens_c_vector_`k' = 0 if multid_poor_`k'==0 
	label var cens_c_vector_`k' "vector de conteo censurado para pobres con k=`k'"
	}


// label var cens_c_vector_26 "vector de conteo censurado para pobres con k=26"

/*======================================================================================
                        M0, H y A para todos los cortes de pobreza 
========================================================================================*/

// Con estos comandos se obtienen la Tasa de Incidencia de Pobreza MD (H), la Intensidad 
// de la pobreza entre los pobres (A), y la Tasa de Incidencia Ajustada (M0).

sum multid_poor_* [aw = facpob], sep(15)   

forvalue k = 1(1)100 {
	sum cens_c_vector_`k' if multid_poor_`k'==1 [aw = facpob], sep(15)  
	}

forvalue k = 1(1)100 {
	sum cens_c_vector_`k' [aw = facpob], sep(15)   // Valor de mO para cada valor de k
	}

//

/*======================================================================================
                           TASAS DE PRIVACION NO CENSURADAS
========================================================================================*/

foreach var in $ed $sa $em $vi {  
	svy: mean `var'
	}

// Este proceso se hace solo a modo de guardar como variable en la base las tasas y su error estandar

foreach var in $ed $sa $em $vi {  
	svy: mean `var'
	mat E=e(b)
	gen	un_`var' = E[1,1]*100
	lab var un_`var'  "Tasa de privacion NO censurada: % de personas privadas en cada indicador"
	mat V=e(V)
	gen un_`var'_se = sqrt(V[1,1])*100
	lab var un_`var'_se  "Tasa de privacion NO censurada (Standard Error)"
	gen un_`var'_li = _b[`var']*100 - 1.96 * un_`var'_se
	lab var un_`var'_li  "Limite inferior"
	gen un_`var'_ls = _b[`var']*100 + 1.96 * un_`var'_se
	lab var un_`var'_ls  "Limite superior"
}


sum un_* [aw =facpob], sep(15)

// OJO: generamos una base tempo para llevar a excel, para ver bien las variables
// En este momento cargamos un hoja Excel en la carpeta EPH del añ¯ ±ue estamos trabajando

// Tasas no censuradas
preserve
tempfile tasa_nocensu
gen one=1
collapse(mean) un_*, by(one)                   
export excel using "$results\Resultados_2025.xlsx", firstrow(variables) sheet("TASAS_NO_CENSURADA_2025") sheetreplace
tempfile close            
restore

/*=======================================================================================
                                    K = 26%
=========================================================================================
   Incidencia, intencidad y tasa de incidencia ajustada para k=26                 */
svy: mean multid_poor_26

// Incidencia de la pobreza mulidimensional (H) 
	
local k = 26 
	svy: mean multid_poor_`k'
	mat E = e(b)
	gen	H_`k' = E[1,1]*100
	lab var H_`k' "Tasa de recuento (H):% Poblacion en pobreza mult, k =`k'"
	mat V = e(V)
	gen H_`k'_se = sqrt(V[1,1])*100
	label var H_`k'_se "Error Estandar de (H), k=`k'"
	gen H_`k'_li = _b[multid_poor_`k']*100 - 1.96 * H_`k'_se
	lab var H_`k'_li  "Limite inferior"
	gen H_`k'_ls = _b[multid_poor_`k']*100 + 1.96 * H_`k'_se
	lab var H_`k'_ls  "Limite superior"

/*======================================================================================
                  Intensidad de la pobreza entre los pobres para k = 26% (A)
========================================================================================*/

local k = 26
svy: mean cens_c_vector_`k' if multid_poor_`k'==1

/*======================================================================================
                  Intensidad de la pobreza entre los pobres para k = 26% (A) 
========================================================================================*/
	local k = 26 
		svy: mean cens_c_vector_`k' if multid_poor_`k'==1
		mat E = e(b)
		gen	A_`k' = E[1,1]*100
		lab var A_`k'  "Intensidad de la privacion entre los pobres (A): promedio de las privaciones ponderadas"
		mat V = e(V)
		gen A_`k'_se = sqrt(V[1,1])*100
		lab var A_`k'_se "error estandar de (A), k=`k'"
	    gen A_`k'_li = _b[cens_c_vector_`k']*100 - 1.96 * A_`k'_se
		lab var A_`k'_li  "Limite inferior"
	    gen A_`k'_ls = _b[cens_c_vector_`k']*100 + 1.96 * A_`k'_se
		lab var A_`k'_ls  "Limite superior"


sum A_*

/*======================================================================================
                    Tasa de incidencia ajustada (M0) para k = 26%
========================================================================================*/

svy: mean cens_c_vector_26

/*======================================================================================
	                   Ratio de recuento ajustado (M0) 
========================================================================================*/
	local k = 26 
		svy: mean cens_c_vector_`k'
		mat E = e(b)
		gen	M0_`k' = E[1,1]
		lab var M0_`k' "Tasa de incidencia ajustada (M0 = H*A): Entre 0 y 1, k=`k'"
		mat V = e(V)
		gen M0_`k'_se = sqrt(V[1,1])
		lab var M0_`k'_se "Error Standard de M0, k=`k'"
		gen M0_`k'_li = _b[cens_c_vector_`k'] - 1.96 * M0_`k'_se
		lab var M0_`k'_li  "Limite inferior"
	    gen M0_`k'_ls = _b[cens_c_vector_`k'] + 1.96 * M0_`k'_se
		lab var M0_`k'_ls  "Limite superior"

sum M0_*

/*======================================================================================
                     Matriz de privación censurada para K=26
========================================================================================*/
local k = 26

foreach var in $ed $sa $em $vi {

	gen	g0_`var' = `var'
	replace g0_`var' = 0 if multid_poor_`k'==0 
	lab var g0_`var'  "Indicador `var' censurado para(k=`k')"
	}


/*=======================================================================================
                     Tasas de privación censuradas
=========================================================================================

Las tasas de privacion censuradas de cada indicador representan la proporcion de la poblacion.   
que son pobres Y privados en dicho indicador.
Se pueden obtener como la media de la columna de la matriz censurada de privaciones.    */

global indicat_cens = "g0_hh_d_ni_noasis g0_hh_d_esc_retardada g0_hh_d_logro_min g0_hh_d_sin_salud g0_hh_d_agua_mejor g0_hh_d_san_mejor g0_hh_d_combus g0_hh_d_destotalmax g0_hh_d_subocup_max g0_hh_d_10a17_ocup g0_hh_d_no_afil g0_hh_d_jubi_pens g0_hh_d_materialidad g0_hh_d_hacinamiento g0_hh_d_sin_basur"
	

	local k = 26
	foreach var of global indicat_cens {
			svy: mean `var'
			mat E = e(b)
			gen	cen_`var' = E[1,1]*100 
			lab var cen_`var'  "Tasa de privacion censurada: % poblacion que es pobre y privada en (k=`k')"
			mat V = e(V)
			gen cen_`var'_se = sqrt(V[1,1])*100
			lab var cen_`var'_se "Error Standard-Tasa de privacion censurada (k=`k')"
			gen cen_`var'_li = _b[`var']*100 - 1.96 * cen_`var'_se
			lab var cen_`var'_li  "Limite inferior"
			gen cen_`var'_ls = _b[`var']*100 + 1.96 * cen_`var'_se
			lab var cen_`var'_ls  "Limite superior"
		}
	
// Tasas censuradas
preserve
tempfile tasa_censu
gen one=1
collapse(mean) cen_*, by(one)
export excel using "$results\Resultados_2025.xlsx",  firstrow(variables) sheet("TASAS_CENSURADA_2025") sheetreplace
tempfile close 
restore

/*======================================================================================
                 Desagregación por dimensiones: contribuciones porcentuales
========================================================================================*/

foreach var in $ed $sa $em $vi {	
   //multiplicar la tasa de priv censurada simple por su ponderador y dividir por el m0
	gen	porc_cont_`var' = (cen_g0_`var' * w_`var') / M0_26   
	lab var porc_cont_`var' "Contribucion porcentual a M0_26"
	}

sum porc_cont_* [aw =facpob], sep(30) format 

// Contribución a nivel nacional
preserve
tempfile Contribucion nacional
gen one=1
collapse(mean) porc_cont_*, by(one)
export excel using "$results\Resultados_2025.xlsx",  firstrow(variables) sheet("Contrib_26_nac") sheetreplace
               
tempfile close 
restore

drop multid_poor_1 - multid_poor_25
drop multid_poor_27 - multid_poor_100
drop cens_c_vector_1 - cens_c_vector_25
drop cens_c_vector_27 - cens_c_vector_100
order hhid upm nvivi nhoga factor facpob dpto area estgeo pobrezai pobnopoi

save "$results\tempo_MPI2025.dta", replace

/*=======================================================================================
                            Descomposición por subgrupos - área
========================================================================================*/

// Primero recodificar area en 1 y 2
replace area=2 if area==6
label def area 1"Urbano" 2"Rural", replace
label values area area

/*=======================================================================================
                            Tasas de privación no censuradas por área
========================================================================================*/
// Check
local k = 26
foreach var in $ed $sa $em $vi {  
	forvalue r = 1/2 {
	svy: mean `var' if area==`r'
	}
}


// Este proceso se hace solo a modo de guardar como variable en la base las tasas y su error estandar

local k = 26
foreach var in $ed $sa $em $vi {  
	forvalue r = 1/2 {
	svy: mean `var' if area==`r'
	mat E=e(b)
	gen	un_`r'_`var' = E[1,1]*100 if area==`r'
	lab var un_`r'_`var'  "Tasa de privacion NO censurada-AREA `r'"
	mat V=e(V)
	gen un_`r'_`var'_se = sqrt(V[1,1])*100 if area==`r'
	lab var un_`r'_`var'_se  "Error Standar-Tasa NO censurada-AREA `r'"
	gen un_`r'_`var'_li = _b[`var']*100 - 1.96 * un_`r'_`var'_se
	lab var un_`r'_`var'_li  "Limite inferior"
	gen un_`r'_`var'_ls = _b[`var']*100 + 1.96 * un_`r'_`var'_se
	lab var un_`r'_`var'_ls  "Limite superior"
	}
}


// Tasas no censuradas por área
preserve
tempfile Tasas no censuradaas por area
gen one=1
collapse(mean) un_1* un_2*, by(one)
export excel using "$results\Resultados_2025.xlsx",  firstrow(variables) sheet("No_censu_area") sheetreplace              
tempfile close 
restore

// Check
svy: mean multid_poor_26
svy: mean multid_poor_26, over(area)

/*========================================================================================
                              Incidencia de la pobreza multidimensional (H) - por área
========================================================================================*/

local k = 26 
forvalue r = 1/2 {
	svy: mean multid_poor_`k' if area==`r'
	mat E = e(b)
	gen	H_area_`r' = E[1,1]*100 if area==`r'
	lab var H_area_`r' "Tasa de incidencia (H)-AREA `r'"
	mat V = e(V)
	gen H_area_`r'_se = sqrt(V[1,1])*100 if area==`r'
	label var H_area_`r'_se "Error Estandar de (H)- AREA `r'"
	gen H_area_`r'_li = _b[multid_poor_`k']*100 - 1.96 * H_area_`r'_se
	lab var H_area_`r'_li  "Limite inferior"
	gen H_area_`r'_ls = _b[multid_poor_`k']*100 + 1.96 * H_area_`r'_se
	lab var H_area_`r'_ls  "Limite superior"
	
	}

// H por área
sum H_area*

/*========================================================================================
               Intensidad de la pobreza entre los pobres para k = 26% (A)
========================================================================================*/
// Check
local k = 26
svy: mean cens_c_vector_`k' if multid_poor_`k'==1, over(area)

/*========================================================================================
            Intensidad de la pobreza entre los pobres para k = 26% (A)- por área
========================================================================================*/
	local k = 26 
		forvalue r = 1/2 {
		svy: mean cens_c_vector_`k' if multid_poor_`k'==1 & area==`r'
		mat E = e(b)
		gen	A_area_`r' = E[1,1]*100 if area==`r'
		lab var A_area_`r'  "Intensidad de la privacion(A)-AREA_`r'"
		mat V = e(V)
		gen A_area_`r'_se = sqrt(V[1,1])*100 if area==`r'
		lab var A_area_`r'_se "Error estandar de (A)-AREA_`r'"
	    gen A_area_`r'_li = _b[cens_c_vector_`k']*100 - 1.96 * A_area_`r'_se
		lab var A_area_`r'_li  "Limite inferior"
	    gen A_area_`r'_ls = _b[cens_c_vector_`k']*100 + 1.96 * A_area_`r'_se
		lab var A_area_`r'_ls  "Limite superior"
	}
	
//
sum A_area*

/*========================================================================================
                      Tasa de incidencia ajustada (M0) para k = 26% - por área
========================================================================================*/
// Check
svy: mean cens_c_vector_26, over(area)

/*========================================================================================
                      (M0) - Rartio de recuento ajustado - por área
========================================================================================*/
	local k = 26 
		forvalue r = 1/2 {
		svy: mean cens_c_vector_`k' if area==`r'
		mat E = e(b)
		gen	M0_area_`r' = E[1,1] if area==`r'
		lab var M0_area_`r' "(M0 = H*A)-AREA_`r'"
		mat V = e(V)
		gen M0_area_`r'_se = sqrt(V[1,1]) if area==`r'
		lab var M0_area_`r'_se "Error Standard de M0-AREA_`r'"
		gen M0_area_`r'_li = _b[cens_c_vector_`k'] - 1.96 * M0_area_`r'_se
		lab var M0_area_`r'_li  "Limite inferior"
	    gen M0_area_`r'_ls = _b[cens_c_vector_`k'] + 1.96 * M0_area_`r'_se
		lab var M0_area_`r'_ls  "Limite superior"
		
	}
	
// M0 por área	
sum M0_area*


/*========================================================================================
                              Tasas de privacion censuradas por region (área)
========================================================================================*/

global indicat_cens = "g0_hh_d_ni_noasis g0_hh_d_esc_retardada g0_hh_d_logro_min g0_hh_d_sin_salud g0_hh_d_agua_mejor g0_hh_d_san_mejor g0_hh_d_combus g0_hh_d_destotalmax g0_hh_d_subocup_max g0_hh_d_10a17_ocup g0_hh_d_no_afil g0_hh_d_jubi_pens g0_hh_d_materialidad g0_hh_d_hacinamiento g0_hh_d_sin_basur"
	

	local k = 26
	foreach var of global indicat_cens {
		forvalue r = 1/2 {
			svy: mean `var' if area==`r'
			mat E = e(b)
			gen	cen_`r'_`var' = E[1,1]*100 if area==`r' 
			lab var cen_`r'_`var'  "Tasa censurada - area `r'"
			mat V = e(V)
			gen cen_`r'_`var'_se = sqrt(V[1,1])*100 if area==`r'
			lab var cen_`r'_`var'_se "Error Standard-Tasa censurada - area `r'"
			gen cen_`r'_`var'_li = _b[`var']*100 - 1.96 * cen_`r'_`var'_se
			lab var cen_`r'_`var'_li  "Limite inferior"
			gen cen_`r'_`var'_ls = _b[`var']*100 + 1.96 * cen_`r'_`var'_se
			lab var cen_`r'_`var'_ls  "Limite superior"
		}
	}
 
 
sum cen_1*, sep(6)
sum cen_2*, sep(6)

// Tasas censuradas por área
preserve
tempfile Tasas censuradaas por area
gen one=1
collapse(mean) cen_1* cen_2*, by(one)
export excel using "$results\Resultados_2025.xlsx",  firstrow(variables) sheet("tasa_censu_area") sheetreplace              
tempfile close 
restore

/*========================================================================================
	                       Contribucion de cada indicador, por región (área)
========================================================================================*/

local k = 26

forvalue r = 1/2 {
	foreach var in $ed $sa $em $vi {	
		sum	cens_c_vector_`k' [aw =facpob] if area==`r'  // Calcular el M0 para cada área
		loc	M0_a`r' = r(mean)
		gen	p_area`r'_`var' = (cen_`r'_g0_`var' * w_`var') / `M0_a`r'' if area==`r'
		lab var p_area`r'_`var' "Contribucion % a M0 - area `r'"
		}
	}


	sum p_area* [aw =facpob], sep(7)


// Contribución por área
preserve
tempfile Contribucion por area
gen one=1
collapse(mean) p_area*, by(one)
export excel using "$results\Resultados_2025.xlsx",  firstrow(variables) sheet("Contrib_26_area") sheetreplace                   
tempfile close 
restore
 
save "$results\primer_MPI2025.dta", replace


/*========================================================================================
                                   H, A Y M0 por Dpto
========================================================================================*/

// H por Dpto

local k = 26
levelsof dpto, local(dpt)
		gen H_dpto=.
		gen H_dpto_se=.
		gen H_dpto_li=.
		lab var H_dpto_li  "Limite inferior"
		gen H_dpto_ls =.
		lab var H_dpto_ls  "Limite superior"
		foreach p of local dpt {
			svy: mean multid_poor_`k' if dpto==`p'
			mat E=e(b)
			replace H_dpto=E[1,1]*100 if dpto==`p'
			mat V=e(V)
			replace H_dpto_se=sqrt(V[1,1])*100 if dpto==`p'
			label var H_dpto "H por Dpto `p'"
			label var H_dpto_se "Standard error-H por Dpto`p'"
	     replace H_dpto_li = _b[multid_poor_`k']*100 - 1.96 * H_dpto_se if dpt==`p'
	     replace H_dpto_ls = _b[multid_poor_`k']*100 + 1.96 * H_dpto_se if dpto==`p'
			
		}
	
// Check
svy: mean multid_poor_26, over(dpto)
svy: mean H_dpto*, over(dpto)



// A por Dpto
// multid_poor_26
local k = 26
levelsof dpto, local(dpt)
		gen A_dpto=.
		gen A_dpto_se=.
		gen A_dpto_li=.
		lab var A_dpto_li  "Limite inferior"
		gen A_dpto_ls =.
		lab var A_dpto_ls  "Limite superior"
		foreach p of local dpt {
			svy: mean cens_c_vector_`k' if multid_poor_`k'==1 & dpto==`p'
			mat E=e(b)
			replace A_dpto=E[1,1]*100 if dpto==`p'
			mat V=e(V)
			replace A_dpto_se=sqrt(V[1,1])*100 if dpto==`p'
			label var A_dpto "A por Dpto `p'"
			label var A_dpto_se "Standard error-A por Dpto`p'"
			replace A_dpto_li = _b[cens_c_vector_`k']*100 - 1.96 * A_dpto_se if dpto==`p'
			replace A_dpto_ls = _b[cens_c_vector_`k']*100 + 1.96 * A_dpto_se if dpto==`p'
	
		}
	

// Check
svy: mean cens_c_vector_26 if multid_poor_26==1, over(dpto)
svy: mean A_dpto*, over(dpto)


/*========================================================================================
	                                                   M0
========================================================================================*/

local k = 26
levelsof dpto, local(dpt)
		gen M0_dpto=.
		gen M0_dpto_se=.
		gen M0_dpto_li=.
		lab var M0_dpto_li  "Limite inferior"
		gen M0_dpto_ls =.
		lab var M0_dpto_ls  "Limite superior"
		foreach p of local dpt {
			svy: mean cens_c_vector_`k' if dpto==`p'
			mat E=e(b)
			replace M0_dpto=E[1,1]*100 if dpto==`p'
			mat V=e(V)
			replace M0_dpto_se=sqrt(V[1,1])*100 if dpto==`p'
			label var M0_dpto "M0 por Dpto `p'"
			label var M0_dpto_se "Standard error-M0 por Dpto`p'"
			replace M0_dpto_li = _b[cens_c_vector_`k']*100 - 1.96 * M0_dpto_se if dpto==`p'
			replace M0_dpto_ls = _b[cens_c_vector_`k']*100 + 1.96 * M0_dpto_se if dpto==`p'
	
		}
	
		
// Check
svy: mean cens_c_vector_26, over(dpto)
svy: mean M0_dpto*, over(dpto)
	
/*========================================================================================
                             Tasas censuradas por dpto
========================================================================================*/

global indicat_cens = "g0_hh_d_ni_noasis g0_hh_d_esc_retardada g0_hh_d_logro_min g0_hh_d_sin_salud g0_hh_d_agua_mejor g0_hh_d_san_mejor g0_hh_d_combus g0_hh_d_destotalmax g0_hh_d_subocup_max g0_hh_d_10a17_ocup g0_hh_d_no_afil g0_hh_d_jubi_pens g0_hh_d_materialidad g0_hh_d_hacinamiento g0_hh_d_sin_basur"	

set more off 

local k = 26
levelsof dpto, local(dpt)
		foreach p of local dpt {
	foreach var of global indicat_cens {
			svy: mean `var' if dpto==`p'
			mat E = e(b)
			gen	cen_d`p'_`var' = E[1,1]*100 if dpto==`p' 
			lab var cen_d`p'_`var'  "Tasa censurada - dpto `p'"
			mat V = e(V)
			gen cen_d`p'_`var'_se = sqrt(V[1,1])*100 if dpto==`p'
			lab var cen_d`p'_`var'_se "Error Standard-Tasa censurada - dpto `p'"
			gen cen_d`p'_`var'_li = _b[`var']*100 - 1.96 * cen_d`p'_`var'_se
			lab var cen_d`p'_`var'_li  "Limite inferior"
			gen cen_d`p'_`var'_ls = _b[`var']*100 + 1.96 * cen_d`p'_`var'_se
			lab var cen_d`p'_`var'_ls  "Limite superior"
		}
	}
 

// Check
svy: mean g0_hh*, over(dpto)

/* Para llevar a excel, lo hacemos en tres archivos, porque de una nos da error, 
   dado que es muy extenso (demasiadas variables).  */

// Tasas censuradas por Dpto 1                                                                         
preserve
tempfile Tasas censuradaas por dpto
gen one=1
collapse(mean) cen_d0* cen_d1* cen_d2* cen_d3* cen_d4* cen_d5*, by(one)
export excel using "$results\Resultados_2025.xlsx",  firstrow(variables) sheet("Tasa_censu_dpto_0_1_2_3_4_5") sheetreplace
               
tempfile close 
restore



// Tasas censuradas por Dpto 2     
preserve
tempfile Tasas censuradas por dpto
gen one=1
collapse(mean) cen_d6* cen_d7* cen_d8* cen_d9* cen_d10*, by(one)
export excel using "$results\Resultados_2025.xlsx",  firstrow(variables) sheet("Tasa_censu_dpto_6_7_8_9_10") sheetreplace
               
tempfile close 
restore


// Tasas censuradas por Dpto 3     
preserve
tempfile Tasas censuradas por dpto
gen one=1
collapse(mean) cen_d11* cen_d12* cen_d13* cen_d14* cen_d15* , by(one)
export excel using "$results\Resultados_2025.xlsx",  firstrow(variables) sheet("Tasa_censu_dpto_11_12_13_14_15") sheetreplace
               
tempfile close 
restore


*volvemos a definir los global, dado que abrimos de nuevo la base**

global ed = "hh_d_ni_noasis hh_d_esc_retardada hh_d_logro_min"
global em = "hh_d_destotalmax hh_d_subocup_max hh_d_10a17_ocup hh_d_no_afil hh_d_jubi_pens"
global vi = "hh_d_materialidad hh_d_hacinamiento hh_d_sin_basur"
global sa = "hh_d_sin_salud hh_d_agua_mejor hh_d_san_mejor hh_d_combus"
     
/*========================================================================================
	                         Contribución por dpto
========================================================================================*/
	
levelsof dpto, local(dpt)
	foreach var in $ed $sa $em $vi {	
			foreach p of local dpt {
			gen cont_`var'_dp`p'=.
				sum	cens_c_vector_26 [aw =facpob] if dpto==`p'  // calculamos el M0 para cada dpto
				replace cont_`var'_dp`p'=(cen_d`p'_g0_`var' * w_`var') / r(mean) if dpto==`p' 
				label var cont_`var'_dp`p' "Contribucion de` var 'a MPI por Dpto`p'"
			}
		}

//

// Contribución por dpto
preserve
tempfile Contribucion por dpto
gen one=1
collapse(mean) cont_*, by(one)
export excel using "$results\Resultados_2025.xlsx",  firstrow(variables) sheet("Contrib_26_x_dpto") sheetreplace                   

tempfile close 
restore

save "$results\MPI2025_fin.dta", replace

use "$results\MPI2025_fin.dta", clear

/*========================================================================================                          Resumen de indicadores principales
                            H, A Y M0 por area, para k=26
========================================================================================*/

/* OJO: las salidas que se vean por departamento de H, A y M0, se debe cortar y pegar en un excel.
Los hogares que tienen en promedio 4 privaciones o más son pobres multidimensionales

Calcular la H por área                                                              */

set dp comma
tab area [w=facpob], sum(multid_poor_26)

// Cuadro 1 (H)
svy: mean multid_poor_26
svy: mean multid_poor_26, over(area)

// Cuadro 2 (A)
svy: mean cens_c_vector_26 if multid_poor_26==1
svy: mean cens_c_vector_26 if multid_poor_26==1, over(area)

// Cuadro 3 (M0)
svy: mean cens_c_vector_26 
svy: mean cens_c_vector_26 , over(area)

// Cuadro 8
svy: mean multid_poor_26, over(dpto)
svy: mean cens_c_vector_26 if multid_poor_26==1, over(dpto)
svy: mean cens_c_vector_26 , over(dpto)

//Cuadro 9
tab area [w=facpob], sum(multid_poor_26)

// Calcular la A por área
tab area [w=facpob] if multid_poor_26==1, sum(cens_c_vector_26)

// Calcular la M0 por área
tab area [w=facpob] if multid_poor_26==1

/*========================================================================================
                           H, A Y M0 por Dpto, para k=26
==========================================================================================
OJO: las salidas que se vean por departamento de H, A y M0, se debe cortar y pegar en un excel.
Calcular la H por dpto // Este a񯠬a encuesta abarc󠵮icamente los Departamentos representativos.                                                                      */
set dp comma
tab dpto [w=facpob], sum(multid_poor_26)

// Calculamos la A por dpto
tab dpto [w=facpob] if multid_poor_26==1, sum(cens_c_vector_26)

// Calculamos la M0 por dpto
tab dpto [w=facpob], sum(cens_c_vector_26)



