#/usr/bin/env python
"""
Simple pedestrian model by jakob.erdmann@dlr.de
some code adapted from the pygame chimp-tutorial
"""
import os, pygame
from pygame.locals import *
import random

# constants
WIDTH = 9
YSIZE = 100
XMAX = 1300
GAP = 50
MAX_PEDS = 100
PROB = 0.2
PEDWIDTH = 20
PEDLENGTH = 30
ENTRYSPEED = 20
DEBUG = None
# global list of pedestrians
PEDS = []

#functions to create our resources
def load_image(name, colorkey=None):
    fullname = os.path.join(name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()


class Pedestrian(pygame.sprite.Sprite):
    index = 0
    """moves a pedstrian across the screen."""
    def __init__(self, lane):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.image, self.rect = load_image('chimp.bmp', -1)
        self.speed = random.randint(2,10)
        self.yspeed = random.randint(1,5)
        self.x = -ENTRYSPEED
        self.y = lane * YSIZE
        self.index = Pedestrian.index
        Pedestrian.index += 1
        self.rect.topleft = self.x, self.y

    def lane(self):
        return int(round(self.y / float(YSIZE)))

    def otherlane(self):
        offset = self.y - self.lane() * YSIZE
        if offset > (YSIZE - PEDWIDTH):
            return self.lane() + 1
        elif offset < -(YSIZE - PEDWIDTH):
            return self.lane() - 1
        else:
            return self.lane()

    def walk(self, leaders):
        vsafe = get_vsafe(leaders, self.x, self.speed, self.index)
        chosen = self.lane() 
        # disallow lanes which are to far away
        for i,v in enumerate(vsafe):
            if abs(i - chosen) > 1:
                vsafe[i] = -1 
        # select best lane if the current isn't best
        if vsafe[chosen] != self.speed:
            chosen = max([(v,i) for i,v in enumerate(vsafe)])[1]
        xspeed = min(vsafe[self.lane()], vsafe[self.otherlane()])
        # DEBUG
        if self.index == DEBUG:
            print "pos=%s,%s l=%s ol=%s chosen=%s xs=%s %s %s" % (
                    self.x, self.y, self.lane(), self.otherlane(), chosen,
                    xspeed, [(p.index, p.lane()) for p in leaders], vsafe)
        # y-move
        delta = (chosen * YSIZE) - self.y
        if delta > self.yspeed:
            delta = self.yspeed
        elif delta < -self.yspeed:
            delta = -self.yspeed
        # execute movement
        self.y += delta
        self.x += xspeed
        self.rect.topleft = self.x, self.y


def get_vsafe(leaders, x, vmax, index=None):
    vsafe = [vmax] * WIDTH
    for ped in leaders:
        if ped.index == index:
            continue # ignore self
        if ped.x > x:
            for l in [ped.lane(), ped.otherlane()]:
                vsafe[l] = min(vsafe[l], max(0, ped.x - x - GAP))
        elif ped.x + PEDLENGTH > x:
            for l in [ped.lane(), ped.otherlane()]:
                vsafe[l] = 0
    return vsafe

def freelanes(PEDS):
    PEDS.sort(key=sort_by_x)
    ENTRYSPEED
    vsafe = get_vsafe(PEDS[-WIDTH:], 0, ENTRYSPEED)
    return [i for i,v in enumerate(vsafe) if v == ENTRYSPEED]

def sort_by_x(p):
    return -p.x

def update(allsprites):
    if random.random() < PROB and len(PEDS) < MAX_PEDS:
        # insert new pedestrian
        lanes = freelanes(PEDS)
        if lanes:
            ped = Pedestrian(random.choice(lanes))
            PEDS.append(ped)
            allsprites.add(ped)
    # update
    PEDS.sort(key=sort_by_x)
    remove = []
    for i,p in enumerate(PEDS):
        p.walk(PEDS[max(0,i-WIDTH):i + WIDTH + 1])
        if p.x > XMAX:
            remove.append(p)
    for p in remove:
        PEDS.remove(p)
        allsprites.remove(p)
    allsprites.update()

def draw_text(background, text, x, y, color):
    if pygame.font:
        font = pygame.font.Font(None, 30)
        text = font.render(text, 1, color)
        textpos = text.get_rect(centerx=x, centery=y)
        background.blit(text, textpos)

def main():
    random.seed(42)
    pygame.init()
    screen = pygame.display.set_mode((XMAX, WIDTH*YSIZE))
    pygame.display.set_caption('Pedestrian Fever')
    pygame.mouse.set_visible(1)
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    clock = pygame.time.Clock()
    allsprites = pygame.sprite.RenderPlain()

#Main Loop
    stop = False
    while True:
        clock.tick(50)
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif (event.type == KEYDOWN and event.key == K_s or
                    event.type == MOUSEBUTTONDOWN):
                stop = not stop

        if not stop:
            update(allsprites)

        background.fill((250, 250, 250))
        screen.blit(background, (0, 0))
        allsprites.draw(screen)
        for p in PEDS:
            draw_text(screen, str(p.index), p.rect.center[0], p.rect.center[1], (255, 10, 10))
        draw_text(screen, str(len(PEDS)), XMAX - 50, 10, (10,255,10))
        pygame.display.flip()

if __name__ == '__main__': 
    main()

