from django.shortcuts import render
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import CDN

from .forms import (
    FormularioBw,
    FormularioRsw,
    FormularioViscosidadAgua,
    FormularioCompresibilidadAgua,
    FormularioDensidadAgua,
)
from .correlaciones import (
    volumen_formacion_agua_mccain,
    rsw_culberson_mcketta,
    viscosidad_agua_meehan,
    compresibilidad_agua_meehan,
    densidad_agua_sc,
    densidad_agua_reservorio,
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
    Vista para calcular Bw (McCain) y mostrar una gráfica Bw vs P.
    Incluimos salinidad, aunque la correlación usada no la
    incluye explícitamente. El efecto de la salinidad lo
    reflejamos en la densidad.
    """
    resultado_bw = None
    presion = None
    temperatura = None
    salinidad = None

    if request.method == "POST":
        formulario = FormularioBw(request.POST)
        if formulario.is_valid():
            presion = formulario.cleaned_data["presion_psi"]
            temperatura = formulario.cleaned_data["temperatura_f"]
            salinidad = formulario.cleaned_data["salinidad_pct"]
            resultado_bw = volumen_formacion_agua_mccain(presion, temperatura)
    else:
        temperatura = 200.0
        salinidad = 10.0
        formulario = FormularioBw(
            initial={
                "temperatura_f": temperatura,
                "salinidad_pct": salinidad,
                "presion_psi": 3000,
            }
        )

    presiones_grafica = list(range(1000, 11000, 1000))
    valores_bw = [
        volumen_formacion_agua_mccain(p, temperatura) for p in presiones_grafica
    ]

    min_bw = min(valores_bw)
    max_bw = max(valores_bw)

    grafica = figure(
        title=(
            f"Bw (McCain) vs Presión "
            f"a {temperatura:.1f} °F y S={salinidad:.1f} %"
        ),
        x_axis_label="Presión (psi)",
        y_axis_label="Bw (bbl/STB)",
        sizing_mode="stretch_width",
        height=400,
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )

    _configurar_estilo_grafica(grafica, min_bw, max_bw)

    grafica.line(
        presiones_grafica,
        valores_bw,
        line_width=3,
        legend_label="Bw (McCain)",
    )
    grafica.circle(
        presiones_grafica,
        valores_bw,
        size=6,
        legend_label="Bw (McCain)",
    )

    script_bokeh, div_bokeh = components(grafica)
    recurso_bokeh = CDN.render()

    contexto = {
        "formulario": formulario,
        "bw": resultado_bw,
        "presion": presion,
        "temperatura": temperatura,
        "salinidad": salinidad,
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

    min_rsw = min(valores_rsw)
    max_rsw = max(valores_rsw)

    grafica = figure(
        title=(
            f"Rsw (Culberson–McKetta) vs Presión "
            f"a {temperatura:.1f} °F y S={salinidad:.1f} %"
        ),
        x_axis_label="Presión (psi)",
        y_axis_label="Rsw (scf/bbl)",
        sizing_mode="stretch_width",
        height=400,
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )

    _configurar_estilo_grafica(grafica, min_rsw, max_rsw)

    grafica.line(presiones_grafica, valores_rsw, line_width=3, legend_label="Rsw")
    grafica.circle(presiones_grafica, valores_rsw, size=6, legend_label="Rsw")

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

def correlacion_viscosidad(request):
    """
    Viscosidad del agua (Meehan) y gráfica µw vs P.
    """
    resultado_mu = None
    presion = None
    temperatura = None
    salinidad = None

    if request.method == "POST":
        formulario = FormularioViscosidadAgua(request.POST)
        if formulario.is_valid():
            presion = formulario.cleaned_data["presion_psi"]
            temperatura = formulario.cleaned_data["temperatura_f"]
            salinidad = formulario.cleaned_data["salinidad_pct"]
            resultado_mu = viscosidad_agua_meehan(
                presion,
                temperatura,
                salinidad,
            )
    else:
        temperatura = 200.0
        salinidad = 5.0
        formulario = FormularioViscosidadAgua(
            initial={
                "temperatura_f": temperatura,
                "salinidad_pct": salinidad,
                "presion_psi": 3000,
            }
        )

    presiones_grafica = list(range(500, 15500, 1000))
    valores_mu = [
        viscosidad_agua_meehan(p, temperatura, salinidad)
        for p in presiones_grafica
    ]

    min_mu = min(valores_mu)
    max_mu = max(valores_mu)

    grafica = figure(title=(f"Viscosidad del agua (Meehan) vs Presión "
            f"a {temperatura:.1f} °F y S={salinidad:.1f} %"
        ),
                     x_axis_label="Presión (psi)",
                     y_axis_label="µw (cP)",
                     sizing_mode="stretch_width",
                     height=400,
                     tools="pan,wheel_zoom,box_zoom,reset,save")
    grafica.line(presiones_grafica, valores_mu, line_width=3, legend_label="µw")
    grafica.circle( presiones_grafica, valores_mu, size=6, legend_label="µw")

    script_bokeh, div_bokeh = components(grafica)
    recurso_bokeh = CDN.render()

    contexto = {
        "formulario": formulario,
        "mu": resultado_mu,
        "presion": presion,
        "temperatura": temperatura,
        "salinidad": salinidad,
        "script_bokeh": script_bokeh,
        "div_bokeh": div_bokeh,
        "recurso_bokeh": recurso_bokeh,
    }

    return render(request, "agua/correlacion_viscosidad.html", contexto)

def correlacion_compresibilidad(request):
    """
    Compresibilidad del agua (Meehan) y gráfica cw vs P.
    """
    resultado_cw = None
    presion = None
    temperatura = None
    salinidad = None

    if request.method == "POST":
        formulario = FormularioCompresibilidadAgua(request.POST)
        if formulario.is_valid():
            presion = formulario.cleaned_data["presion_psi"]
            temperatura = formulario.cleaned_data["temperatura_f"]
            salinidad = formulario.cleaned_data["salinidad_pct"]
            resultado_cw = compresibilidad_agua_meehan(
                presion,
                temperatura,
                salinidad,
            )
    else:
        temperatura = 200.0
        salinidad = 5.0
        formulario = FormularioCompresibilidadAgua(
            initial={
                "temperatura_f": temperatura,
                "salinidad_pct": salinidad,
                "presion_psi": 3000,
            }
        )

    presiones_grafica = list(range(500, 15500, 1000))
    valores_cw = [
        compresibilidad_agua_meehan(p, temperatura, salinidad)
        for p in presiones_grafica
    ]

    min_cw = min(valores_cw)
    max_cw = max(valores_cw)

    grafica = figure(
        title=(
            f"Compresibilidad del agua (Meehan) vs Presión "
            f"a {temperatura:.1f} °F y S={salinidad:.1f} %"
        ),
        x_axis_label="Presión (psi)",
        y_axis_label="cw (1/psi)",
        sizing_mode="stretch_width",
        height=400,
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )

    _configurar_estilo_grafica(grafica, min_cw, max_cw)

    grafica.line(presiones_grafica, valores_cw, line_width=3, legend_label="cw")
    grafica.circle(presiones_grafica, valores_cw, size=6, legend_label="cw")

    script_bokeh, div_bokeh = components(grafica)
    recurso_bokeh = CDN.render()

    contexto = {
        "formulario": formulario,
        "cw": resultado_cw,
        "presion": presion,
        "temperatura": temperatura,
        "salinidad": salinidad,
        "script_bokeh": script_bokeh,
        "div_bokeh": div_bokeh,
        "recurso_bokeh": recurso_bokeh,
    }

    return render(request, "agua/correlacion_compresibilidad.html", contexto)

def correlacion_densidad(request):
    """
    Vista para calcular densidad de agua/salmuera y
    mostrar una gráfica densidad vs salinidad.
    """
    dens_sc = None
    dens_res = None
    presion = None
    temperatura = None
    salinidad = None

    if request.method == "POST":
        formulario = FormularioDensidadAgua(request.POST)
        if formulario.is_valid():
            presion = formulario.cleaned_data["presion_psi"]
            temperatura = formulario.cleaned_data["temperatura_f"]
            salinidad = formulario.cleaned_data["salinidad_pct"]
            dens_sc = densidad_agua_sc(salinidad)
            dens_res = densidad_agua_reservorio(presion, temperatura, salinidad)
    else:
        presion = 3000.0
        temperatura = 200.0
        salinidad = 10.0
        formulario = FormularioDensidadAgua(
            initial={
                "presion_psi": presion,
                "temperatura_f": temperatura,
                "salinidad_pct": salinidad,
            }
        )

    # Gráfica: densidad en yacimiento vs salinidad para P y T fijos
    salinidades_grafica = list(range(0, 31, 5))  # 0, 5, 10, ..., 30 %
    valores_dens = [
        densidad_agua_reservorio(presion, temperatura, s)
        for s in salinidades_grafica
    ]

    min_rho = min(valores_dens)
    max_rho = max(valores_dens)

    grafica = figure(
        title=(
            f"Densidad del agua/salmuera vs Salinidad\n"
            f"P={presion:.0f} psi, T={temperatura:.1f} °F"
        ),
        x_axis_label="Salinidad (%)",
        y_axis_label="Densidad (lb/ft³)",
        sizing_mode="stretch_width",
        height=400,
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )

    _configurar_estilo_grafica(grafica, min_rho, max_rho)

    grafica.line(
        salinidades_grafica,
        valores_dens,
        line_width=3,
        legend_label="ρw (reservorio)",
    )
    grafica.circle(
        salinidades_grafica,
        valores_dens,
        size=6,
        legend_label="ρw (reservorio)",
    )

    script_bokeh, div_bokeh = components(grafica)
    recurso_bokeh = CDN.render()

    contexto = {
        "formulario": formulario,
        "densidad_sc": dens_sc,
        "densidad_reservorio": dens_res,
        "presion": presion,
        "temperatura": temperatura,
        "salinidad": salinidad,
        "script_bokeh": script_bokeh,
        "div_bokeh": div_bokeh,
        "recurso_bokeh": recurso_bokeh,
    }

    return render(request, "agua/correlacion_densidad.html", contexto)

# GRÁFICAS
def _configurar_estilo_grafica(grafica, min_y, max_y):
    """
    Ajusta el rango en Y y el estilo visual de la gráfica.

    min_y y max_y son los valores mínimos y máximos de la propiedad.
    """
    # margen de 10% (si todos los puntos son iguales, ponemos algo pequeño)
    diferencia = max_y - min_y
    if diferencia <= 0:
        margen = max_y * 0.1 if max_y != 0 else 0.1
    else:
        margen = diferencia * 0.1

    grafica.y_range.start = min_y - margen
    grafica.y_range.end = max_y + margen

    # Estilos generales
    grafica.background_fill_alpha = 0.0
    grafica.border_fill_alpha = 0.0

    grafica.grid.grid_line_alpha = 0.3
    grafica.grid.grid_line_dash = "dotted"

    grafica.outline_line_alpha = 0.0
    grafica.toolbar_location = "above"

    grafica.legend.location = "bottom_right"
    grafica.legend.click_policy = "hide"