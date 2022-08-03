from PIL import Image, ImageDraw
import random
import datetime

total_loops = 1000000
line_length = 10

file_name = 'starry-night'
file_extension = 'jpeg'


def pixel_list_to_nested_array(pixel_list, size):
    
    height = size[0]
    pixels = []
    pixel_row = []
    for pixel_ind, pixel in enumerate(pixel_list):
        if pixel_ind % height == 0:
            if len(pixels) > 0 or len(pixel_row) > 0:
                pixels.append(pixel_row)
            pixel_row = []

        pixel_row.append(pixel)

    pixels.append(pixel_row)
    return pixels

def random_coordinates(size):

    get_coords = True
    while get_coords:
        start_x = random.randint(0, size[0] - 1)
        start_y = random.randint(0, size[1] - 1)

        min_x = max(0, start_x - line_length)
        max_x = min(start_x+line_length, size[0] - 1)

        min_y = max(0, start_y - line_length)
        max_y = min(start_y+line_length, size[1] - 1)

        end_x = random.randint(min_x, max_x)
        end_y = random.randint(min_y, max_y)

        if start_x != end_x or start_y != end_y:
            get_coords = False


    return (start_x, start_y, end_x, end_y)

def line_points(coordinates):
    start_x, start_y, end_x, end_y = coordinates

    orig_dist_x = end_x - start_x
    orig_dist_y = end_y - start_y

    new_x = start_x
    new_y = start_y

    points = []

    while new_x != end_x or new_y != end_y:
        dist_x = end_x - new_x
        dist_y = end_y - new_y

        step_x = int(dist_x / abs(dist_x)) if dist_x != 0 else 0
        step_y = int(dist_y / abs(dist_y)) if dist_y != 0 else 0


        if dist_y == 0:
            step_y = 0
        else:
            offset_ratio = abs(dist_x) * 1.0 / abs(dist_y)
            if offset_ratio > 1.0:
                offset_ratio -= 1
                if random.random() < offset_ratio:
                    step_y = 0
            elif offset_ratio < 1.0:
                offset_ratio = 1 - offset_ratio
                if random.random() < offset_ratio:
                    step_x = 0

        new_x = new_x + step_x
        new_y = new_y + step_y
        points.append((new_x, new_y))

    return points

def get_line_average_colors(line_points, pixels):


    r_total = 0
    g_total = 0
    b_total = 0
    pixel_count = len(line_points)
    for coordinate in line_points:
        x = coordinate[0]
        y = coordinate[1]
        pixel = pixels[y][x]
    
        r_total += pixel[0]
        g_total += pixel[1]
        b_total += pixel[2]

    avg_color = (int(r_total / pixel_count), int(g_total/pixel_count), int(b_total/pixel_count))

    return avg_color

def image_difference(image_a, image_b):
    pixels_a = list(image_a.getdata())
    pixels_b = list(image_b.getdata())

    total_difference = 0

    for pixel_index in range(0, len(pixels_a)):
        for color_slot in [0,1,2]:
            total_difference += abs(pixels_a[pixel_index][color_slot] - pixels_b[pixel_index][color_slot])

    return total_difference

def melt_color(point, color, pixels):
    base_color = pixels[point[1]][point[0]]
    r = int((color[0] + base_color[0]) / 2)
    g = int((color[1] + base_color[1]) / 2)
    b = int((color[2] + base_color[2]) / 2)
    return (r,g,b)

def set_color_to_map(point, point_color, pixels):
    pixels[point[1]][point[0]] = point_color

with Image.open(f'input/{file_name}.{file_extension}') as original_image:
    print(original_image.size)

    image_1 = Image.new('RGB', original_image.size, (0,0,0))

    image_1_draw = ImageDraw.Draw(image_1)

    original_image_pixels = list(original_image.getdata())
    height, width = original_image.size
    original_image_pixel_map = pixel_list_to_nested_array(list(original_image.getdata()), original_image.size)
    adjusted_image_pixel_map = pixel_list_to_nested_array(list(image_1.getdata()), image_1.size)

    percent_size = total_loops / 100
    for ind in range(0,total_loops):
        if ind % percent_size == 0:
            print(f'{int(ind/percent_size)}% complete')

        coorindates = random_coordinates(image_1.size)
        points = line_points(coorindates)

        color = get_line_average_colors(points, original_image_pixel_map)

        for point in points:
            point_color = melt_color(point, color, adjusted_image_pixel_map)
            set_color_to_map(point, point_color, adjusted_image_pixel_map)
                     
            image_1_draw.point(point, fill=point_color)

    image_1.show()

    current_dt = datetime.datetime.now()
    timestamp = current_dt.strftime("%Y%m%d%H%M%S")
    image_1.save(f'output/{file_name}_v3_{timestamp}_line_{line_length}_iter_{total_loops}.{file_extension}', "JPEG")
