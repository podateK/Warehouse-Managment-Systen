class Wearhous:
    def __init__(self, H1, P1, M1, M2, M3, W1):
        self.H1 = H1
        self.P1 = P1
        self.M1 = M1
        self.M2 = M2
        self.M3 = M3
        self.W1 = W1


H1 = Wearhous("-", "RIGHT", "LEFT", "2LEFT", "3LEFT", "FORWARD")
P1 = Wearhous("LEFT", "-", "RIGHT-LEFT", "RIGHT-2LEFT", "RIGHT-3LEFT", "RIGHT")
W1 = Wearhous("FORWARD", "LEFT", "3RIGHT", "2RIGHT", "RIGHT", "-")
M1 = Wearhous("RIGHT", "RIGHR-LEFT", "-", "LEFT-LEFT", "LEFT-2RIGHT", "LEFT")
M2 = Wearhous("RIGHT", "RIGHT-LEFT", "RIGHT-RIGHT", "-", "LEFT-RIGHT", "LEFT")
M3 = Wearhous("RIGHT", "RIGHT_LEFT", "RIGHT-2RIGHT", "RIGHT-RIGHT", "-", "LEFT")

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


def get_flat_moves_from_mapa():
    """Return a flattened list of moves from module-level `mapa`, filtering out '-' placeholders.

    The order is by mapa.keys() iteration and, for each source, by the same keys order.
    """
    try:
        names = list(mapa.keys())
    except Exception:
        return []
    out = []
    for src in names:
        obj = mapa.get(src)
        if not obj: 
            continue
        for dst in names:
            if dst == 'name':
                continue
            try:
                v = getattr(obj, dst, None)
            except Exception:
                v = None
            if v and v != '-':
                out.append(v)
    return out


def update_mapa_from_canvas(points, connections):
    """Build a simple `mapa` mapping from point names to objects.

    `points` is a list of dicts (as in MapCanvas.points). Each point should
    have a 'name' (string). `connections` is a list of (src_idx, dst_idx)
    tuples.

    The function creates objects where attributes named after other points
    are set to a simple marker ("CONNECTED") if a direct connection exists,
    otherwise they are None. The module-level `mapa` variable is replaced.
    """
    try:
        from types import SimpleNamespace
    except Exception:
        SimpleNamespace = None

    names = []
    for i, p in enumerate(points):
        n = (p.get('name') or '').strip()
        if not n:
            n = f'#${i}'
        names.append(n)

    new_mapa = {}
    for n in names:
        attrs = {other: None for other in names}
        attrs['name'] = n
        if SimpleNamespace:
            obj = SimpleNamespace(**attrs)
        else:
            class Obj:
                pass
            obj = Obj()
            for k, v in attrs.items():
                setattr(obj, k, v)
        new_mapa[n] = obj

    def compute_direction(src_pt, dst_pt):
        try:
            import math
            dx = (dst_pt.get('x', 0) - src_pt.get('x', 0))
            dy = (src_pt.get('y', 0) - dst_pt.get('y', 0))
            if dx == 0 and dy == 0:
                return 'HERE'
            angle = math.degrees(math.atan2(dy, dx))
            if -45 <= angle <= 45:
                return 'RIGHT'
            if 45 < angle <= 135:
                return 'FORWARD'
            if angle > 135 or angle <= -135:
                return 'LEFT'
            return 'BACK'
        except Exception:
            return 'CONNECTED'

    for s, d in connections:
        if 0 <= s < len(names) and 0 <= d < len(names):
            sname = names[s]
            dname = names[d]
            try:
                src_pt = points[s] if 0 <= s < len(points) else {}
                dst_pt = points[d] if 0 <= d < len(points) else {}
                dir_str = compute_direction(src_pt, dst_pt)
                setattr(new_mapa[sname], dname, dir_str)
            except Exception:
                try:
                    setattr(new_mapa[sname], dname, 'CONNECTED')
                except Exception:
                    pass

    globals()['mapa'] = new_mapa
    try:
        print('route_logger: mapa updated ->', list(new_mapa.keys()))
    except Exception:
        pass


def print_directions():
    """Print only the directional mapping for direct connections.

    Format: "SRC -> DST : DIRECTION" per line.
    """
    try:
        names = list(mapa.keys())
    except Exception:
        print('route_logger: mapa not available')
        return
    for src, obj in mapa.items():
        for dst in names:
            if dst == 'name':
                continue
            try:
                v = getattr(obj, dst, None)
            except Exception:
                v = None
            if v:
                print(f"{src} -> {dst} : {v}")


def sequence_from_canvas(points, connections, start_name=None):
    """Return a list of point names following first outgoing links starting from start_name (or H1/first).

    It follows the first non-visited outgoing edge at each step to build a linear route.
    """
    names = []
    for i, p in enumerate(points):
        raw = (p.get('name') or '').strip()
        if not raw:
            names.append(f'#${i}')
        else:
            names.append(raw)

    adj = {}
    for s, d in connections:
        if 0 <= s < len(names) and 0 <= d < len(names):
            adj.setdefault(s, []).append(d)

    start_idx = None
    if start_name:
        try:
            start_idx = names.index(start_name)
        except ValueError:
            start_idx = None
    if start_idx is None:
        if 'H1' in names:
            start_idx = names.index('H1')
        else:
            start_idx = 0 if names else None

    if start_idx is None:
        return []

    import re
    display = list(names)
    for i, n in enumerate(names):
        if n.startswith('#$'):
            raw_type = ''
            try:
                raw_type = (points[i].get('type') or '').strip()
            except Exception:
                raw_type = ''
            if raw_type:
                m2 = re.match(r'^([A-Za-z]+)', raw_type)
                display[i] = m2.group(1) if m2 else raw_type
            else:
                display[i] = 'X'

    seq = []
    visited = set()
    cur = start_idx
    while cur is not None and cur not in visited:
        seq.append(display[cur])
        visited.add(cur)
        outs = [dst for dst in adj.get(cur, []) if dst not in visited]
        cur = outs[0] if outs else None

    return seq


def print_sequence_from_canvas(points, connections, start_name=None):
    """Update internal mapa and print the linear sequence found from canvas connections."""
    update_mapa_from_canvas(points, connections)
    seq = sequence_from_canvas(points, connections, start_name=start_name)
    if seq:
        print('SEQUENCE:', ','.join(seq))
    else:
        print('SEQUENCE: (empty)')
    return seq


def build_warehouse_objects(fill='-'):
    """Build Warehouse-like objects for each key in current `mapa`.

    Returns dict name -> object with attributes for each target name.
    Missing directions are filled with `fill`.
    """
    try:
        names = list(mapa.keys())
    except Exception:
        return {}
    try:
        from types import SimpleNamespace
    except Exception:
        SimpleNamespace = None

    objs = {}
    for src in names:
        attrs = {}
        for dst in names:
            if dst == 'name':
                continue
            try:
                v = getattr(mapa[src], dst, None)
            except Exception:
                v = None
            attrs[dst] = v if v else fill
        attrs['name'] = src
        if SimpleNamespace:
            obj = SimpleNamespace(**attrs)
        else:
            class O: pass
            obj = O()
            for k, val in attrs.items():
                setattr(obj, k, val)
        objs[src] = obj
    return objs


def compute_placeholders_and_displays(points):
    """Return (placeholders, displays) lists for given points.

    placeholders: ['#$0', '#$1', ...]
    displays: user-friendly names (point name or type letters) matching indices
    """
    import re
    placeholders = []
    displays = []
    for i, p in enumerate(points):
        raw = (p.get('name') or '').strip()
        ph = raw if raw else f'#${i}'
        placeholders.append(ph)
        if raw:
            displays.append(raw)
        else:
            raw_type = (p.get('type') or '').strip()
            if raw_type:
                m = re.match(r'^([A-Za-z]+)', raw_type)
                displays.append(m.group(1) if m else raw_type)
            else:
                displays.append(f'X{i}')
    return placeholders, displays


def print_warehouse_declarations(order=None, fill='-'):
    """Print Warehouse(...) style declarations for current mapa.

    If `order` is provided it determines the parameter order for Warehouse(...).
    """
    if isinstance(order, (list, tuple)) and len(order) >= 1 and isinstance(order[0], dict):
        points = order
        placeholders, displays = compute_placeholders_and_displays(points)
        vals_order = displays
        for i, src_disp in enumerate(displays):
            src_ph = placeholders[i]
            vals = []
            for j, dst_disp in enumerate(displays):
                dst_ph = placeholders[j]
                try:
                    v = getattr(mapa.get(src_ph, type('o', (), {})()), dst_ph, None)
                except Exception:
                    v = None
                vals.append(v if v else fill)
            vals_s = ', '.join(f'"{v}"' for v in vals)
            print(f'{src_disp} = Warehouse({vals_s})')
        return

    objs = build_warehouse_objects(fill=fill)
    if not objs:
        print('No mapa available')
        return
    names = order or list(objs.keys())
    for name in names:
        obj = objs.get(name)
        if not obj:
            continue
        vals = []
        for dst in names:
            vals.append(getattr(obj, dst, fill))
        vals_s = ', '.join(f'"{v}"' for v in vals)
        print(f'{name} = Warehouse({vals_s})')


def print_compact_mappings(fill='-'):
    """Print compact list of outgoing mappings: 'SRC: DST(dir), ...' showing only set directions."""
    if isinstance(fill, list):
        points = fill
        placeholders, displays = compute_placeholders_and_displays(points)
        for i, src_disp in enumerate(displays):
            src_ph = placeholders[i]
            outs = []
            for j, dst_disp in enumerate(displays):
                dst_ph = placeholders[j]
                try:
                    v = getattr(mapa.get(src_ph, type('o', (), {})()), dst_ph, None)
                except Exception:
                    v = None
                if v and v != '-':
                    outs.append(f'{dst_disp}({v})')
            if outs:
                print(f'{src_disp}: ' + ', '.join(outs))
            else:
                print(f'{src_disp}: (none)')
        return

    objs = build_warehouse_objects(fill=fill)
    if not objs:
        print('No mapa available')
        return
    for src, obj in objs.items():
        outs = []
        for dst in objs.keys():
            if dst == 'name':
                continue
            v = getattr(obj, dst, fill)
            if v and v != fill:
                outs.append(f'{dst}({v})')
        if outs:
            print(f'{src}: ' + ', '.join(outs))
        else:
            print(f'{src}: (none)')


def sequence_indices_from_canvas(points, connections, start_name=None):
    """Return list of indices visited following first-outgoing edges (like sequence_from_canvas but indices)."""
    names = []
    for i, p in enumerate(points):
        raw = (p.get('name') or '').strip()
        if not raw:
            names.append(f'#${i}')
        else:
            names.append(raw)

    adj = {}
    for s, d in connections:
        if 0 <= s < len(names) and 0 <= d < len(names):
            adj.setdefault(s, []).append(d)

    start_idx = None
    if start_name:
        try:
            start_idx = names.index(start_name)
        except ValueError:
            start_idx = None
    if start_idx is None:
        if 'H1' in names:
            start_idx = names.index('H1')
        else:
            start_idx = 0 if names else None

    if start_idx is None:
        return []

    seq = []
    visited = set()
    cur = start_idx
    while cur is not None and cur not in visited:
        seq.append(cur)
        visited.add(cur)
        outs = [dst for dst in adj.get(cur, []) if dst not in visited]
        cur = outs[0] if outs else None

    return seq


def send_route_commands(points, connections, request_sender=None, start_name=None, leg_delay=0.2):
    """Send commands derived from route to Arduino using Warehouse + Way() structure.

    Extracts sequence of points from canvas connections and sends commands using Way() function.
    """
    def _worker():
        try:
            # Update mapa from canvas
            update_mapa_from_canvas(points, connections)
            
            # Get names mapping
            names = []
            for i, p in enumerate(points):
                n = (p.get('name') or '').strip()
                names.append(n if n else f'#${i}')
            
            # Create RequestSender if not provided
            RS = request_sender
            if RS is None:
                try:
                    from functions.RequestSender import RequestSender
                    RS = RequestSender("http://localhost:3000/cmd")
                except Exception:
                    RS = None
            
            # Get sequence of point indices (following first outgoing edges)
            idx_seq = sequence_indices_from_canvas(points, connections, start_name=start_name)
            if not idx_seq or len(idx_seq) < 2:
                print("⚠️  Route has less than 2 points")
                return
            
            # Convert indices to names
            point_names = [names[i] for i in idx_seq]
            
            print(f"\n🚀 Sending route via Warehouse structure: {' → '.join(point_names)}\n")
        
            import time
            Start = mapa.get(point_names[0])
            for i in range(len(point_names) - 1):
                current_point = point_names[i]
                next_point = point_names[i + 1]
                
                try:
                    Way(current_point, next_point, request_sender=RS, leg_delay=leg_delay)
                    Start = mapa.get(next_point)
                    time.sleep(0.5) 
                except Exception as e:
                    print(f"❌ Error processing {current_point} → {next_point}: {e}")
                    continue
            
            print(f"\n✅ Route completed!\n")
            
        except Exception as e:
            print('send_route_commands worker error:', e)

    import threading
    th = threading.Thread(target=_worker, daemon=True)
    th.start()
    return th


def Way(current_point, next_point, line_num=None, request_sender=None, leg_delay=0.2):
    try:
        RS = request_sender
        if RS is None:
            try:
                from functions.RequestSender import RequestSender
                RS = RequestSender("http://localhost:3000/cmd")
            except Exception:
                RS = None
        
        # Get point names
        src_name = current_point if isinstance(current_point, str) else getattr(current_point, 'name', str(current_point))
        dst_name = next_point if isinstance(next_point, str) else getattr(next_point, 'name', str(next_point))
        
        # Get source object from mapa
        src_obj = mapa.get(src_name)
        if src_obj is None:
            print(f"❌ Point '{src_name}' not found in mapa")
            return None
        
        # Get direction attribute
        direction = getattr(src_obj, dst_name, None)
        if direction is None or direction == '-':
            print(f"⚠️  No direction from {src_name} to {dst_name}")
            return None
        
        # Parse direction to get main direction (LEFT/RIGHT/FORWARD)
        dir_upper = direction.upper()
        main_dir = None
        if 'LEFT' in dir_upper:
            main_dir = 'LEFT'
        elif 'RIGHT' in dir_upper:
            main_dir = 'RIGHT'
        elif 'FORWARD' in dir_upper:
            main_dir = 'FORWARD'
        else:
            main_dir = dir_upper
        
        # Build command with line number if provided
        if line_num is not None:
            # Format: "left 2" or "right 1"
            cmd = f"{main_dir} {line_num}".lower()
            print(f"📤 {src_name} → {dst_name}: direction = {main_dir} at line {line_num}")
        else:
            cmd = main_dir.lower()
            print(f"📤 {src_name} → {dst_name}: direction = {main_dir}")
        
        import time
        try:
            if RS:
                RS.send_request(cmd)
            else:
                print(f"   Sending: {cmd}")
        except Exception as e:
            print(f"   ❌ Error sending: {e}")
        
        time.sleep(leg_delay)
        return direction
        
    except Exception as e:
        print(f'Way() error: {e}')
        return None


def send_commands_from_list(points_list, request_sender=None, leg_delay=0.2):
    """Send movement commands based on a list of point names using Way() function.
    
    Args:
        points_list: List of point names, e.g., ['H1', 'M1', 'M2', 'M3', 'P1']
        request_sender: RequestSender instance (if None, creates new one for localhost)
        leg_delay: Delay between commands in seconds (default 0.2)
    
    Example:
        send_commands_from_list(['H1', 'M1', 'M2', 'M3', 'P1'])
    """
    def _worker():
        try:
            RS = request_sender
            if RS is None:
                try:
                    from functions.RequestSender import RequestSender
                    RS = RequestSender("http://localhost:3000/cmd")
                except Exception:
                    print("Error: Could not create RequestSender")
                    return

            if not points_list or len(points_list) < 2:
                print("Error: Need at least 2 points in the list")
                return

            print(f"\n🚀 Sending commands for route: {' → '.join(points_list)}\n")
            
            import time
            
            # Process each pair of consecutive points using Way()
            Start = mapa.get(points_list[0])
            for i in range(len(points_list) - 1):
                current_point = points_list[i]
                next_point = points_list[i + 1]
                
                # Use Way() to send command
                try:
                    Way(current_point, next_point, request_sender=RS, leg_delay=leg_delay)
                    Start = mapa.get(next_point)
                    time.sleep(0.5)  # Pause between point transitions
                except Exception as e:
                    print(f"❌ Error processing {current_point} → {next_point}: {e}")
                    continue
            
            print(f"\n✅ Route completed!\n")
        except Exception as e:
            print(f'send_commands_from_list error: {e}')

    import threading
    th = threading.Thread(target=_worker, daemon=True)
    th.start()
    return th


def send_commands_from_branches(branches, request_sender=None, leg_delay=0.2, start_name='H1'):
    """Send movement commands based on canvas branches with line numbers.
    
    Each branch has: {line_num: int, direction: 'LEFT'|'RIGHT', name: str, point_type: str}
    
    Args:
        branches: List of branch dicts with line_num, direction, name, point_type
        request_sender: RequestSender instance
        leg_delay: Delay between commands
        start_name: Starting point name (usually 'H1')
    
    Example:
        branches = [
            {'line_num': 1, 'direction': 'LEFT', 'name': 'M1', 'point_type': 'M'},
            {'line_num': 2, 'direction': 'RIGHT', 'name': 'M2', 'point_type': 'M'},
        ]
        send_commands_from_branches(branches)
    """
    def _worker():
        try:
            RS = request_sender
            if RS is None:
                try:
                    from functions.RequestSender import RequestSender
                    RS = RequestSender("http://localhost:3000/cmd")
                except Exception:
                    print("Error: Could not create RequestSender")
                    return

            if not branches or len(branches) == 0:
                print("Error: No branches to process")
                return

            print(f"\n🚀 Sending commands from {len(branches)} branches:\n")
            
            import time
            
            # Send starting point first
            current = start_name
            print(f"  Start: {current}")
            
            # Send commands for each branch
            for i, branch in enumerate(branches):
                line_num = branch.get('line_num', 1)
                direction = branch.get('direction', 'LEFT')
                name = branch.get('name', '')
                
                try:
                    # Send command with line number
                    Way(current, name, line_num=line_num, request_sender=RS, leg_delay=leg_delay)
                    current = name
                    time.sleep(0.5)  # Pause between branches
                except Exception as e:
                    print(f"❌ Error processing branch {i}: {e}")
                    continue
            
            print(f"\n✅ All branches completed!\n")
        except Exception as e:
            print(f'send_commands_from_branches error: {e}')

    import threading
    th = threading.Thread(target=_worker, daemon=True)
    th.start()
    return th


def parse_direction(direction_str):
    """Parse direction string and return list of commands.
    
    Handles both '-' and '_' as separators.
    
    Examples:
        'RIGHT' → ['ruch:right']
        'LEFT-LEFT' → ['ruch:left', 'ruch:left']
        'LEFT_LEFT' → ['ruch:left', 'ruch:left']
        '2RIGHT' → ['ruch:right', 'ruch:right']
        'FORWARD' → ['ruch:forward']
        'RIGHT-2LEFT' → ['ruch:right', 'ruch:left', 'ruch:left']
    """
    if not direction_str or direction_str == '-':
        return []
    
    commands = []
    # Handle both '-' and '_' as separators
    normalized = direction_str.replace('_', '-')
    parts = normalized.split('-')
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        # Check if starts with number
        if part[0].isdigit():
            # Extract number and direction (e.g., "2LEFT" → 2, LEFT)
            i = 0
            while i < len(part) and part[i].isdigit():
                i += 1
            count = int(part[:i])
            direction = part[i:].lower() if i < len(part) else ''
            
            if direction in ['left', 'right', 'forward', 'back']:
                for _ in range(count):
                    commands.append(f'ruch:{direction}')
            else:
                commands.append(f'ruch:{direction}')
        else:
            direction = part.lower()
            if direction in ['left', 'right', 'forward', 'back']:
                commands.append(f'ruch:{direction}')
            else:
                commands.append(direction)
    
    return commands


def get_mapa_summary():
    """Return a serializable summary of current `mapa` for inspection.

    Returns a dict mapping point-name -> dict(attribute->value).
    """
    out = {}
    for name, obj in mapa.items():
        try:
            attrs = {k: getattr(obj, k) for k in dir(obj) if not k.startswith('_')}
        except Exception:
            attrs = {}
        clean = {}
        for k, v in attrs.items():
            if callable(v):
                continue
            try:
                clean[k] = v
            except Exception:
                clean[k] = repr(v)
        out[name] = clean
    return out


def print_mapa(verbose=False):
    """Print a readable dump of `mapa` to stdout.

    If `verbose` is False, prints only keys and direct non-empty connections.
    """
    try:
        names = list(mapa.keys())
    except Exception:
        print('route_logger: mapa is not available')
        return

    print('route_logger: mapa keys ->', names)
    for name, obj in mapa.items():
        print(f'- {name}:')
        if verbose:
            summary = get_mapa_summary().get(name, {})
            for k, v in summary.items():
                if k == 'name':
                    continue
                print(f'    {k} -> {v}')
        else:
            found = []
            try:
                for k in names:
                    if k == 'name':
                        continue
                    if getattr(obj, k, None):
                        found.append(k)
            except Exception:
                pass
            print('    connected ->', found)


def way(obj, attr):
    """Return the direction string from obj to attr (attribute access)."""
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
