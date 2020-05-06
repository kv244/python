# check dictionary
import random

c = dict()
d = dict()
final = dict()

c[0] = 'root'

for k in range(100):
    c[k+1] = str(k) + 'ziggy'

for z1 in c:
    n = random.random() * 100
    if n > 50:
        d[n] = str(n) + 'bopp'

for
