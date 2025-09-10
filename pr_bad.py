def add(a,b): return a+b  # flake8: spacing + one-line def
eval("1+1")               # bandit: insecure

def complex_fn(x):
    total = 0
    for i in range(10):
        if x > i:
            if i % 2 == 0:
                if x - i > 3:
                    total += x*i
                else:
                    total -= i
    return total

print('trigger CI')

print('retest')
