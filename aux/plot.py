import json
import numpy as np
import pandas as pd

from calc import equations

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


def plot_approx(ax, num, func, func_r=None, alpha=.6):
    min_v, max_v = ax.get_xlim()

    x = np.linspace(min_v, max_v, num=num)
    y = func(x)

    if func_r:
        err = func_r(x)
        sns.lineplot(x=x, y=y, color='k', ax=ax, alpha=alpha)
        ax.fill_between(x, y-err, y+err, color='k', alpha=alpha/4)
    else:
        sns.lineplot(x=x, y=y, color='k', ax=ax, alpha=alpha)

    ax.set_xlim(min_v, max_v)


def plot_data(canvas, dados, x, y, func, func_exp=None, n=200):
    sns.scatterplot(x=x, y=y, hue='composto', data=dados, hue_order=['Cd', 'Na', 'Hg', 'He'], ax=canvas, zorder=10)
    plot_approx(canvas, n, func, func_exp)


def leg_make(canvas, loc_curv, loc_comp):
    handles = canvas.get_legend_handles_labels()

    # curv_leg = canvas.legend(handles[0][:2], handles[1][:2], loc=loc_curv)
    canvas.legend(handles[0][1:], handles[1][1:], title="Lâmpadas", loc=loc_curv)

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



if __name__ == "__main__":
    desvio = pd.read_csv("../dados/desvio.csv", index_col='id')
    with open("../dados/coefs.json", mode='r') as fcoefs:
        coefs = json.load(fcoefs)

    lin_exp, lin_err, cau_exp, cau_err = equations(coefs)


    fig = plt.figure()
    canvas = plt.axes()

    plot_lin(canvas, desvio, lin_exp, lin_err)
    fig.savefig('reta.png', dpi=200)
    fig.savefig('../figuras/plots/reta.pgf')

    fig.clear()
    canvas = plt.axes()

    plot_cauchy(canvas, desvio, cau_exp, cau_err)
    fig.savefig('cauchy.png', dpi=200)
    fig.savefig('../figuras/plots/cauchy.pgf')
