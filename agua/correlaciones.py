"""
Módulo con funciones de correlaciones PVT para el agua.

Unidades:
- Presión en psi
- Temperatura en °F
- Salinidad en % en peso (1% = 10000 ppm)
- Rsw en scf/bbl (PCN/BN)
- Bw en bbl/STB
"""
from __future__ import annotations


def volumen_formacion_agua_mccain(presion_psi: float, temperatura_f: float) -> float:
    """
    Calcula el factor volumétrico del agua (Bw) usando
    la correlación de McCain (agua pura, sin sal).

    Parámetros
    ----------
    presion_psi : float
        Presión del yacimiento en psi.
    temperatura_f : float
        Temperatura del yacimiento en °F.

    Retorna
    -------
    float
        Bw en bbl/STB.
    """
    p = float(presion_psi)
    t = float(temperatura_f)

    # Término dependiente solo de la temperatura
    termino_t = 1 - 1.0001e-2 + 1.33391e-4 * t + 5.50654e-7 * (t ** 2)

    # Término dependiente de presión y temperatura
    termino_p = (
        1
        - 1.95301e-9 * p * t
        - 1.72834e-13 * (p ** 2) * t
        - 3.58922e-7 * p
        - 2.25341e-10 * (p ** 2)
    )

    bw = termino_t * termino_p
    return bw

# =======================================
# Rsw - Culberson–McKetta (vía McCoy)
# =======================================

def _coeficientes_rsw_culberson_mcketta(temperatura_f: float) -> tuple[float, float, float]:
    """
    Calcula los coeficientes A, B, C de la correlación
    Rswp = A + B*P + C*P^2

    T en °F.
    """
    t = float(temperatura_f)

    a = 2.12 + 3.45e-3 * t - 3.59e-5 * (t ** 2)
    b = 0.0107 - 5.26e-5 * t + 1.48e-7 * (t ** 2)
    c = 8.75e-7 + 3.9e-9 * t - 1.02e-11 * (t ** 2)

    return a, b, c


def rsw_culberson_mcketta(presion_psi: float, temperatura_f: float, salinidad_pct: float = 0.0, ) -> float:
    """
    Calcula la solubilidad del gas natural en agua (Rsw)
    usando la correlación de Culberson–McKetta con el
    ajuste de McCoy y corrección por salinidad.

    Parámetros
    ----------
    presion_psi : float
        Presión del yacimiento en psi (dentro del rango de la correlación).
    temperatura_f : float
        Temperatura del yacimiento en °F.
    salinidad_pct : float, opcional
        Salinidad en % peso (0 a 30%). 1% = 10000 ppm.

    Retorna
    -------
    float
        Rsw en scf/bbl (PCN/BN).
    """
    p = float(presion_psi)
    t = float(temperatura_f)
    s = float(salinidad_pct)

    # 1) Rsw para agua pura (Rswp)
    a, b, c = _coeficientes_rsw_culberson_mcketta(t)
    rsw_pura = a + b * p + c * (p ** 2)

    # 2) Factor de corrección por salinidad
    factor_sal = 1.0 - (0.0753 - 1.73e-4 * t) * s

    rsw = rsw_pura * factor_sal
    return rsw