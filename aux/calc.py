import json
import pickle

import numpy as np
import pandas as pd
from scipy import stats


def print(*args, func=print, **kwargs):
    kwargs['sep'] = ",  "
    func(*args, **kwargs)

sqrt = np.sqrt
coalesce = lambda x, y: np.where(pd.notna(x), x, y)

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

    linear = lambda N: A + B / N
    lin_r = lambda N: sqrt(Ar**2 + (Br/N)**2)

    return linear, lin_r


def saveC(lasers, mmt, yr):
    lasers = pd.DataFrame(lasers[lasers['fenda'] == 'C'], copy=True)
    lasers['yr'] = [yr] * len(lasers.index)
    lasers['bm'] = mmt[mmt.index.str.startswith('C')]['b']
    lasers['bmr'] = mmt[mmt.index.str.startswith('C')]['yr']

    lasers.to_csv("../dados/C.csv", columns=('nDy', 'yr', 'n', 'Dy', 'Dyr', 'b', 'br', 'bm', 'bmr'))

def saveB(lasers, mmt, yr):
    lasers = pd.DataFrame(lasers[lasers['fenda'] == 'B'], copy=True)
    lasers['yr'] = [yr] * len(lasers.index)
    lasers['bm'] = mmt[mmt.index.str.startswith('B')]['b']
    lasers['hm'] = mmt[mmt.index.str.startswith('B')]['h']
    lasers['ymr'] = mmt[mmt.index.str.startswith('B')]['yr']

    lasers.to_csv("../dados/B.csv", columns=('nDy', 'yr', 'n', 'Dy', 'Dyr', 'mL', 'm', 'L', 'Lr', 'b', 'br', 'h', 'hr', 'bm', 'hm', 'ymr'))

def saveA(lasers, yr):
    lasers = pd.DataFrame(lasers[lasers['fenda'] == 'A'], copy=True)

    lasers['dy'] = coalesce(lasers['dy'], lasers['L']/2)
    lasers['dyr'] = coalesce(lasers['dyr'], lasers['Lr']/2)
    lasers['yr'] = [yr] * len(lasers.index)

    lasers.to_csv("../dados/A.csv", columns=('nDy', 'yr', 'n', 'Dy', 'Dyr', 'mL', 'm', 'L', 'Lr', 'b', 'br', 'h', 'hr', 'dy', 'dyr'))

def saveAplt(lasers, yr):
    lasers = pd.DataFrame(lasers[lasers['fenda'] == 'A'], copy=True)

    lasers['dy'] = coalesce(lasers['dy'], lasers['L']/2)
    lasers['dyr'] = coalesce(lasers['dyr'], lasers['Lr']/2)
    lasers['yr'] = [yr] * len(lasers.index)
    lasers['iN'] = 1/lasers['N']

    lasers.to_csv("A.csv", columns=('nDy', 'yr', 'n', 'Dy', 'Dyr', 'mL', 'm', 'L', 'Lr', 'b', 'br', 'h', 'hr', 'dy', 'dyr', 'N', 'iN'))



if __name__ == "__main__":
    with open("../dados/calib.json", mode='r') as fcalib:
        calib = json.load(fcalib)

    calib['zr'] = zr(calib['zres'])
    calib['yr'] = yr(calib['yres'])
    calib['Mr'] = Mr(calib['Mres'])
    print(calib)


    lasers = pd.read_csv("../dados/lasers.csv", index_col='id')
    micromt = pd.read_csv("../dados/micromt.csv", index_col='id')

    micromt['b'] = micromt['y2'] - micromt['y1']
    micromt['h'] = micromt['y3'] - micromt['y1']
    micromt['yr'] = [calib['Mr']] * len(micromt.index)

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
    print(lasers)

    # saveC(lasers, micromt, calib['yr'])
    # saveB(lasers, micromt, calib['yr'])
    # saveA(lasers, calib['yr'])
    saveAplt(lasers, calib['yr'])


    lasers['dy'] = coalesce(lasers['dy'], lasers['L']/2)
    lasers['dyr'] = coalesce(lasers['dyr'], lasers['Lr']/2)
    lin = pd.DataFrame(lasers[(lasers['fenda'] == 'A') & (lasers['N'] > 1)], copy=True)
    A, B, Ar, Br = lst_sq(1/lin['N'], lin['dy'], lin['dyr'])
    print(f"A = {A:.3f}+-{Ar:.3f}", f"B = {B:.4f}+-{Br:.4f}")

    coefs = {'A': A, 'Ar': Ar, 'B': B, 'Br': Br}
    with open("../dados/coefs.json", mode='w') as fcoefs:
        json.dump(coefs, fcoefs, indent=4)

    log = pd.DataFrame()
    log['N'] = np.log10(lin['N'])
    log['dy'] = np.log10(lin['dy'])
    log['dyr'] = lin['dyr']/lin['dy']/np.log(10)
    A, B, Ar, Br = lst_sq(log['N'], log['dy'], log['dyr'])
    print(f"A = {A:.3f}+-{Ar:.3f}", f"B = {B:.4f}+-{Br:.4f}")
