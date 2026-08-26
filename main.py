import pygame
import random
import math
import sys

# PYGAME INIT
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)
gameScore = 0

# SOUND INIT
laserShoot = pygame.mixer.Sound("Audio/laserShoot.wav")
explosionRock = pygame.mixer.Sound("Audio/explosion_rock.wav")
explosionShip = pygame.mixer.Sound("Audio/explosion.wav")
restartSound = pygame.mixer.Sound("Audio/Restart.wav")

# COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# STARSHIP (PLAYER) CLASS
class Ship:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.angle = 0
        self.speed = 0
        self.alive = True
        self.image = pygame.Surface((40, 60), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, WHITE, [(20, 0), (0, 60), (40, 60)])
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def reset(self):
        self.__init__()

    def update(self, keys):
        if not self.alive:
            return

        # ROTATION
        if keys[pygame.K_LEFT]:
            self.angle += 5
        if keys[pygame.K_RIGHT]:
            self.angle -= 5

        # MOVE FORWARD
        if keys[pygame.K_UP]:
            self.speed += 0.2
        else:
            self.speed *= 0.98

        # MOVEMENT CALCULATION
        rad = math.radians(self.angle)
        self.x += -self.speed * math.sin(rad)
        self.y += -self.speed * math.cos(rad)

        # WRAP AROUND SCREEN
        self.x %= WIDTH
        self.y %= HEIGHT

        self.rect.center = (self.x, self.y)

    def draw(self, surface):
        rotated = pygame.transform.rotate(self.image, self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rect.topleft)


# BULLET CLASS
class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 10
        self.lifetime = 60  # frames

    def update(self):
        rad = math.radians(self.angle)
        self.x += -self.speed * math.sin(rad)
        self.y += -self.speed * math.cos(rad)
        self.x %= WIDTH
        self.y %= HEIGHT
        self.lifetime -= 1

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 3)


# ASTEROID CLASS
class Asteroid:
    def __init__(self, x=None, y=None, size=None):
        self.x = x if x is not None else random.randint(0, WIDTH)
        self.y = y if y is not None else random.randint(0, HEIGHT)
        self.size = size if size is not None else random.randint(30, 60)
        self.angle = random.uniform(0, 360)
        self.speed = random.uniform(1, 3)
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE, (self.size//2, self.size//2), self.size//2, 2)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self):
        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.speed
        self.y += math.sin(rad) * self.speed
        self.x %= WIDTH
        self.y %= HEIGHT
        self.rect.center = (self.x, self.y)

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)


# GAME RESET FUNCTION
def reset_game():
    global ship, bullets, asteroids, game_over
    ship = Ship()
    bullets = []
    asteroids = [Asteroid() for _ in range(5)]
    game_over = False


# GAME INIT
reset_game()

# GAME LOOP
while True:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if not game_over and event.key == pygame.K_SPACE and ship.alive:
                bullets.append(Bullet(ship.x, ship.y, ship.angle))
                laserShoot.play()
            if game_over and event.key == pygame.K_r:
                reset_game()
                restartSound.play()
                gameScore = 0

    if not game_over:
        # UPDATE OBJECTS
        ship.update(keys)
        for b in bullets[:]:
            b.update()
            if b.lifetime <= 0:
                bullets.remove(b)
        for a in asteroids:
            a.update()

        # BULLET AND ASTEROID COLLISIONS
        for b in bullets[:]:
            for a in asteroids[:]:
                if a.rect.collidepoint(b.x, b.y):
                    bullets.remove(b)
                    asteroids.remove(a)
                    explosionRock.play()
                    gameScore += 1

                    print("Score: ", gameScore)
                    # Split asteroid if big enough
                    if a.size > 30:
                        for _ in range(2):
                            new_a = Asteroid(a.x, a.y, a.size // 2)
                            asteroids.append(new_a)
                    break

        # SHIP vs ASTEROID COLLISION
        for a in asteroids:
            dist = math.hypot(ship.x - a.x, ship.y - a.y)
            if dist < a.size / 2 + 20:  # rough collision radius
                ship.alive = False
                explosionShip.play()
                game_over = True
                break

        # RESPAWN ASTEROIDS OF ALL DESTROYED
        if not asteroids:
            asteroids = [Asteroid() for _ in range(5)]

    # DRAW SCREEN
    screen.fill(BLACK)
    ship.draw(screen)
    for b in bullets:
        b.draw(screen)
    for a in asteroids:
        a.draw(screen)

    # GAME OVER TEXT
    if game_over:
        text = font.render("GAME OVER!", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))
        small = small_font.render(f"Your Score: {gameScore}", True, WHITE)
        screen.blit(small, (WIDTH // 2 - small.get_width() // 2, HEIGHT // 2 + 40))
        small = small_font.render("Press R to Restart", True, WHITE)
        screen.blit(small, (WIDTH//2 - small.get_width()//2, HEIGHT//2 + 10))

    pygame.display.flip()
    clock.tick(60)
