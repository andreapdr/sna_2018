import networkx as nx
import json
import csv
import collections


def get_repo_user_dict(data):
    repo_dict = dict()
    for user, repoList in data.items():
        for repo in repoList:
            for repoName, val in repo.items():
                a = repo_dict.setdefault(repoName, set())
                # a.append((user, val["commits"]))
                # ho rimosso i pesi per semplicità
                a.add((user, ))

    return repo_dict


def get_coll_dict(repo_dict):
    coll_dict = dict()
    for repoName, userList in repo_dict.items():
        for user in userList:
            user_collaborators = coll_dict.setdefault(user[0], [])
            _userList = userList.copy()
            _userList.remove(user)
            for collaborator in _userList:
                user_collaborators.append(collaborator)

    return coll_dict


def create_network_from_json(coll_dict):
    graph = nx.Graph()
    for user, userList in coll_dict.items():
        graph.add_edges_from(([(user, collaborator) for collaborator in userList]))

    return graph


def create_network_from_csv(csvfile):
    graph = nx.Graph()
    with open(csvfile, "r") as csvfile:
        data_list = list(csv.reader(csvfile, delimiter=";"))
        for elem in data_list:
            graph.add_edge(elem[0], elem[1], weight=elem[2], language=elem[3])

    return graph


def create_csv(coll_dict):
    with open("testCSV.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=";", quotechar="|", quoting=csv.QUOTE_MINIMAL)
        for userName, collaboratorList in coll_dict.items():
            for collaborator in collaboratorList:
                writer.writerow([userName, collaborator[0]])


def define_max_component(graph):
    cc_comp = max(nx.connected_component_subgraphs(graph), key=len)

    return cc_comp


def centrality_analysis(graph):
    bet_cen = nx.betweenness_centrality(graph)
    edge_bet_cen = nx.edge_betweenness_centrality(graph)
    clo_cen = nx.closeness_centrality(graph)
    eig_cen = nx.eigenvector_centrality(graph)

    return bet_cen, edge_bet_cen, clo_cen, eig_cen


def get_sorted_dict(dictionary):
    sort_dict = sorted(dictionary.items(), key=lambda t: t[1], reverse=True)

    return sort_dict


def get_degree_dist(graph):
    degree = list(graph.degree())
    counter = collections.Counter(elem[1] for elem in degree)
    sorted_degree_distribution = counter.most_common()

    return sorted_degree_distribution


def generate_comparable_graphs(nodes, probability, min_degree):
    comparable_graphs = list()

    graph_ER = nx.fast_gnp_random_graph(nodes, probability, directed=False)
    graph_BA = nx.barabasi_albert_graph(nodes, int(min_degree), seed=None)

    comparable_graphs.append(graph_ER)
    comparable_graphs.append(graph_BA)

    return comparable_graphs


def run_analytical_task(graph):
    max_comp = define_max_component(graph)

    nodes = graph.number_of_nodes()
    edges = graph.number_of_edges()
    density = nx.density(graph)
    degree_centrality = nx.degree_centrality(graph)
    avg_degree = 2*edges/nodes
    con_components = nx.number_connected_components(graph)
    degree_dist = get_degree_dist(graph)

    avg_clustering_coef = nx.average_clustering(max_comp)
    bet_cen, edge_bet_cen, clo_cen, eig_cen = centrality_analysis(max_comp)
    diameter = nx.diameter(max_comp)
    # TODO: trovare come implementare in maniera proficua Shortest Path
    # magari implementare Average Path Length
    # shortest_path_length = nx.shortest_path_length(max_comp)

    print_results(nodes, edges, density, degree_dist, degree_centrality, avg_degree,
                  con_components, avg_clustering_coef, bet_cen, edge_bet_cen,
                  clo_cen, eig_cen, diameter)


def print_results(nodes, edges, density, degree_dist, degree_centrality, avg_degree,
                  con_components, avg_clustering_coef, bet_cen, edge_bet_cen,
                  clo_cen, eig_cen, diameter):
    print("--- Network Analysis:")
    print("Nodes: " + str(nodes))
    print("Edges: " + str(edges))
    print("Density: " + str(density))
    print("Max Degree: " + str(max(degree_dist)[0]))

    print("Degree Centrality: " + str(get_sorted_dict(degree_centrality)[:1]))
    print("Average Degree: " + str(avg_degree))
    print("Connected Components: " + str(con_components))

    print("\n")
    print("---Biggest Component Analysis:")
    print("Average Clustering Coefficient: " + str(avg_clustering_coef))
    print("Betweenness Centrality : " + str(get_sorted_dict(bet_cen)[:1]))
    print("Edge Betweenness Centrality : " + str(get_sorted_dict(edge_bet_cen)[:1]))
    print("Closeness Centrality : " + str(get_sorted_dict(clo_cen)[:1]))
    print("Eigenvector Centrality : " + str(get_sorted_dict(eig_cen)[:1]))
    print("Diameter: " + str(diameter))
    print("\n")


def generate_edgelist(comparable_graphs):
    nx.write_edgelist(comparable_graphs[0], "outER.csv", delimiter=";")
    nx.write_edgelist(comparable_graphs[1], "outBA.csv", delimiter=";")


def main():

    csvfile = "CSVlabel.csv"

    graph_crawled = create_network_from_csv(csvfile)

    nodes = graph_crawled.number_of_nodes()
    edges = graph_crawled.number_of_edges()

    edge_probability_ER = 2*edges/(nodes*(nodes-1))
    min_degree_BA = edges/nodes

    run_analytical_task(graph_crawled)

    comparable_graphs = generate_comparable_graphs(nodes, edge_probability_ER, min_degree_BA)

    for graph in comparable_graphs:
        # TODO: qui vorrei che stampasse al posto della riga il nome del network in analisi: tipo alla prima
        # iterazione Graph_ER, alla seconda Graph_BA (sono i nomi degli elementi nella lista comparable_graphs...)
        print("____________________________________________________________________________________")
        run_analytical_task(graph)

    generate_edgelist(comparable_graphs)


main()