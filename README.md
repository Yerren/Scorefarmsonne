# Scorefarmsonne
This is a living file documenting the progress of using image recognition to automate the scoring of farms in the board game Carcassonne.

# The Plan:
1. Find and clean images of the base game (for now) tiles.
2. Add matching segmentation maps to the tile images.
3. Tag each edge of each tile to indicate what regions they're connected to.
4. Create a Blender scene to generate synthetic training data.
5. Train models.
    * One-pass image segmentation.
    * One-pass tile classification.
    * Multi-pass tile classification (first approximate the locations of each tile, and then pass these to a second model for classification).
  
# 1. Creating Assets
* Sourced the tile images from [here](https://boardgamegeek.com/filepage/15609/base-tilespdf).
* Created a simple python script resize tile images all to a consistent size.
* Created segmentation maps. 
  * Initial segmentation maps generated using simple OpenCV image processing.
  * Manual refinement: just "quick and dirty" pass in Photoshop, as the segmentation maps don't need to be perfect for this task. Additionally, the blurriness of the images makes it difficult to define precise borders anyway.
  * Checked the refined segmentation maps for consistency: e.g., no overlaps or blank spots (aside from cloisters).
  * Sample segmentation maps:
    * <img src="https://github.com/Yerren/Scorefarmsonne/blob/main/raw_images_v2/CRRF_000_3.png?raw=true" height="100" /> <img src="https://github.com/Yerren/Scorefarmsonne/blob/main/seg_maps_refined/CRRF_000_3_road_mask.png?raw=true" height="100" /> <img src="https://github.com/Yerren/Scorefarmsonne/blob/main/seg_maps_refined/CRRF_000_3_city_mask.png?raw=true" height="100" /> <img src="https://github.com/Yerren/Scorefarmsonne/blob/main/seg_maps_refined/CRRF_000_3_grass_mask.png?raw=true" height="100" />
    
# 2. Tagging Tiles
* The goal is to tag the edge of each tile such that we can determine which regions are connected.
  * We want to do this for cities and fields - and we'll do roads while we are at it.
* Cities and roads are simple, as there can only be one relevant item on each edge of the tile. Fields, however, can be split in half by roads.
  * Therefore, for fields, we will have two tags for each tile edge.
  * We will always start with the top edge (or top-left for fields) and then continue clockwise. We will tag connected regions with the same number, starting from 0. -1 will indicate that the terrain type isn't applicable. 
  * Consider the following example:
    * <img src="https://github.com/Yerren/Scorefarmsonne/blob/main/example_images/CFRR_000_3_edge_tag_example_city.png?raw=true" height="100" /> <img src="https://github.com/Yerren/Scorefarmsonne/blob/main/example_images/CFRR_000_3_edge_tag_example_road.png?raw=true" height="100" /> <img src="https://github.com/Yerren/Scorefarmsonne/blob/main/example_images/CFRR_000_3_edge_tag_example_grass.png?raw=true" height="100" />
* While we could automate this using the segmentation maps, it's easy enough to do this by hand. We'll save the tags in a CSV file.

# 3. Blender Scene
* To create synthetic scenes, we first need to create two types of Blender objects:
  1. Tiles - just a simple, thin cuboid on to which we can apply the tile textures.
  2. Meeples - used a [base model by CoralineDIY](https://www.thingiverse.com/thing:3910021), and set up a matt colour. Later, can look into adding a procedural wooden texture.
* Next, we need a script to create the board.
  * The basic structure for this is as follows:
    1. Keep track of the board state using arrays. These are somewhat inefficiently initialized to be just large enough to store the entire set of tiles if they were placed in a straight line in any direction (this could certainly be optimized).
       1. Where tiles are currently placed.
       2. Valid placement locations for future tiles.
       3. The surrounding edge types for each valid placement location.
    2. Place the pre-set starting tile in the centre of the board.
    3. Shuffle the remaining tiles into a queue.
    4. Pop a tile from the queue, and check in which of the current valid placement locations it can be placed (reshuffle the queue if there are no valid locations). That is to say, for each of the valid placement locations, see if it matches all the edges currently surrounding that location (and store which orientations were valid).
    5. Select one of the possible valid placement locations (and corresponding orientation), weighted by whether that location will add on to an existing city (most likely), road, or field (least likely). The weighting loosely reflects a real game, where players are more likely to extend cities than roads (and both are more likely than fields).
    6. Update the board state arrays, and place the tile in Blender.
  * Sample rendered boards:
       * <img src="https://github.com/Yerren/Scorefarmsonne/blob/main/blender_files/rendered_scene_1.png?raw=true" height="200" /> <img src="https://github.com/Yerren/Scorefarmsonne/blob/main/blender_files/rendered_scene_1.png?raw=true" height="200" />
  * TODO: Add Meeple placement.
