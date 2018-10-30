import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
import seaborn as sns
sns.set(context='paper', style='darkgrid', palette='muted', font='serif', color_codes=True)


def plot_approx(ax, min_v, max_v, num, func, func_r=None, alpha=.6):
    x = np.linspace(min_v, max_v, num=num)

    sns.lineplot(x=x, y=func(x), color='k', ax=ax, alpha=alpha)

    if func_r:
        sns.lineplot(x=x, y=func_r(x), color='k', ax=ax, alpha=alpha/2)


def plot_data(canvas, dados, x, y, func, func_exp=None, n=100):
    pad = dados[x].std()/3
    min_v = dados[x].min()-pad
    max_v = dados[x].max()+pad

    sns.scatterplot(x=x, y=y, hue='composto', data=dados, hue_order=['Cd', 'Na', 'Hg', 'He'], ax=canvas)

    plot_approx(canvas, min_v, max_v, n, func, func_exp)


def plot_lin(canvas, dados, exp, real=None):
    plot_data(canvas, dados, 'il2', 'n', exp, real, 200)


def plot_cauchy(canvas, dados, exp, real=None):
    plot_data(canvas, dados, 'dm', 'lambda', exp, real, 200)


def func_gen(coefs):
    A, B, a = coefs[['A', 'B', 'alpha']]

    sin = lambda deg: np.sin(np.deg2rad(deg))
    n = lambda dm: sin((a+dm)/2) / sin(a/2)

    lin = lambda il2: A + B * il2
    cauchy = lambda dm: np.sqrt(B / (n(dm) - A)) * 1000

    return lin, cauchy


if __name__ == "__main__":
    desvio = pd.read_csv("../dados/desvio.csv", index_col='id')
    coefs = pd.read_csv("coefs.csv", index_col='id')

    lin_exp, cau_exp = func_gen(coefs.loc['exp'])
    lin_real, cau_real = func_gen(coefs.loc['real'])


    fig = plt.figure()
    canvas = plt.axes()

    plot_lin(canvas, desvio, lin_exp, lin_real)
    fig.savefig('reta.png')
    fig.savefig('../figuras/plots/reta.pgf')

    fig.clear()
    canvas = plt.axes()

    plot_cauchy(canvas, desvio, cau_exp, cau_real)
    fig.savefig('cauchy.png')
    fig.savefig('../figuras/plots/cauchy.pgf')
