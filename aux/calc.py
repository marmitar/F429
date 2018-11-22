import json
import pickle

import numpy as np
import pandas as pd
from scipy import stats


def print(*args, func=print, **kwargs):
    kwargs['sep'] = ",  "
    func(*args, **kwargs)

sqrt = np.sqrt


def zr(res):
    return res * sqrt(3)/6

def yr(res):
    return zr(res)

def Mr(res):
    return res * sqrt(3)/2


def Dy(nDy, n, yr):
    return nDy/n, yr/n

def L(mL, m, yr):
    return Dy(mL, m, yr)


def hN(N, l, z, dy, zr, dyr):
    fac = l / (N * dy)
    err2 = zr**2 + (z*dyr/dy)**2
    return fac*z, fac*sqrt(err2)

def b(l, z, Dy, zr, Dyr):
    return hN(1, l, z, Dy/2, zr, Dyr/2)

def h2(l, z, L, zr, Lr):
    return hN(2, l, z, L/2, zr, Lr/2)


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

    return A, B, uA, uB


def rounder(digits):
    return lambda f: np.round(f, decimals=digits)


def equations(coefs):
    A, B = coefs['A'], coefs['B']
    Ar, Br = coefs['Ar'], coefs['Br']

    linear = lambda iN: A + B * iN
    lin_r = lambda iN: sqrt(Ar**2 + (iN*Br)**2)

    return linear, lin_r



if __name__ == "__main__":
    coalesce = lambda x, y: np.where(pd.notna(x), x, y)

    with open("../dados/calib.json", mode='r') as fcalib:
        calib = json.load(fcalib)

    calib['zr'] = zr(calib['zres'])
    calib['yr'] = yr(calib['yres'])
    calib['Mr'] = Mr(calib['Mres'])
    # print(calib)


    lasers = pd.read_csv("../dados/lasers.csv", index_col='id')
    # print(lasers)

    lasers['Dy'], lasers['Dyr'] = Dy(lasers['nDy'], lasers['n'], calib['yr'])
    lasers['L'], lasers['Lr'] = L(lasers['mL'], lasers['m'], calib['yr'])
    lasers['dy'], lasers['dyr'] = lasers['2dy']/2, [calib['yr']/2] * lasers['2dy']/lasers['2dy']
    lasers['b'], lasers['br'] = b(
        calib['lambda'], calib['z'], lasers['Dy'], calib['zr'], lasers['Dyr']
    )


    h2, h2r = h2(calib['lambda'], calib['z'], lasers['L'], calib['zr'], lasers['Lr'])
    hN, hNr = hN(lasers['N'], calib['lambda'], calib['z'], lasers['dy'], calib['zr'], lasers['dyr'])
    lasers['h'] = coalesce(h2, hN)
    lasers['hr'] = coalesce(h2r, hNr)
    # print(lasers)


    for key in "Dy", "L", "dy", "b", "h":
        lasers[key] = lasers[key].apply(rounder(5))
        lasers[key+'r'] = lasers[key+'r'].apply(rounder(5))
    # lasers['Dy'] = lasers['Dy'].apply(rounder(2))
    # desvio['n'] = desvio['n'].apply(rounder(3))
    # desvio['nr'] = desvio['nr'].apply(rounder(3))
    # desvio['il2'] = desvio['il2'].apply(rounder(2))
    for fenda in lasers['fenda'].unique():
        lasers[lasers['fenda'] == fenda].to_csv(f"../dados/{fenda}.csv")
    # print(lasers)


    lasers['dy'] = coalesce(lasers['dy'], lasers['L']/2)
    lasers['dyr'] = coalesce(lasers['dyr'], lasers['Lr']/2)
    lin = pd.DataFrame(lasers[(lasers['fenda'] == 'A') & (lasers['N'] > 1)], copy=True)
    lin['1/N'] = 1/lin['N']
    A, B, Ar, Br = lst_sq(lin['1/N'], lin['dy'], lin['dyr']*0)
    print(f"A = {A:.3f}+-{Ar:.3f}", f"B = {B:.4f}+-{Br:.4f}")

    coefs = {'A': A, 'Ar': Ar, 'B': B, 'Br': Br}
    with open("../dados/coefs.json", mode='w') as fcoefs:
        json.dump(coefs, fcoefs, indent=4)

