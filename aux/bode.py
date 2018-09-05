# %%
import numpy as np
import pandas as pd
from scipy import interpolate
from matplotlib import pyplot as plt
import seaborn as sns

params = {
    'axes': {
        'labelcolor': '#000000',
        'labelsize': 'medium'
    },
    'figure': {
        'dpi': 96,
        'titlesize': 'x-large'
    },
    'font': {
        'family': 'serif'
    },
    'legend': {
        'fontsize': 10,
        'labelspacing': .1,
        'handlelength': 1.5
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
        'color': 'dimgray',
        'bottom': True,
        'minor.visible': True
    },
    'ytick': {
        'color': 'dimgray',
        'left': True,
        'minor.visible': True
    }
}

sns.set(style="darkgrid", palette="muted", color_codes=True)
for group, options in params.items():
    plt.rc(group, **options)
# print(plt.rcParams)  # para ajustes


# %%
def bode_plots(**kwargs):
    """Inicializa o pyplot para o diagrama de Bode."""

    mode = kwargs.get('mode')

    if mode == "transmission":
        fig, xmit = plt.subplots(1, 1)
        phase = None

    elif mode == "phase":
        fig, phase = plt.subplots(1, 1)
        xmit = None

    else:
        fig, (xmit, phase) = plt.subplots(2, 1)

    fig.suptitle("Diagrama de Bode")

    return xmit, phase


def plot_threshold(horizontal, plot, threshold, **kwargs):
    """Monta uma linha de limite em algum valor."""

    if horizontal:
        plot.axhline(threshold, c="rosybrown", **kwargs)
    else:
        plot.axvline(threshold, c="darkgray", **kwargs)


def plot_interpolation(plot, x, y, color, **kwargs):
    """Monta uma interpolação (logarítmica) para os valores coletados."""

    if 'num' not in kwargs:
        kwargs['num'] = len(x)

    if 'xmask' in kwargs:
        y = y[x >= kwargs['xmask']]
        x = x[x >= kwargs['xmask']]
        del kwargs['xmask']

    if 'ymask' in kwargs:
        x = x[y >= kwargs['ymask']]
        y = y[y >= kwargs['ymask']]
        del kwargs['ymask']

    x_log = np.log10(x)
    x_new = np.logspace(x_log.min(), x_log.max(), **kwargs)

    del kwargs['num']

    tck = interpolate.splrep(x, y, k=5, **kwargs)
    y_new = interpolate.splev(x_new, tck)

    plot.semilogx(x_new, y_new, c=color)


def plot_ticks(plot, base, min_v, max_v, points, minor):
    """Desenha marcadores"""

    full_range = max_v - min_v

    step = full_range/points/base
    step = np.round(step)

    base = base * step

    lower = np.arange(0, min_v, -base)
    lower = lower[lower.nonzero()]
    lower = np.flip(lower)

    upper = np.arange(0, max_v, base)
    upper = upper[upper.nonzero()]

    full_range = np.concatenate((lower, [0], upper))
    plot.set_yticks(full_range, minor)


def bode_diagram(csv_file, **kwargs):
    """
        Faz o diagram de Bode a partir de um arquivo CSV. O modo do diagrama
        pode ser "transmission", "phase" or "both".

        Também podem ser alterados os nomes dos campos a serem buscados no
        arquivo com os dados e as cores a serem impressas.
    """

    data = pd.read_csv(csv_file)
    freq, phase, xmit = data['frequencia'], data['fase'], data['T_dB']

    xmit_plt, phase_plt = bode_plots(**kwargs)

    if xmit_plt:
        if 'marks' in kwargs:
            marks = kwargs['marks']
            plot_threshold(
                False, xmit_plt, marks.pop(),
                ls='--', alpha=.8, label="Frequências de controle"
            )
            for mark in marks:
                plot_threshold(False, xmit_plt, mark, ls='--', alpha=.8)
            del kwargs['marks']

        # limite de filtragem teórico
        plot_threshold(True, xmit_plt, -3, alpha=.5)
        # limite de filtragem aceito
        plot_threshold(True, xmit_plt, -10,
                       alpha=.8, label='Limite de filtragem')
        xmit_plt.legend(loc='right')

        # pontos coletados
        xmit_plt.plot(freq, xmit, '.', c='C0')

        # aproximação
        plot_interpolation(xmit_plt, freq, xmit, 'C1', **kwargs)

        xmit_plt.set_ylabel(r"Transmitância \textbf{[dB]}")
        if not phase_plt:
            xmit_plt.set_xlabel(r"Frequência \textbf{[Hz]}")

        # marcadores
        plot_ticks(xmit_plt, 5, min(xmit), max(xmit), 5, False)
        plot_ticks(xmit_plt, 2.5, min(xmit), max(xmit), 10, True)

    if phase_plt:
        # coletados
        phase_plt.plot(freq, phase, '.', c='C4')

        # aproximação
        plot_interpolation(phase_plt, freq, phase, 'C8', **kwargs)

        phase_plt.set_xlabel(r"Frequência \textbf{[Hz]}")
        phase_plt.set_ylabel(r"Fase \textbf{[graus]}")

        # marcadores
        plot_ticks(phase_plt, 15, min(phase), max(phase), 5, False)
        plot_ticks(phase_plt, 5, min(phase), max(phase), 15, True)


bode_diagram("dados/parte1.csv", xmask=50, marks=[120, 8000])
plt.savefig("figuras/parciais/parte1.pgf")

bode_diagram("dados/parte2.csv", marks=[100, 1000, 10000])
plt.savefig("figuras/parciais/parte2.pgf")
