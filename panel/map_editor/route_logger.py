from editor_page import resolve_key

class Warehouse:
    def __init__(self, H1, P1, M1, M2, M3, W1):
        self.H1 = H1
        self.P1 = P1
        self.M1 = M1
        self.M2 = M2
        self.M3 = M3
        self.W1 = W1



H1 = Warehouse


mapa = {
    resolve_key(H1): H1,
}


print("mapa: ", mapa)

def Way(OBJ, ATTR):
    print(getattr(OBJ,ATTR))


print("podaj ilosc punktow")

y = int(input())
list = []

for _ in range(y):
    print("punkt")

    list.append(input())

Start = H1
for M in range(len(list) - 1):

    Way(Start,list[M + 1])
    Start = mapa[list[M+1]]