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
    min_y, max_y = ax.get_ylim()
    dev_y = (max_y - min_y) / 10

    x = np.linspace(min_v, max_v, num=num)
    y = func(x)

    if func_r:
        err = func_r(x)
        sns.lineplot(x=x, y=y, color='k', ax=ax, alpha=alpha)
        ax.fill_between(x, y-err, y+err, color='k', alpha=alpha/4)
    else:
        sns.lineplot(x=x, y=y, color='k', ax=ax, alpha=alpha)

    ax.set_xlim(min_v, max_v)
    ax.set_ylim(min_y-dev_y, max_y+dev_y)


def plot_data(canvas, dados, x, y, func, func_exp=None, n=200):
    sns.scatterplot(x=x, y=y, data=dados, ax=canvas, zorder=10)
    plot_approx(canvas, n, func, func_exp)


def plot_lin(canvas, dados, exp, real=None):
    plot_data(canvas, dados, 'N', 'dy', exp, real, 200)

    canvas.set_xlabel(r"$N$")
    canvas.set_ylabel(r"$\delta y$ $\left[\si{\milli\meter}\right]$")

    canvas.set_title("Regressão para a fórmula de Cauchy")



if __name__ == "__main__":
    desvio = pd.read_csv("A.csv", index_col='id')
    with open("../dados/coefs.json", mode='r') as fcoefs:
        coefs = json.load(fcoefs)

    lin_exp, lin_err = equations(coefs)


    fig = plt.figure()
    canvas = plt.axes()

    plot_lin(canvas, desvio, lin_exp, lin_err)
    fig.savefig('lin.png', dpi=200)

    canvas.set_xscale('log')
    canvas.set_yscale('log')
    fig.savefig('log.png', dpi=200)

    # fig.savefig('../figuras/plots/lin.pgf')

    # fig.clear()
    # canvas = plt.axes()

    # plot_cte(canvas, desvio, cte_exp, cte_err)
    # fig.savefig('cte.png', dpi=200)
    # fig.savefig('../figuras/plots/cte.pgf')


    # coefs['dmr'], coefs['ar'] = 0.0, 0.0
    # _, _, _, cau_err = equations(coefs)


    # l, r = canvas.get_xlim()
    # x = np.linspace(l, r, num=200)
    # y, err = cte_exp(x), cau_err(x)
    # canvas.fill_between(x, y-err, y+err, color='k', alpha=.6/4)

    # fig.savefig('cauchyr.png', dpi=200)
# fig.savefig('../figuras/plots/cauchy.pgf')