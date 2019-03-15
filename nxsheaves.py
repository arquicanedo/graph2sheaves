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
            print('link can be created') 
            self.add_edge(src_seed, dst_seed)
            self.node[dst_seed]['connectors'].remove(src_seed)
            self.node[src_seed]['connectors'].remove(dst_seed)
        else:
            print('link cannot be created')
            
    def connectors(self):
        available_connectors = []
        for i in self.nodes():
            for connector in self.nodes[i]['connectors']:
                available_connectors.append((i,connector))

        print('Available connectors: ', available_connectors)
        print('Links: ', self.edges(data=True))


    def is_connected(self):
        return nx.is_connected(self)


def join_sections(section1, section2, seed1, seed2):
    if section1.is_connected() and section2.is_connected():
        new_section = nx.compose(section1, section2)
        new_section.add_link(seed1, seed2)
        if new_section.is_connected():
            return new_section
    return None

if __name__ == "__main__":
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

