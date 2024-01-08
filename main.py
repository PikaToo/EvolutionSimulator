import pygame
import sys
from pygame.locals import *     # used for keys and events
from levels import world
from random import randint
from functions import get_average_vals, circle_rect_is_colliding, squared_distance, clamp, FPS_color, find_best

# Game set up
pygame.init()
FPS = 240
fpsClock = pygame.time.Clock()
window_width = 1200
window_height = 600
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Evolution Simulator')
icon = pygame.Surface((20, 20))
pygame.display.set_icon(icon)

# initializing font for later use
pygame.font.init()
font = pygame.font.SysFont('arial', 40)
m_font = pygame.font.SysFont('arial', 25)

# used for get FPS
tick = pygame.time.Clock()

# list of entities/platforms/specimens to track them all
entities = []
platforms = []
specimens = []
foods = []


class Entity(object):
    def __init__(self, x, y, width, height, color, type):
        self.rect = pygame.Rect(x, y, width, height)
        entities.append(self)
        self.color = color
        self.type = type
    def delete_self(self):
        entities.remove(self)
        if self.type == "Platform":
            platforms.remove(self)
        if self.type == "Specimen":
            specimens.remove(self)
        if self.type == "Food":
            foods.remove(self)
        del self 
    def draw(self):
        pygame.draw.rect(window, self.color, self.rect)

class Platform(Entity):
    def __init__(self, x, y, color):
        super().__init__(x, y, 30, 30, color, "Platform")
        platforms.append(self)

class Food(Entity):
    def __init__(self, x, y, radius, color):
        super().__init__(x, y, radius, radius, color, "Food")
        foods.append(self)
    def draw(self):
        pygame.draw.circle(window, self.color, self.rect.center, self.rect.width)

class Specimen(Entity):
    def __init__(self, x, y, color, t1, t2, t3):
        super().__init__(x, y, 20 + (t3/10), 20 + (t3/10), color, "Specimen")
        specimens.append(self)

        self.y_vel = 0
        self.x_vel = 0
        
        self.speed = round((0.2 + round(t1/250, 1)), 1)             # trait 1 affects speed (and food lost per frame)
        self.terminal_velocity = 5 + (t1/50)

        self.food_needed = self.rect.w*self.rect.h/160                         # trait 3 affects size and food needed
        self.food_eaten = 0

        self.home_pos = (x, y)

        self.trait_1 = t1
        self.trait_2 = t2
        self.trait_3 = t3

    def move(self):

        # sees which food to chase
        best_score = 99999999
        movement_point = self.rect.x, self.rect.y

        for edible in foods:

            ed_distance_squared = squared_distance(edible.rect.center, self.rect.center)

            score = (ed_distance_squared)**0.5                       # higher score (worse) if farther
            score -= 2*self.trait_2*(edible.rect.w)**2            # trait 2 decides selectiveness for big food

            if score < best_score:
                movement_point = edible.rect.center
                best_score = score
            
            if circle_rect_is_colliding(edible.rect.center, edible.rect.w, self.rect.center, (self.rect.w, self.rect.h)):
                edible.delete_self()
                self.food_eaten += (edible.rect.w*edible.rect.w/30)
                break
        
        # loss of food over time
        self.food_eaten -= (2**(self.speed/10))/50  

        # moving to point
        if self.rect.center[0] < movement_point[0]:
            self.x_vel += self.speed
        if self.rect.center[0] > movement_point[0]:
            self.x_vel -= self.speed
        if self.rect.center[1] < movement_point[1]:
            self.y_vel += self.speed
        if self.rect.center[1] > movement_point[1]:
            self.y_vel -= self.speed
        
        # friction
        if self.x_vel > 0:
            self.x_vel -= 0.1
        elif self.x_vel < 0:
            self.x_vel += 0.1
        if self.y_vel > 0:
            self.y_vel -= 0.1
        elif self.y_vel < 0:
            self.y_vel += 0.1
        
        self.x_vel = clamp(self.x_vel, (-self.terminal_velocity, self.terminal_velocity))   # y-terminal velocity
        self.y_vel = clamp(self.y_vel, (-self.terminal_velocity, self.terminal_velocity))   # y-terminal velocity
                
        self.collide(0, self.y_vel)          # separate collisions for x and y
        self.collide(self.x_vel, 0)

    def collide(self, x, y):
        self.rect.y += y
        self.rect.x += x

        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if x > 0:
                    self.rect.right = plat.rect.left
                    self.x_vel = 0
                elif x < 0:
                    self.rect.left = plat.rect.right
                    self.x_vel = 0
                if y > 0:
                    self.rect.bottom = plat.rect.top
                    self.y_vel = 0
                elif y < 0:
                    self.rect.top = plat.rect.bottom
            
    def reset_pos(self):
        self.rect.x = self.home_pos[0]
        self.rect.y = self.home_pos[1]
        self.x_vel = 0
        self.y_vel = 0

def generate_level(level):
    # deleting all platforms, need to first make a list of them or it doesn't work for some reason
    plat_to_del = [x for x in platforms]
    for plat in plat_to_del:
        plat.delete_self()
    # adding new platforms
    x = 0
    y = 0
    for row in level:
        for value in row:
            if value == "W":                                # wall
                Platform(x, y, (255, 255, 255))
            x += 30
        x = 0
        y += 30

def main():
    # only uses level 0- a blank walled-in area; could easily change level, though
    level = 0
    generate_level(world[level])

    previous_backspace = False
    show_FPS = False
    FPS_list = [60, 60, 60, 60]

    timer = 0

    # initializing objects
    for i in range(0, 11):
        trait_1 = randint(0, 100)
        trait_2 = randint(0, 100)
        trait_3 = randint(0, 100)
        color = (int(trait_1*255/100), int(trait_2*255/100), 0)
        Specimen(30 + (i*110), 50, color, trait_1, trait_2, trait_3)
    avg1, avg2, avg3 = get_average_vals(specimens)
    b_1, b_2, b_3, most_food = "x", "x", "x", 0
    wr_1, wr_2, wr_3, world_most_food = b_1, b_2, b_3, -999999
    for i in range(0, 5):
        Food(randint(50, 1150), randint(100, 550), randint(5, 10), (randint(0, 255), randint(0, 255), randint(0, 255)))


    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        window.fill((0, 0, 0))
        timer += 1

        # timer things
        if timer % 25 == 0:     # making food
            Food(randint(60, 1140), randint(100, 550), randint(1, 14), (randint(0, 255), randint(0, 255), randint(0, 255)))
        if timer > 600:        # new cycle
            b_1, b_2, b_3, best_food_eaten = find_best(specimens)
            if best_food_eaten > world_most_food:
                wr_1, wr_2, wr_3, world_most_food = b_1, b_2, b_3, best_food_eaten

            timer = 0
            survived = []
            
            for spec in specimens:                      # getting survivors
                if spec.food_eaten > spec.food_needed:
                    survived.append(spec)
            
            to_del = [x for x in specimens]             # deleting all, can't do in same loop as above
            for sp in to_del:                           # or doesn't work.
                sp.delete_self()
            
            if len(survived) == 0:                      # getting random vals if none
                for i in range(0, 11):
                    trait_1 = randint(0, 100)
                    trait_2 = randint(0, 100)
                    trait_3 = randint(0, 100)
                    color = (int(trait_1*255/100), int(trait_2*255/100), 0)
                    Specimen(30 + (i*110), 50, color, trait_1, trait_2, trait_3)

            else:    
                old_list_len = len(survived)
                while len(survived) < 11:                     # expanding list with children until filled
                    spec = survived[randint(0, old_list_len-1)]
                    trait_1 = clamp(spec.trait_1 + randint(-10, 10), (0, 100))
                    trait_2 = clamp(spec.trait_2 + randint(-10, 10), (0, 100))
                    trait_3 = clamp(spec.trait_3 + randint(-10, 10), (0, 100))
                    color = (int(trait_1*255/100), int(trait_2*255/100), 0)
                    survived.append(survived[randint(0, len(survived)-1)])
                
                for i, spec in enumerate(survived):         # all species then get varied a little
                    spec = survived[randint(0, len(survived)-1)]
                    trait_1 = clamp(spec.trait_1 + randint(-5, 5), (0, 100))
                    trait_2 = clamp(spec.trait_2 + randint(-5, 5), (0, 100))
                    trait_3 = clamp(spec.trait_3 + randint(-5, 5), (0, 100))
                    color = (int(trait_1*255/100), int(trait_2*255/100), 0)
                    Specimen(30 + (i*110), 50, color, trait_1, trait_2, trait_3)
            
            avg1, avg2, avg3 = get_average_vals(specimens)

        # drawing the entities
        for ent in entities:
            ent.draw()

        # moving specimens and seeing if passed
        for spec in specimens:
            spec.move()
        
        # drawing text
        window.blit(m_font.render(f"Average:", True, (0, 0, 0)), pygame.Rect(10, 2, 0, 0))
        window.blit(m_font.render(f"1 - Speed: {avg1}", True, (200, 0, 0)), pygame.Rect(100, 2, 0, 0))
        window.blit(m_font.render(f"2 - Selectiveness: {avg2}", True, (0, 200, 0)), pygame.Rect(270, 2, 0, 0))
        window.blit(m_font.render(f"3 - Size: {avg3}", True, (80, 80, 80)), pygame.Rect(510, 2, 0, 0))
        window.blit(m_font.render(f"Seconds Elapsed: {round(timer/60, 2)}", True, (100, 100, 100)), pygame.Rect(680, 2, 0, 0))


        window.blit(m_font.render(f"Best Specimen (last generation):", True, (0, 0, 0)), pygame.Rect(10, 570, 0, 0))
        window.blit(m_font.render(f"{b_1}", True, (200, 0, 0)), pygame.Rect(350, 570, 0, 0))
        window.blit(m_font.render(f"{b_2}", True, (0, 200, 0)), pygame.Rect(400, 570, 0, 0))
        window.blit(m_font.render(f"{b_3}", True, (80, 80, 80)), pygame.Rect(450, 570, 0, 0))

        window.blit(m_font.render(f"Best Specimen (all generations):", True, (0, 0, 0)), pygame.Rect(610, 570, 0, 0))
        window.blit(m_font.render(f"{wr_1}", True, (200, 0, 0)), pygame.Rect(950, 570, 0, 0))
        window.blit(m_font.render(f"{wr_2}", True, (0, 200, 0)), pygame.Rect(1000, 570, 0, 0))
        window.blit(m_font.render(f"{wr_3}", True, (80, 80, 80)), pygame.Rect(1050, 570, 0, 0))


        # seeing FPS
        if pygame.key.get_pressed()[K_BACKSPACE]:
            if previous_backspace == False:
                if show_FPS:      
                    show_FPS = False
                else:
                    show_FPS = True
            previous_backspace = True
        else:
            previous_backspace = False

        tick.tick()                                 # doing this calculation even when not using it so that
        FPS_list.append(int(tick.get_fps()))        # the FPS displayed when it is shown is more accurate
        del FPS_list[0]
        average_FPS = sum(FPS_list) / len(FPS_list)

        if show_FPS:
            window.blit(m_font.render(f"FPS: {average_FPS}", True, FPS_color(average_FPS)), pygame.Rect(1100, 2, 0, 0))

        # making game run
        fpsClock.tick(FPS)
        pygame.display.update()


if __name__ == "__main__":
    main()
