import networkx as nx


# ATOM is the basic element
class ATOM(tuple):
    def __init__(self, pair):
        return

# A SEED is a vertex and the set of edges that connect to it. That is, it is the pair (v,Ev) 
# where v is a single vertex, and Ev is a set of edges containing that vertex, i.e. that set 
# of edges having v as one or the other endpoint. The vertex v may be called the GERM of the 
# seed. For each edge in the edge set, the other vertex is called the CONNECTOR
class SEED:
    def __init__(self, germ, connectors):
        self.germ = None
        self.connectors = []
        self.add_germ(germ)
        [self.add_connector(x) for x in connectors]
        return

    def __str__(self):
        return 'seed: %s %s' % (self.germ, self.connectors)

    def add_germ(self, germ):
        self.germ = germ
        return

    def add_connector(self, connector):
        self.connectors.append(connector)
        return


# A SECTION is a set of seeds
class SECTION:
    def __init__(self, seeds):
        self.seeds = []
        self.links = []
        [self.add_seed(x) for x in seeds]

    def add_seed(self, seed):
        self.seeds.append(seed)
        return

    def add_link(self, link):
        self.links.append(link)
        return

    def __str__(self):
        return 'section: %s' % (self.seeds)

    # Definition. Given a section S, a "link" is any edge (v1,v2) where both 
    # v1 and v2 appear as germs of seeds in S. Two seeds are "connected"
    # when there is a link between them.
    # Assumptions:
    # - v1 and v2 are Atoms
    # - links are between Atoms
    def join(self, v1, v2):
        v1_found = False
        v2_found = False
        v1_seed = None
        v2_seed = None
        for i in self.seeds:
            if v1 == i.germ and v2 in i.connectors:
                v1_found = True
                v1_seed = i
            if v2 == i.germ and v1 in i.connectors:
                v2_found = True
                v2_seed = i
        # A link can be formed only when germ v1 has v2 as connector, and also
        # at the same time, the germ v2 has v1 as connector.
        if v1_found and v2_found:
            if (v1_seed, v2_seed) not in self.links:
                self.add_link((v1_seed.germ, v2_seed.germ))
            # The joining is also meant to consume the connectors as a resource: 
            # once two connectors have been connected, neither one is free to make 
            # connections elsewhere.
            v1_seed.connectors.remove(v2)
            v2_seed.connectors.remove(v1)
            return True
        else:
            return False

    def connectors(self):
        result = []
        for seed in self.seeds:
            available_connectors = []
            for j in seed.connectors:
                available_connectors.append(j)
            result.append((seed.germ, available_connectors))
        print('Available connectors: ', result)

    # Definition. A CONNECTED SECTION, or a CONTIGUOUS SECTION is a section 
    # where every germ is connected to every other germ via a path through the edges.
    def is_connected(self):
        # Build a graph with nodes as elements in the SECTION and edges as links in the SECTION
        # and check for connectedness
        G = nx.Graph()
        print('Section # of seeds %s' % (len(self.seeds)))
        [G.add_node(x.germ) for x in self.seeds]
        [G.add_edges_from([x]) for x in self.links]
        print('Section has %s nodes and %s edges' % (len(G.nodes()), len(G.edges())))
        print(G.nodes())
        print(G.edges())
        return nx.is_connected(G)


def disjoint_section_from_graph(G):
    section = Section()
    for germ in G.nodes():
        H = nx.Graph()
        [H.add_edges_from([x]) for x in G.edges(germ)]
        section.append(Seed(H, germ))
    return section 

if __name__ == "__main__":


    A = ATOM(('A', 'any'))
    B = ATOM(('B', 'any'))
    C = ATOM(('C', 'any'))
    D = ATOM(('D', 'any'))
    Aseed = SEED(A, [B,C]) 
    Bseed = SEED(B, [A,D])
    Cseed = SEED(C, [A,D])
    Dseed = SEED(D, [C,B])
    mysection = SECTION([Aseed, Bseed, Cseed, Dseed])
    print(mysection.connectors())
    mysection.join(A, B)
    mysection.join(A, C)
    mysection.join(C, D)
    mysection.join(B, D)
    print('connected section: ', mysection.is_connected())
    print(mysection.connectors())
