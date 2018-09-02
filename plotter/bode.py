# %%
import numpy as np
from scipy import interpolate
from matplotlib import pyplot as plt

params = {
    'axes': {
        'labelcolor': '#000000',
        'labelsize': 'medium'
    },
    'figure': {
        'dpi': 96
    },
    'font': {
        'family': 'serif',
        'serif': ['Computer Modern']
    },
    'text': {
        'usetex': True,
        'latex.unicode': True,
        'latex.preamble': [
            r"\usepackage[utf8x]{inputenc}",
            r"\usepackage[T1]{fontenc}",
            r"\usepackage[portuguese]{babel}"
        ]
    },
    'xtick': {
        'color': '#000000',
        'minor.visible': True
    },
    'ytick': {
        'color': '#000000',
        'minor.visible': True
    }
}
plt.style.use('ggplot')
for group, options in params.items():
    plt.rc(group, **options)
# print(plt.rcParams)  # para ajustes

# cores para o diagrama de bode
colors = {
    'tx': {
        'thold': "rosybrown",
        'pts': "steelblue",
        'ipol': "darkorange",
    },
    'ph': {
        'pts': "steelblue",
        'ipol': "darkorange"
    }
}


# %%
def bode_diagram(
        csv_name, mode="both", _freq="frequencia",
        _phase="fase", _xmit="T_dB"
    ): # noqa
    """
        Faz o diagram de Bode a partir de um arquivo CSV. O modo do diagrama
        pode ser "transmission", "phase" or "both".

        Também podem ser alterados os nomes dos campos a serem buscados no
        arquivo com os dados e as cores a serem impressas.
    """

    data = np.genfromtxt(csv_name, delimiter=',', names=True)

    # inicialização das figuras
    if mode == "both":
        fig, (xmit, phase) = plt.subplots(2, 1)
    elif mode == "transmission":
        fig, xmit = plt.subplots(1, 1)
        phase = None
    elif mode == "phase":
        fig, phase = plt.subplots(1, 1)
        xmit = None
    else:
        raise ValueError("Invalid mode")

    fig.suptitle("Diagrama de Bode")

    # valore para interpolação
    sample_amount = 60
    spline_level = 5
    freq_log = np.log10(data[_freq])
    freq_new = np.logspace(freq_log.min(), freq_log.max(), sample_amount)

    if xmit:
        # interpolação da transmitância
        tck = interpolate.splrep(data[_freq], data[_xmit], k=spline_level)
        xmit_new = interpolate.splev(freq_new, tck)

        # limite de filtragem
        threshold = -3.0  # dB
        xmit.axhline(threshold, color=colors['tx']['thold'])

        # pontos coletados
        xmit.semilogx(
            data[_freq],
            data[_xmit],
            '.',
            color=colors['tx']['pts']
        )

        # valores interpolados
        xmit.semilogx(freq_new, xmit_new, color=colors['tx']['ipol'])

        xmit.set_ylabel(r"Transmitância \textbf{[dB]}")
        if mode != "both":
            xmit.set_xlabel(r"Frequência \textbf{[Hz]}")

    if phase:
        # interpolação da fase
        tck = interpolate.splrep(data[_freq], data[_phase], k=spline_level)
        phase_new = interpolate.splev(freq_new, tck)

        # coletados
        phase.semilogx(
            data[_freq],
            data[_phase],
            'o',
            color=colors['ph']['pts']
        )

        # interpolados
        phase.semilogx(freq_new, phase_new, color=colors['ph']['ipol'])

        phase.set_xlabel(r"Frequência \textbf{[Hz]}")
        phase.set_ylabel(r"Fase [graus]")


bode_diagram("plotter/parte2.csv", mode="both")
plt.savefig("figuras/parte2.pgf")
