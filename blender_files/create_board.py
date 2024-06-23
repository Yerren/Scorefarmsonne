import numpy as np
import pandas as pd
from math import radians
from enum import Enum
import random

BASE_PATH = "C:/Users/45Red1/Scorefarmsonne"
IMAGE_PATH = "cropped_images_v2"
TILE_DETAILS_PATH = "edge_tags.csv"
TOTAL_NUM_TILES = 72

IN_BLENDER = True

if IN_BLENDER:
    import bpy
    from mathutils import Vector


class EdgeType(Enum):
    CITY = 1
    ROAD = 2
    GRASS = 3


def check_if_add_to_placements(pos_in):
    if current_placements[pos_in]:
        return False
    return not(pos_in[0] < 0 or pos_in[0] > TOTAL_NUM_TILES * 2 - 1 or pos_in[1] < 0 or pos_in[1] > TOTAL_NUM_TILES * 2 - 1)


def check_if_valid_placement(chosen_placement_location, edges_in):
    if not valid_placements[chosen_placement_location]:
        return False

    # I think this is checking the wrong side of the edge
    for index, edge in enumerate(edges_in):
        if current_edges[chosen_placement_location][index] != 0 and current_edges[chosen_placement_location][index] != edge:
            return False

    return True


def try_update_board_state(chosen_placement_location, edges_in):
    # Sanity check:
    # if not check_if_valid_placement(chosen_placement_location, edges_in):
    #     return False

    valid_placements[chosen_placement_location] = False
    current_placements[chosen_placement_location] = True

    # Expand potential locations
    expand_pos = (chosen_placement_location[0] - 1, chosen_placement_location[1])
    if check_if_add_to_placements(expand_pos):
        valid_placements[expand_pos] = True
        current_edges[expand_pos][2] = edges_in[0]

    expand_pos = (chosen_placement_location[0] + 1, chosen_placement_location[1])
    if check_if_add_to_placements(expand_pos):
        valid_placements[expand_pos] = True
        current_edges[expand_pos][0] = edges_in[2]

    expand_pos = (chosen_placement_location[0], chosen_placement_location[1] - 1)
    if check_if_add_to_placements(expand_pos):
        valid_placements[expand_pos] = True
        current_edges[expand_pos][1] = edges_in[3]

    expand_pos = (chosen_placement_location[0], chosen_placement_location[1] + 1)
    if check_if_add_to_placements(expand_pos):
        valid_placements[expand_pos] = True
        current_edges[expand_pos][3] = edges_in[1]

    # Set edges
    current_edges[chosen_placement_location] = np.zeros(4)

    return True

def chose_placement_location(edges_in, city_weight=10, road_weight=5, grass_weight=1):
    edges_in_rolled = np.vstack((edges_in, np.roll(edges_in, 1), np.roll(edges_in, 2), np.roll(edges_in, 3)))
    potential_placements = np.where(valid_placements)
    valid_potential_placements = []
    edge_val_list = []
    valid_potential_rotations_list = []
    for potential_row, potential_col in zip(potential_placements[0], potential_placements[1]):
        potential_placement_edges = current_edges[potential_row, potential_col]
        matched_edges = np.any((edges_in_rolled - potential_placement_edges) * potential_placement_edges, axis=1)
        edge_array = np.zeros(3)
        valid_potential_rotations = np.where(matched_edges == 0)[0]
        if valid_potential_rotations.any():
            valid_potential_placements.append((potential_row, potential_col))
            valid_potential_rotations_list.append(valid_potential_rotations)

            edge_vals = np.unique(potential_placement_edges)
            edge_vals = edge_vals[edge_vals.nonzero()]
            edge_array[edge_vals - 1] = 1
            edge_val_list.append(edge_array)

    edge_val_array = np.array(edge_val_list)
    if not edge_val_array.any():
        return None, None

    # rotation_value = (chosen_edge_location[-1] - selected_edge_index) % 4
    possible_edges = np.where(edge_val_array.any(axis=0))[0]
    weight_array = np.array([city_weight, road_weight, grass_weight])
    weight_array = weight_array[possible_edges]
    selected_edge_type = np.random.choice(possible_edges, p=weight_array / weight_array.sum())

    potential_indices = np.where(edge_val_array[:, selected_edge_type])[0]
    chosen_placement_index = np.random.choice(potential_indices)
    chosen_placement = valid_potential_placements[chosen_placement_index]

    valid_potential_rotations_array = valid_potential_rotations_list[chosen_placement_index]
    chosen_rotation = np.random.choice(valid_potential_rotations_array)

    return chosen_placement, chosen_rotation


def place_tile(first_tile=False):
    while True:
        chosen_tile = tile_queue_list[0]

        # Tile edges
        city_edges = chosen_tile[2:6]
        road_edges = chosen_tile[6:10]
        dummy_grass_edges = np.zeros_like(road_edges)
        combined_edges = np.vstack((city_edges, road_edges, dummy_grass_edges))
        combined_edges = combined_edges.argmax(axis=0) + 1

        if first_tile:
            chosen_placement_location = (TOTAL_NUM_TILES - 1, TOTAL_NUM_TILES - 1)
            rotation_value = 0
        else:
            chosen_placement_location, rotation_value = chose_placement_location(combined_edges)
            if chosen_placement_location is None:
                # Tile could not be placed, so reshuffle queue
                random.shuffle(tile_queue_list)
                continue

        combined_edges = np.roll(combined_edges, rotation_value)

        if try_update_board_state(chosen_placement_location, combined_edges):
            break
        else:
            print("Invalid placement attempted.")
            exit(1)
        
    tile_queue_list.pop(0)

    if not IN_BLENDER:
        return

    # Create copy of base tile
    src_tile = bpy.data.objects["Base_Tile"]
    new_tile = src_tile.copy()
    new_tile.data = src_tile.data.copy()
    new_tile.animation_data_clear()
    new_tile.hide_render = False
    bpy.data.collections.get("Tile_Collection").objects.link(new_tile)
    
    # Set position of new tile
    blender_x = chosen_placement_location[1] - TOTAL_NUM_TILES + 1
    blender_y = TOTAL_NUM_TILES - chosen_placement_location[0] - 1
    blender_rotation_value = (4 - rotation_value) % 4
    
    new_pos = Vector((blender_x, blender_y, 0))
    new_pos *= 0.045 / bpy.data.scenes["Scene"].unit_settings.scale_length
    new_tile.location = new_pos
    
    # Placeholder: set random rotation
    new_tile.rotation_euler[2] = radians(blender_rotation_value * 90)
    
    # Set tile texture
    tile_material_obj = bpy.data.materials.new(new_tile.name + '-Material')
    tile_material_obj.use_nodes = True
    
    bsdf = tile_material_obj.node_tree.nodes["Principled BSDF"]
    texImage = tile_material_obj.node_tree.nodes.new('ShaderNodeTexImage')
    
    texImage.image = bpy.data.images.load(f"{BASE_PATH}/{IMAGE_PATH}/{chosen_tile[0]}.png")
    tile_material_obj.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
    new_tile.data.materials.append(tile_material_obj)
    
    new_tile.active_material_index = 2

    bpy.context.view_layer.objects.active = new_tile

    # toggle to edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    # make sure face select mode is enabled
    bpy.context.tool_settings.mesh_select_mode = [False, False, True]
    
    bpy.ops.object.vertex_group_select()
    
    # assign the material
    bpy.ops.object.material_slot_assign()

    # toggle to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return chosen_placement_location


def remove_all_tiles():
    collection = bpy.data.collections.get("Tile_Collection")
    for obj in collection.objects:
        # Unlink the object from the collection
        collection.objects.unlink(obj)
        # Delete the object
        bpy.data.objects.remove(obj, do_unlink=True)


tile_details = pd.read_csv(f"{BASE_PATH}/{TILE_DETAILS_PATH}")

reps = 1
TOTAL_NUM_TILES *= reps

tile_queue = np.zeros((TOTAL_NUM_TILES, tile_details.shape[1]), dtype=object)

count = 0
start_tile = None
for row in tile_details.to_numpy():
    for i in range(row[1] * reps):
        if start_tile is None and row[0] == "CRFR_000_4":
            # Hold out one copy of the starting tile
            start_tile = row

        tile_queue[count] = row
        count += 1


np.random.shuffle(tile_queue)
tile_queue_list = list(tile_queue)
tile_queue_list.insert(0, start_tile)

current_placements = np.zeros((TOTAL_NUM_TILES*2-1, TOTAL_NUM_TILES*2-1), dtype=bool)
valid_placements = np.zeros((TOTAL_NUM_TILES*2-1, TOTAL_NUM_TILES*2-1), dtype=bool)
valid_placements[TOTAL_NUM_TILES - 1, TOTAL_NUM_TILES - 1] = True
current_edges = np.zeros((TOTAL_NUM_TILES*2-1, TOTAL_NUM_TILES*2-1, 4), dtype=int)

#if True:
#    if IN_BLENDER:
#        remove_all_tiles()

#    place_tile(first_tile=True)
#    for _ in range(TOTAL_NUM_TILES - 1):
#       place_tile()
#else:
#    place_tile()

remove_all_tiles()
