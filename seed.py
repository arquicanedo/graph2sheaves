import networkx as nx



class Section(list):
    connected_seeds = []

    def __init__(self):
        return 
    
    # Definition. Given a section S, a "link" is any edge (v1,v2) where both 
    # v1 and v2 appear as germs of seeds in S. Two seeds are "connected"
    # when there is a link between them.
    # A link can be formed only when germ v1 has v2 as connector, and also
    # at the same time, the germ v2 has v1 as connector.
    def link(self, v1, v2):
        v1_found = False
        v2_found = False
        v1_seed = None
        v2_seed = None
        for i in self:
            if v1 == i.germ and v2 in i.connectors:
                v1_found = True
                v1_seed = i
            if v2 == i.germ and v1 in i.connectors:
                v2_found = True
                v2_seed = i
        if v1_found and v2_found:
            if (v1_seed, v2_seed) not in self.connected_seeds:
                self.connected_seeds.append((v1_seed, v2_seed))
            return True
        else:
            return False

    def __str__(self):
        return str([x for x in self])


class Seed:
    seed = None
    germ = None
    connectors = None

    def __init__(self, G, germ):
        self.germ = germ
        self.connectors = [x[1] for x in G.edges(self.germ)]

    def __str__(self):
        return 'seed: %s %s %s' % (self.germ, G.edges(), self.connectors)


def enumerate_seeds(G):
    section = Section()
    for germ in G.nodes():
        H = nx.Graph()
        [H.add_edges_from([x]) for x in G.edges(germ)]
        section.append(Seed(H, germ))

    print(section)
    for i in section:
        print(i)



    return section 

if __name__ == "__main__":
    G = nx.Graph()
    G.add_edge(1,2)
    G.add_edge(1,3)
    G.add_edge(1,4)
    G.add_edge(2,4)

    section = enumerate_seeds(G)
    print(section.link(1,2))    # True
    print(section.link(2,3))    # False
    print(section.link(1,1))    # False since self loop not specified
    print(section.connected_seeds)
