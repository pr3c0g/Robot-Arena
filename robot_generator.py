#!/usr/local/opt/python/bin/python3.7
import random
from tabulate import tabulate
from weapon_generator import Weapon
robot_map = {0: 'tank',
             1: 'assault',
             2: 'support',
             3: 'gunner'}


class Robot:

    def __init__(self, team, robot_type=None, weapon_type=None):
        self.type = get_random_robot_type() \
                    if robot_type is None else robot_map[int(robot_type)]

        self.hp, \
            self.armor, \
            self.weapon_modifiers = globals()["generate_" + self.type]()

        name_list = open('robot_names.txt').read().splitlines()
        self.name = random.choice(name_list)
        self.team = team
        self.weapon = Weapon() if weapon_type is None else Weapon(weapon_type)
        self.weapon.power, \
            self.weapon.accuracy, \
            self.weapon.speed = self._apply_weapon_modifiers()
        self.cooldown = 0
        self.heat = 100
        self.active = True
        self.alive = True

    def _apply_weapon_modifiers(self):
        power = max(
                self.weapon_modifiers["wpn_pwr_mod"]
                + self.weapon.power, 1)
        accuracy = max(
                   self.weapon_modifiers["wpn_acc_mod"]
                   + self.weapon.accuracy, 1)
        speed = max(
                self.weapon_modifiers["wpn_spd_mod"]
                + self.weapon.speed, 1)

        return power, accuracy, speed

    def _describe(self):
        table = []
        table.append((self.name,
                      self.type,
                      self.hp,
                      self.armor,
                      self.weapon.name,
                      self.weapon.power,
                      self.weapon.accuracy,
                      self.weapon.speed))

        print(tabulate(table, headers=['Name',
                                       'Type',
                                       'HP',
                                       'Armor',
                                       'Weapon',
                                       'Power',
                                       'Accuracy',
                                       'Speed'], tablefmt="fancy_grid"))


def get_random_robot_type():
    return robot_map[random.randint(0, 3)]


def generate_tank():
    hp = random.randint(70, 80)
    armor = 3
    weapon_modifiers = {"wpn_pwr_mod": 2,
                        "wpn_spd_mod": -1,
                        "wpn_acc_mod": 0}

    return hp, armor, weapon_modifiers


def generate_gunner():
    hp = random.randint(50, 60)
    armor = 1
    weapon_modifiers = {"wpn_pwr_mod": 1,
                        "wpn_spd_mod": 1,
                        "wpn_acc_mod": 1}

    return hp, armor, weapon_modifiers


def generate_assault():
    hp = random.randint(45, 55)
    armor = 0
    weapon_modifiers = {"wpn_pwr_mod": 0,
                        "wpn_spd_mod": 3,
                        "wpn_acc_mod": -1}

    return hp, armor, weapon_modifiers


def generate_support():
    hp = random.randint(40, 50)
    armor = 2
    weapon_modifiers = {"wpn_pwr_mod": 1,
                        "wpn_spd_mod": 0,
                        "wpn_acc_mod": 2}

    return hp, armor, weapon_modifiers


if __name__ == '__main__':
    Robot("red", 0, 0)._describe()
    Robot("red")._describe()
