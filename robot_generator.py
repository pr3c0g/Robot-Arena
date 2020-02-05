#!/usr/local/opt/python/bin/python3.7
import random
import logging
from mechanics import status_effects_map
from weapon_generator import Weapon

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

robot_map = {0: 'Tank',
             1: 'Assault',
             2: 'Support',
             3: 'Gunner'}


class Robot:

    def __init__(self, team, name, weapon_type=None):

        # Create core
        self.core = Core()

        self.name = name
        self.team = team

        # Robot weapons
        self.weapon = Weapon() if weapon_type is None else Weapon(weapon_type)

        # Status effects is declared as a set to have unique values
        # TODO: Think about better ways to handle status effects
        self.status_effects = set()

        # General states for the Robot
        self.active = True
        self.alive = True

    def check_core(self):
        self.core.check_level(self)

    def __repr__(self):
        return f"{self.name}"
        # return (f'{self.name}|'
        #         f'{self.type}|'
        #         f'HP:{self.hp}|'
        #         f'ARM:{self.armor}|'
        #         f'{self.weapon.name}|'
        #         f'PWR:{self.weapon.power}|'
        #         f'ACC:{self.weapon.accuracy}|'
        #         f'SPD:{self.weapon.speed}\n'
        #         f'CORE:{repr(self.core)}')

    def __str__(self):
        return f"{self.name}"


class Core:
    """ This is the Core class that is created
    during the Robot class init, that handles
    the heat mechanic.
    TODO:
    - Implement other effects / events
    regarding the core and damage types
    - Think about soul/spirit concept and
    implement it into the core
    """

    def __init__(self):
        self.optimal_heat = 100
        self.heat = 100
        self.heat_max_threshold = 175
        self.heat_min_threshold = 0
        self.heat_dissipation = 25
        self.heat_generation = 25

    def increase_heat(self, qt):
        self.heat += qt

    def decrease_heat(self, qt):
        self.heat -= qt

    def stabilize(self, owner):
        # Attempt to stabilize at optimal heat
        log.debug(f"{owner}'s core is at {self.heat}")
        self.heat = self.heat + self.heat_generation \
            if self.heat < self.optimal_heat \
            else self.heat
        self.heat = self.heat - self.heat_dissipation \
            if self.heat > self.optimal_heat \
            else self.heat
        log.debug(f'Stabilized at {self.heat}')
        self.check_level(owner)

    def check_level(self, owner):
        log.debug(f'Checking if {owner.name} robot.active has to switch, '
                  f'currently at {owner.active}')

        if self.heat > self.heat_max_threshold:
            if "Overheating" not in owner.status_effects:
                print(f'It is now {status_effects_map["Overheating"]}')
            owner.status_effects.add("Overheating")
            owner.status_effects.discard("Frozen")
            owner.active = False
            log.debug(f'Active: {owner.active}')
            return

        if self.heat < self.heat_min_threshold:
            if "Frozen" not in owner.status_effects:
                print(f'It is now {status_effects_map["Frozen"]}')
            owner.status_effects.add("Frozen")
            owner.status_effects.discard("Overheating")
            owner.active = False
            log.debug(f'Active: {owner.active}')
            return

        owner.status_effects.discard("Frozen")
        owner.status_effects.discard("Overheating")
        owner.active = True
        log.debug(f'Active: {owner.active}')

    def __str__(self):
        return f"Current heat at {self.heat}"

    def __repr__(self):
        return (f'LVL:{self.heat}|'
                f'OPT:{self.optimal_heat}|'
                f'MAX:{self.heat_max_threshold}|'
                f'MIN:{self.heat_min_threshold}|'
                f'DIS:{self.heat_dissipation}|'
                f'GEN:{self.heat_generation}')


# TODO: The following functions should eventually be replaced
# with class inheritance
def get_random_robot_type():
    return robot_map[random.randint(0, 3)]


class Tank(Robot):
    def __init__(self, team, name, weapon_type=None):
        self.type = "Tank"
        super().__init__(team, name, weapon_type)
        self.hp = random.randint(200, 230)
        self.armor = 3
        self.weapon.power += 2
        self.weapon.speed -= 1
        # self.weapon.accuracy += 1


class Gunner(Robot):
    def __init__(self, team, name, weapon_type=None):
        self.type = "Gunner"
        super().__init__(team, name, weapon_type)
        self.hp = random.randint(150, 175)
        self.armor = 1
        self.weapon.power += 1
        self.weapon.speed += 1
        self.weapon.accuracy += 1


class Assault(Robot):
    def __init__(self, team, name, weapon_type=None):
        self.type = "Assault"
        super().__init__(team, name, weapon_type)
        self.hp = random.randint(100, 125)
        self.armor = 0
        # self.weapon.power += 1
        self.weapon.speed += 3
        self.weapon.accuracy -= 1


class Support(Robot):
    def __init__(self, team, name, weapon_type=None):
        self.type = "Support"
        super().__init__(team, name, weapon_type)
        self.hp = random.randint(125, 150)
        self.armor = 2
        self.weapon.power += 1
        #  self.weapon.speed += 1
        self.weapon.accuracy += 2


if __name__ == '__main__':

    example = Support("red", "Bot")
    print(repr(example))

    print("RANDOM:")
    print(repr(globals()[robot_map[random.randint(0, 3)]]("Red", "RandomBot")))
