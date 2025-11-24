from django.shortcuts import render
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import CDN

from .forms import FormularioBw, FormularioRsw
from .correlaciones import (
    volumen_formacion_agua_mccain,
    rsw_culberson_mcketta,
)

def inicio(request):
    # Datos de ejemplo (después los cambiamos por correlaciones reales)
    presiones = [1000, 2000, 3000, 4000, 5000]
    rsw_ejemplo = [10, 18, 25, 30, 32]

    grafica = figure(title="Gráfica de prueba Bokeh - Correlaciones de agua",
                     x_axis_label="Presión (psi)",
                     y_axis_label="Rsw (SCF/bbl)",
                     sizing_mode="stretch_width",
                     height=400)
    grafica.line(presiones, rsw_ejemplo, line_width=2)

    script_bokeh, div_bokeh = components(grafica)
    recurso_bokeh = CDN.render()

    contexto = {
        "script_bokeh": script_bokeh,
        "div_bokeh": div_bokeh,
        "recurso_bokeh": recurso_bokeh,
    }
    return render(request, "agua/inicio.html", contexto)

def correlacion_bw(request):
    """
    Vista para calcular Bw (McCain) y mostrar una gráfica Bw vs P
    para una temperatura dada.
    """
    resultado_bw = None
    presion = None
    temperatura = None

    if request.method == "POST":
        formulario = FormularioBw(request.POST)
        if formulario.is_valid():
            presion = formulario.cleaned_data["presion_psi"]
            temperatura = formulario.cleaned_data["temperatura_f"]
            resultado_bw = volumen_formacion_agua_mccain(presion, temperatura)
    else:
        formulario = FormularioBw()
        # temperatura por defecto para la gráfica cuando aún no hay POST
        temperatura = 200.0

    # Rango de presiones para la gráfica (simple por ahora)
    presiones_grafica = list(range(1000, 11000, 1000))
    valores_bw = [
        volumen_formacion_agua_mccain(p, temperatura) for p in presiones_grafica
    ]

    grafica = figure(title=f"Bw (McCain) vs Presión a {temperatura:.1f} °F",
                     x_axis_label="Presión (psi)",
                     y_axis_label="Bw (bbl/STB)",
                     sizing_mode="stretch_width",
                     height=400)
    grafica.line(presiones_grafica, valores_bw, line_width=2)

    script_bokeh, div_bokeh = components(grafica)
    recurso_bokeh = CDN.render()

    contexto = {
        "formulario": formulario,
        "bw": resultado_bw,
        "presion": presion,
        "temperatura": temperatura,
        "script_bokeh": script_bokeh,
        "div_bokeh": div_bokeh,
        "recurso_bokeh": recurso_bokeh,
    }

    return render(request, "agua/correlacion_bw.html", contexto)

def correlacion_rsw(request):
    """
    Vista para calcular Rsw (Culberson–McKetta) y mostrar
    una gráfica Rsw vs Presión para una T y salinidad dadas.
    """
    resultado_rsw = None
    presion = None
    temperatura = None
    salinidad = None

    if request.method == "POST":
        formulario = FormularioRsw(request.POST)
        if formulario.is_valid():
            presion = formulario.cleaned_data["presion_psi"]
            temperatura = formulario.cleaned_data["temperatura_f"]
            salinidad = formulario.cleaned_data["salinidad_pct"]
            resultado_rsw = rsw_culberson_mcketta(
                presion,
                temperatura,
                salinidad,
            )
    else:
        # Valores por defecto para la gráfica
        temperatura = 150.0
        salinidad = 0.0
        formulario = FormularioRsw(
            initial={
                "temperatura_f": temperatura,
                "salinidad_pct": salinidad,
                "presion_psi": 3000,
            }
        )

    # Rango de presiones para la gráfica
    presiones_grafica = list(range(500, 10500, 500))
    valores_rsw = [
        rsw_culberson_mcketta(p, temperatura, salinidad)
        for p in presiones_grafica
    ]

    grafica = figure(
        title=(
            f"Rsw (Culberson–McKetta) vs Presión "
            f"a {temperatura:.1f} °F y S={salinidad:.1f} %"
        ),
        x_axis_label="Presión (psi)",
        y_axis_label="Rsw (scf/bbl)",
        sizing_mode="stretch_width",
        height=400,
    )
    grafica.line(presiones_grafica, valores_rsw, line_width=2)

    script_bokeh, div_bokeh = components(grafica)
    recurso_bokeh = CDN.render()

    contexto = {
        "formulario": formulario,
        "rsw": resultado_rsw,
        "presion": presion,
        "temperatura": temperatura,
        "salinidad": salinidad,
        "script_bokeh": script_bokeh,
        "div_bokeh": div_bokeh,
        "recurso_bokeh": recurso_bokeh,
    }

    return render(request, "agua/correlacion_rsw.html", contexto)