'''
This is my attempt at a game and have been learning so much while making this

Gameplay
    A)  Each level has 1 monster you have to duel without movement left or right, defeat a monster move on
        1. using a swing sequence to make combos ie. LEFT RIGHT LEFT ...
        2. Each of the first five scenes, player will have to figure out a random combo to learn a new move,
        3. Combo will be named after the monster defeated
        4. Stamina bar will grow over the first 5 levels
        5. Moving and swings will cost stamina

    B)  Constantly running forward defeating enemies as you go
        1.Forward movement will always increase to a max run speed
        2.Players have some choice  in left and right as the road has 3 lanes, player can swap lanes

still working on how it will play out, hopefull I can try both ways and see what is more fun

Todo list:
    -DONE-Fix collisions in the "def check_collision_with_enemy():" its not working :(
    -get texture for sword and eventually replace it with your own 3d model
    -FIRST PASS DONE -Work on getting better FPS (use ground over voxel cubes)
        a.Check player input
        b. player keys
        c. Enemy update
        d. collision checks!
    -Fix an issue when turning around by spamming left or right will point player in incorrect direction
    -Work on the skybox, try and make it into a square for front, back and side art
    -Add sound effect for hits and movement
    -Add head, sword "bob" to simulate movement
    -Add enemies and textures

'''

from ursina import *
import random
from FirstPersonControllerCustom import FirstPersonControllerCustom    # I replaced the first person controller due to it haveing some built in commands i wanted to change
from ursina.shaders import lit_with_shadows_shader
from ursina.prefabs.health_bar import HealthBar
#from player import Player     # I want to move the player entity to another file
#from enemy import Enemy      # I want to move the enemy AI to another file
#from collider import ObjectCollider      # use this to make a collider based on a .obj size

app = Ursina()


sword_model = load_model('Katana_LP_Final.obj')
sword_model2 = load_model('Katana_LP_Final.obj')
'''
#trying the different textures that came with the 3d model, none seem to work and i am not sure what to do with the texture
#sword_texture = load_texture('assets/sword.png')
#sword_texture = load_texture('Katana_d.tga')
#sword_texture = load_texture('Katana_n.tga')
'''




random.seed(0)  # not sure what this does
Entity.default_shader = lit_with_shadows_shader  # im assuming a shader


#stops editor camera ?  err engages pause camera
editor_camera = EditorCamera(enabled=False, ignore_paused=True)

#ENTITYS
# floor to map, will need to use a custom model for a rectangle, using voxel cubes uses to much fps
ground = Entity(model='plane', collider='box', scale=(128), texture='grass', texture_scale=(4,4))


# The code below is creating the sword entity
sword = Entity(model=sword_model, parent=camera, position=(0, -.2, 3), scale=(.005, .005, .005), rotation=(0, 0, -90), color=color.dark_gray)
sword_size = Vec3(717.347, 58.9473, 57.7639)  #See see collider.py to call the class or pregenerate vector3
sword.collider = BoxCollider(sword, center=(0, 0, 0), size=sword_size)
sword.flash = Entity(parent=sword, z=1, world_scale=1, model='quad', color=color.yellow, enabled=False)






#shootables_parent = Entity()  # Target for raytracing ???? residual code from ursinafps game
sword_target = Entity()
#mouse.traverse_target = shootables_parent   # Not sure about this, but it should go soon

#Global variables
sword_dmg = 15
sword_cooldown = False
enemy = None
esword = None
do_block = False
i = 0
text_entity = ''
text_entity2 = ''
text_entity3 = ''

'''
#This creates the floor and boxes that have clickable features (like changing color) and I thought it would be better then 1 large ground texture
class Voxel(Button):
    def __init__(self, position = (0,5,0), texture = grass_texture):
        super().__init__(
            parent = scene,
            position = position,
            model = 'assets/block',
            origin_y = .2,
            origin_x = 5,
            origin_z = 2,
            texture = texture,
            color = color.color(0,0,random.uniform(0.9,1)),
            highlight_color = color.lime,
            scale = .5)
'''


class Enemy(Entity):
    global sword_dmg
    def __init__(self,max_hp, **kwargs):
        super().__init__(model='cube', scale_y=2, origin_y=-.5, color=color.light_gray, **kwargs)
        self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, scale=(1.5, .1, .1))
        self.max_hp = max_hp
        self._hp = self.max_hp
        # Add BoxCollider component
        self.collider = BoxCollider(self, size=self.scale)
        self.melee_in_progress = False


    def blink_animation(self, blink_color):
        duration = 0.2  # Duration of each blink
        num_blinks = 5  # Number of blinks
        for _ in range(num_blinks):
            self.color = blink_color
            invoke(self.set_default_color, delay=duration / 2)
            duration += 0.2

    def set_default_color(self):
        # Set your default color here
        self.color = color.white

    def reset_melee_flag(self):
        self.melee_in_progress = False


    def melee_move(self):
        if self.melee_in_progress:
            return

        self.melee_in_progress = True
        what_to_do = random.randint(1, 5)

        if what_to_do == 1:
            self.animate_position(self.position + (1, 0, 0), duration=.7)
            self.blink_animation(color.black)
        elif what_to_do == 2:
            self.animate_position(self.position + (2, 0, 1), duration=.7)
            self.blink_animation(color.cyan)
        elif what_to_do == 3:
            self.animate_position(self.position + (-1, 0, 0), duration=.7)
            self.blink_animation(color.green)
        elif what_to_do == 4:
            self.animate_position(self.position + (0, 0, -1), duration=.7)
            self.blink_animation(color.yellow)
        elif what_to_do == 5:
            self.animate_position(self.position + (0, 0, -2), duration=.7)
            self.blink_animation(color.blue)

            # Reset the melee_in_progress flag after the melee action is completed
        invoke(self.reset_melee_flag, delay=2.0)



    def update(self):
        self.look_at_2d(player.position, 'y')
        dist = distance_xz(player.position, self.position)

        if dist > 4:
            self.position += self.forward * time.dt * 2
        elif dist > 3.5:
            self.melee_move()                            #call random move direction for more intense fights
            self.position += self.right * time.dt * .001 #keeps the enemy from "vibrating" at this range
        elif dist > 0:
            self.position -= self.forward * time.dt * 8

        if self.intersects(sword).hit:
            global seq,i
            if seq[i] is None:
                self.color=color.white
            
            if seq[i] == 'left':
                self.color= color.lime
            if seq[i] == 'right':
                self.color = color.orange

            if self.hp <= 0:        #I put this here b/c getting missing obj err if hp < 0 b4
                destroy(self)

            else:
                self.hp = self.hp - sword_do_damage()    #Set sword damage here



    @property
    def hp(self):
        return self._hp

    @hp.setter          #This is need for the dmg to work, not sure y
    def hp(self, value):
        global enemy, i
        self._hp = value
        sword_reset_pos()
        if value <= 0:
            destroy(self)
            enemy = spawn_enemy()
            seq.append(random.choice(['left', 'right']))
            self.health_bar.alpha = 0

            return

        self.health_bar.scale_x = self.hp / self.max_hp * 1.5        # Enemy Health bar
        self.health_bar.alpha = 1                                    # shows the HP when hit


def spawn_enemy():
    global enemy, esword, current_swing, seq, text_entity
    enemy = Enemy(max_hp=120, position=(20, 0, 0))
    esword = Entity(model=sword_model2, parent=enemy, position=(0.02, 1, .8), scale=(.002, .003, .003), rotation=(0, 0, -90), color=color.dark_gray)
    esword_size = Vec3(717.347, 58.9473, 57.7639)
    esword.collider = BoxCollider(esword, center=(0, 0, 0), size=esword_size)
    current_swing = []  # Resets the current swing set
    display_seq()
    return enemy

def point_at_enemy():
    if enemy is not None:  # Check if an enemy exists
        player.look_at_2d(enemy.position, 'y')  # Use the position of the stored enemy

    else:
        print("No enemy to point at.")



def display_seq():
    global text_entity
    if text_entity:
        destroy(text_entity)
    text_entity = Text(text=seq, origin=(0, -5), scale=2.5, color=color.yellow, background=False)


def sequencer():  # This checks the swing, sees if the player is matching the sequence and if so deciding NOT to block the shot
    global do_block, i, seq, sword_dmg, current_swing
    distance = distance_xz(player.position, enemy.position)
    if distance > 7:                    # IF player is outside the _ range then clear the current swing list
        print("Dist ", distance)        #for testing
        print('reseting seq',' i=', i)  #for testing
        print('seq', seq)               #for testing
        current_swing = []           # clearing the current swing list
        destroy(text_entity2)
        i = 0                           # i variable to scale with the sequence list, this resets the counter to 0 because the enemy is out of range
    else:

        if seq[i] is None:              # error check
            do_block = False
            print('No Sequence found')
            return do_block

        if len(current_swing) > len(seq):   # If player keeps swinging, then keep blocking
            do_block = True
            current_swing = []
            destroy(text_entity2)
            i = 0
            return do_block, current_swing, i

        if i < len(seq) and i < len(current_swing) and seq[i] == current_swing[i]:
            if len(current_swing)-1 == len(seq)-1:
                do_block = False
                print('Combo!')
                sword_dmg = 45
                current_swing = []
                destroy(text_entity2)
                i = 0
                return do_block, sword_dmg, current_swing, i
            else:
                do_block = False
                print('matched ', i)
                i += 1
                return do_block, i
        else:
            i = 0
            print('You missed the sequence !')
            do_block = True
            current_swing = []
            destroy(text_entity2)
            i = 0
            return do_block, sword_dmg, current_swing, i




def input(key):                #May need to look at changing all the "if"s to elifs or other changes to improve fps

    #forwards and backwards
    if key == 'w':              #For moving forward 1 square
        point_at_enemy()   #player.look_at_2d(enemies[0].position, 'y')
        player.position += player.forward
        sword.rotation = (0, 0, -90)
    if held_keys['w']:          #For running forward  this may need work when I have things hit the player
        player.position += player.forward
    if key == 's':
        player.position -= player.forward
    if held_keys['s']:
        player.position -= player.forward
        sword.rotation = (0, 0, -90)


    # Left and right (for turning around)
    if key == 'a':
        player.position += player.left * 3
        point_at_enemy()
    if key == 'd':
        player.position += player.right * 3
        point_at_enemy()

    #Swing left and right

    if key == 'left arrow':
        swing_left()
    if key == 'right arrow':
        swing_right()
    if key == 'up arrow':
        swing_down()








first_in_seq = random.choice(['left', 'right'])
seq = ['right', 'left']
current_choice = 2  # Initialize current_choice with an index value
current_swing = []

def sword_reset_pos():
    sword.rotation = (0, 0, -90)
    sword.position = (.3, -.9, 3)
    esword.position = (0.02, 1, .8)
    esword.rotation = (0, 0, -90)

def swing_right():
    global seq, do_block, current_swing, text_entity2
    current_swing.append('right')
    print('swinging right', current_swing)
    destroy(text_entity2)
    text_entity2 = Text(text=current_swing, origin=(1, 0), scale=2.5, color=color.yellow, background=False)
    sequencer()
    if do_block == False: # if the do_block is false then the Enemy does NOT want to block the shot, letting it though
        sword_reset_pos()
        sword.animate('rotation_z', sword.rotation_z + 90, duration=.12)
        sword.animate('rotation_y', sword.rotation_y - 80, duration=.12)
        sword_reset_pos()
    else:
        sword_reset_pos()
        sword.animate('rotation_z', sword.rotation_z + 90, duration=.12)
        sword.animate('rotation_y', sword.rotation_y - 40, duration=.12)
        sword_reset_pos()
        esword.position = (-.8, .8, .8)
        esword.animate('rotation_x', sword.rotation_x + 35, duration=.12)
        esword.animate('rotation_z', sword.rotation_z - 35, duration=.12)
def swing_left():
    global seq, do_block, current_swing, text_entity2
    current_swing.append('left')
    print('swinging left', current_swing)
    destroy(text_entity2)
    text_entity2 = Text(text=current_swing, origin=(1, 0), scale=2.5, color=color.yellow, background=False)
    sequencer()
    if do_block == False:
        sword_reset_pos()
        sword.animate('rotation_z', sword.rotation_z - 90, duration=.12)
        sword.animate('rotation_y', sword.rotation_y + 80, duration=.12)
        sword_reset_pos()

    else:
        sword_reset_pos()
        sword.animate('rotation_z', sword.rotation_z - 90, duration=.12)
        sword.animate('rotation_y', sword.rotation_y + 40, duration=.12)
        sword_reset_pos()
        esword.position = (.8, .8, .8)
        esword.animate('rotation_x', sword.rotation_x + 35, duration=.12)
        esword.animate('rotation_z', sword.rotation_z + 35, duration=.12)
        print('not correct choice')





def swing_down():
    sword.rotation = (0,0,-90)
    sword.position = (0,-.9,3)
    sword.animate('rotation_x', sword.rotation_x +90, duration=.12)
def sword_reset_cooldown():
    global sword_cooldown
    sword_cooldown = False

def sword_do_damage():
    global sword_dmg, sword_cooldown
    if sword_cooldown:
        return 0
    sword_cooldown = True
    sword_dmg = 15
    invoke(sword_reset_cooldown, delay=.3)  # Reset the cooldown after .2 seconds
    return sword_dmg


def update():
    #global sword_dmg, sword_invis
    if sword.intersects(sword_target).hit:
        sword.blink(color.yellow)


#Pause the game
def pause_input(key):
    if key == 'tab':    # press tab to toggle edit/play mode
        editor_camera.enabled = not editor_camera.enabled
        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        sword.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position
        application.paused = editor_camera.enabled


# this only works when at the bottom here
pause_handler = Entity(ignore_paused=True, input=pause_input)


'''
# Calls Enemy entity
spawn_x = random.uniform(0, 100)  # Modify the range as desired for the x-axis
spawn_z = random.uniform(0, -5)  # Modify the range as desired for the y-axis
#enemies = [Enemy(x=random.uniform(0, 100), z=random.uniform(0, -5), max_hp=random.uniform(50, 150)) for x in range(int(random.uniform(1,4)))] # More random added
#enemies = Enemy(max_hp=100, position=(5,0,0))  #for summoning 1 enemy
'''
enemy = spawn_enemy()
#text_entity = Text(text=seq, origin=(1, 1), scale=2.5, color=color.yellow, background=False)

player = FirstPersonControllerCustom(rotation_y=90, position=(0,50,0))    # I want to change this to reference the Player class, might need to move stuff from FPC to Player
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

sun = DirectionalLight()
sun.look_at(Vec3(1,-1,-1))
Sky()  # Calls the skybox that makes a sphere around player, I want to change this to a square where the sides and front can paint the sceen

app.run()


#saved for learning soundfx & invoke & delay functions
'''          saved for learning soundfx & invoke & delay functions

def shoot():
    if not gun.on_cooldown:
        # print('shoot')
        gun.on_cooldown = True
        gun.muzzle_flash.enabled=True
        from ursina.prefabs.ursfx import ursfx
        ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise', pitch=random.uniform(-13,-12), pitch_change=-12, speed=3.0)
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.15)

        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 10
            mouse.hovered_entity.blink(color.red)


'''
'''    
Note 1  see collider.py

Note 2

        dist = distance_xz(player.position, self.position)
        if dist > 40:
            self.position += self.forward * time.dt * 15
            return

        #self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)

        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0, 1, 0), self.forward, 30, ignore=(self,))

        if hit_info.entity == player:
            if dist > 2:
                self.position -= self.forward * time.dt * 5
                #txt=Text(text="help!")
            else:
                txt=Text(text="")

        if self.intersects(sword).hit:
            self.blink(color.red)
            self.position -= self.forward * time.dt * 15
            if self.hp <= 0:
                destroy(self)
            else:
                self.hp -= 10
                txt = Text(text="Ouch!")
                is_hit = True

        '''

