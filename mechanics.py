#!/usr/local/opt/python/bin/python3.7
import random
import string


def strategy_random(active_team, active_robot, target_team, teams):

    if not any(robot.alive for robot in target_team.robots):
        return None

    target = random.choice(list(
                robot
                for robot in target_team.robots
                if robot.alive is True))

    return target


def strategy_focused(active_team, active_robot, target_team, teams):

    if not any(robot.alive for robot in target_team.robots):
        return None

    available_targets = [robot for robot in target_team.robots
                         if robot.alive is True]
    if len(available_targets) >= 1:
        target = available_targets[0]
        for a_target in available_targets:
            target = a_target \
                     if a_target.hp == min(a_target.hp for a_target in
                                           available_targets) \
                     else target

    return target


def miss_or_hit(robot, weapon_acc, distance):
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
    status_effect_text = ""
    if weapon.dmg_type == "Lava":

        if float("{:.2f}".format(random.random())) >= 0.85:
            target.status_effects.append("Melted")
            target.alive = False
            target.hp = 0

        target.heat += 25


status_effects_map = {"Melted": "head melted off!"}
