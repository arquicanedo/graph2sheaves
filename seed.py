import networkx as nx



class Section(set):
    def __init__(self):
        return 
    
    def links(self):
        for i in self:
            print(i)

    def __str__(self):
        return str([x for x in self])


class Seed:
    seed = None
    germ = None
    connectors = None

    def __init__(self, G, germ):
        self.G = G.copy()
        self.germ = germ
        self.connectors = [x[1] for x in self.G.edges(self.germ)]

    def __str__(self):
        return 'seed: %s %s %s' % (self.germ, self.G.edges(), self.connectors)


def enumerate_seeds(G):
    # TODO: consider changing list for Set if order is not important
    section = Section()
    for germ in G.nodes():
        H = nx.Graph()
        [H.add_edges_from([x]) for x in G.edges(germ)]
        section.add(Seed(H, germ))

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

    enumerate_seeds(G)
