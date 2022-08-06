from PIL import Image, ImageDraw
import random
import datetime
import sys

file_name = 'lion-1k'
file_extension = 'jpeg'

shift_amount = 0

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

def random_coordinates_from_list(size, line_length, pixel_list):
    get_coords = True
    while get_coords:
        starting_pixel = pixel_list.pop(0)[0]
        start_x = starting_pixel[1]
        start_y = starting_pixel[0]

        end_x = random.randint(start_x - line_length, start_x + line_length)
        end_x = min(max(0, end_x), size[0] - 1)

        dist_x = abs(end_x - start_x)

        # print('start_x', start_x, 'dist_x', dist_x, 'end_x', end_x, 'start_y', start_y, 'line_length', line_length)

        dist_y = int(((line_length ** 2) - (dist_x ** 2)) ** .5)

        if random.random() < .5:
            dist_y *= -1
            
        end_y = min(max(0, start_y + dist_y), size[1] - 1)

        if start_x != end_x or start_y != end_y:
            get_coords = False

    return (start_x, start_y, end_x, end_y)

def random_coordinates(size, line_length):

    get_coords = True
    while get_coords:
        start_x = random.randint(0, size[0] - 1)
        start_y = random.randint(0, size[1] - 1)


        end_x = random.randint(start_x - line_length, start_x + line_length)
        end_x = min(max(0, end_x), size[0] - 1)

        dist_x = abs(end_x - start_x)

        dist_y = int(((line_length ** 2) - (dist_x ** 2)) ** .5)

        if random.random() < .5:
            dist_y *= -1
            
        end_y = min(max(0, start_y + dist_y), size[1] - 1)

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

        step_x = int(dist_x / abs(dist_x)) if dist_x != 0 else 0
        step_y = int(dist_y / abs(dist_y)) if dist_y != 0 else 0

        if dist_y != 0 and abs(dist_x) > abs(dist_y):
            if random.random() < ((abs(dist_x) - abs(dist_y)) / abs(dist_y)):
                step_y = 0
        
        elif dist_x != 0 and dist_y > dist_x:
            if random.random() < ((abs(dist_y) - abs(dist_x)) / abs(dist_x)):
                step_x = 0

        if step_x !=0 or step_y != 0:
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

def validate_edge(mark, bound):
    return min(max(0, mark), bound-1)

def mutated_coordinates(coordinates, shift, size):

    return (validate_edge(coorindates[0] + shift, size[0]), validate_edge(coorindates[1] + shift, size[1]), coordinates[2], coordinates[3])

def get_all_colors(pixels, make_unique=True, color_flatten=1):
    colors = []
    for pixel in pixels:
        if color_flatten > 1:
            for color in pixel:
                color = int(int(color / color_flatten) * color_flatten)
        colors.append(pixel)

    if make_unique:
        colors = list(set(colors))
    return colors

def get_random_color(colors):
    return colors[int(random.random() * (len(colors) - 1))]

def pixel_difference_list(original_image_pixel_map, adjusted_image_pixel_map):

    pixel_difference = []

    for row_ind, row in enumerate(original_image_pixel_map):
        for col_ind, pixel in enumerate(row):
            original_color = original_image_pixel_map[row_ind][col_ind]
            adjusted_color = adjusted_image_pixel_map[row_ind][col_ind]
            color_diff = get_residual(original_color, adjusted_color)
            pixel_difference.append(((col_ind, row_ind), color_diff))

    # print('pixel_difference', pixel_difference[0:10])

    reverse_list = random.random() < .5

    return sorted(pixel_difference, key=lambda elem: elem[1], reverse=reverse_list)

def get_residual(color_a, color_b):
    return ((color_a[0] - color_b[0]) ** 2) +  ((color_a[1] - color_b[1]) ** 2) + ((color_a[2] - color_b[2]) ** 2)

def get_RMSE( n, rsum):
    # return the root mean squared error of the vector of residuals
    if (n != 0):
        return ((rsum / n) ** .5)

    return 0


def should_draw_line(original_image_pixel_map, adjusted_image_pixel_map, color, points):
    num_points = len(points)
    rsum_new = 0
    rsum_original = 0

    for point in points:
        original_color = original_image_pixel_map[point[1]][point[0]]
        adjusted_color = adjusted_image_pixel_map[point[1]][point[0]]

        rsum_new += get_residual(original_color, color)
        rsum_original += get_residual(original_color, adjusted_color)
        
    new_RMSE = get_RMSE(num_points, rsum_new)
    old_RMSE = get_RMSE(num_points, rsum_original)

    if (new_RMSE < (old_RMSE * 1.2)):
        return True
    else:
        return False

begin_dt = datetime.datetime.now()

with Image.open(f'input/{file_name}.{file_extension}') as original_image:
    print(original_image.size)

    image_1 = Image.new('RGB', original_image.size, (0,0,0))

    image_1_draw = ImageDraw.Draw(image_1)

    original_image_pixels = list(original_image.getdata())
    height, width = original_image.size
    # O(h * w)
    original_image_pixel_map = pixel_list_to_nested_array(original_image_pixels, (height, width))
    adjusted_image_pixel_map = pixel_list_to_nested_array(list(image_1.getdata()), (height, width))

    line_length = int( height * width / 100000)
    total_loops = int(height * width * .25)
    percent_size = total_loops / 100

    # O(h * w)
    all_colors = get_all_colors(original_image_pixels, make_unique=True, color_flatten=1)

    line_add_count = 0
    # O( h * w * 2)
    for ind in range(0,total_loops):
        if ind % (percent_size * 5) == 0:
            print(f'{int(ind/percent_size)}% complete')

        if ind % (percent_size) == 0:
            pixel_list = pixel_difference_list(original_image_pixel_map=original_image_pixel_map, adjusted_image_pixel_map=adjusted_image_pixel_map)

        # O( 1 )
        #coorindates = random_coordinates((height, width), line_length)
        coorindates = random_coordinates_from_list((height, width), line_length, pixel_list)
        # O( l )
        points = line_points(coorindates)

        # O( 1 )
        color = get_random_color(all_colors)

        # O( l )
        if should_draw_line(original_image_pixel_map = original_image_pixel_map, adjusted_image_pixel_map=adjusted_image_pixel_map, color=color, points=points):
            #image_1_draw.line(points, fill=color)
            line_add_count +=1
            # O( l )
            for point in points:
                adjusted_image_pixel_map[point[1]][point[0]] = color

    # O( h * w )
    for row_ind, row in enumerate(adjusted_image_pixel_map):
        for col_ind, color in enumerate(row):
            image_1_draw.point((col_ind, row_ind), fill=color)
    
    print(f'{line_add_count} of {total_loops} lines drawn. {line_add_count * 100.0 / total_loops}%')
    image_1 = image_1.resize((int(height/4) , int(width/4)), resample=Image.LANCZOS)
    image_1.show()

    end_dt = datetime.datetime.now()
    timestamp = end_dt.strftime("%Y%m%d%H%M%S")
    image_1.save(f'output/{file_name}_v5_{timestamp}_line_{line_length}_iter_{total_loops}.{file_extension}', "JPEG")
    seconds_elapsed = (end_dt - begin_dt).total_seconds()
    print(f'Program ran in {seconds_elapsed} seconds')
