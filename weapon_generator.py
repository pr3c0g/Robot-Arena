#!/usr/local/opt/python/bin/python3.7
import random
import string

weapon_map = {0: "rifle",
              1: "sniper",
              2: "cannon",
              3: "handgun"}


class Weapon:

    def __init__(self, weapon_type=None):
        self.type = get_random_weapon_type() \
            if weapon_type is None else weapon_map[int(weapon_type)]
        self.dmg_type = get_random_dmg_type()

        self.traits = get_random_traits()
        self.name = ' '.join(
                        (' '.join(trait for trait in self.traits
                                  if trait is not None),
                            self.dmg_type,
                            string.capwords(self.type)))
        self.power, \
            self.accuracy, \
            self.speed = globals()["generate_" + self.type]()

    def _describe(self):
        print(f'{self.name}')
        print(f'Power: {self.power}')
        print(f'Speed: {self.speed}')
        print(f'Accuracy: {self.accuracy}')


def get_random_traits():

    weapon_traits = [random.choice(['High-speed',
                                    'Long-range',
                                    'Rapid-fire',
                                    'Multi-shot',
                                    'Charging'])]

    weapon_traits.append(random.choice(['Piercing',
                                        'Destroyer',
                                        'Obliterating',
                                        'Annihilating',
                                        None]))
    return weapon_traits


def get_random_weapon_type():
    # weapon_type = ['rifle', 'sniper', 'cannon', 'handgun']
    # return random.choice(weapon_type)
    return weapon_map[random.randint(0, 3)]


def get_random_dmg_type():
    dmg_type = ['Lava',
                'Frost',
                'Shock',
                'Mecha'
                'Laser']
    return random.choice(dmg_type)


def generate_rifle():
    power = random.randint(15, 20)
    accuracy = random.randint(3, 3)
    speed = 4

    return power, accuracy, speed


def generate_sniper():
    power = random.randint(25, 30)
    accuracy = random.randint(4, 5)
    speed = 1

    return power, accuracy, speed


def generate_cannon():
    power = random.randint(30, 40)
    accuracy = random.randint(1, 2)
    speed = 1

    return power, accuracy, speed


def generate_handgun():
    power = random.randint(18, 23)
    accuracy = random.randint(3, 3)
    speed = 3

    return power, accuracy, speed


if __name__ == '__main__':
    Weapon(0)._describe()
    Weapon(1)._describe()
    Weapon(2)._describe()
    Weapon(3)._describe()
