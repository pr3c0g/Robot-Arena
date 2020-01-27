#!/usr/local/opt/python/bin/python3.7
import random
import string
import logging
import operator
from itertools import compress

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# All status effects and their messages
# TODO: Create a separate json or something with this
status_effects_map = {
                        "Melted": "head melted off!",
                        "Overheating": "too hot, and has to shutdown!",
                        "Frozen": "frozen!"
                     }


def strategy_random(active_team, active_robot, target_team, teams):
    """ Combat strategy for randomly selecting targets"""

    if not any(robot.alive for robot in target_team.robots):
        return None

    target = random.choice(list(
                robot
                for robot in target_team.robots
                if robot.alive is True))

    return target


def strategy_focused(active_team, active_robot, target_team, teams):
    """ Combat strategy for focusing on the target
    with the least HP.
    TODO: Create modifications for targetting:
        - Snipers or other weapon type
        - Highest damange output enemy
        - Quickest enemies
    """

    if not any(robot.alive for robot in target_team.robots):
        return None

    available_targets = [robot for robot in target_team.robots
                         if robot.alive is True]
    active_targets = [robot.active for robot in available_targets]
    filtered_targets = list(compress(available_targets, active_targets))
    log.debug(f'All available targets : {available_targets}')
    log.debug(f'All active targets : {active_targets}')

    if len(available_targets) >= 1 and len(filtered_targets) >= 1:
        log.debug(f"I'm looking for the lowest HP in {filtered_targets}")
        lowest_hp_first = sorted(filtered_targets,
                                 key=operator.attrgetter('hp'))
        log.debug(f"Decided with {lowest_hp_first[0]}")
        target = lowest_hp_first[0]
    elif len(active_targets) <= 0:
        log.debug(f"No active targets, so I'll pick "
                  f"the lowest HP from all the live ones")
        target = min(robot.hp for robot in available_targets)
    else:
        log.debug(f"There's noone else  alive in the target team")
        target = None
    return target


def miss_or_hit(robot, weapon_acc, distance):
    """ Calculate if attack hits or misses
    TODO: In the future it would be nice to have in account
    things like obstacles, climate and other battlefield
    modifiers

    There's also the possibility this will be merged
    with the resolve damage function
    """
    if (weapon_acc / distance / random.random()) >= 0.5:
        return 1
    else:
        return 0


def resolve_damage(robot, target):
    initial_damage = int(robot.weapon.power * random.uniform(0.9, 1.1))
    critical = True if (
        float("{:.2f}".format(random.random()))) >= 0.9 else False
    initial_damage = int(
        initial_damage * 1.5) if critical is True else initial_damage
    final_damage = max(initial_damage - target.armor, 0)

    target.hp -= final_damage

    status_effect = apply_status_effects(robot.weapon, target)

    return critical,\
        initial_damage,\
        final_damage,\
        target.hp


def apply_status_effects(weapon, target):
    """Damage types cause different effects:
    Lava    - causes a lot of heat and has a chance to melt off the target
    Shock   - has a chance to short circuit the target
    Laser   - causes heat and has a chance to cut off the target
    Frost   - causes cold and has a chance to freeze the target
    """

    if weapon.dmg_type == "Lava":
        # TODO: Check resistance to damage type before melting
        chance = float("{:.2f}".format(random.random()))
        log.debug(f'Lava status effect rolled a {chance}')

        if chance >= 0.93:
            target.status_effects.add("Melted")
            target.core.increase_heat(250)
            target.alive = False
            return

        log.debug(f'Increasing heat by 75 because of Lava')
        target.core.increase_heat(75)
        target.check_core()


if __name__ == "__main__":
    logging.basicConfig()
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
