# Scorefarmsonne
This is a living file documenting the progress of using image recognition to automate the scoring of farms in the board game Carcassonne.

# The Plan:
1. Find and clean images of the base game (for now) tiles.
2. Add matching segmentation maps to the tile images.
3. Create a Blender scene to generate synthetic training data.
4. Train models.
    * One-pass image segmentation.
    * One-pass tile classification.
    * Multi-pass tile classification (first approximate the locations of each tile, and then pass these to a second model for classification).
  
# 1. Creating Assets
* Sourced the tile images from [here](https://wikicarpedia.com/car/Tile_Reference_(1st_edition)).
