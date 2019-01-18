import networkx as nx



class Section(set):
    links = []

    def __init__(self):
        return 
    
    def link(self, v1, v2):
        v1_found = False
        v2_found = False
        for i in self:
            if v1 == i.germ and v2 in i.connectors:
                v1_found = True
            if v2 == i.germ and v1 in i.connectors:
                v2_found = True

        if v1_found and v2_found:
            self.links.append((v1,v2))
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


    print(section.link(1,2))
    print(section.link(2,3))
    print(section.links)

    return section 

if __name__ == "__main__":
    G = nx.Graph()
    G.add_edge(1,2)
    G.add_edge(1,3)
    G.add_edge(1,4)
    G.add_edge(2,4)

    enumerate_seeds(G)
