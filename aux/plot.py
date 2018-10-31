import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
import seaborn as sns
sns.set(context='paper', style='darkgrid', palette='muted', font='serif', color_codes=True)


params = {
    'axes': {
        'labelcolor': '#000000',
        'labelsize': 'medium'
    },
    'figure': {
        'autolayout': True,
        'figsize': [5, 3],
        'titlesize': 'x-large'
    },
    'legend': {
        'fontsize': 10,
        'labelspacing': .1,
        'handlelength': 1.5
    },
    'text': {
        'usetex': True,
        'latex.preamble': [
            r"\usepackage[utf8]{inputenc}",
            r"\usepackage[T1]{fontenc}",
            r"\usepackage[portuguese]{babel}",
            r"\usepackage{siunitx}",
            r"\usepackage{gensymb}"
        ]
    },
    'pgf': {
        'preamble': [
            r"\usepackage[utf8]{inputenc}",
            r"\usepackage[T1]{fontenc}",
            r"\usepackage[portuguese]{babel}",
            r"\usepackage{siunitx}",
            r"\usepackage{gensymb}"
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
for group, options in params.items():
    plt.rc(group, **options)


def plot_approx(ax, min_v, max_v, num, func, func_r=None, alpha=.6):
    x = np.linspace(min_v, max_v, num=num)

    if func_r:
        sns.lineplot(x=x, y=func(x), color='k', ax=ax, alpha=alpha, label="Regressão")
        sns.lineplot(x=x, y=func_r(x), color='k', ax=ax, alpha=alpha/2, label="Esperado")
    else:
        sns.lineplot(x=x, y=func(x), color='k', ax=ax, alpha=alpha)


def plot_data(canvas, dados, x, y, func, func_exp=None, n=100):
    pad = dados[x].std()/3
    min_v = dados[x].min()-pad
    max_v = dados[x].max()+pad

    plot_approx(canvas, min_v, max_v, n, func, func_exp)

    sns.scatterplot(x=x, y=y, hue='composto', data=dados, hue_order=['Cd', 'Na', 'Hg', 'He'], ax=canvas)


def leg_make(canvas, loc_curv, loc_comp):
    handles = canvas.get_legend_handles_labels()

    # curv_leg = canvas.legend(handles[0][:2], handles[1][:2], loc=loc_curv)
    canvas.legend(handles[0], handles[1], title="Lâmpadas", loc=loc_curv)

    # canvas.add_artist(curv_leg)


def plot_lin(canvas, dados, exp, real=None):
    plot_data(canvas, dados, 'il2', 'n', exp, real, 200)

    canvas.set_xlabel(r"$1/\lambda^2$ $\left[\SI{}{\micro\meter^{-2}}\right]$")
    canvas.set_ylabel(r"Índice de refração")

    leg_make(canvas, 'lower right', 'upper left')

    canvas.set_title("Linearização da fórmula de Cauchy")


def plot_cauchy(canvas, dados, exp, real=None):
    plot_data(canvas, dados, 'dm', 'lambda', exp, real, 200)

    canvas.set_xlabel(r"Desvio mínimo [\degree]")
    canvas.set_ylabel(r"Comprimento de onde [\SI{}{\nano\meter}]")

    leg_make(canvas, 'upper right', 'lower left')

    canvas.set_title("Relação para o espectrômetro")


def func_gen(coefs):
    A, B, a = coefs[['A', 'B', 'alpha']]

    sin = lambda deg: np.sin(np.deg2rad(deg))
    n = lambda dm: sin((a+dm)/2) / sin(a/2)

    lin = lambda il2: A + B * il2
    cauchy = lambda dm: np.sqrt(B / (n(dm) - A)) * 1000

    return lin, cauchy


if __name__ == "__main__":
    desvio = pd.read_csv("../dados/desvio.csv", index_col='id')
    coefs = pd.read_csv("../dados/coefs.csv", index_col='id')

    lin_exp, cau_exp = func_gen(coefs.loc['exp'])
    # lin_real, cau_real = func_gen(coefs.loc['real'])


    fig = plt.figure()
    canvas = plt.axes()

    plot_lin(canvas, desvio, lin_exp)
    fig.savefig('reta.png')
    fig.savefig('../figuras/plots/reta.pgf')

    fig.clear()
    canvas = plt.axes()

    plot_cauchy(canvas, desvio, cau_exp)
    fig.savefig('cauchy.png')
    fig.savefig('../figuras/plots/cauchy.pgf')
