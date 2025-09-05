# FLAKE8: spacing + one-line def
def add(a,b): return a+b

# BANDIT: insecure eval (B307)
eval("1+1")

# RADON: nested branches -> high cyclomatic complexity
def complex_fn(x):
    total = 0
    for i in range(10):
        if x > i:
            if i % 2 == 0:
                if x - i > 3:
                    total += x*i
                else:
                    if x % 3 == 0:
                        total += i
                    else:
                        if x < 10:
                            total += 1
                        else:
                            total -= 1
            else:
                if i % 3 == 0:
                    total += i*i
                else:
                    if (x-i) % 2 == 0:
                        total += 2*i
                    else:
                        total -= 2*i
    return total
