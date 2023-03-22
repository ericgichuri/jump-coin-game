import pygame
import random
import os
from pygame import mixer

pygame.init()
clock=pygame.time.Clock()
FPS=60

#define
SCREEN_WIDTH=1000
SCREEN_HEIGHT=600
GROUND=SCREEN_HEIGHT-SCREEN_HEIGHT//4
GRAVITY=1
JUMP_THRESH=60
MAX_BLOCKS=10
SCROLL_THRESH=SCREEN_WIDTH-SCREEN_WIDTH//10
#define colors
WHITE=(255,255,255)

scroll=0
bg_scroll=0
gameover=False
MAX_BARRIERS=5
MAX_REDCOIN=8
MAX_GOLDCOIN=15
score=0
gold_coinvalue=5
red_coinvalue=10

if os.path.exists('score.txt'):
    with open('score.txt','r') as file:
        high_score=int(file.read())
else:
    high_score=0

screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Jumpy Game")

# looad images
icon=pygame.image.load("icons/gameicon.png").convert_alpha()
pygame.display.set_icon(icon)

#music
mixer.music.load("music/bgmusic.mp3")
mixer.music.play(-1)
mixer.music.set_volume(0.1)

#game images 
background_image=pygame.image.load("icons/background.png").convert_alpha()
ground_image=pygame.image.load("icons/ground.png").convert_alpha()
player_image=pygame.image.load("icons/player.png").convert_alpha()
enemy_image=pygame.image.load("icons/enemy.png").convert_alpha()
barrier_image=pygame.image.load("icons/barriers.png").convert_alpha()
block_image=pygame.image.load("icons/blocks.png").convert_alpha()
gold_coin_image=pygame.image.load("icons/gold_coin.png").convert_alpha()
red_coin_image=pygame.image.load("icons/red_coin.png").convert_alpha()

small_font=pygame.font.SysFont('times',24)
large_font=pygame.font.SysFont('times',50)

def draw_score(text,font,text_col,x,y):
    img=font.render(text,font,text_col)
    screen.blit(img,(x,y))
def draw_highscore(text,font,text_col,x,y):
    img=font.render(text,font,text_col)
    screen.blit(img,(x,y))
def disp_gameover(text,font,color,x,y):
    img=large_font.render(text,font,color)
    screen.blit(img,(x,y))
def disp_replayover(text,font,color,x,y):
    img=small_font.render(text,font,color)
    screen.blit(img,(x,y))

def draw_backgroud():
    screen.blit(background_image,(0+bg_scroll,0))
    screen.blit(background_image,(1000+bg_scroll,0))
def draw_ground():
    image=pygame.transform.scale(ground_image,(SCREEN_WIDTH,SCREEN_HEIGHT//4))
    screen.blit(image,(0,SCREEN_HEIGHT-SCREEN_HEIGHT//4))

class Player():
    def __init__(self,x,y):
        self.image=pygame.transform.scale(player_image,(30,30))
        self.width=30
        self.height=30
        self.rect=pygame.Rect(0,0,self.width,self.height)
        self.rect.center=(x+(self.width/2),y-(self.height/2))
        self.vel_y=0
        self.jumptimes=0
        self.jumpmax=2
        self.flip=False
    
    def move(self):
        dx=0
        dy=0

        #key processes
        key=pygame.key.get_pressed()
        if key[pygame.K_RIGHT] or key[pygame.K_d]:
            dx=5
            self.flip=False
        if key[pygame.K_LEFT] or key[pygame.K_a]:
            dx=-5
            self.flip=True
        
        
        self.vel_y+=GRAVITY
        dy+=self.vel_y
        
        #limit player from out of screen
        if self.rect.left+dx<0:
            dx=-self.rect.left
        
        if self.rect.right+dx>SCREEN_WIDTH:
            dx=SCREEN_WIDTH-self.rect.right
        
        #limit player to go above
        if self.rect.top-dy<JUMP_THRESH:
            self.rect.y=self.rect.bottom
            self.vel_y=18
            dy+=self.vel_y
        
        #limit player to go past ground
        if self.rect.bottom+dy>GROUND:
            dy=0
            self.vel_y=0
            if key[pygame.K_UP] or key[pygame.K_w]:
                self.vel_y=-18
                dy=self.vel_y
        
        
        
        if self.jumptimes>self.jumpmax:
            dy=0
            self.vel_y=0
            print(self.jumptimes)
            self.jumptimes=0

        for block in block_group:
            if block.rect.colliderect(self.rect.x,self.rect.y+dy,self.width,self.height):
                if self.rect.bottom<block.rect.centery:
                        if self.vel_y>0:
                            self.rect.bottom=block.rect.top
                            dy=0
                            self.vel_y=0
                            if key[pygame.K_UP] or key[pygame.K_w]:
                                self.vel_y=-18
                                dy=self.vel_y
        for block in block_group:
            if block.rect.colliderect(self.rect.x,self.rect.y+dy,self.width,self.height):
                if self.rect.top<block.rect.bottom:
                    self.rect.y=self.rect.bottom
                    self.vel_y=18
                    dy+=self.vel_y
        
        
        
        #update rect position
        self.rect.x+=dx
        self.rect.y+=dy
        
    
    def draw(self):
        screen.blit(pygame.transform.flip(self.image,self.flip,False),(self.rect.x,self.rect.y))
        #pygame.draw.rect(screen,WHITE,self.rect,1)


class Enemy():
    def __init__(self,x,y):
        self.image=pygame.transform.scale(enemy_image,(30,30))
        self.width=30
        self.height=30
        self.rect=pygame.Rect(0,0,self.width,self.height)
        self.rect.center=(x+(self.width/2),y)
        #self.vel_y=0
    
    def draw(self):
        screen.blit(pygame.transform.flip(self.image,True,False),(self.rect.x,self.rect.y))

class Barrier(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.transform.scale(barrier_image,(70,16))
        self.width=70
        self.height=16
        self.rect=pygame.Rect(0,0,self.width,self.height)
        self.rect.center=(x+(self.width/2),y-(self.height/2))
        #self.vel_y=0
    
    def draw(self):
        screen.blit(pygame.transform.flip(self.image,False,False),(self.rect.x,self.rect.y))

class Blocks(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.transform.scale(block_image,(100,30))
        self.width=100
        self.height=30
        self.rect=pygame.Rect(0,0,self.width,self.height)
        self.rect.center=(x+(self.width/2),y-(self.height/2)-100)
        #self.vel_y=0
    
    def draw(self):
        screen.blit(pygame.transform.flip(self.image,False,False),(self.rect.x,self.rect.y))

class Gold_coin(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.transform.scale(gold_coin_image,(30,30))
        self.width=30
        self.height=30
        self.rect=pygame.Rect(0,0,self.width,self.height)
        self.rect.center=(x+(self.width/2),y-(self.height/2))
        #self.vel_y=0
    
    def draw(self):
        screen.blit(pygame.transform.flip(self.image,False,False),(self.rect.x,self.rect.y))
        

class Red_coin(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.transform.scale(red_coin_image,(30,30))
        self.width=30
        self.height=30
        self.rect=pygame.Rect(0,0,self.width,self.height)
        self.rect.center=(x+(self.width/2),y-(self.height/2))
        #self.vel_y=0
    
    def draw(self):
        screen.blit(pygame.transform.flip(self.image,False,False),(self.rect.x,self.rect.y))


jumpy=Player(0,GROUND)
enemy=Enemy(SCREEN_WIDTH//2,GROUND-30)
barrier=Barrier(SCREEN_WIDTH//6,GROUND)
barrier_group=pygame.sprite.Group()
barrier_group.add(barrier)

block=Blocks(0,GROUND)
block_group=pygame.sprite.Group()
block_group.add(block)



gold_coin=Gold_coin(0,block.rect.top)
gold_coin_group=pygame.sprite.Group()
gold_coin_group.add(gold_coin)

red_coin=Red_coin(100,GROUND)
red_coin_group=pygame.sprite.Group()
red_coin_group.add(red_coin)




running=True
while running:
    clock.tick(FPS)
    if gameover==False:
        jumpy.move()
        draw_backgroud()
        draw_ground()
        
        
        if len(block_group)<MAX_BLOCKS:
            b_y=GROUND
            b_x=block.rect.x+100+random.randint(50,150)
            block=Blocks(b_x,b_y)
            block_group.add(block)
        if len(barrier_group)<MAX_BARRIERS:
            br_y=GROUND
            br_x=barrier.rect.x+50+random.randint(100,200)
            barrier=Barrier(br_x,br_y)
            barrier_group.add(barrier)
        if len(red_coin_group)<MAX_REDCOIN:
            r_y=GROUND
            r_x=red_coin.rect.x+50+random.randint(30,70)
            red_coin=Red_coin(r_x,r_y)
            red_coin_group.add(red_coin)
        if len(gold_coin_group)<MAX_GOLDCOIN:
            g_y=block.rect.top
            g_x=gold_coin.rect.x+20+random.randint(30,70)
            gold_coin=Gold_coin(g_x,g_y)
            gold_coin_group.add(gold_coin)

        block_group.draw(screen)
        enemy.draw()
        barrier_group.draw(screen)
        red_coin_group.draw(screen)
        gold_coin_group.draw(screen)
        jumpy.draw()
        for r in barrier_group:
            if r.rect.colliderect(jumpy.rect):
                gameover=True
                gameovertext="GAME OVER !"
                disp_gameover(gameovertext,large_font,(255,0,0),SCREEN_WIDTH//3-40,SCREEN_HEIGHT//3-60)
                disp_replayover("Press R to replay",small_font,(0,0,255),SCREEN_WIDTH//3,SCREEN_HEIGHT//3-10)
        for i in red_coin_group:
            if i.rect.colliderect(jumpy.rect):
                score=score+red_coinvalue
                sound=mixer.Sound("music/coin_sound.mp3")
                sound.play()
                i.kill()
        for j in gold_coin_group:
            if j.rect.colliderect(jumpy.rect):
                score=score+gold_coinvalue
                sound=mixer.Sound("music/coin_sound.mp3")
                sound.play()
                j.kill()
        if jumpy.rect.right>=SCREEN_WIDTH:
            #jumpy=Player(0,GROUND)
            red_coin_group.empty()
            gold_coin_group.empty()

            gold_coin=Gold_coin(0,block.rect.top)
            gold_coin_group.add(gold_coin)
            red_coin=Red_coin(100,GROUND)
            red_coin_group.add(red_coin)

            red_coin_group.draw(screen)
            gold_coin_group.draw(screen)
    else:
        pass
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            
            
            running=False
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_r:
                if score>=high_score:
                    high_score=score
                    with open('score.txt',"w") as file:
                        file.write(str(high_score))
                gameover=False
                gameovertext=""
                score=0
                red_coin_group.empty()
                gold_coin_group.empty()

                gold_coin=Gold_coin(0,block.rect.top)
                gold_coin_group.add(gold_coin)
                red_coin=Red_coin(100,GROUND)
                red_coin_group.add(red_coin)

                red_coin_group.draw(screen)
                gold_coin_group.draw(screen)
                jumpy=Player(0,GROUND)
                
    
    draw_score(f'SCORE: {score}',small_font,(0,0,0),10,10)
    draw_highscore(f'High Score {high_score}',small_font,(0,0,0),SCREEN_WIDTH-300,10)
    pygame.display.update()
pygame.quit()
