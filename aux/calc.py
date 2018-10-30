import numpy as np
import pandas as pd
from scipy import stats


def n(desvio, alpha):
    sup = np.sin(np.deg2rad((alpha+desvio)/2))
    inf = np.sin(np.deg2rad(alpha/2))
    return sup/inf


if __name__ == "__main__":

    alpha1 = 56.5
    alpha2 = 298.35
    alpha = (alpha1 + 360 - alpha2)/2
    print(f"alpha = {alpha:.2f}")


    desvio = pd.read_csv("../dados/desvio.csv", index_col='id')

    desvio['dm'] = desvio['dm_d'] + desvio['dm_m']/60.0
    desvio['n'] = n(desvio['dm'], alpha)

    desvio['il2'] = 1/(desvio['lambda']/10**3)**2

    desvio.to_csv("../dados/desvio.csv")

    B, A, _, _, err = stats.linregress(desvio['il2'], desvio['n'])
    print(f"A = {A:.2f},  B = {B:.4f},  E = {err:.4f}")

    coefs = pd.DataFrame({
        'id': ["exp", "real"],
        'A': [A, 1.6070],
        'B': [B, 0.00825],
        'Ar': [0, 0.0003],
        'Br': [0, 0.00007],
        'alpha': [alpha, alpha],
        'ar': [0, 0]
    })
    coefs.to_csv("coefs.csv", index=False)
