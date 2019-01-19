import networkx as nx


# A SECTION is a set of seeds
class Section(list):
    links = []
    connectors = []

    def __init__(self):
        return 
    
    # Definition. Given a section S, a "link" is any edge (v1,v2) where both 
    # v1 and v2 appear as germs of seeds in S. Two seeds are "connected"
    # when there is a link between them.
    # A link can be formed only when germ v1 has v2 as connector, and also
    # at the same time, the germ v2 has v1 as connector.
    def join(self, v1, v2):
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
            if (v1_seed, v2_seed) not in self.links:
                self.links.append((v1_seed, v2_seed))
            return True
        else:
            return False

    def __str__(self):
        return str([x for x in self])


    def find_seed(self, v1):
        for i in self:
            if v1 == i.germ:
                return i
        return None

    def seeds_connected(self, v1, v2):
        v1_seed = self.find_seed(v1)
        v2_seed = self.find_seed(v2)
        if (v1_seed, v2_seed) in self.links:
            return True
        else:
            return False

    # Definition. A CONNECTED SECTION, or a CONTIGUOUS SECTION is a section 
    # where every germ is connected to every other germ via a path through the edges.
    def connected(self):
        # Build a graph with nodes as elements in the SECTION and edges as links in the SECTION
        # and check for connectedness
        G = nx.Graph()
        [G.add_node(x) for x in self]
        [G.add_edges_from([x]) for x in self.links]
        return nx.is_connected(G)


# A SEED is a vertex and the set of edges that connect to it. That is, it is the pair (v,Ev) 
# where v is a single vertex, and Ev is a set of edges containing that vertex, i.e. that set 
# of edges having v as one or the other endpoint. The vertex v may be called the GERM of the 
# seed. For each edge in the edge set, the other vertex is called the CONNECTOR
class Seed:
    seed = None
    germ = None
    connectors = None

    def __init__(self, G, germ):
        self.germ = germ
        self.connectors = [x[1] for x in G.edges(self.germ)]

    def __str__(self):
        return 'seed: %s %s %s' % (self.germ, G.edges(), self.connectors)


def disjoint_section_from_graph(G):
    section = Section()
    for germ in G.nodes():
        H = nx.Graph()
        [H.add_edges_from([x]) for x in G.edges(germ)]
        section.append(Seed(H, germ))
    return section 

if __name__ == "__main__":
    G = nx.Graph()
    G.add_edge(1,2)
    G.add_edge(1,3)
    G.add_edge(1,4)
    G.add_edge(2,4)

    section = disjoint_section_from_graph(G)
    print(section.join(1,2))    # True
    print(section.join(2,3))    # False
    print(section.join(1,1))    # False since self loop not specified
    print(section.links)
    print(section.seeds_connected(1,2))
    print(section.seeds_connected(1,3))
    print('section connected', section.connected())

    section.join(1,3)
    section.join(1,4)
    section.join(2,4)
    print('section connected', section.connected())

