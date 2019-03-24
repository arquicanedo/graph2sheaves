import networkx as nx
from itertools import combinations


# Given a networkx graph generate all possible seeds
def seeds_from_graph(G):
    germs = []
    connectors = []
    for v in G.nodes():
        germs.append(v)
        connectors.append([x for x in G.neighbors(v)])
    return germs, connectors


# (semi) Definition:  two connected sections can be linked together to form a larger connected section
def join_sections(section1, section2, seed1, seed2):
    if section1.is_connected() and section2.is_connected():
        new_section = nx.compose(section1, section2)
        new_section.add_link(seed1, seed2)
        if new_section.is_connected():
            return new_section
    return None


# An open subgraph U of a graph G is defined to be a section of G. 
# Germs are kept. Alternative would be to provide germs to trim.
def open_subgraph(G, germs=None):
    section = Section()
    for v in germs:
        section.add_seed(v, list(G.neighbors(v)))
    section.connect()
    print('open subgraph: %s links %s' % (section.germs(data=True), section.edges()))
    #print(section.is_connected())
    return section

# A collection {Ui} of open subgraphs is an open cover for an open subgraph U 
# if the union of all the Ui contain U.
def open_cover(U, Ui):
    assert isinstance(Ui, list)
    union = Section()
    sheaf = Sheaf()
    [sheaf.add_section(x) for x in Ui]
    for v in U.germs():
        proj_germ, proj_connectors = sheaf.pierce(v)
        union.add_seed(proj_germ, proj_connectors)
    #print(union.connectors())
    union.connect()
    #print(union.connectors())
    return union, nx.is_isomorphic(U, union)




def section_from_text(text):
    tokens = text.split()
    section = Section()
    for count, token in enumerate(tokens):
        if count == 0:
            section.add_seed(tokens[count], [tokens[count+1]])
        elif count < len(tokens)-1:
            section.add_seed(tokens[count], [tokens[count-1], tokens[count+1]])
        else:
            section.add_seed(tokens[count], [tokens[count-1]])
    section.connect()
    return section

def section_quotient(section, seeds, target):
    new_section = section.copy()
    q_connectors = []
    # Add the new seed
    new_section.add_seed(target, q_connectors)
    # Remove seeds from section in the list
    new_section.remove_nodes_from(seeds)
    # Collect all connectors from nodes
    for s in seeds:
        for neighbor in section.neighbors(s):
            if neighbor not in q_connectors:
                q_connectors.append(neighbor)
    print(q_connectors)
    # Add connectors to the projected node
    for i in q_connectors:
        new_section.node[i]['connectors'].append(target)
    # Link the dangling connectors
    new_section.connect()
    return new_section


class Stalk():
    def __init__(self, p_germ):
        self.seeds = []
        self.projected_germ = p_germ
        self.seed_map = []

    def add_seed(self, seed_germ, seed_connectors):
        self.seeds.append((seed_germ, seed_connectors))

    # Append germ and connectors to stalk's seeds, and map germ to section
    def add_seed_map(self, seed_germ, seed_connectors, section):
        self.seeds.append((seed_germ, seed_connectors))
        self.seed_map.append(section)

    def projection(self):
        # set eliminates the need to check for duplicates
        connectors = set()
        for s in self.seeds:
            for c in s[1]:
                connectors.add(c)
        return self.projected_germ, list(connectors)
    
    def is_empty(self):
        if not self.seeds:
            return True
        else:
            return False

# The stalk field only has individuals seeds up and down each stalk; the stalks are not linked to one-another.
class StalkField():
    def __init__(self):
        self.stalks = []

    def add_stalk(self, stalk):
        self.stalks.append(stalk)

    def projection(self):
        stalk_projections = []
        for count, stalk in enumerate(self.stalks):
            stalk_projections.append(stalk.projection())
        return stalk_projections


class Section(nx.Graph):
    def __init__(self):
        super().__init__()
        self.germs = self.nodes

    def __str__(self):
        return str(id(self))

    def add_seed(self, seed_germ, seed_connectors):
        self.add_node(seed_germ, connectors=seed_connectors)

    def add_link(self, src_seed, dst_seed):
        ta = tb = False
        src_type = src_seed
        dst_type = dst_seed
        if src_type in self.node[dst_seed]['connectors']:
            ta = True
        if dst_type in self.node[src_seed]['connectors']:
            tb = True
        if ta and tb:
            #print('link can be created') 
            self.add_edge(src_seed, dst_seed)
            self.node[dst_seed]['connectors'].remove(src_seed)
            self.node[src_seed]['connectors'].remove(dst_seed)
        else:
            #print('link cannot be created')
            pass

    def add_links_from(self, link_list):
        for link in link_list:
            self.add_link(link[0], link[1])
            
    def connectors(self):
        available_connectors = []
        for i in self.nodes():
            for connector in self.nodes[i]['connectors']:
                available_connectors.append((i,connector))

        print('Available connectors: ', available_connectors)
        print('Links: ', self.edges(data=True))

    def is_connected(self):
        return nx.is_connected(self)

    def connect(self):
        for c in combinations(self.nodes(), 2):
            self.add_link(c[0], c[1])

    # Query for a seed. If exists return the germ and connectors
    def get_seed(self, seed):
        if self.has_node(seed):
            germ = seed
            all_connectors = set()
            for i in self.get_neighbors(germ):
                all_connectors.add(i)
            for i in self.get_open_connectors(germ):
                all_connectors.add(i)
            return germ, list(all_connectors)
        return None, None

    # Returns open connectors for germ
    def get_open_connectors(self, germ):
        if self.has_node(germ):
            connectors = self.germs[germ]['connectors']
            return connectors
        return None

    # Returns neighbors for germ
    def get_neighbors(self, germ):
        if self.has_node(germ):
            connectors = [x for x in self.neighbors(germ)]
            return connectors
        return None

    # Build a graph from the section
    def build_graph(self):
        G = nx.Graph()
        G.add_nodes_from(self.nodes())
        G.add_edges_from(self.edges())
        return G

class Sheaf():
    def __init__(self):
        self.stalks = []
        self.stalkfields = []
        self.sections = []

    def add_stalk(self, stalk):
        self.stalks.append(stalk)

    def add_stalkfield(self, stalkfield):
        self.stalkfields.append(stalkfield)

    def add_section(self, section):
        self.sections.append(section)

    def add_sections_from(self, sections):
        for s in sections:
            self.add_section(s)

    def pierce(self, key):
        stalk = Stalk(key)
        for layer, s in enumerate(self.sections):
            germ, connectors = s.get_seed(key)
            if germ:
                #stalk.add_seed(germ, connectors)
                stalk.add_seed_map(germ, connectors, s)
                print('Pierce found key=%s in section layer=%s section=%s' % (key, layer, id(s)))
        if not stalk.is_empty():
            self.add_stalk(stalk)
        print('Stalk of key=(%s) projection=%s' % (stalk.projection()))
        print('Stalk map count = %s' % (len(stalk.seed_map)))
        return stalk.projection()

    def germs(self):
        all_germs = set()
        for s in self.sections:
            for g in s.germs():
                all_germs.add(g)
        return all_germs

    def pierce_all_sections(self):
        all_germs = self.germs()
        union = Section()
        for v in all_germs:
            union.add_seed(*self.pierce(v))
        union.connect()
        return union



def test_join_sections():
    sec1 = Section()
    sec1.add_seed('a',['b','c'])
    sec1.add_seed('b',['a'])
    sec1.add_link('a', 'b')
    sec1.connectors()

    sec2 = Section()
    sec2.add_seed('c', ['d','a'])
    sec2.add_seed('d', ['c'])
    sec2.add_link('c','d')
    sec2.connectors()

    sec3 = join_sections(sec2, sec1, 'c', 'a')
    sec3.connectors()


def test_graph_quotient():
    sec = Section()
    sec.add_seed('a', ['b','c','d'])
    sec.add_seed('b', ['a','e'])
    sec.add_seed('c', ['a','e'])
    sec.add_seed('d', ['a','e'])
    sec.add_seed('e', ['b','c','d'])
    sec.add_links_from([('a','b'),  ('a','c'), ('a','d'), ('e','b'), ('e','c'), ('e', 'd')])
    quotient = section_quotient(sec, ['b','c','d'], 'x')
    quotient.connectors()

def test_stalk():
    stalk = Stalk('x')
    stalk.add_seed('a', ['b','c'])
    stalk.add_seed('d', ['e','f','g','h'])
    print(stalk.seeds)
    print(stalk.projection())

def test_stalkfield():
    stalk1 = Stalk('foo')
    stalk1.add_seed('a', ['b','c'])
    stalk1.add_seed('d', ['e','f'])
    stalk2 = Stalk('bar')
    stalk2.add_seed('x', ['y','z'])
    stalk2.add_seed('w', ['u','v'])
    stalk3 = Stalk('zar')
    stalk3.add_seed('m', ['n', 'o'])
    stalkfield = StalkField()
    stalkfield.add_stalk(stalk1)
    stalkfield.add_stalk(stalk2)
    stalkfield.add_stalk(stalk3)
    print(stalkfield.projection())


def test_sheaf():
    sheaf = Sheaf()
    section1 = section_from_text('fly like a butterfly')
    section2 = section_from_text('airplanes that fly')
    section3 = section_from_text('fly fishing')
    section4 = section_from_text('fly away home')
    section5 = section_from_text('fly ash in concrete')
    section6 = section_from_text('when sparks fly')
    section7 = section_from_text('lets fly a kite')
    section8 = section_from_text('learn to fly helicopters')
    sheaf.add_sections_from([section1, section2, section3, section4, section5, section6, section7, section8])
    sheaf.pierce('fly')
    sheaf.pierce('a')
    print(len(sheaf.sections))
    print(len(sheaf.stalks))

def test_open_subgraph():
    G = nx.Graph()
    G.add_edges_from([('a','b'), ('a','c'), ('b','c'), ('b','d'), ('c','d')])
    
    section = open_subgraph(G, ['b','c'])
    section = open_subgraph(G, ['a','d'])
    section = open_subgraph(G, ['a','b'])
    section = open_subgraph(G, ['a','b','c','d'])

    # Claim: res_{U,U}:F(U)->F(U) is the identity of F(U)
    section = open_subgraph(G, ['a'])

    # Claim: For a sequence of open subgraphs the restrictions compose 
    H = open_subgraph(G, ['a', 'c', 'd']).build_graph()
    print(H.nodes(), H.edges())
    I = open_subgraph(H, ['a', 'd']).build_graph()
    print(I.nodes(), I.edges())


def test_open_cover():
    G = nx.Graph()
    G.add_edges_from([('a','b'), ('a','c'), ('b','c'), ('b','d'), ('c','d')])
    os_original = open_subgraph(G, ['a','b','c','d'])
    os1 = open_subgraph(G, ['a','b'])
    os2 = open_subgraph(G, ['b','c'])
    print(open_cover(os_original, [os1, os2]))
    os3 = open_subgraph(G, ['d'])
    print(open_cover(os_original, [os1, os2, os3]))
    print(open_cover(os_original, [os_original]))


def test_sheaf_from_sections():

    sheaf = Sheaf()
    section1 = section_from_text('fly like a butterfly')
    section2 = section_from_text('airplanes that fly')
    section3 = section_from_text('fly fishing')
    section4 = section_from_text('fly away home')
    section5 = section_from_text('fly ash in concrete')
    section6 = section_from_text('when sparks fly')
    section7 = section_from_text('lets fly a kite')
    section8 = section_from_text('learn to fly helicopters')
    sheaf.add_sections_from([section1, section2, section3, section4, section5, section6, section7, section8])
    sheaf_projection = sheaf.pierce_all_sections()
    print(sheaf_projection.connectors())



if __name__ == "__main__":
    #test_join_sections()
    #test_graph_quotient()
    #test_stalk()
    #test_stalkfield()
    #test_sheaf()
    #test_open_subgraph()
    #test_open_cover()
    test_sheaf_from_sections()


