import random # For generating random numbers
import sys
from time import sleep # We will use sys.exit to exit the program
import pygame
from pygame.compat import raw_input_
from pygame.locals import * # Basic pygame imports
from PIL import Image   
import keyboard                                                                             
import getpass

# Global Variables for the game
FPS = 32
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'gallery/sprites/bird.png'
BACKGROUND = 'gallery/sprites/background.png'
PIPE = 'gallery/sprites/pipe.png'


def welcomeScreen():  
    """
    Shows welcome images on the screen
    """
    
    playerx = int(SCREENWIDTH/5)
    playery = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height())/2)
    messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width())/2)
    messagey = int(SCREENHEIGHT*0.13)
    basex = 0
    while True:
        for event in pygame.event.get():
            # if user clicks on cross button, close the game
            if event.type == pygame.QUIT or (event.type==pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

            # If the user presses space or up key, start the game for them
            elif event.type==pygame.KEYDOWN and (event.key==pygame.K_SPACE or event.key == pygame.K_UP):
                return
            else:
                SCREEN.blit(GAME_SPRITES['background'], (0, 0))    
                SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))    
                SCREEN.blit(GAME_SPRITES['message'], (messagex,messagey ))    
                SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))    
                pygame.display.update()
                FPSCLOCK.tick(FPS)

def mainGame():
    global j
    j = 0
    score1 = 0
    playerx = int(SCREENWIDTH/5)
    playery = int(SCREENWIDTH/2)
    basex = 0

    # Create 2 pipes for blitting on the screen
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # my List of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH+200, 'y':newPipe1[0]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[0]['y']},
    ]
    # my List of lower pipes
    lowerPipes = [
        {'x': SCREENWIDTH+200, 'y':newPipe1[1]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[1]['y']},
    ]

    pipeVelX = -4

    playerVelY = -9
    playerMaxVelY = 10
    playerMinVelY = -8
    playerAccY = 1

    playerFlapAccv = -8 # velocity while flapping
    playerFlapped = False # It is true only when the bird is flapping


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                if playery > 0:
                    playerVelY = playerFlapAccv
                    playerFlapped = True
                    GAME_SOUNDS['wing'].play()


        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes) # This function will return true if the player is crashed
        if crashTest:
            return     

        #check for score
        playerMidPos = playerx + GAME_SPRITES['player'].get_width()/2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width()/2
            if pipeMidPos<= playerMidPos < pipeMidPos +4:
                score1 +=1
                j = score1
                print(f"Your score1 is {j}") 
                GAME_SOUNDS['point'].play()


        if playerVelY <playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY

        if playerFlapped:
            playerFlapped = False            
        playerHeight = GAME_SPRITES['player'].get_height()
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)

        # move pipes to the left
        for upperPipe , lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        # Add a new pipe when the first is about to cross the leftmost part of the screen
        if 0<upperPipes[0]['x']<5:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        # if the pipe is out of the screen, remove it
        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)
        
        # Lets blit our sprites now
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
        myDigits = [int(x) for x in list(str(score1))]
        width = 0
        for digit in myDigits:
            width += GAME_SPRITES['numbers'][digit].get_width()
        Xoffset = (SCREENWIDTH - width)/2

        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT*0.12))
        Xoffset += GAME_SPRITES['numbers'][digit].get_width()
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def isCollide(playerx, playery, upperPipes, lowerPipes):
    if playery> GROUNDY - 25  or playery<0:
        GAME_SOUNDS['hit'].play()
        return True
    

    for pipe in upperPipes:
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        if(playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width()):
            GAME_SOUNDS['hit'].play()
            return True

    for pipe in lowerPipes:
        if (playery + GAME_SPRITES['player'].get_height() > pipe['y']) and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
            GAME_SOUNDS['hit'].play()
            return True
    
    return False


def getRandomPipe():
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT/3
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height()  - 1.2 *offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
        {'x': pipeX, 'y': -y1}, #upper Pipe
        {'x': pipeX, 'y': y2} #lower Pipe
    ]
    return pipe


if __name__ == "__main__":
    # This will be the main point from where our game will start
    pygame.init() # Initialize all pygame's modules
    game_font = pygame.font.Font('freesansbold.ttf', 20)
    game_font2 = pygame.font.Font('freesansbold.ttf', 20)
    game_over = pygame.font.Font('freesansbold.ttf', 30)
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Bird by Rohinshan')
     
    GAME_SPRITES['numbers'] = ( 
        pygame.image.load('gallery/sprites/0.png').convert_alpha(),
        pygame.image.load('gallery/sprites/1.png').convert_alpha(),
        pygame.image.load('gallery/sprites/2.png').convert_alpha(),
        pygame.image.load('gallery/sprites/3.png').convert_alpha(),
        pygame.image.load('gallery/sprites/4.png').convert_alpha(),
        pygame.image.load('gallery/sprites/5.png').convert_alpha(),
        pygame.image.load('gallery/sprites/6.png').convert_alpha(),
        pygame.image.load('gallery/sprites/7.png').convert_alpha(),
        pygame.image.load('gallery/sprites/8.png').convert_alpha(),
        pygame.image.load('gallery/sprites/9.png').convert_alpha(),
    )
    
    GAME_SPRITES['message'] =pygame.image.load('gallery/sprites/message.png').convert_alpha()
    GAME_SPRITES['base'] =pygame.image.load('gallery/sprites/base.png').convert_alpha()
    GAME_SPRITES['pipe'] =(pygame.transform.rotate(pygame.image.load( PIPE).convert_alpha(), 180), pygame.image.load(PIPE).convert_alpha())

        
      
    # Game sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('gallery/audio/die.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')

    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()
    global multiquit
    global z, y
    z = 0
    y = 0
    multiquit = 0 
    while True:
        s = 0
        m = 0   
        blac= pygame.image.load('black.png')
        logo = pygame.image.load('logo.png')
        quitgaming = pygame.image.load('escquit.png')
        image1 = pygame.image.load('single.png')
        image2 = pygame.image.load('single_press.png')
        image3 = pygame.image.load('multi.png')
        image4 = pygame.image.load('multi_press.png')
        SCREEN.blit(blac, [0,0])
        SCREEN.blit(logo, (50,0))
        SCREEN.blit(quitgaming, [0,350])
        SCREEN.blit(image1, [0, 125])
        SCREEN.blit(image2, [200,125])
        SCREEN.blit(image3, [0, 250])
        SCREEN.blit(image4, [200, 250])
        pygame.display.update()     
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                s = s + 1
                break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                m = m + 1
                break
        if s == 1:
            while True:
                welcomeScreen() # Shows welcome screen to the user until he presses a button
                mainGame() # This is the main game function
                blac1= pygame.image.load('black.png')
                score_surf1 = game_font.render("Your Score " + str(j),True, (0,255,255))
                over1 = game_over.render("GAME OVER!", True, (255,2,2))
                sp1 = game_font2.render("Press 'q' to Main Menu...", True, (255,5,2))
                SCREEN.blit(blac1, [0,0])
                SCREEN.blit(score_surf1, (20,35))
                SCREEN.blit(over1, (20,64))
                SCREEN.blit(sp1, (20,110))
                pygame.display.update()
                if keyboard.wait(hotkey='q'):
                    continue
                break

        if m == 1:
            pygame.init()
            pygame.display.set_caption("Flying Bird Multiplayer")
            clock = pygame.time.Clock()
            game_font = pygame.font.Font('freesansbold.ttf', 20)
            game_font2 = pygame.font.Font('freesansbold.ttf', 20)
            game_over = pygame.font.Font('freesansbold.ttf', 30)


            #game variables
            
            gravity = 0.25
            bird_movement = 0
            game_active = False
            score = 0
            high_score = 0
            first_try = True
            playerone= False
            playertwo = False

            background = pygame.image.load("background.png").convert()
            floor = pygame.image.load("floor.png").convert()
            floor = pygame.transform.scale2x(floor)
            floorsX = 0

            def getFloor():
                SCREEN.blit(floor, (floorsX, 500))
                SCREEN.blit(floor, (floorsX + 387, 500))


            def create_pipe():
                rand_pipeh = random.choice(pipe_height)
                rand_gap = random.choice(gap_dist)
                new_pipe = pipe.get_rect(midtop=(420,rand_pipeh))
                opp_pipe = pipe.get_rect(midbottom=(420,rand_pipeh-rand_gap))
                return new_pipe, opp_pipe


            def move_pipe(pipes):
                for pipex in pipes:
                    pipex.centerx -=5
                return pipes

            def show_pipe(pipes):
                for pipex in pipes:
                    if pipex.bottom>600:
                        SCREEN.blit(pipe, pipex)
                    else:
                        SCREEN.blit(pygame.transform.flip(pipe,False, True), pipex)

            def check_collision(pipes):
                for pipex in pipes:
                    if bird_rect.colliderect(pipex):
                        return True
                return False

            def rcheck_collision(pipes):
                for pipex in pipes:
                    if rbird_rect.colliderect(pipex):
                        return True
                return False

            def rotated_bird(bird):
                new_bird = pygame.transform.rotozoom(bird, -bird_movement*3, 1)
                return new_bird

            def score_display():
                score_surf = game_font.render("Score " + str(score),True, (0,0,0))
                SCREEN.blit(score_surf, (15,35))

            def high_score_display():
                high_score_surf = game_font2.render("High Score "+str(high_score),True,(0,0,0))
                SCREEN.blit(high_score_surf, (15,85))

            def gameover(x):
                over = game_over.render("GAME OVER", True, (255,2,2))
                sp = game_font2.render("press space to retry", True, (255,5,2))
                quitting = game_font2.render("press 'q' to quit", True, (255,200,2))
                SCREEN.blit(over, (15,255))
                SCREEN.blit(sp, (15,320))
                SCREEN.blit(quitting, (15, 380))
                playerwins(x)
                

            def welcome():
                over = game_over.render("Welcome!! ", True, (0,0,230))
                ll = game_font2.render("press space to play", True,(0,0,230))
                faster = game_font2.render("Who survives?", True, (0,0,0))
                SCREEN.blit(over, (15,255))
                SCREEN.blit(ll, (15,320))
                SCREEN.blit(faster, (15, 370))

            def playerwins(who):
                over = game_over.render(who+" wins!!", True, (0,230,23))
                SCREEN.blit(over, (15,200))

            bird2 = pygame.image.load("bird2.png").convert_alpha()
            bird1 = pygame.image.load("bird1.png").convert_alpha()
            bird3 = pygame.image.load("bird3.png").convert_alpha()
            birdlist = [bird1, bird2, bird3]
            bird_index = 0
            bird = birdlist[bird_index]
            bird_rect = bird.get_rect(center=(50,300))
            BIRDFLAP =  pygame.USEREVENT +1
            pygame.time.set_timer(BIRDFLAP, 200)


            #second brid info
            rbird1 = pygame.image.load("rbird1.png")
            rbird2 = pygame.image.load("rbird2.png")
            rbird3 = pygame.image.load("rbird3.png")
            rbirdlist = [rbird1, rbird2, rbird3]
            rbirdindex = 1
            rbird = rbirdlist[rbirdindex]
            rbird_rect = rbird.get_rect(center=(50,300))
            rbird_movement = 0

            pipe = pygame.image.load("pipe-green.png")
            pipe = pygame.transform.scale(pipe,(70,400))
            pipe_list = []
            SPAWNPIPE = pygame.USEREVENT
            pygame.time.set_timer(SPAWNPIPE, 1200)
            pipe_height = [450,350,400,375,285,225,300,425,275]
            #gap_dist = [150,125,137,175]
            gap_dist = [250]


            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key==pygame.K_UP:
                            bird_movement=0
                            bird_movement -=7
                        if event.key ==pygame.K_w:
                            rbird_movement = 0
                            rbird_movement -=7
                        if event.key == pygame.K_SPACE and game_active==False:
                            score = 0
                            game_active = True
                    if event.type == SPAWNPIPE and game_active:
                        pipe_list.extend(create_pipe())
                    if event.type == BIRDFLAP:
                        if bird_index <2:
                            bird_index +=1
                        else:
                            bird_index=0
                        bird = birdlist[bird_index]
                        if rbirdindex <2:
                            rbirdindex +=1
                        else:
                            rbirdindex=0
                        rbird = rbirdlist[rbirdindex]


                SCREEN.blit(background,(0,0))
                if not game_active and first_try:
                    welcome()
                if game_active:
                        # bird movement
                        first_try = False
                        if bird_rect.centery < 5:
                            bird_movement = 0
                            bird_rect.centery = 5
                        if rbird_rect.centery < 5:
                            rbird_movement = 0
                            rbird_rect.centery = 5

                        bird_movement += gravity
                        rbird_movement += gravity
                        rot_bird = rotated_bird(bird)
                        rot_rbird = rotated_bird(rbird)
                        rbird_rect.centery += rbird_movement
                        bird_rect.centery += bird_movement
                        SCREEN.blit(rot_bird, bird_rect)
                        SCREEN.blit(rot_rbird, rbird_rect)

                        # collision code
                        if  check_collision(pipe_list) or bird_rect.centery > 494:
                            game_active = False
                            pipe_list.clear()
                            bird_movement = 0
                            bird_rect.centery = 300
                            rbird_movement = 0
                            rbird_rect.centery = 300
                            high_score_display()
                            playertwo = True
                        if rcheck_collision(pipe_list) or rbird_rect.centery>494:
                            game_active = False
                            pipe_list.clear()
                            bird_movement = 0
                            bird_rect.centery = 300
                            rbird_movement = 0
                            rbird_rect.centery = 300
                            high_score_display()
                            playerone = True
                #pipe movement
                        pipe_list = move_pipe(pipe_list)
                        show_pipe(pipe_list)

                        # floor movement
                        floorsX -= 1

                        if floorsX < -400:
                            floorsX = 0

                        if len(pipe_list)>0 and  pipe_list[-1].centerx==bird_rect.centerx:
                            score += 1
                        if score>high_score:
                            high_score = score

                elif not first_try:

                    if playerone:
                        win = "Red-Bird"
                    if playertwo:
                        win ="Yellow-Bird"
                    playertwo =False
                    playerone =False
                    gameover(win)


                score_display()
                high_score_display()
                getFloor()
                pygame.display.update()
                clock.tick(64)
                if keyboard.is_pressed('q'):
                    break
                