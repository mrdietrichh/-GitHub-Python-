class Fibo:
    def __init__(self):
        self.a = 0
        self.b = 1

    def __iter__(self):
        return self

    def __next__(self):
        result = self.a
        self.a, self.b = self.b, self.a + self.b
        return result


def integers():
    n = 0
    while True:
        yield n
        n += 1


def primes():
    n = 2
    while True:
        is_prime = True
        i = 2
        while i * i <= n:
            if n % i == 0:
                is_prime = False
                break
            i += 1
        if is_prime:
            yield n
        n += 1

fib = Fibo()
for _ in range(10):
    print(next(fib), end=' ')
print()

int_gen = integers()
for _ in range(10):
    print(next(int_gen), end=' ')
print()

prime_gen = primes()
for _ in range(10):
    print(next(prime_gen), end=' ')
print()