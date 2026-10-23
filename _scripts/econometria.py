# Estimador común: mínimos cuadrados ponderados con errores agrupados (CR1) y wild cluster bootstrap restringido (Webb).
# Lo usan did_04_modelos.py (análisis departamental) y cen_02_modelos_distritales.py (análisis censal).
import numpy as np, patsy
from scipy import stats

rng = np.random.default_rng(2024)
REPS = 999


class Fit:
    def __init__(self, formula, d, var, grupo='cod_dpto'):
        d = d.dropna(subset=[c for c in d.columns if c in formula] + ['w']).copy()
        y, X = patsy.dmatrices(formula, d, return_type='dataframe')
        self.d = d.loc[y.index]; self.y = y.iloc[:, 0].values; self.X = X
        self.sw = np.sqrt(self.d.w.values)
        self.g = self.d[grupo].values; self.G = np.unique(self.g)
        self.var = var; self.j = list(X.columns).index(var)
        self.Xw = X.values * self.sw[:, None]
        self.XtXi = np.linalg.pinv(self.Xw.T @ self.Xw)
        self.idx = [np.where(self.g == gg)[0] for gg in self.G]
        self.b, self.se = self._fit(self.y)
        self.n = len(self.y)

    def _fit(self, y, only_j=False):
        yw = y * self.sw
        b = self.XtXi @ (self.Xw.T @ yw)
        u = yw - self.Xw @ b
        n, k = self.Xw.shape; G = len(self.G)
        A = self.XtXi[self.j] if only_j else self.XtXi
        s = np.array([self.Xw[i].T @ u[i] for i in self.idx])  # G x k
        if only_j:
            v = ((s @ A) ** 2).sum()
        else:
            v = A @ (s.T @ s) @ A
        c = G / (G - 1) * (n - 1) / (n - k)
        se = np.sqrt(c * (v if only_j else np.diag(v)))
        return b, se

    def coef(self): return self.b[self.j]
    def p_cluster(self):
        return 2 * stats.t.sf(abs(self.b[self.j] / self.se[self.j]), len(self.G) - 1)

    def p_wild(self, reps=REPS):
        """Wild cluster bootstrap restringido (pesos de Webb), H0: coef = 0."""
        Xr = np.delete(self.Xw, self.j, axis=1)
        br = np.linalg.lstsq(Xr, self.y * self.sw, rcond=None)[0]
        fit_r = Xr @ br; u_r = self.y * self.sw - fit_r
        t0 = self.b[self.j] / self.se[self.j]
        webb = np.array([-np.sqrt(1.5), -1, -np.sqrt(.5), np.sqrt(.5), 1, np.sqrt(1.5)])
        gi = np.searchsorted(self.G, self.g)
        cnt = 0
        for _ in range(reps):
            ystar = (fit_r + u_r * rng.choice(webb, len(self.G))[gi]) / self.sw
            b, se = self._fit(ystar, only_j=True)
            cnt += abs(b[self.j] / se) >= abs(t0)
        return (cnt + 1) / (reps + 1)
