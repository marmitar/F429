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
        'dpi': 96,
        'titlesize': 'x-large'
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


# controle de cores para o diagrama de bode
colors = {
    'tx': {
        'pts': "steelblue",
        'ipol': "darkorange",
    },
    'ph': {
        'pts': "slateblue",
        'ipol': "mediumseagreen"
    },
    'th': {
        'h': "rosybrown",
        'v': "darkgray"
    }
}


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

    if 'title' in kwargs:
        fig.suptitle(kwargs['title'])

    return xmit, phase


def plot_threshold(horizontal, plot, threshold, **kwargs):
    """Monta uma linha de limite em algum valor."""

    if 'legend' in kwargs:
        legend = kwargs['legend']
        del kwargs['legend']
    else:
        legend = None

    if horizontal:
        line = plot.axhline(threshold, c=colors['th']['h'], **kwargs)
    else:
        line = plot.axvline(threshold, c=colors['th']['v'], **kwargs)

    if legend:
        plot.legend((line,), (legend,))


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

    if 'legend' in kwargs:
        legend = kwargs['legend']
        del kwargs['legend']
    else:
        legend = None

    x_log = np.log10(x)
    x_new = np.logspace(x_log.min(), x_log.max(), **kwargs)

    del kwargs['num']

    tck = interpolate.splrep(x, y, k=5, **kwargs)
    y_new = interpolate.splev(x_new, tck)

    ipol, = plot.semilogx(x_new, y_new, c=colors[color]['ipol'])

    if legend:
        plot.legend((ipol,), (legend,))


def bode_diagram(csv_name, **kwargs):
    """
        Faz o diagram de Bode a partir de um arquivo CSV. O modo do diagrama
        pode ser "transmission", "phase" or "both".

        Também podem ser alterados os nomes dos campos a serem buscados no
        arquivo com os dados e as cores a serem impressas.
    """

    data = np.genfromtxt(csv_name, delimiter=',', names=True)
    freq, phase, xmit = data['frequencia'], data['fase'], data['T_dB']

    xmit_plt, phase_plt = bode_plots(**kwargs)
    if 'title' in kwargs:
        del kwargs['title']

    if xmit_plt:
        if 'marks' in kwargs:
            for mark in kwargs['marks']:
                plot_threshold(False, xmit_plt, mark, ls='--', alpha=.7)
            del kwargs['marks']

        # limite de filtragem teórico
        plot_threshold(True, xmit_plt, -3, alpha=.4)
        # limite de filtragem aceito
        plot_threshold(True, xmit_plt, -10, alpha=.7)

        # pontos coletados
        xmit_plt.semilogx(freq, xmit, '.', c=colors['tx']['pts'])

        # aproximação
        plot_interpolation(xmit_plt, freq, xmit, 'tx', **kwargs)

        xmit_plt.set_ylabel(r"Transmitância \textbf{[dB]}")
        if not phase_plt:
            xmit_plt.set_xlabel(r"Frequência \textbf{[Hz]}")

    if phase_plt:
        # coletados
        phase_plt.semilogx(freq, phase, '.', c=colors['ph']['pts'])

        # aproximação
        plot_interpolation(phase_plt, freq, phase, 'ph', **kwargs)

        phase_plt.set_xlabel(r"Frequência \textbf{[Hz]}")
        phase_plt.set_ylabel(r"Fase \textbf{[graus]}")


title = "Diagrama de Bode"

bode_diagram("dados/parte1.csv", xmask=50, marks=[120, 8000], title=title)
plt.savefig("figuras/parciais/parte1.pgf")

bode_diagram("dados/parte2.csv", marks=[100, 1000, 10000], title=title)
plt.savefig("figuras/parciais/parte2.pgf")
