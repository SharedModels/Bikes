import networkx as nx
import pandas as pd
import os
import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from mpl_toolkits.basemap import Basemap


def combine_csvs(filepath):
    csv_list = []
    for root, dirs, files in os.walk(filepath):
        for file in files:
            if file.endswith(".csv"):
                csv_list.append(pd.read_csv(file))
    return pd.concat(csv_list, axis=0).sort_values('timestamp')


def build_base_graph(df):
    graph = nx.Graph()
    graph.add_nodes_from(list(df))
    return graph


def create_list_sizes(df):
    max_bikes = df.max()
    bike_size = []
    df.apply(lambda x: bike_size.append((x / max_bikes).tolist()), axis=1)
    return bike_size


def dock_positions():
    with open('metadata.json') as f:
        data = json.load(f)

    position_dict = {}
    for key, value in data.items():
        position_dict[key] = (value['Long'], value['Lat'])

    return position_dict


# def update_bikes(i):
#     graph = build_base_graph(a)
#     return nx.draw_networkx(graph, pos=dock_pos, node_size=[j * 20 for j in list_sizes[i]], with_labels=False)

def update_bikes(i):
    nodes.set_sizes(sizes=[j * 20 for j in list_sizes[i]])
    # nodes.set_label(time_stamp_list[i])
    fig.suptitle(time_stamp_list[i])
    # fig.set_label(time_stamp_list[i])
    return nodes, fig


a = pd.read_csv('test7bikes_present_3.csv', index_col=0)
a = a.dropna(axis=1)
time_stamp_list = a.timestamp.tolist()

dock_pos = dock_positions()

remove_cols = [i for i in list(a) if i not in dock_pos.keys()]
a = a.drop(remove_cols, axis=1)

list_sizes = create_list_sizes(a)
graph = build_base_graph(a)

fig = plt.figure()
fig.suptitle(time_stamp_list[0])
m = Basemap(llcrnrlon=-0.25, llcrnrlat=51.4, urcrnrlon=0, urcrnrlat=51.56)
m.readshapefile('Areas', 'areas')

nodes = nx.draw_networkx_nodes(graph, label='hello', pos=dock_pos, node_size=[j * 20 for j in list_sizes[0]])

anim = FuncAnimation(fig, update_bikes, frames=np.arange(0, a.shape[0]), interval=200, repeat=True)
# plt.show()
anim.save('test7bikes_present_3.gif', dpi=80, writer='imagemagick')



# a = pd.read_csv('bikes_present.csv', index_col=0)
# a = a.dropna(axis=1)
#
# dock_pos = dock_positions()
#
# remove_cols = [i for i in list(a) if i not in dock_pos.keys()]
# a = a.drop(remove_cols, axis=1)
#
# list_sizes = create_list_sizes(a)
#
# fig = plt.figure()
# anim = FuncAnimation(fig, update_bikes, frames=np.arange(0, a.shape[0]), interval=200)
# # plt.show()
# anim.save('line.gif', dpi=80, writer='imagemagick')

# nx.draw_networkx(graph, pos=dock_pos, node_size=[i * 30 for i in list_sizes[0]], with_labels=False)
# plt.show()
