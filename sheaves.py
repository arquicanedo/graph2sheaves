import networkx as nx
from itertools import combinations

# Utility functions

# Given a graph generate all possible seeds
def seeds_from_graph(G):
    seed_collection = []
    for v in G.nodes():
        atom = ATOM((v, v))
        seed = SEED(atom, [x for x in G.neighbors(v)])
        seed_collection.append(seed) 
    return seed_collection


# Definition. An OPEN SUBGRAPH U of a graph G is defined to be a section of G.
# Open subgraphs will always be subgraphs of the base space B
#
# This function makes sure that the claim holds true:
# Claim. There exists a functor F such that, for each open subgraph U of the base graph
# B, there exists some collection F(U) of sections above U
# This function is the functor F: graph(B) -> section(U)
def open_subgraph(G, nodes_in_section=None):
    seed_collection = []
    germs = nodes_in_section
    for v in germs:
        atom = ATOM((v,v))
        seed = SEED(atom, [x for x in G.neighbors(v)])
        seed_collection.append(seed)
    section = SECTION(seed_collection)
    section.connect()
    return section


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


    def copy(self):
        return SEED(self.germ, self.connectors)


# Typed seed
class SECTION:
    def __init__(self, seeds, links=None):
        self.seeds = []
        self.links = []
        [self.add_seed(x) for x in seeds]
        if links:
            [self.add_link(x) for x in links]

    def add_seed(self, seed):
        self.seeds.append(seed)
        return

    def add_link(self, link):
        self.links.append(link)
        return

    def __str__(self):
        return 'section: %s' % (self.seeds)

    def copy(self):
        return SECTION(self.seeds, self.links)

    def connect(self):
        print('Connecting section')
        for c in combinations(self.seeds, 2):
            self.join(c[0], c[1])


    # Join the list of pairs of seeds
    def join_from(self, pairs_of_seeds):
        for pair in pairs_of_seeds:
            self.join(pair[0], pair[1])
            print('Joining %s with %s' % (pair[0], pair[1]))

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

    def connectors(self):
        result = []
        for seed in self.seeds:
            available_connectors = []
            for j in seed.connectors:
                available_connectors.append(j)
            result.append((seed.germ, available_connectors))
        print('Available connectors: ', result)
        print('Links:', self.links)

# (semi) Definition:  two connected sections can be linked together to form a larger connected section
def join_sections(s1, s2, c1,  c2):
    new_section = None
    if s1.is_connected() and s2.is_connected():
        all_seeds = []
        [all_seeds.append(x) for x in s1.seeds]
        [all_seeds.append(x) for x in s2.seeds]

        all_links = []
        [all_links.append(x) for x in s1.links]
        [all_links.append(x) for x in s2.links]

        new_section = SECTION(all_seeds, all_links)
        new_section.join(c1, c2)
        
        if new_section.is_connected():
            return new_section

    return None
        
# Given a map \pi:E->B, where both E and B are collections of seeds,
# the STALK above b \in B is the set S of seeds in E such that for each s = (v,C_v) \in S,
# one has \pi(s) = b. The map \pi can be decomposed into a pair \pi = (\pi_g, \pi_c) such that,
# for every \gamma \in C_v one has that \pi(v,\gamma) = (\pi_g(v), \pi_c(\gamma)) such that
# \pi_c(\gamma) \in Cb. That is, \pi_g maps the germs of E to the germs of B and \pi_c maps the 
# connectors in E to specific connectors in B.
# Note: a Stalk is a stack of seeds
# Note: a Stalk consists of collection of seeds, a map, and the projection (a seed)
class STALK:
    def __init__(self, pi):
        self.E = pi.E
        self.map = pi
        self.B = pi.B

# The stalk field only has individual seeds up and down each stalk; the stalks are
# not linked to one-another. In the general case, the stalks are
# linked to one-another; 
class STALK_FIELD:
    def __init__(self, stalk_collection):
        self.stalks = stalk_collection 
        self.projection = []
        for stalk in stalk_collection:
            self.projection.append(stalk.B)
        self.section = SECTION(self.projection)

# The target of \pi is a graph quotient \pi : E -> B
class MAP():
    def __init__(self, E_seeds):
        # The assumption is that all map to a single node
        B_connectors = []
        for e in E_seeds:
            for connector in e.connectors:
                if connector not in B_connectors:
                    B_connectors.append(connector)
        X = ATOM(('X', 'x'))
        self.E = E_seeds
        self.B = SEED(X, B_connectors)

def test_section_composition():
    A = ATOM(('A','a'))
    B = ATOM(('B','b'))
    C = ATOM(('C','c'))
    Aseed = SEED(A, ['b'])
    Bseed = SEED(B, ['a', 'c'])
    Cseed = SEED(C, ['b', 'x'])
    mysection = SECTION([Aseed, Bseed, Cseed])
    mysection.join(Aseed, Bseed)
    mysection.join(Bseed, Cseed)
 
    print('------------------')
    X = ATOM(('X','x'))
    Y = ATOM(('Y','y'))
    Z = ATOM(('Z','z'))
    Xseed = SEED(X, ['y', 'c'])
    Yseed = SEED(Y, ['x', 'z'])
    Zseed = SEED(Z, ['y'])
    mysection2 = SECTION([Xseed, Yseed, Zseed])
    mysection2.join(Xseed,Yseed)
    mysection2.join(Zseed,Yseed)

    #print(mysection2.is_connected())
    mysection.connectors()
    mysection2.connectors()

    print(mysection.is_connected())
    print(mysection2.is_connected())

    foo = join_sections(mysection, mysection2, Cseed, Xseed)
    print(foo.is_connected())


def test_stalks():
    A = ATOM(('A','a'))
    B = ATOM(('B','b'))
    C = ATOM(('C','c'))
    D = ATOM(('D','d'))
    Aseed = SEED(A, ['b', 'c'])
    Bseed = SEED(B, ['a', 'd'])
    Cseed = SEED(C, ['a', 'd'])
    Dseed = SEED(D, ['b', 'c'])

    mystalk = STALK(MAP([Bseed, Cseed]))
    print(mystalk.map)
    print(mystalk.E)
    print(mystalk.B)


def test_stalk_field():
    A = ATOM(('A','a'))
    B = ATOM(('B','b'))
    C = ATOM(('C','c'))
    D = ATOM(('D','d'))
    E = ATOM(('E','e'))
    Aseed = SEED(A, ['a1', 'a2', 'a3'])
    Bseed = SEED(B, ['b1', 'b2', 'b3'])
    Cseed = SEED(C, ['c1', 'c2', 'c3'])
    Dseed = SEED(D, ['d1', 'd2'])
    Eseed = SEED(E, ['e1', 'e2'])

    stalk1 = STALK(MAP([Aseed, Bseed]))
    stalk2 = STALK(MAP([Cseed]))
    stalk3 = STALK(MAP([Dseed, Eseed]))

    print(stalk1.B)
    print(stalk2.B)
    print(stalk3.B)

    stalk_field = STALK_FIELD([stalk1, stalk2, stalk3])
    print(stalk_field.projection)
    print(stalk_field.section)



def test_open_subgraphs():
    G = nx.Graph()
    G.add_edges_from([('A','B'), ('A','C'), ('B','D'), ('B','E'), ('D','E')])
    seeds = seeds_from_graph(G)
    #print(*seeds)

    section = open_subgraph(G, ['A','B'])
    for s in section.seeds:
        print(s)
    print(section.is_connected())

if __name__ == "__main__":
    #test_section_composition()
    #test_stalks()
    #test_stalk_field()
    test_open_subgraphs()
