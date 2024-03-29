#!/usr/bin/env python

import random
import operator
import functools
import time
import logging
import mechanics
import robot_generator
import weapon_generator
from itertools import compress
from tabulate import tabulate


strategy_map = {0: "Focused",
                1: "Random"}
robot_map = robot_generator.robot_map
weapon_map = weapon_generator.weapon_map
name_map = open('robot_names.txt').read().splitlines()


# For coloring the output
class Colors:
    Red = '\033[31m'
    Blue = '\033[34m'
    Yellow = '\033[33m'
    Purple = '\033[35m'
    endc = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'


def user_input_validation(question, choices):
    print(question)
    while True:
       print(choices)
       choice = input()
       try:
           choice = int(choice)
           if choice in choices:
               return choice
       except:
           pass
       print("Pick a valid choice")
    

class Team:

    def __init__(self, name, size, max_pwrlvl, strategy,
                 random_robots=True, player=False):

        self.name = name
        self.strategy = strategy
        self.ai = True if player is False else False
        if self.ai is True or random_robots is True:

            # Create list of random names, avoiding duplicates
            robot_names = []
            for _ in range(int(size)):
                random_name = random.choice(name_map)
                robot_names.append(random_name)
                name_map.remove(random_name)

            self.robots = [
                (getattr(
                    robot_generator,
                    robot_map[random.randint(0, 3)])(
                        self.name,
                        robot_names[_]
                        ))
                for _ in range(int(size))]
        else:
            self.robots = []
            for _ in range(size):
                robot_type = user_input_validation("Pick robot type:", robot_map)
                weapon_type = user_input_validation("Pick weapon type:", weapon_map)
                type_to_generate = robot_map[int(robot_type)]
                robot_name = random.choice(name_map)
                name_map.remove(robot_name)
                self.robots.append(
                    getattr(
                        robot_generator,
                        type_to_generate)(
                            self.name,
                            robot_name,
                            int(weapon_type)))
                print(f'Creating robot {_}: {self.robots[_].name}\n')

        self.total_hp = sum(robot.hp for robot in self.robots)
        self.alive_robots = [x.alive for x in self.robots].count(True)
        self.acc_average = float("{:.2f}".format(sum((
            robot.weapon.accuracy for robot in self.robots))
            / len(self.robots)))
        self.spd_average = float("{:.2f}".format(sum((
            robot.weapon.speed for robot in self.robots))
            / len(self.robots)))
        self.total_power = sum((robot.weapon.power for robot in self.robots))
        self.powerlevel = int("{:.0f}".format(
            self.total_power * self.acc_average * self.spd_average / 10))

    def describe(self):

        print(f'\n{self.name} Team, '
              f'\n{self.strategy} strategy, '
              f'{len(self.robots)} robots:')
        robots_table = []

        # Sort the robots by speed before presenting them, so it's easier
        # to refer to the table while following the rounds
        robots_by_speed = sorted(
            self.robots,
            reverse=True,
            key=operator.attrgetter('weapon.speed'))

        for robot in robots_by_speed:
            robots_table.append((robot.name,
                                 robot.type,
                                 robot.hp,
                                 robot.armor,
                                 robot.weapon.name,
                                 robot.weapon.power,
                                 robot.weapon.accuracy,
                                 robot.weapon.speed))

        print(tabulate(robots_table, headers=['Name',
                                              'Type',
                                              'HP',
                                              'Armor',
                                              'Weapon',
                                              'Power',
                                              'Accuracy',
                                              'Speed'], tablefmt="fancy_grid"))

        team_table = [(self.total_power,
                       self.acc_average,
                       self.spd_average,
                       self.total_hp,
                       self.powerlevel)]

        print(tabulate(team_table,
                       headers=['TotalPower',
                                'AccAvg',
                                'SpdAvg',
                                'TotalHP',
                                'Powerlevel'], tablefmt="fancy_grid"))


class Battlefield:
    # TODO: - Battlefield climates to affect cooldowns and heat
    # TODO: - Obstacles

    def __init__(self, team1, team2):
        self.teams = []
        self.teams.extend((team1, team2))

    def spread_teams(self):
        self.distance = random.randint(1, 10)
        print(f'The distance betweeen teams is {self.distance}')

    def prepare_turn(self, round, robots):
        """ Recreate alive_robots and begin turn
            Beggining of turn   1 - Stabilize core
                                2 - Cooldown weapons
                                3 - Check status effects besides
                                    heat level ones
                                4 - Present summary
        """

        alive_robots = (x for x in robots if x.alive is True)
        round_table = []
        for robot in alive_robots:
            # 1 - Stabilize core
            robot.core.stabilize(robot)
            # 2 - Cooldown weapons
            robot.weapon.cooldown = robot.weapon.cooldown - 1 \
                if robot.weapon.cooldown > 0 else 0
            # 3 - Remove Shocked status effects
            if "Shocked" in robot.status_effects:
                robot.status_effects.discard("Shocked")
                robot.active = True
            # 4 - Prepare for Summary
            round_table.append((robot.team,
                                robot.name,
                                robot.hp,
                                robot.active,
                                (",".join(robot.status_effects)
                                    if len(robot.status_effects) > 0
                                    else "None"),
                                robot.core.heat))

        # Show robots that will skip the turn and explain why
        print(f'{Colors.bold}Robots for this round summary:'
              f'{round}{Colors.endc}')
        # Sort the list by team color before printing
        round_table.sort(key=lambda tuple: tuple[0])
        print(tabulate(round_table, headers=['Team',
                                             'Name',
                                             'HP',
                                             'Active',
                                             'Status Effects',
                                             'Heat'], tablefmt="fancy_grid"))

        
    def resolve_turn(self, round, robots):
        """ This function receives the robots already ordered by speed
        So all iterators begin with the fastest robot.


        Combat phase        1 - check weapon cooldown
                            2 - check team strategy
                            3 - define target based on strategy
                            4 - check hit or miss
                            5 - resolve damage + status effects

        Ending of turn      1 - Check total hp in teams
        """

        self.prepare_turn(round, robots)

        print(f'{Colors.bold}\nStarting round {round}{Colors.endc}')

        input(f"Ready for combat?\n")

        # Combat phase
        for robot in robots:
            log.debug(f"{robot.name} is resolving his turn..")
            # time.sleep(1)
            if robot.alive is False:
                continue
            if robot.active is False:
                print(f"{getattr(Colors, robot.team)}{robot.name}{Colors.endc}"
                      f" is skipping this turn due to being "
                      f"{next(iter(robot.status_effects))}! "
                      f"Core at {robot.core.heat}.")
                continue

            robot_team = self.teams[1] if self.teams[1].name == robot.team \
                else self.teams[0]
            target_team = self.teams[0] if self.teams[1].name == robot.team \
                else self.teams[1]

            if all(robot.alive is False for robot in target_team.robots):
                continue

            # 1 - check weapon cooldown
            if robot.weapon.cooldown > 0:
                print(f"{getattr(Colors, robot.team)}{robot.name}{Colors.endc}"
                      f"'s weapon is cooling down, "
                      f"{robot.weapon.cooldown} turns remaining.")
                continue

            if robot_team.ai is False:
                print(f'Choose target for {robot.name} ..')

                # available_targets = [robot for robot in target_team.robots
                                     # if robot.alive is True]
                available_targets = {i: robot for (i, robot) in enumerate(target_team.robots)
                                     if robot.alive is True}

                # for i, r in enumerate(available_targets):
                    # print(f'{i} - {r.name}')
                choice = user_input_validation("", available_targets)
                print(choice)
                target = available_targets[choice]
            else:
                # 2 - check team strategy
                strat = getattr(mechanics, "strategy_"
                                + str.lower(robot_team.strategy))
                # 3 - define target based on strategy
                target = strat(robot_team,
                               robot,
                               target_team,
                               self.teams)
            if target is None:  # If there's no more targets end the round
                print(f'{robot.team} has no more targets')
                break

            print(f"{getattr(Colors, robot.team)}{robot.name}{Colors.endc}"
                  f" attacks {getattr(Colors, target.team)}"
                  f"{target.name}{Colors.endc}",
                  end="... ")
            robot.weapon.cooldown = 5 - robot.weapon.speed

            # 4 - check hit or miss
            hit = mechanics.miss_or_hit(robot,
                                        robot.weapon.accuracy,
                                        self.distance)
            if hit == 0:
                print(f'{getattr(Colors, robot.team)}{robot.name}'
                      f'{Colors.endc} misses.')
                continue

            # 5 - resolve damage + status effects
            critical, \
                initial_damage, \
                final_damage, \
                target.hp = mechanics.resolve_damage(robot, target)

            if critical is True:
                print(f'{Colors.bold}{Colors.Yellow}Critical Hit!'
                      f'{Colors.endc}', end=" ")

            if final_damage == 0:
                print(f'The shot from '
                      f'{getattr(Colors, robot.team)}{robot.name}'
                      f'{Colors.endc} hits, but was resisted!',
                      end=" ")
            else:
                print(f"It hits "
                      f"{getattr(Colors, target.team)}{target.name}"
                      f"{Colors.endc} for {final_damage} damage "
                      f"({initial_damage} - {target.armor}).", end=" ")
            if target.hp <= 0:
                target.hp = 0
                target.alive = False
                target.active = False

            if len(target.status_effects) > 0:
                for status in target.status_effects:
                    print(f"{getattr(Colors, target.team)}{target.name}"
                          f"{Colors.endc}{Colors.Yellow}"
                          f"'s {status}"
                          f"{Colors.endc},",
                          end=" ")

            if target.alive is False:
                print(f'{getattr(Colors, target.team)}{target.name} '
                      f'is dead.{Colors.endc}')

            else:
                print(f'{target.hp} HP remains!')

        for team in self.teams:
            team.alive_robots = [x.alive for x in team.robots].count(True)
            team.total_hp = sum(robot.hp for robot in team.robots)

        print(f'\nEnding round {round}')
        input()
        for team in self.teams:
            print(f'{team.alive_robots} robots '
                  f'on team {getattr(Colors, team.name)}'
                  f'{team.name}{Colors.endc} survived')

    def resolve_battle(self):
        print(f'\nStarting battle!')
        self.spread_teams()
        robots_by_speed = sorted(
            (self.teams[1].robots + self.teams[0].robots),
            reverse=True,
            key=operator.attrgetter('weapon.speed'))
        round = 1

        # TODO: This will be a problem in the future
        #       because the combat can end if there are still
        #       robot.hp > 0 in some teams

        while all(team.alive_robots > 0 for team in self.teams):
            self.resolve_turn(round, robots_by_speed)
            round += 1

        if all(team.total_hp <= 0 for team in self.teams):
            print(f"\nNo robot survived.. it's a draw!")
            return

        winning_team = None
        winner = 0
        for team in self.teams:
            if team.alive_robots > winner:
                winner = team.alive_robots
                winning_team = team.name

        print(f'{getattr(Colors, winning_team)}\n{winning_team}'
              f' wins with {winner} robots alive remaining!{Colors.endc}')


if __name__ == '__main__':

    logging.basicConfig()
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    log.debug(f"BEGIN DEBUG LOGGING")
    # Define battle parameters
    # max_pwrlvl = input(f'What is the max powerlevel per team? ')
    max_pwrlvl = 100
    team_size = int(input(f'What is the number of robots per team? '))
    random_robots_choice = input(f'Random robots? y/n ')
    random_robots = True if random_robots_choice == "y" else False
    # Create player team based on input
    # player_team_name = input(f"What's the team color? ")
    player_team_name = "Blue"
    strategy = user_input_validation("Pick strategy for targetting:", strategy_map)
    player_team = Team(player_team_name,
                       team_size,
                       max_pwrlvl,
                       strategy_map[strategy],
                       random_robots,
                       True)
    player_team.describe()

    # Create AI team
    red_team = Team("Red",
                    team_size,
                    max_pwrlvl,
                    strategy_map[strategy],
                    False)
    # blue_team = Team("Blue",
    #                  team_size,
    #                  max_pwrlvl,
    #                  "Random",
    #                  False)

    red_team.describe()
    # blue_team.describe()

    # Battle
    Battlefield(red_team, player_team).resolve_battle()
