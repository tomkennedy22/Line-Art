from PIL import Image, ImageDraw
import random
import datetime

total_loops = 50000
line_length = 30

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

    new_x = start_x
    new_y = start_y

    points = []

    while new_x != end_x or new_y != end_y:
        dist_x = end_x - new_x
        dist_y = end_y - new_y

        if dist_x == 0:
            step_x = 0
        elif dist_x < 0:
            step_x = -1
        elif dist_x > 0:
            step_x = 1

        if dist_y == 0:
            step_y = 0
        elif dist_y < 0:
            step_y = -1
        elif dist_y > 0:
            step_y = 1

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

    avg_color = (int(r_total / pixel_count), int(g_total/pixel_count), int(b_total/pixel_count), 32)

    return avg_color

def image_difference(image_a, image_b):
    pixels_a = list(image_a.getdata())
    pixels_b = list(image_b.getdata())

    total_difference = 0

    for pixel_index in range(0, len(pixels_a)):
        for color_slot in [0,1,2]:
            total_difference += abs(pixels_a[pixel_index][color_slot] - pixels_b[pixel_index][color_slot])

    return total_difference


file_name = 'bend1'
file_extension = 'jpeg'

with Image.open(f'{file_name}.{file_extension}') as original_image:
    print(original_image.size)
    # original_image.show()

    image_1 = Image.new('RGB', original_image.size)
    # image_2 = Image.new('RGB', original_image.size)

    image_1_draw = ImageDraw.Draw(image_1)
    # image_2_draw = ImageDraw.Draw(image_2)

    original_image_pixels = list(original_image.getdata())
    height, width = original_image.size
    original_image_pixel_map = pixel_list_to_nested_array(list(original_image.getdata()), original_image.size)

    for ind in range(0,total_loops):
        if ind % 1000 == 0:
            print(f'Looped {ind} times')

        coorindates = random_coordinates(image_1.size)
        points = line_points(coorindates)

        color = get_line_average_colors(points, original_image_pixel_map)

        image_1_draw.point(points, fill=color)


    image_1.show()
    original_image.show()

    current_dt = datetime.datetime.now()
    timestamp = current_dt.strftime("%Y%m%d%H%M%S")
    image_1.save(f'{file_name}_{timestamp}_line_{line_length}_iter_{total_loops}.{file_extension}', "JPEG")
