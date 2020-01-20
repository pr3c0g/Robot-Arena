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

    return critical, initial_damage, final_damage, target.hp

    # if critical is True:
    #     print(f'{colors.bold}{colors.Yellow}Critical Hit!{colors.endc}',
    #           end=" ")

    # if final_damage == 0:
    #     print(f'The shot from '
    #           f'{getattr(colors, robot.team)}{robot.name}{colors.endc}'
    #           f' hits, but was resisted!',
    #           end=" ")
    # else:
    #     print(f"It hits "
    #           f"{getattr(colors, target.team)}{target.name}{colors.endc}"
    #           f" for {final_damage} damage ({initial_damage}"
    #           f" - {target.armor}).", end=" ")

    # target.hp -= final_damage

    # return
