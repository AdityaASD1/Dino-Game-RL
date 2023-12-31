import numpy as np
import pygame
import os
import random

import torch

pygame.init()
import math
import neat

# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")).convert_alpha(),
           pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png")).convert_alpha()]
JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png")).convert_alpha()
DUCKING = [pygame.image.load(os.path.join("Assets/Dino", "DinoDuck1.png")).convert_alpha(),
           pygame.image.load(os.path.join("Assets/Dino", "DinoDuck2.png")).convert_alpha()]

SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")).convert_alpha(),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")).convert_alpha(),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png")).convert_alpha()]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")).convert_alpha(),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")).convert_alpha(),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png")).convert_alpha()]

BIRD = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")).convert_alpha(),
        pygame.image.load(os.path.join("Assets/Bird", "Bird2.png")).convert_alpha()]

CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))

BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))


class Dinosaur:
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.extra = None

    def handle_input(self,userInput):
        if userInput == 0 and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput == 1 and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput == 1):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

    def update(self, userInput):
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()
        if self.step_index >= 10:
            self.step_index = 0
        self.extra = userInput
        if isinstance(userInput, int):
            self.handle_input(userInput)
            return

        if userInput[pygame.K_UP] and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput[pygame.K_DOWN]):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()

        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.7
        if self.jump_vel < - self.JUMP_VEL:
            self.dino_jump = False
            if isinstance(self.extra, int):
                self.dino_rect.x = self.X_POS
                self.dino_rect.y = 310
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))




class Cloud:
    def __init__(self, screen_width, game_speed):
        self.SCREEN_WIDTH = screen_width
        self.game_speed = game_speed
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= self.game_speed
        if self.x < -self.width:
            self.x = self.SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, image, type, SCREEN_WIDTH, game_speed, obstacles):
        self.obstacles = obstacles
        self.game_speed = game_speed
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= self.game_speed
        if self.rect.x < -self.rect.width:
            self.obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image, SCREEN_WIDTH, game_speed, obstacles):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type, SCREEN_WIDTH, game_speed, obstacles)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image, SCREEN_WIDTH, game_speed, obstacles):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type, SCREEN_WIDTH, game_speed, obstacles)
        self.rect.y = 300


class Bird(Obstacle):
    def __init__(self, image, SCREEN_WIDTH, game_speed, obstacles):
        self.type = 0
        super().__init__(image, self.type, SCREEN_WIDTH, game_speed, obstacles)
        self.rect.y = 250
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index//5], self.rect)
        self.index += 1



import pygame
import random
MAX_JUMP_VEL = 11
MAX_GAME_SPEED = 100
class DinosaurGame:
    def __init__(self):
        pygame.init()
        self.SCREEN_WIDTH = 1100
        self.SCREEN_HEIGHT = 600
        self.SCREEN = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Dinosaur Game")
        SCREEN = self.SCREEN
        self.game_speed = 18
        self.x_pos_bg = 0
        self.obstacle_type = -1
        self.y_pos_bg = 380
        self.points = 0
        self.speed_increment = 0.001
        self.obstacles = []

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        self.death_count = 0
        self.player = Dinosaur()
        self.cloud = Cloud(self.SCREEN_WIDTH,self.game_speed)
        self.run = True


    def score(self):
        self.points += 1
        if self.points % 100 == 0:
            self.game_speed += 1
        text = self.font.render("score :" + str(self.points),True,(0,0,0))
        textRect = text.get_rect()
        textRect.center = (1000, 40)
        self.SCREEN.blit(text, textRect)

    def background(self):
        image_width = BG.get_width()
        self.SCREEN.blit(BG, (self.x_pos_bg, self.y_pos_bg))
        self.SCREEN.blit(BG, (image_width + self.x_pos_bg, self.y_pos_bg))
        if self.x_pos_bg <= -image_width:
            self.SCREEN.blit(BG, (image_width + self.x_pos_bg, self.y_pos_bg))
            self.x_pos_bg = 0
        self.x_pos_bg -= self.game_speed

    def run_game(self):

        while self.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False

            self.SCREEN.fill((255, 255, 255))
            userInput = pygame.key.get_pressed()

            self.player.draw(self.SCREEN)
            self.player.update(userInput)

            if len(self.obstacles) == 0:
                if random.randint(0, 2) == 0:
                    self.obstacles.append(SmallCactus(SMALL_CACTUS,self.SCREEN_WIDTH,self.game_speed,self.obstacles))
                elif random.randint(0, 2) == 1:
                    self.obstacles.append(LargeCactus(LARGE_CACTUS,self.SCREEN_WIDTH,self.game_speed,self.obstacles))
                elif random.randint(0, 2) == 2:
                    self.obstacles.append(Bird(BIRD,self.SCREEN_WIDTH,self.game_speed,self.obstacles))

            for obstacle in self.obstacles:
                obstacle.draw(self.SCREEN)
                obstacle.update()
                if self.player.dino_rect.colliderect(obstacle.rect):
                    self.run = False

            self.background()

            self.cloud.draw(self.SCREEN)
            self.cloud.update()

            self.score()

            self.clock.tick(30)
            pygame.display.update()

        pygame.quit()

    def step(self, action):

        self.SCREEN.fill((255, 255, 255))

        self.player.draw(self.SCREEN)

        self.player.update(action)

        extra = False
        if len(self.obstacles) == 0:
            extra = True
            if random.randint(0, 2) == 0:
                self.obstacle_type = 0
                self.obstacles.append(SmallCactus(SMALL_CACTUS, self.SCREEN_WIDTH, self.game_speed, self.obstacles))
            elif random.randint(0, 2) == 1:
                self.obstacle_type = 1
                self.obstacles.append(LargeCactus(LARGE_CACTUS, self.SCREEN_WIDTH, self.game_speed, self.obstacles))
            elif random.randint(0, 2) == 2:
                self.obstacle_type = 2
                self.obstacles.append(Bird(BIRD, self.SCREEN_WIDTH, self.game_speed, self.obstacles))

        for obstacle in self.obstacles:
            obstacle.draw(self.SCREEN)
            obstacle.update()
            if self.player.dino_rect.colliderect(obstacle.rect):
                self.run = False

        reward = self.get_reward()
        self.background()

        self.cloud.draw(self.SCREEN)
        self.cloud.update()

        self.score()

        self.clock.tick(30)

        pygame.display.update()
        return [self.state(), reward, not self.run]

    def get_reward(self):
        reward = 0
        if len(self.obstacles) > 0:
            if self.player.dino_rect.colliderect(self.obstacles[0].rect):
                reward -= 10  # penalize for hitting obstacle
                return reward
            elif self.obstacles[0].rect.right < self.player.dino_rect.left:
                reward += 5  # give reward for crossing obstacle
                return reward
        reward += 0.01  # small reward for playing time
        return reward

    def state(self):

        is_running = self.run
        dinoY = self.player.dino_rect.y
        game_speed = self.game_speed
        obstacleX = SCREEN_WIDTH
        obstacle_type = -1
        if len(self.obstacles)!=0:
            obstacleX = self.obstacles[0].rect.x
            obstacle_type = self.obstacle_type
        return np.array([is_running, dinoY, game_speed, obstacleX, obstacle_type])


    def reset(self):
        self.SCREEN.fill((255, 255, 255))
        self.player.draw(self.SCREEN)
        self.player = Dinosaur()
        self.points = 0
        self.obstacles = []
        self.game_speed = 20
        self.run = True

        self.player.dino_rect.x = self.player.X_POS
        self.player.dino_rect.y = self.player.Y_POS

        self.background()
        self.cloud.draw(self.SCREEN)
        self.cloud.update()

        pygame.display.update()
        second_arg = (SCREEN_WIDTH,SCREEN_WIDTH)
        return self.state()




