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


# controle de cores para o diagrama de bode
colors = {
    'tx': {
        'th_min': "darkkhaki",
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
def bode_plots(mode, title="Diagrama de Bode"):
    """Inicializa o pyplot para o diagrama de Bode."""

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

    fig.suptitle(title)

    return xmit, phase


def plot_threshold(plot, threshold, color, legend=None):
    """Monta uma linha de limite em algum valor."""

    th_line = plot.axhline(threshold, c=colors[color[0]][color[1]])
    if legend:
        plot.legend((th_line,), (legend,))


def plot_interpolation(plot, x, y, color, size=None, level=1, legend=None):
    """Monta uma interpolação (logarítmica) para os valores coletados."""

    if not size:
        size = len(x)

    x_log = np.log10(x)
    x_new = np.logspace(x_log.min(), x_log.max(), size)

    tck = interpolate.splrep(x, y, k=level)
    y_new = interpolate.splev(x_new, tck)

    ipol, = plot.semilogx(x_new, y_new, c=colors[color]['ipol'])
    if legend:
        plot.legend((ipol,), (legend,))


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

    xmit, phase = bode_plots(mode)

    if xmit:
        # limite de filtragem teórico
        plot_threshold(xmit, -3., ('tx', 'th_min'))
        # limite de filtragem aceito
        plot_threshold(xmit, -10., ('tx', 'thold'))

        # pontos coletados
        xmit.semilogx(
            data[_freq],
            data[_xmit],
            '.',
            c=colors['tx']['pts']
        )

        plot_interpolation(xmit, data[_freq], data[_xmit], 'tx')

        xmit.set_ylabel(r"Transmitância \textbf{[dB]}")
        if mode != "both":
            xmit.set_xlabel(r"Frequência \textbf{[Hz]}")

    if phase:
        # coletados
        phase.semilogx(
            data[_freq],
            data[_phase],
            'o',
            c=colors['ph']['pts']
        )

        plot_interpolation(phase, data[_freq], data[_phase], color='ph')

        phase.set_xlabel(r"Frequência \textbf{[Hz]}")
        phase.set_ylabel(r"Fase [graus]")


bode_diagram("plotter/parte1.csv")
plt.savefig("figuras/parte1.pgf")

bode_diagram("plotter/parte2.csv")
plt.savefig("figuras/parte2.pgf")
