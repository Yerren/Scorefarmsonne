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
* Sourced the tile images from [here](https://boardgamegeek.com/filepage/15609/base-tilespdf).
* Created a simple python script resize tile images all to a consistent size.
* Created segmentation maps. 
  * Initial segmentation maps generated using simple OpenCV image processing.
  * Manual refinement: just "quick and dirty" pass in Photoshop, as the segmentation maps don't need to be perfect for this task. Additionally, the blurriness of the images makes it difficult to define precise borders anyway.
  * Checked the refined segmentation maps for consistency: e.g., no overlaps or blank spots (aside from cloisters). 