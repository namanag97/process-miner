
import numpy as np
import scipy.stats as stats
import time

N = 1_000_000

print(f"Benchmarking generation of {N} variates...")

# 1. Numpy Random (LogNormal)
start = time.time()
data_np = np.random.lognormal(mean=0, sigma=1, size=N)
end = time.time()
print(f"Numpy LogNormal: {end - start:.4f} seconds")

# 2. Scipy Stats (LogNormal) - rvs
start = time.time()
data_sp = stats.lognorm.rvs(s=1, scale=np.exp(0), size=N)
end = time.time()
print(f"Scipy LogNormal (rvs): {end - start:.4f} seconds")

# 3. Numpy Random (Poisson)
start = time.time()
data_np_pois = np.random.poisson(lam=5, size=N)
end = time.time()
print(f"Numpy Poisson: {end - start:.4f} seconds")

# 4. Scipy Stats (Poisson)
start = time.time()
data_sp_pois = stats.poisson.rvs(mu=5, size=N)
end = time.time()
print(f"Scipy Poisson: {end - start:.4f} seconds")
