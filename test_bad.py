# test_bad.py

def add(a,b): return a+b    # flake8: one-line def / spacing

eval("1+1")                 # bandit: insecure eval

def complex_fn(x, n=7):
    total = 0
    for i in range(n):
        if x > i:
            if i % 2 == 0:
                if x - i > 3:
                    total += x*i
                else:
                    if x % 3 == 0:
                        if (x+i) % 5 == 0:
                            total += i
                        else:
                            total -= i
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
