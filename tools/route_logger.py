class Wearhous:
    def __init__(self, H1, P1, M1, M2, M3, W1):
        self.H1 = H1
        self.P1 = P1
        self.M1 = M1
        self.M2 = M2
        self.M3 = M3
        self.W1 = W1


# Instances - using the values you provided (I didn't change your strings)
H1 = Wearhous("-", "RIGHT", "LEFT", "2LEFT", "3LEFT", "FORWARD")
P1 = Wearhous("LEFT", "-", "RIGHT-LEFT", "RIGHT-2LEFT", "RIGHT-3LEFT", "RIGHT")
W1 = Wearhous("FORWARD", "LEFT", "3RIGHT", "2RIGHT", "RIGHT", "-")
M1 = Wearhous("RIGHT", "RIGHR-LEFT", "-", "LEFT-LEFT", "LEFT-2RIGHT", "LEFT")
M2 = Wearhous("RIGHT", "RIGHT-LEFT", "RIGHT-RIGHT", "-", "LEFT-RIGHT", "LEFT")
M3 = Wearhous("RIGHT", "RIGHT_LEFT", "RIGHT-2RIGHT", "RIGHT-RIGHT", "-", "LEFT")

# register names on objects for nicer logging
H1.name = 'H1'
P1.name = 'P1'
W1.name = 'W1'
M1.name = 'M1'
M2.name = 'M2'
M3.name = 'M3'

mapa = {
    "H1": H1,
    "P1": P1,
    "W1": W1,
    "M1": M1,
    "M2": M2,
    "M3": M3
}


def way(obj, attr):
    """Return the direction string from obj to attr (attribute access)."""
    # getattr will return None if attribute missing
    return getattr(obj, attr, None)


def compute_route(start_name, points):
    """Compute and log route starting from start_name through the list `points`.

    Prints each leg to console in the form: "H1 -> M1 : RIGHT".
    """
    if start_name not in mapa:
        print(f"Start point '{start_name}' not in map")
        return

    current_name = start_name
    current_obj = mapa[current_name]

    for next_name in points:
        if next_name not in mapa:
            print(f"  SKIP: unknown point '{next_name}'")
            continue
        direction = way(current_obj, next_name)
        print(f"{current_name} -> {next_name} : {direction}")
        # advance
        current_name = next_name
        current_obj = mapa[current_name]


class RouteLogger:
    """Helper class to maintain an evolving route and log new legs when points are appended.

    Usage:
      rl = RouteLogger(start='H1')
      rl.add_point('M1')   # prints leg H1 -> M1
      rl.add_point('P1')   # prints M1 -> P1
      rl.get_points()      # returns list of added points
    """

    def __init__(self, start='H1'):
        if start not in mapa:
            raise ValueError(f"Unknown start point: {start}")
        self.start = start
        self.points = []

    def add_point(self, point_name):
        """Add a new point and print the leg from previous location to this point.

        If this is the first added point, the leg is from start to point_name.
        """
        prev = self.start if not self.points else self.points[-1]
        if point_name not in mapa:
            print(f"Cannot add unknown point '{point_name}'")
            return
        prev_obj = mapa[prev]
        dir_str = way(prev_obj, point_name)
        print(f"{prev} -> {point_name} : {dir_str}")
        self.points.append(point_name)

    def compute_all(self):
        """Compute the whole route from start through all points and print it."""
        compute_route(self.start, self.points)

    def get_points(self):
        return list(self.points)


def interactive():
    """Simple interactive console flow:
    - ask for initial number of points, read them and print full route
    - then allow adding new points one-by-one; each addition prints the new leg
    - type 'q' to quit
    """
    print("Podaj ilosc punktow (0 for none):")
    try:
        y = int(input().strip())
    except Exception:
        print("Nieprawidlowy numer, zakladam 0")
        y = 0

    pts = []
    for i in range(y):
        print(f"punkt {i+1}:")
        name = input().strip()
        pts.append(name)

    rl = RouteLogger(start='H1')
    # add initial points and log sequentially
    for p in pts:
        rl.add_point(p)

    print("Start interactive adding. Enter point name to append, or 'q' to quit.")
    while True:
        v = input('new point> ').strip()
        if not v:
            continue
        if v.lower() in ('q', 'quit', 'exit'):
            print('Exiting')
            break
        rl.add_point(v)


if __name__ == '__main__':
    interactive()
