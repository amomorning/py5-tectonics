import momepy
import geopandas
from libpysal import graph
import random
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

profile = momepy.street_profile(streets, buildings)
print(profile.head(5))


# enclosures = momepy.enclosures(streets, limit=convex_hull)
enclosures = momepy.enclosures(streets)
print(enclosures.head(5))
tessellation = momepy.enclosed_tessellation(buildings, enclosures)


ax = enclosures.plot(figsize=(10, 10), color=gray)
tessellation.boundary.plot(ax=ax, color='black', )

buildings.plot(ax=ax, color='white')
streets.plot(ax=ax, color='black')
ax.set_axis_off()
plt.show()