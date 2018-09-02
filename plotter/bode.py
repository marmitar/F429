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
        'pts': "slateblue",
        'ipol': "mediumseagreen"
    },
    'th_cmap': "tab20b"
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


def plot_threshold(horizontal, plot, threshold, color=None, legend=None):
    """Monta uma linha de limite em algum valor."""

    if color:
        color = colors[color[0]][color[1]]
    else:
        cmap = plt.get_cmap(colors['th_cmap'])
        color = cmap(np.random.rand())

    if horizontal:
        line = plot.axhline(threshold, c=color)
    else:
        line = plot.axvline(threshold, c=color)

    if legend:
        plot.legend((line,), (legend,))


def plot_interpolation(
        plot, x, y, color,
        size=80, level=5,
        mask=None, legend=None
    ): # noqa
    """Monta uma interpolação (logarítmica) para os valores coletados."""

    if not size:
        size = len(x)

    if mask:
        y = y[x >= mask]
        x = x[x >= mask]

    x_log = np.log10(x)
    x_new = np.logspace(x_log.min(), x_log.max(), size)

    tck = interpolate.splrep(x, y, k=level)
    y_new = interpolate.splev(x_new, tck)

    ipol, = plot.semilogx(x_new, y_new, c=colors[color]['ipol'])
    if legend:
        plot.legend((ipol,), (legend,))


def bode_diagram(
        csv_name, mode="both", _freq="frequencia",
        _phase="fase", _xmit="T_dB", mask=None, marks=None
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
        if marks:
            for mark in marks:
                plot_threshold(False, xmit, mark)

        # limite de filtragem teórico
        plot_threshold(True, xmit, -3, ('tx', 'th_min'))
        # limite de filtragem aceito
        plot_threshold(True, xmit, -10, ('tx', 'thold'))

        # pontos coletados
        xmit.semilogx(
            data[_freq], data[_xmit],
            '.', c=colors['tx']['pts']
        )

        plot_interpolation(xmit, data[_freq], data[_xmit], 'tx', mask=mask)

        xmit.set_ylabel(r"Transmitância \textbf{[dB]}")
        if mode != "both":
            xmit.set_xlabel(r"Frequência \textbf{[Hz]}")

    if phase:
        # coletados
        phase.semilogx(
            data[_freq], data[_phase],
            '.', c=colors['ph']['pts']
        )

        plot_interpolation(
            phase, data[_freq], data[_phase],
            color='ph', mask=mask
        )

        phase.set_xlabel(r"Frequência \textbf{[Hz]}")
        phase.set_ylabel(r"Fase \textbf{[graus]}")


bode_diagram("plotter/parte1.csv", mask=50, marks=[120, 8000])
plt.savefig("figuras/parte1.pgf")

bode_diagram("plotter/parte2.csv", marks=[100, 1000, 10000])
plt.savefig("figuras/parte2.pgf")
