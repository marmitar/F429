import json
import pickle

import numpy as np
import pandas as pd
from scipy import stats


def print(*args, func=print, **kwargs):
    kwargs['sep'] = ",  "
    # func()
    func(*args, **kwargs)

sqrt = np.sqrt
sin = lambda deg: np.sin(np.deg2rad(deg))
cos = lambda deg: np.cos(np.deg2rad(deg))


def n(desvio, alpha):
    sup = sin((alpha+desvio)/2)
    inf = sin(alpha/2)
    return sup/inf


def nr(dm, a, dmr, ar):
    dnda = sin(dm/2) / (cos(a)-1)
    # dnddm2 = (cos(a+dm)+1) / (cos(a)-1)
    dnddm = (sin(a/2) * cos((a+dm)/2)) / (cos(a)-1)

    nr2 = (ar * dnda)**2 + (dmr * dnddm)**2
    return sqrt(nr2)


def calc_desvio(dados, err):
    d1 = dados['d1'] + dados['m1']/60
    d2 = dados['d2'] + dados['m2']/60
    d3 = dados['d3'] + dados['m3']/60

    dm = (d1 + d2 + d3)/3
    varn = (d1-dm)**2 + (d2-dm)**2 + (d3-dm)**2
    dmr = sqrt((varn/3 + 2*err**2)/3)
    dmr = varn + err - varn

    dados['dm'] = dm
    dados['dmr'] = dmr


def lst_sq(x, y, yerr):
    n = len(x)
    xs = sum(x)
    ys = sum(y)
    x2s = sum(x * x)
    xys = sum(x * y)
    yrs = sum(yerr)
    xyrs = sum(x * yerr)

    lower = n*x2s - xs**2

    A = (ys*x2s - xys*xs) / lower
    B = (n*xys - xs*ys) / lower

    s2 = sum((y-A-B*x)**2) / (n-2)
    sA2 = (s2 * x2s) / lower
    sB2 = (s2 * n) / lower

    eA2 = ((yrs*x2s)**2 + (xyrs*xs)**2) / lower**2
    eB2 = ((n*xyrs)**2 + (xs*yrs)**2) / lower**2

    uA = sqrt(sA2 + eA2)
    uB = sqrt(sB2 + eB2)

    # print(f"s: {sqrt(s2)}")
    # print(f"sA = {sqrt(sA2)}", f"sB = {sqrt(sB2)}")
    # print(f"eA = {sqrt(eA2)}", f"eB = {sqrt(eB2)}")

    return A, B, uA, uB


def degerr(res, par):
    res = res/(2 * sqrt(6))
    par = par/sqrt(3)

    return sqrt(res**2 + par**2)


def rounder(digits):
    return lambda f: np.round(f, decimals=digits)


def equations(coefs):
    A, B, a = coefs['A'], coefs['B'], coefs['alpha']
    Ar, Br, ar = coefs['Ar'], coefs['Br'], coefs['ar']
    dr = coefs['dmr']  #, coefs['nr']

    sina, cosa = sin(a/2), cos(a/2)
    n = lambda dm: sin((a+dm)/2)/sina

    linear = lambda il2: A + B * il2
    lin_r = lambda il2: sqrt(Ar**2 + (il2*Br)**2)

    cauchy = lambda dm: sqrt(B / (n(dm) - A)) * 1000

    def cauchy_r(dm):
        nl = n(dm)
        nA = nl-A
        k = 1/(2 * nA)
        ni = cos((a+dm)/2)/sina
        nd = ni - nl * cosa/sina

        sA = Ar**2 * B / nA
        sB = Br**2 * nA / B
        sd = dr**2 * B / nA * ni**2 / 4
        sa = ar**2 * B / nA * nd**2 / 4

        return k * sqrt(sA + sB + sd + sa) * 1000

    return linear, lin_r, cauchy, cauchy_r


if __name__ == "__main__":

    with open("../dados/calib.json", mode='r') as fcalib:
        calib = json.load(fcalib)

    err = degerr(calib['resolução']/60, calib['paralaxe'] / 60)
    print(f"err: {err:.3f}")

    L1 = calib['L1d'] + calib['L1m']/60
    L2 = calib['L2d'] + calib['L2m']/60
    alpha = (L1 + 360 - L2)/2
    ar = err * sqrt(2)/2

    print(f"alpha = {alpha:.3f}+-{ar:.3f}")


    desvio = pd.read_csv("../dados/desvio.csv", index_col='id')
    desvio['dm'] = desvio['dm_d'] + desvio['dm_m']/60
    # desvio['dmr'] = desvio['dm'] - desvio['dm'] + err

    desvio['n'] = n(desvio['dm'], alpha)
    desvio['nr'] = nr(desvio['dm'], alpha, err, ar)

    desvio['il2'] = 1/(desvio['lambda']/10**3)**2

    desvio['dm'] = desvio['dm'].apply(rounder(2))
    desvio['n'] = desvio['n'].apply(rounder(3))
    desvio['nr'] = desvio['nr'].apply(rounder(3))
    desvio['il2'] = desvio['il2'].apply(rounder(2))
    desvio.to_csv("../dados/desvio.csv")


    A, B, Ar, Br = lst_sq(desvio['il2'], desvio['n'], desvio['nr']*0)
    print(f"A = {A:.3f}+-{Ar:.3f}", f"B = {B:.4f}+-{Br:.4f}")

    coefs = {
        'A': A,
        'B': B,
        'Ar': Ar,
        'Br': Br,
        'alpha': alpha,
        'ar': ar,
        'dmr': err,
        # 'nr': nr(0, 0, 0, 0)
    }
    with open("../dados/coefs.json", mode='w') as fcoefs:
        json.dump(coefs, fcoefs, indent=4)


    _, _, _, cauchy = equations(coefs)
    resols = cauchy(desvio['dm'])
    l_r = min(resols)

    print(f"res. spec.: {l_r:.1f}")
