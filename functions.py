# takes input of (value, (minimum, maximum)) to clamp.
def clamp(value, val_range):
    if value < val_range[0]:    return val_range[0]
    if value > val_range[1]:    return val_range[1]
    return value

def get_average_vals(list_of_specimens):
    length = len(list_of_specimens)
    avg1 = 0; avg2 = 0; avg3 = 0; 
    for spec in list_of_specimens:
        avg1 += spec.trait_1
        avg2 += spec.trait_2
        avg3 += spec.trait_3
    avg1 = round(avg1/length, 2)
    avg2 = round(avg2/length, 2)
    avg3 = round(avg3/length, 2)
    return avg1, avg2, avg3

def find_best(list_of_specimens):
    best = list_of_specimens[0].food_eaten - list_of_specimens[0].food_needed
    best_spec = list_of_specimens[0]
    for spec in list_of_specimens:
        if spec.food_eaten - spec.food_needed > best:
            best = spec.food_eaten - spec.food_needed
            best_spec = spec
    return best_spec.trait_1, best_spec.trait_2, best_spec.trait_3, best

def circle_rect_is_colliding(circle_center, circle_radius, rect_center, rect_span):
    length = rect_span[0]/2
    height = rect_span[1]/2

    x_distance = abs(circle_center[0] - rect_center[0])
    y_distance = abs(circle_center[1] - rect_center[1])

    # if it is clearly outside of the shape
    if x_distance > (length + circle_radius):
        return False
    if y_distance > (height + circle_radius):
        return False
    
    # if it is clearly within the shape
    if x_distance <= length:
        return True 
    if y_distance <= height:
        return True

    # if at the corner, thinks of the corner as a circle and does a circle-circle collision.
    distance_from_corner_sqr = squared_distance((x_distance, y_distance), (length, height))
    
    return distance_from_corner_sqr <= (circle_radius*circle_radius)

def squared_distance(center1, center2):
    x_dif = center1[0] - center2[0]
    y_dif = center1[1] - center2[1]
    return (x_dif*x_dif) + (y_dif*y_dif)

def FPS_color(average_FPS):
    if average_FPS < 15:
        return (255, 0, 0)
    if average_FPS < 30:
        return (255, 255, 0)
    return (200, 200, 200)