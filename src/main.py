from Align_ras import align_rasters
from AOI_identify import identify_top_AOIs
import matplotlib.pyplot as plt
from rasterio.plot import show
import rasterio

def plot_raster(src, title):
    """
    Plots the raster using matplotlib.

    Args:
    - src: rasterio object to plot.
    - title: Title for the plot.
    """
    plt.figure(figsize=(8, 8))
    show(src)  # Display the raster data
    plt.title(title)
    plt.show()


def main():
    lst_raster = r'F:\InternshipWRI\Amsterdam_LST.tif'
    ndvi_raster = r'F:\InternshipWRI\Amsterdam_NDVI.tif'
    tree_height_raster = r'F:\InternshipWRI\Amsterdam_CanopyHeight.tif'
    target_crs = rasterio.crs.CRS.from_epsg(28992)


    lst_aligned, ndvi_aligned, tree_aligned, aligned_meta = align_rasters(lst_raster, ndvi_raster, tree_height_raster, target_crs)

    print("New Transform from Aligned Meta:")
    print(aligned_meta['transform'])

    # plot_raster(lst_aligned, "LST Raster")
    # plot_raster(ndvi_aligned, "NDVI Raster")
    # plot_raster(tree_aligned, "Tree Height Raster")

    # identify_top_AOIs(lst_aligned, ndvi_aligned, tree_aligned, aligned_meta)

    #result is: {'top_left': (1605940.0007625178, 8479385.865001518), 'bottom_right': (1607940.0007625178, 8481385.865001518)}
    #top 3 result is: {'top_left': (1605940.0007625178, 8479385.865001518), 'bottom_right': (1607940.0007625178, 8481385.865001518)},
    # {'top_left': (1603940.0007625178, 8477385.865001518), 'bottom_right': (1605940.0007625178, 8479385.865001518)},
    # {'top_left': (1601940.0007625178, 8477385.865001518), 'bottom_right': (1603940.0007625178, 8479385.865001518)}
if __name__ == "__main__":
    main()
