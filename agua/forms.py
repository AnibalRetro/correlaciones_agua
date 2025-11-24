from django import forms


class FormularioBw(forms.Form):
    """
    Formulario sencillo para calcular Bw con McCain.
    """

    presion_psi = forms.FloatField(label="Presión del yacimiento (psi)",
                                   min_value=14.7,
                                   max_value=15000,
                                   required=True)

    temperatura_f = forms.FloatField(label="Temperatura del yacimiento (°F)",
                                     min_value=60,
                                     max_value=400,
                                     required=True)

class FormularioRsw(forms.Form):
    """
    Formulario para calcular Rsw (Culberson–McKetta).
    """

    presion_psi = forms.FloatField(label="Presión del yacimiento (psi)",
                                   min_value=100,
                                   max_value=10000,
                                   required=True)

    temperatura_f = forms.FloatField(label="Temperatura del yacimiento (°F)",
                                     min_value=70,
                                     max_value=250,
                                     help_text="Rango típico de la correlación: 70–250 °F",
                                     required=True)

    salinidad_pct = forms.FloatField(label="Salinidad del agua (%)",
                                     min_value=0,
                                     max_value=30,
                                     initial=0,
                                     help_text="0–30 %, 1% = 10000 ppm",
                                     required=True)