#!/usr/local/opt/python/bin/python3.7
import random
from robot_generator import Robot
from tabulate import tabulate


class Team:

    def __init__(self, player=False, color, size):

        self.color = color
        self.robots = {Robot() for _ in range(size)}
        self.total_hp = sum(robot.hp for robot in self.robots)
        self.acc_average = float("{:.2f}".format(sum((
            robot.weapon.accuracy for robot in self.robots))
            / len(self.robots)))
        self.spd_average = float("{:.2f}".format(sum((
            robot.weapon.speed for robot in self.robots))
            / len(self.robots)))
        self.total_power = sum((robot.weapon.power for robot in self.robots))
        self.powerlevel = int("{:.0f}".format(
            (self.total_power * self.acc_average * len(self.robots)) / 3))

    def describe(self):

        print(f'\n{self.color} Team, {len(self.robots)} robots:')
        robots_table = []
        for robot in self.robots:
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

    def miss_or_hit(self, robot, weapon_acc, distance):
        if (weapon_acc / distance / random.random()) >= 0.5:
            return 1
        else:
            return 0

    def resolve_damage(self, robot, target):
        initial_damage = int(robot.weapon.power * random.uniform(0.9, 1.1))
        critical = True if (
            float("{:.2f}".format(random.random()))) >= 0.9 else False
        initial_damage = int(
            initial_damage * 1.5) if critical is True else initial_damage
        final_damage = max(initial_damage - target.armor, 0)

        if critical is True:
            print(f'Critical Hit!', end=" ")

        if final_damage == 0:
            print(f'The shot from {robot.name} hits, but was resisted!',
                  end=" ")
        else:
            print(f"It hits {target.name} for {final_damage} damage"
                  f" ({initial_damage} - {target.armor}).", end=" ")

        target.hp -= final_damage

        return

    def resolve_turn(self, round):

        round
        print(f'\n###### Starting round {round} ######\n')

        random.shuffle(self.teams)

        for index, team in enumerate(self.teams):
            print(f'\n{team.color} team turn!\n')

            for robot in team.robots:

                if robot.alive is False:
                    continue

                if any(robot.alive for robot in self.teams[index - 1].robots):
                    target = random.choice(
                             list(
                              robot for robot in self.teams[index - 1].robots
                              if robot.alive is True))
                else:
                    print(f'{robot.name} has no more targets')
                    continue

                if robot.cooldown <= 0:
                    print(f'{robot.name} fires at {target.name}', end="... ")
                    robot.cooldown = 5 - robot.weapon.speed
                    hit = self.miss_or_hit(robot,
                                           robot.weapon.accuracy,
                                           self.distance)
                    if hit == 0:
                        print(f'{robot.name} misses.')
                        continue

                    self.resolve_damage(robot, target)

                    if target.hp <= 0:
                        target.hp = 0
                        target.alive = False
                        print(f'{target.name} was destroyed!')
                    else:
                        print(f'{target.hp} HP remains!')

                else:
                    print(f"{robot.name}'s weapon is cooling down, "
                          f"{robot.cooldown} turns remaining.")
                    robot.cooldown -= robot.weapon.speed

        for team in self.teams:
            team.total_hp = sum(robot.hp for robot in team.robots)

        print(f'\nEnding round {round}')
        for team in self.teams:
            print(f'{(sum([robot.alive for robot in team.robots]))} robots '
                  f'on team {team.color} survived')
        input("Press Enter to continue...")

    def resolve_battle(self):
        print(f'\nStarting battle!')
        self.spread_teams()
        round = 1

        while all(team.total_hp > 0 for team in self.teams):
            self.resolve_turn(round)
            round += 1

        if all(team.total_hp <= 0 for team in self.teams):
            print(f"\nNo robot survived.. it's a draw!")
            return

        winning_team = None
        winner = 0
        for team in self.teams:
            print(f'{team.color} finished with {team.total_hp} HP remaining!')
            if team.total_hp > winner:
                winner = team.total_hp
                winning_team = team.color

        print(f'\n{winning_team} wins!')


if __name__ == '__main__':

    red_team = Team("Red", (random.randint(7, 7)))
    player_team = Team(True, team_name, 7)
    red_team.describe()
    player_team.describe()

    Battlefield(red_team, player_team).resolve_battle()
