def add(a,b): return a+b  # style issue: one-line def

eval("1+1")  # security issue: bandit should flag this

def complex_fn(x):
    total = 0
    for i in range(5):
        if x > i:
            if i % 2 == 0:
                total += i
            else:
                if x - i > 2:
                    total += x*i
                else:
                    total -= i
    return total
