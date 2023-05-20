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
        -Check player input, player keys, Enemy update and collision checks!
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
from player import Player     # I want to move the player entity to another file
#from enemy import Enemy      # I want to move the enemy AI to another file
#from collider import ObjectCollider      # use this to make a collider based on a .obj size

app = Ursina()


sword_model = load_model('Katana_LP_Final.obj')
# trying the different textures that came with the 3d model, none seem to work and i am not sure what to do with the texture
#sword_texture = load_texture('assets/sword.png')
#sword_texture = load_texture('Katana_d.tga')
#sword_texture = load_texture('Katana_n.tga')
grass_texture = load_texture('assets/grass_block.png')

random.seed(0)  # not sure what this does
Entity.default_shader = lit_with_shadows_shader  # im assuming a shader

#stops editor camera ?  err engages pause camera
editor_camera = EditorCamera(enabled=False, ignore_paused=True)

#ENTITYS

# floor to map, will need to use a custom model for a rectangle, using voxel cubes uses to much fps
ground = Entity(model='plane', collider='box', scale=(64), texture='grass', texture_scale=(4,4))

# The code below is creating the sword entity
sword = Entity(model=sword_model, parent=camera, position=(0, -.2, 3), scale=(.005, .005, .005), rotation=(0, 0, -90), color=color.dark_gray)
sword_size = Vec3(717.347, 58.9473, 57.7639)  #See see collider.py to call the class or pregenerate vector3
sword.collider = BoxCollider(sword, center=(0, 0, 0), size=sword_size)


shootables_parent = Entity()  # Target for raytracing ???? residual code from ursinafps game
sword_target = Entity()
mouse.traverse_target = shootables_parent   # Not sure about this, but it should go soon

'''
# This creates the floor and boxes that have clickable features (like changing color) and I thought it would be better then 1 large ground texture
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
    def __init__(self,max_hp, **kwargs):
        super().__init__(parent=sword_target, model='cube', scale_y=2, origin_y=-.5, color=color.light_gray, **kwargs)
        self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, scale=(1.5, .1, .1))
        self.max_hp = max_hp
        self._hp = self.max_hp
        # Add BoxCollider component
        self.collider = BoxCollider(self, size=self.scale)

    def update(self):
        self.look_at_2d(player.position, 'y') # not sure what this does or y but Enemy goes weird directions if off
        #player_dist = raycast(self.world_position + Vec3(0, 1, 0), self.forward, 30, ignore=(self,))
        dist = distance_xz(player.position, self.position) # checks the distance to player

        #this part changes the Enemy distance from player
        if dist > 40:
            self.color = color.red
            self.position += self.forward * time.dt * random.uniform(1, 5)
        elif dist > 7:
            self.position += self.forward * time.dt * random.uniform(1, 5)
            self.health_bar.alpha = 0      #Hides HP bar when far away from player
            #txt = Text(text="Charge!")
        elif dist > .1:
            self.position -= self.forward * time.dt * random.uniform(1, 5)
            #txt = Text(text="I'll get you!")

        # check to see if Enemy intersects the sword entity if so flash red, - hp
        if self.intersects(sword).hit:
            self.blink(color.red)
            if self.hp <= 0:        #I put this here b/c getting missing obj err if hp < 0 b4
                destroy(self)
            else:
                self.hp -= 1    #Set sword damage here
                #txt = Text(text="Ouch!")
                #self.animate('position_y', self.position + 90, duration=.2)
                #self.animate_position(self.position + Vec3(-5, 0, 0), duration=.2)
                #self.position -= self.forward * time.dt * 15
        #see Note 2 for original version
    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:
            destroy(self)
            return

        self.health_bar.scale_x = self.hp / self.max_hp * 1.5        # Enemy Health bar
        self.health_bar.alpha = 1                                    # shows the HP when hit



def input(key):                #May need to look at changing all the "if"s to elifs or other changes to improve fps
    #forwards and backwards
    if key == 'w':              #For moving forward 1 square
        player.position += player.forward
        sword.rotation = (0, 0, -90)
        #player.position_y = (5)
    if held_keys['w']:          #For running forward  this may need work when I have things hit the player
        player.position += player.forward
    if key == 'd':
        player.position -= player.forward
    if held_keys['d']:
        player.position -= player.forward
        sword.rotation = (0, 0, -90)

    # Left and right (for turning around)
    if key == 'a':
        player.animate('rotation_y', player.rotation_y + 180, duration=.3)
    if key == 'd':
        player.animate('rotation_y', player.rotation_y - 180, duration=.3)
    # See Notes 1   bug when spamming key

    #Swing left and right
    if key == 'left arrow':
        swing_right()
    if key == 'right arrow':
        swing_left()
def swing_left():
    sword.rotation = (0,0,-90)                                         # reset sword position
    sword.position = (0, -.9, 3)                                       # move sword down some
    sword.animate('rotation_z', sword.rotation_z + 90, duration=.12)    # sword swing down from center
    sword.animate('rotation_y', sword.rotation_y - 90, duration=.12)
    #sword.animate('rotation_z', sword.rotation_z - 90, duration=.03)  # sword swing down from center
    #sword.animate('rotation_y', sword.rotation_y + 90, duration=.03)
    # sword swing forwards
def swing_right():
    sword.rotation = (0, 0, -90)                                        # reset sword position
    sword.position = (0, -.9, 3)                                        # move sword down some
    sword.animate('rotation_z', sword.rotation_z - 90, duration=.12)     # sword swing down from center
    sword.animate('rotation_y', sword.rotation_y + 90, duration=.12)     # sword swing forwards

def update():
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
#This makes the ground, could do more depending on how to switch levels
# Turned off right now as it leads to a big drop in framrate
for z in range(3):
    for x in range(40):
        voxel = Voxel(position = (x,0,z))

'''
# Calls Enemy entity
enemies = [Enemy(x=x*4,max_hp=100) for x in range(4)]  # summons 4 enemies with 100 hp
#enemies = [Enemy(x=x*4, max_hp=random.uniform(50, 150)) for x in range(random.uniform(1,4))] # More random added
#enemies = Enemy(max_hp=100)  #for summoning 1 enemy



player = FirstPersonControllerCustom(rotation_y=90)    # I want to change this to reference the Player class, might need to move stuff from FPC to Player
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))
#sword.collider = MeshCollider(sword, center=sword.model.center, size=sword.model.size)


sun = DirectionalLight()
sun.look_at(Vec3(1,-1,-1))
Sky()  # Calls the skybox that makes a sphere around player, I want to change this to a square where the sides and front can paint the sceen

app.run()





'''


'''
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
