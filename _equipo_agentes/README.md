# Equipo de agentes técnicos

Cuatro agentes especializados apoyan el análisis. Cada uno tiene una ficha TLDR con su enfoque, las fuentes que aportó, los vacíos y cómo se unen sus datos al resto.

| Agente | Ficha | Se ocupa de | Carpetas que aportó |
|---|---|---|---|
| Ciencia de datos | [ciencia_de_datos.md](ciencia_de_datos.md) | Claves de unión, calidad, catálogo maestro, pipeline reproducible | `_arquitectura/`, `12_INE_complementario/` |
| Infraestructura vial | [infraestructura.md](infraestructura.md) | Cómo medir "camino de todo tiempo" y calidad del camino; programas de caminos vecinales | `11_infraestructura_vial_complementaria/` |
| Economía | [economia.md](economia.md) | Canales económicos (fletes, precios, mercados, ingreso) y estrategia de identificación | `10_economia_y_mercados/` |
| Social | [social.md](social.md) | Acceso a salud, educación, electricidad, conectividad e instituciones | `09_servicios_complementarios/` |

Para sumar una fuente: guardarla en una carpeta nueva, registrarla en el CSV de fuentes de su carpeta (o en `_scripts/datos_fuentes_maestro.py`) y volver a correr los scripts de `ARQUITECTURA_BASE_DE_DATOS.md`, sección 6.
