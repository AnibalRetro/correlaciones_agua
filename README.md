# Proyecto `correlaciones del agua`

Proyecto para calcular y graficar correlaciones PVT
del agua usando **Bokeh**.

El código está pensado como si fuera un proyecto de estudiante de
ingeniería de la UNAM que está empezando con Django y Bokeh:
claro, directo y sin demasiada magia.

## Tecnologías

- Python 3.x
- Django 5.x (o la versión que uses)
- Bokeh
- Pycharm (IDE)

## Estructura básica

- `correlaciones_agua/`
  - Proyecto Django (settings, urls, etc.)
- `agua/`
  - App con las correlaciones
  - `correlaciones.py`: funciones PVT (Bw, Rsw, µw, cw, densidad)
  - `forms.py`: formularios para capturar P, T y salinidad
  - `views.py`: vistas Django que llaman a las correlaciones y
    construyen gráficas Bokeh
  - `templates/agua/`: páginas HTML para cada correlación

## Propiedades implementadas

- Factor volumétrico del agua **Bw** (McCain)
- Solubilidad gas–agua **Rsw** (Culberson–McKetta, ajuste McCoy)
- Viscosidad del agua / salmuera **µw** (Meehan)
- Compresibilidad del agua / salmuera **cw** (Meehan)
- Densidad del agua / salmuera **ρw** (a condiciones estándar y de yacimiento)

Todas las gráficas se acompañan de una tabla de datos generada con
los mismos puntos que se usan en las curvas.

**Creado y editar por Itzel Amador Alcántara**