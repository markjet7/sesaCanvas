import igraph as ig

def generate_random_string(n):
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase, k=n))

def layout_system(
        sys
):
    G = ig.Graph(directed=True)
    vertices = {}

    ids = []
    for i, u in enumerate(sys.units):
        if u.ID == "" or u.ID in ids:
            print("Old ID:", u.ID)
            print("Unit ID is empty or already exists. Assigning new ID.")
            u.ID = f"{generate_random_string(3)}{u.ID}"
            print("New ID:", u.ID)
        ids.append(u.ID)

    for i, s in enumerate(sys.streams):
        if s.ID == "" or s.ID in ids:
            print("Old ID:", s.ID)
            print("Unit ID is empty or already exists. Assigning new ID.")
            s.ID = f"{generate_random_string(3)}{s.ID}"
            print("New ID:", s.ID)
        ids.append(s.ID)

    ix = 0
    for s in set(sys.units + sys.feeds + sys.products):
        vertices[s.ID] = ix
        ix += 1

    edges = []
    labels = []
    for u in sys.streams:
        if u.source and u.sink:
            edges.append((vertices.get(u.source.ID, 1), vertices.get(u.sink.ID, 1)))
            
            labels.append(u.ID)
        elif u.source and not u.sink:
            edges.append((vertices.get(u.source.ID, 1), vertices.get(u.ID, 1)))
            labels.append(u.ID)
        elif not u.source and u.sink:
            edges.append((vertices.get(u.ID, 1), vertices.get(u.sink.ID, 1)))
            labels.append(u.ID)
        else:
            print("Stream with no sink or source: " + u.ID)
    G.add_vertices(len(vertices))
    G.add_edges(edges)

    G.vs["label"] = list(vertices.keys())
    
    G.es["label"] = labels

    l = G.layout("tree")
    l.rotate(270)
    l.mirror(1)
    return G, l, sys

