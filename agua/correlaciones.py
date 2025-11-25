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

# ==========================
# Bw - McCain (agua pura)
# ==========================
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
# Coeficientes - Culberson–McKetta (vía McCoy)
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

# =======================================
# Rsw - Culberson–McKetta (vía McCoy)
# =======================================
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

# ===============================
# Viscosidad del agua - Meehan
# ===============================
def viscosidad_agua_meehan(presion_psi: float, temperatura_f: float, salinidad_pct: float = 0.0) -> float:
    """
    Viscosidad del agua / salmuera según Meehan (1980).

    µw = µ* * f

    donde:
    - µ* = A + B / T
    - A y B dependen de la salinidad S (% peso)
    - f es la corrección por presión.

    Retorna µw en cP.
    """
    p = float(presion_psi)
    tf = float(temperatura_f)
    s = float(salinidad_pct)

    # Término a temperatura y salinidad (µ*).
    a = -0.04518 + 0.009313 * s - 0.000393 * (s ** 2)
    b = 70.634 + 0.09576 * (s ** 2)
    mu_estrella = a + b / tf

    # Corrección por presión (f).
    f = 1.0 + 3.5e-12 * (p ** 2) * (tf - 40.0)

    mu_w = mu_estrella * f
    return mu_w

# =====================================
# Compresibilidad del agua - Meehan
# =====================================
def compresibilidad_agua_meehan(presion_psi: float, temperatura_f: float, salinidad_pct: float = 0.0) -> float:
    """
    Compresibilidad isotérmica del agua/salmuera según Meehan (1980).

    cw = S_c * (a + b*T + c*T^2) * 1e-6

    donde S_c corrige por salinidad.
    Retorna cw en 1/psi.
    """
    p = float(presion_psi)
    tf = float(temperatura_f)
    nacl = float(salinidad_pct)  # % peso

    # Coeficientes dependientes de presión
    a = 3.8546 - 0.000134 * p
    b = -0.01052 + 4.77e-7 * p
    c = 3.9267e-5 - 8.8e-10 * p

    # Factor por salinidad S_c (NaCl en % peso)
    s_c = 1.0 + (nacl ** 0.7) * (
        -0.052
        + 0.00027 * tf
        - 1.14e-6 * (tf ** 2)
        + 1.121e-9 * (tf ** 3)
    )

    cw = s_c * (a + b * tf + c * (tf ** 2)) * 1e-6
    return cw

# ==========================================
# Densidad del agua / salmuera
# ==========================================
def densidad_agua_sc(salinidad_pct: float) -> float:
    """
    Densidad de salmuera a condiciones estándar
    (14.7 psia y 60 °F) usando una correlación
    sencilla basada en la salinidad.

    Usamos la forma típica:
        rho_wSC = C_mgL / 25000 + 62.428

    donde:
    - C_mgL se aproxima como salinidad_pct * 10,000
      (1 % peso ≈ 10,000 ppm ≈ 10,000 mg/L)

    Retorna
    -------
    float
        Densidad en lb/ft³.
    """
    s_pct = float(salinidad_pct)
    c_mg_l = s_pct * 10000.0
    rho_sc = c_mg_l / 25000.0 + 62.428
    return rho_sc

# =======================================
# Densidad del agua / reservorio
# =======================================
def densidad_agua_reservorio(presion_psi: float, temperatura_f: float, salinidad_pct: float) -> float:
    """
    Densidad de la salmuera a condiciones de yacimiento.

    Aproximamos:
        rho_wR = rho_wSC / Bw

    usando Bw de McCain (que depende de P y T).

    Retorna
    -------
    float
        Densidad en lb/ft³.
    """
    bw = volumen_formacion_agua_mccain(presion_psi, temperatura_f)
    rho_sc = densidad_agua_sc(salinidad_pct)
    rho_res = rho_sc / bw
    return rho_res