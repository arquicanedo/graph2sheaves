import networkx as nx



# ATOM is the basic element
class ATOM(tuple):
    def __init__(self, pair):
        self._vertex = pair[0]
        self._type = pair[1]
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
        v1_seed = None
        v2_seed = None
        for i in self.seeds:
            if v1 == i.germ and v2 in i.connectors:
                v1_seed = i
            if v2 == i.germ and v1 in i.connectors:
                v2_seed = i
        # A link can be formed only when germ v1 has v2 as connector, and also
        # at the same time, the germ v2 has v1 as connector.
        if v1_seed and v2_seed:
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
        print('Links:', self.links)

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



# Typed seed
class tSECTION(SECTION):
    # Definition. Given a section S, a LINK between seeds s1 = (v1,C1) and s2 = (v2,C2) 
    # is any edge (v1,v2) where v1 is in one of the types in C2 and v2 is in one of the types in C1.
    # That is, there exists a pair (v1,ta) \in C1 such that v2 \in ta and, symmetrically,
    # there exists a pair (v2,tb) \in C2 such that v1 \in tb . 
    # Assumptions:
    # - s1 and s2 are SEEDS
    # - links are between *SEEDS*
    def join(self, s1, s2):
        v1 = s1.germ
        v2 = s2.germ
        C1 = s1.connectors
        C2 = s2.connectors
        ta = None
        tb = None

        # (v1,ta) \in C2
        for i in C2:
            if v1._type == i:
                ta = i
                break
        # (v2,tb) \in C2
        for i in C1:
            if v2._type == i:
                tb = i
                break
        # Link sections
        if ta and tb:
            self.add_link((s1, s2))
            s1.connectors.remove(tb)
            s2.connectors.remove(ta)


    def type_check(self, v1, v2):
        if v1._type == v2._type or v2._type == "any":
            return True
        else:
            return False

    # Definition. Two seeds are CONNECTED when there is a link between them. 
    def is_connected(self):
        # Build a graph with nodes as elements in the SECTION and edges as links in the SECTION
        # and check for connectedness
        G = nx.Graph()
        print('Section # of seeds %s' % (len(self.seeds)))
        [G.add_node(x.germ) for x in self.seeds]
        [G.add_edges_from([(x[0].germ, x[1].germ)]) for x in self.links]
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
    mysection.join(A, B)
    mysection.join(A, C)
    mysection.join(C, D)
    mysection.join(B, D)
    print('connected section: ', mysection.is_connected())
    print(mysection.connectors())


    print('------------------')
    X = ATOM(('X','x'))
    Y = ATOM(('Y','y'))
    Z = ATOM(('Z','z'))
    Xseed = SEED(X, ['x'])
    Yseed = SEED(Y, ['x', 'z'])
    Zseed = SEED(Z, ['y'])
    mysection2 = tSECTION([Xseed, Yseed, Zseed])
    mysection2.join(Xseed,Yseed)
    mysection2.join(Zseed,Yseed)

    mysection2.connectors()
    print(mysection2.is_connected())

