#!/usr/local/opt/python/bin/python3.7
import random
import operator
import mechanics
from robot_generator import Robot
from tabulate import tabulate

strategy_map = {0: "Focused",
                1: "Random"}


# For coloring the output
class colors:
    Red = '\033[31m'
    Blue = '\033[34m'
    Yellow = '\033[33m'
    Purple = '\033[35m'
    endc = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'


class Team:

    def __init__(self, name, size, max_pwrlvl, strategy, player=False):

        self.name = name
        self.strategy = strategy
        self.ai = True if player is False else False
        if self.ai is True:
            self.robots = [Robot(self.name) for _ in range(int(size))]
        else:
            self.robots = []
            for _ in range(size):
                robot_type = input("Pick robot type: "
                                   + "0:tank|"
                                   + "1:assault|"
                                   + "2:support|"
                                   + "3:gunner)")
                weapon_type = input("Pick weapon type: "
                                    + "0:rifle|"
                                    + "1:sniper|"
                                    + "2:cannon|"
                                    + "3:handgun)")
                self.robots.append(Robot(self.name, robot_type, weapon_type))
                print(f'Creating robot {_}: {self.robots[_].name}\n')

        self.total_hp = sum(robot.hp for robot in self.robots)
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

    def __init__(self, team1, team2):
        self.teams = []
        self.teams.extend((team1, team2))

    def spread_teams(self):
        self.distance = random.randint(1, 10)
        print(f'The distance betweeen teams is {self.distance}')

    def resolve_turn(self, round, robots):
        """ The turn is divided into 4 phases:
        Beggining of turn - cooldown weapons,
                          - cooldown robot (heat)



        """

        print(f'\n###### Starting round {round} ######\n')

        # Beggining of turn:
        for robot in robots:
            robot.cooldown = robot.cooldown - 1 if robot.cooldown > 0 else 0
            robot.heat = robot.heat - 25 if robot.heat > 100 else 100
            if robot.heat >= 150:
                robot.active = False
                print(f"{getattr(colors, robot.team)}{robot.name}{colors.endc}"
                      f"'s is too hot to function!"
                      f"Shutting down to cool off")

        for robot in robots:

            if robot.alive is False or robot.active is False:
                continue

            robot_team = self.teams[1] if self.teams[1].name == robot.team \
                else self.teams[0]
            target_team = self.teams[0] if self.teams[1].name == robot.team \
                else self.teams[1]

            strat = getattr(mechanics, "strategy_"
                            + str.lower(robot_team.strategy))
            target = strat(robot_team,
                           robot,
                           target_team,
                           self.teams)
            if target is None:
                print(f'{robot.team} has no more targets')
                break

            if robot.cooldown <= 0:
                print(f"{getattr(colors, robot.team)}{robot.name}{colors.endc}"
                      f" fires at {getattr(colors, target.team)}"
                      f"{target.name}{colors.endc}",
                      end="... ")
                robot.cooldown = 5 - robot.weapon.speed
                hit = mechanics.miss_or_hit(robot,
                                            robot.weapon.accuracy,
                                            self.distance)
                if hit == 0:
                    print(f'{getattr(colors, robot.team)}{robot.name}'
                          f'{colors.endc} misses.')
                    continue

                critical, \
                    initial_damage, \
                    final_damage, \
                    target.hp = mechanics.resolve_damage(robot, target)

                if target.alive is False:
                    print(f'{getattr(colors, target.team)}{target.name} '
                          f'is dead.{colors.endc}')

                else:
                    if critical is True:
                        print(f'{colors.bold}{colors.Yellow}Critical Hit!'
                              f'{colors.endc}', end=" ")

                    if final_damage == 0:
                        print(f'The shot from '
                              f'{getattr(colors, robot.team)}{robot.name}'
                              f'{colors.endc} hits, but was resisted!',
                              end=" ")
                    else:
                        print(f"It hits "
                              f"{getattr(colors, target.team)}{target.name}"
                              f"{colors.endc} for {final_damage} damage "
                              f"({initial_damage} - {target.armor}).", end=" ")

                    if target.hp <= 0:
                        target.hp = 0
                        target.alive = False
                        print(f'{getattr(colors, target.team)}{target.name}'
                              f' {colors.underline}{colors.Purple}'
                              f'was destroyed!{colors.endc}')
                    else:
                        print(f'{target.hp} HP remains!')

            else:
                print(f"{getattr(colors, robot.team)}{robot.name}{colors.endc}"
                      f"'s weapon is cooling down, "
                      f"{robot.cooldown} turns remaining.")

        for team in self.teams:
            team.total_hp = sum(robot.hp for robot in team.robots)

        print(f'\nEnding round {round}')
        for team in self.teams:
            print(f'{(sum([robot.alive for robot in team.robots]))} robots '
                  f'on team {getattr(colors, team.name)}'
                  f'{team.name}{colors.endc} survived')
        input("Press Enter to continue...")

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

        while all(team.total_hp > 0 for team in self.teams):
            self.resolve_turn(round, robots_by_speed)
            round += 1

        if all(team.total_hp <= 0 for team in self.teams):
            print(f"\nNo robot survived.. it's a draw!")
            return

        winning_team = None
        winner = 0
        for team in self.teams:
            if team.total_hp > winner:
                winner = team.total_hp
                winning_team = team.name

        print(f'{getattr(colors, winning_team)}\n{winning_team}'
              f' wins with {team.total_hp} HP remaining!{colors.endc}')


if __name__ == '__main__':

    # Define battle parameters
    # max_pwrlvl = input(f'What is the max powerlevel per team? ')
    max_pwrlvl = 100
    team_size = int(input(f'What is the number of robots per team? '))
    strategy = int(input("Pick strategy for round:\n"
                         + "0: Focused\n"
                         + "1: Random\n"))

    # Create player team based on input
    # player_team_name = input(f"What's the team color? ")
    player_team_name = "Blue"
    player_team = Team(player_team_name,
                       team_size,
                       max_pwrlvl,
                       strategy_map[strategy],
                       True)

    # Create AI team
    red_team = Team("Red",
                    team_size,
                    max_pwrlvl,
                    "Focused",
                    False)
    # blue_team = Team("Blue", team_size, max_pwrlvl, False)

    # Pre battle start
    red_team.describe()
    # blue_team.describe()
    player_team.describe()

    # Battle
    Battlefield(red_team, player_team).resolve_battle()
