import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import networkx as nx
import matplotlib.pyplot as plt

# Вставьте свои данные
vk_token = "user_token" # Замените "user_token" на Ваш токен
username = 'user_name' # Замените 'user_name' на имя пользователя
node_colors = []

# Инициализация API
vk_session = vk_api.VkApi(token=vk_token)
vk = vk_session.get_api()
user_id = vk.users.get(user_ids=username)[0]['id'] 

# Получение друзей пользователя
friends = vk.friends.get(user_id=user_id, count=15)["items"]

def build_graph(user_id):
  #Строит граф друзей и друзей друзей
  graph = nx.Graph()
  graph.add_node(user_id) # Добавление пользователя в граф

  # Добавление друзей пользователя в граф
  for friend_id in friends:
    graph.add_node(friend_id)
    graph.add_edge(user_id, friend_id, weight=1) # Добавление веса 1

  # Получение друзей друзей
  for friend_id in friends:
    try:
      friends_of_friend = vk.friends.get(user_id=friend_id, count=15)["items"]
      for friend_of_friend_id in friends_of_friend:
        if friend_of_friend_id not in graph.nodes:
          graph.add_node(friend_of_friend_id)
        graph.add_edge(friend_id, friend_of_friend_id, weight=1) # Добавление веса 1
    except vk_api.exceptions.ApiError as e:
      print(f"Ошибка при получении друзей пользователя {friend_id}: {e}")

  return graph

# Построение графа
graph = build_graph(user_id)

# Подсчет центральности
betweenness_centrality = nx.betweenness_centrality(graph)
closeness_centrality = nx.closeness_centrality(graph)
eigenvector_centrality = nx.eigenvector_centrality(graph)

# Вывод результатов
print("Центральность по посредничеству:")
for node, centrality in betweenness_centrality.items():
  print(f"Пользователь {node}: {centrality}")

print("\nЦентральность по близости:")
for node, centrality in closeness_centrality.items():
  print(f"Пользователь {node}: {centrality}")

print("\nЦентральность собственного вектора:")
for node, centrality in eigenvector_centrality.items():
  print(f"Пользователь {node}: {centrality}")

# Визуализация графа
plt.figure(figsize=(8, 8)) # Установка размера изображения
pos = nx.shell_layout(graph)

# Используйте алгоритм пружинно-электрической компоновки для уточнения расположения узлов
pos = nx.spring_layout(graph, pos=pos, k=0.9, iterations=50)

# Определение цвета узлов
for node in graph.nodes:
 if node == user_id:
  node_colors.append("red") # Пользователь - красный
 elif node in friends:
  node_colors.append("green") # Друзья - зеленый
 else:
  node_colors.append("pink") # Друзья друзей - розовый

# Отрисовка графа
nx.draw(graph, pos, with_labels=True, node_color=node_colors, node_size=100, font_size=3, font_weight="bold") 

# Цвет ребер при определенных условиях
friend_edges = [(u, v) for u, v in graph.edges if u in friends and v in friends]
other_edges = [(u, v) for u, v in graph.edges if u not in friends or v not in friends]

common_friend_edges = []
for u, v in friend_edges:
  common_friends = set(graph.neighbors(u)) & set(graph.neighbors(v))
  if len(common_friends) > 0:
    common_friend_edges.append((u, v))

# Увеличение толщины ребер для связей между друзьями
# Отрисовка ребер
nx.draw_networkx_edges(graph, pos, edgelist=other_edges, width=1, edge_color='grey')
nx.draw_networkx_edges(graph, pos, edgelist=common_friend_edges, width=1.5, edge_color='yellow')

# Добавление легенды
legend_handles = [
  plt.Line2D([0], [0], marker='o', color='w', label='Пользователь', markerfacecolor='red', markersize=8),
  plt.Line2D([0], [0], marker='o', color='w', label='Друг', markerfacecolor='green', markersize=8),
  plt.Line2D([0], [0], marker='o', color='w', label='Друг друга', markerfacecolor='pink', markersize=8),
  plt.Line2D([0], [0], marker='o', color='w', label='Общий друг', markerfacecolor='yellow', markersize=8),
]
plt.legend(handles=legend_handles, loc='upper right', fontsize=10)

# Установка заголовка графа
plt.title("Граф друзей и друзей друзей (ограничение 15)", fontsize=16, fontweight="bold")

# Отображение графика
plt.show()