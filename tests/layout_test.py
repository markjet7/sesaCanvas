#%%
import sys 
sys.path.append("/Users/markmw/Github/sesaCanvas/src")

# from _misc import layout_system
import biosteam as bst 
import igraph as ig
#%%
with open("../src/MSW_to_Jet_Reference_Case.py", "r") as file:
    exec(file.read())

# G,l, sys = layout_system(sys)
#%%
s = list(filter(lambda x: x.ID == "SSS3", sys.streams))[0]
# %%
s
# %%
systems = {}
for name, obj in globals().items():
    if isinstance(obj, bst.System):
        systems[name] = obj
systems
# %%
# G, l, sys2 = layout_system(systems["pretreatment"])
# %%
def generate_random_string(n):
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))

sys = systems["pretreatment"]
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
        s.ID = f"{generate_random_string(3)}{s.ID}{i}"
        print("New ID:", s.ID)
    ids.append(s.ID)
#%%
ix = 0
for s in set(sys.units + sys.feeds + sys.products):
    print(s.ID, ix)
    vertices[s.ID] = ix
    ix += 1

#%%
edges = []
labels = []
for u in sys.streams:
    if u.source and u.sink:
        # edges.append((vertices[u.source.ID], vertices[u.sink.ID]))
        edges.append((vertices.get(u.source.ID, 1), vertices.get(u.sink.ID, 1)))
        labels.append(u.ID)
    elif u.source and not u.sink:
        edges.append((vertices[u.source.ID], vertices[u.ID]))
        labels.append(u.ID)
    elif not u.source and u.sink:
        edges.append((vertices[u.ID], vertices[u.sink.ID]))
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
#%%
vertices
# %%
a = list(sorted(
    [u.ID for u in sys.units] +
    [s.ID for s in sys.feeds] + 
    [s.ID for s in sys.products] 
    ))
a
# %%
for r in a:
    if r not in vertices.keys():
        print(r)
# %%
vertices
# %%
sys.units + sys.feeds + sys.products
# %%
