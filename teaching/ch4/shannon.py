import momepy as mm
import geopandas as gpd
import matplotlib.pyplot as plt
from libpysal import graph

path = mm.datasets.get_path('bubenec')
buildings = gpd.read_file(path, layer='buildings')

tessellation = mm.morphological_tessellation(buildings)
G = graph.Graph.build_contiguity(tessellation).higher_order(k=1)
# G = graph.Graph.build_knn(buildings.centroid, k=5)
from mapclassify import classify
bins = classify(buildings.area, scheme='HeadTailBreaks').bins
print(bins)
print(mm.shannon_diversity(buildings.area, bins))
buildings['shannon'] = mm.shannon(buildings.area, G)

ax = tessellation.plot(color=(0.8, 0.8, 0.8), edgecolor='k', figsize=(10, 10))
# buildings.plot(ax=ax, color='w', alpha=0.7)

buildings.plot(ax=ax, column='shannon', legend=True)
G.plot(buildings, ax=ax, color='w')

ax.set_axis_off()
plt.show()
