import igraph as ig

def layout_system(
        sys
):
    G = ig.Graph(directed=True)
    vertices = {}
    i = 0
    for u in sys.units:
        vertices[u.ID] = i
        i += 1
    for s in sys.feeds:
        vertices[s.ID] = i
        i += 1
    for s in sys.products:
        vertices[s.ID] = i
        i += 1

    edges = []
    labels = []
    for u in sys.streams:
        if u.source and u.sink:
            edges.append((vertices[u.source.ID], vertices[u.sink.ID]))
            labels.append(u.ID)
        elif u.source and not u.sink:
            edges.append((vertices[u.source.ID], vertices[u.ID]))
            labels.append(u.ID)
        elif not u.source and u.sink:
            edges.append((vertices[u.ID], vertices[u.sink.ID]))
            labels.append(u.ID)
    G.add_vertices(len(vertices))
    G.add_edges(edges)

    G.vs["label"] = list(vertices.keys())
    
    G.es["label"] = labels

    l = G.layout("tree")
    l.rotate(270)
    l.mirror(1)
    return G, l

