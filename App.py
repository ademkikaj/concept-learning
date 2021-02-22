import networkx as nx
import matplotlib.pyplot as plt
from networkx.classes.graph import Graph
import pandas as pd
import itertools
from collections import OrderedDict


dataset = pd.read_csv("function1.csv")
# array = ["x1", "x2", "x3", "y"]


def distinct_values(dataset):
    dict = {}
    for column in dataset.columns[:-1]:
        dict[column] = list(OrderedDict.fromkeys((dataset[column].tolist())))
    return dict


def get_combinations(attributes):
    dict = {}
    for key, val in attributes.items():
        combination = []
        for k, v in attributes.items():
            if key != k:
                combination.append(k)
        dict[key] = combination
    return dict


def get_target_lookup(r, dataset):
    found = False
    target = None
    for index, row in dataset.iterrows():
        for key, val in r.items():
            if row[key] != val:
                found = False
                break
            else:
                found = True
        if found:
            return row[len(r)]
    return target


def get_concept_tables(combinations, attributes, dataset):
    dict_to_look = {}
    res = []
    matrix = []
    combination_matrix = {}
    list_for_cartesian = []
    for key, val in combinations.items():
        dict_to_look[key] = None
        for v in val:
            list_for_cartesian.append(attributes[v])
            dict_to_look[v] = None
        for v in attributes[key]:
            for elements in itertools.product(*list_for_cartesian):
                dict_to_look[key] = v
                for i in range(0, len(elements)):
                    dict_to_look[list(dict_to_look.keys())[i + 1]] = elements[i]
                res.append(get_target_lookup(dict_to_look, dataset))
            matrix.append(res)
            res = []

        combination_matrix[key] = matrix
        matrix = []
        list_for_cartesian = []
        dict_to_look.clear()
    return combination_matrix


def inverse(concept_input):
    my_len = len(concept_input[0])
    full_table = []
    for i in range(0, my_len):
        inverse_arr = []
        for arr in concept_input:
            inverse_arr.append(arr[i])
        full_table.append(inverse_arr)
    return full_table


def can_add_node(group):
    can_add = False
    for v in group:
        if v != None:
            return True
    return can_add


def build_graph(groups):
    G = nx.Graph()
    for group in groups:
        if can_add_node(group):
            G.add_node(tuple(group))
    return G


def is_incompatabile(n, m):
    incompatabile = False
    for i, v in enumerate(n):
        if n[i] != m[i] and n[i] != None and m[i] != None:
            return True
    return incompatabile


def build_edges(graph: Graph):
    for n in graph.nodes():
        for m in graph.nodes():
            if n != m:
                if is_incompatabile(n, m):
                    graph.add_edge(n, m)


def has_color(node):
    if len(node) == 0:
        return False
    return True


def find_color(color, graph, neigbors):
    neighbor_colors = []
    for neighbor in neigbors:
        if has_color(graph.nodes[neighbor]):
            neighbor_colors.append(graph.nodes[neighbor]["color"])
    unique_colors = list(set(color) - set(neighbor_colors))
    if len(unique_colors) == 0:
        if len(color) == 0:
            color.append(1)
        else:
            color.append(color[-1] + 1)
        return color[-1]
    else:
        return unique_colors[0]


def color_graph(graph: Graph):
    colors = []
    for node in graph.nodes():
        nx.set_node_attributes(
            graph, {node: find_color(colors, graph, graph.neighbors(node))}, "color"
        )


def get_cartesian(keys, attributes):
    list_of_attributes = []
    cartesian_product = []
    for key in keys:
        list_of_attributes.append(attributes[key])
    for element in itertools.product(*list_of_attributes):
        cartesian_product.append(element)
    return cartesian_product


def show_table(current, combinations, attributes, groups, i_groups, graph):
    cartesian_product = inverse(get_cartesian(combinations, attributes))
    list_concepts = []
    for i, attr in enumerate(combinations):
        print(
            "{} {} | {}".format(
                "  ",
                attr,
                " ".join(str(x).ljust(5) for x in cartesian_product[i]),
            )
        )
    print(current, "-------------------------------------------------")
    for i, attr in enumerate(attributes[current]):
        print(
            "{} | {}".format(
                attr.ljust(5), " ".join(str(x).ljust(5) for x in groups[i])
            )
        )
    print("--------------------------------------------------------")
    for group in i_groups:
        if can_add_node(group):
            list_concepts.append(graph.nodes[tuple(group)]["color"])
        else:
            list_concepts.append("-")
    print(
        "{} | {}".format("c".ljust(5), " ".join(str(x).ljust(5) for x in list_concepts))
    )


# tolook = {"x1": "med", "x2": "lo", "x3": "lo"}
# print(get_target_lookup(tolook, dataset))
attributes = distinct_values(dataset)
combinations = get_combinations(attributes)

# print(attributes)
# print(combinations)
concepts_inputs = get_concept_tables(combinations, attributes, dataset)

for key, val in concepts_inputs.items():
    # print(key, val)
    groups = inverse(val)
    graph = build_graph(groups)
    build_edges(graph)
    color_graph(graph)
    show_table(key, combinations[key], attributes, val, groups, graph)
    print("\n\n\n")
    labels = nx.get_node_attributes(graph, "color")
    nx.draw(graph, with_labels=True, labels=labels)
    plt.show()