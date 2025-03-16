import momepy
import geopandas
from libpysal import graph
import matplotlib.pyplot as plt
import osmnx as ox

center = (40.783169, -73.978315)
radius = 520
gray = (0.8, 0.8, 0.8)

def get_buildings(center, radius):
    gdf = ox.features_from_point(center, dist=radius, tags={"building": True})
    gdf_projected = ox.projection.project_gdf(gdf)
    buildings = gdf_projected[
        gdf_projected.geom_type.isin(["Polygon", "MultiPolygon"])
    ].reset_index()
    return buildings

def get_street_network(center, radius, network_type='drive'):
    streets_graph = ox.graph_from_point(center, dist=radius, network_type=network_type)
    streets_graph = ox.projection.project_graph(streets_graph)
    streets = ox.graph_to_gdfs(
        ox.convert.to_undirected(streets_graph),
        nodes=False,
        edges=True,
        node_geometry=False,
        fill_edge_geometry=True,
    )
    return streets

buildings = get_buildings(center, radius)
streets = get_street_network(center, radius)
convex_hull = streets.union_all().convex_hull


tessellation = momepy.morphological_tessellation(buildings)
enclosures = momepy.enclosures(streets)

# ax = blocks.plot()
ax = enclosures.plot(figsize=(10, 10), color=gray)
buildings.plot(ax=ax, color='white', edgecolor=gray)
streets.plot(ax=ax, color='black')
ax.set_axis_off()
plt.show()