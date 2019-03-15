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
    def __init__(self):
        self.seeds = []

    def add_seed(self, seed_germ, seed_connectors):
        self.seeds.append((seed_germ, seed_connectors))

    def projection(self, seed_germ):
        # set eliminates the need to check for duplicates
        connectors = set()
        for s in self.seeds:
            for c in s[1]:
                connectors.add(c)
        return seed_germ, list(connectors)


class StalkField():
    def __init__(self):
        self.stalks = []

    def add_stalk(self, stalk):
        self.stalks.append(stalk)

    def projection(self, projection_name):
        stalk_projections = []
        for count, stalk in enumerate(self.stalks):
            stalk_projections.append(stalk.projection(projection_name+str(count)))
        return stalk_projections


class Section(nx.Graph):
    def __init__(self):
        super().__init__()

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
    stalk = Stalk()
    stalk.add_seed('a', ['b','c'])
    stalk.add_seed('d', ['e','f','g','h'])
    print(stalk.seeds)
    print(stalk.projection('x'))

def test_stalkfield():
    stalk1 = Stalk()
    stalk1.add_seed('a', ['b','c'])
    stalk1.add_seed('d', ['e','f'])
    stalk2 = Stalk()
    stalk2.add_seed('x', ['y','z'])
    stalk2.add_seed('w', ['u','v'])
    stalkfield = StalkField()
    stalkfield.add_stalk(stalk1)
    stalkfield.add_stalk(stalk2)
    print(stalkfield.projection('foo'))

if __name__ == "__main__":
    #test_join_sections()
    #test_graph_quotient()
    #test_stalk()
    test_stalkfield()


