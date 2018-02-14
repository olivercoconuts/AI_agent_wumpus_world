# ======================================================================
# FILE:        MyAI.py
#
# AUTHOR:      Oliver Chen
#
# DESCRIPTION: This file contains your agent class, which you will
#              implement. You are responsible for implementing the
#              'getAction' function and any helper methods you feel you
#              need.
#
# NOTES:       - If you are having trouble understanding how the shell
#                works, look at the other parts of the code, as well as
#                the documentation.
#
#              - You are only allowed to make changes to this portion of
#                the code. Any changes to other portions of the code will
#                be lost when the tournament runs your code.
# ======================================================================

from Agent import Agent
from sys import maxsize
from collections import defaultdict
from queue import PriorityQueue

class MyAI ( Agent ):

    def __init__ ( self ):
    # ======================================================================
    # YOUR CODE BEGINS
    # ======================================================================
        self.pos = (1, 1)
        self.dir = 3  # Down - 0; Left - 1; Up - 2; Right - 3
        self.turning = False
        self.desired_dir = -1
        self.wumpus_alive = True
        self.wumpus_unique = False
        self.has_arrow = True
        self.shot_arrow = False
        self.turned_before_go_home = False
        self.finished = False
        self.moves = 0
        self.visited = {(1, 1)}
        self.world= defaultdict(set)
        self.top_boundary = maxsize
        self.right_boundary = maxsize
        self.move_types = [Agent.Action.TURN_LEFT,
                   Agent.Action.TURN_RIGHT,
                   Agent.Action.FORWARD]

    def getAction(self, stench, breeze, glitter, bump, scream ):
        if self.finished:
            action = self._go_home()
        elif glitter:
            action = Agent.Action.GRAB
            self.finished = True
        elif self.turning:
            action = self._turn()
        else:
            self._remember(stench, breeze, bump, scream)
            if breeze:
                self._predict_danger('pit', 'breeze')
            if stench and self.wumpus_alive:
                self._predict_danger('wumpus', 'stench')
            if float(self.moves) / len(self.visited) > 3.9:
                self.finished = True
                action = self._go_home()
            elif 'wumpus' in self.world[self._postion_ahead()] and self.has_arrow \
                                and 'pit' not in self.world[self._postion_ahead()]:
                self.shot_arrow = True
                action = Agent.Action.SHOOT
            else:
                dir = self._decide_dir()
                if type(dir) is int:
                    self.desired_dir = dir
                    if self.desired_dir != self.dir:
                        self.turning = True
                        action = self._turn()
                    else:
                        action = Agent.Action.FORWARD
                else:
                    action = Agent.Action.CLIMB

        self._update(action)
        return action

    # ======================================================================
    # Helper functions
    # ======================================================================

    def _postion_ahead(self):
        if self.dir == 0:
            return (self.pos[0] - 1, self.pos[1])
        if self.dir == 1:
            return (self.pos[0], self.pos[1] - 1)
        if self.dir == 2:
            return (self.pos[0] + 1, self.pos[1])
        if self.dir == 3:
            return (self.pos[0], self.pos[1] + 1)

    def _adjacent_rooms(self, pos):
        result = []
        if pos[0] + 1 <= self.top_boundary:
            result.append((pos[0] + 1, pos[1]))
        if pos[1] + 1 <= self.right_boundary:
            result.append((pos[0], pos[1] + 1))
        if pos[0] - 1 > 0:
            result.append((pos[0] - 1, pos[1]))
        if pos[1] - 1 > 0:
            result.append((pos[0], pos[1] - 1))
        return result

    def _remember(self, stench, breeze, bump, scream):
        if self.shot_arrow:
            if scream:
                for key in self.world:
                    if 'wumpus' in self.world[key]:
                        self.world[key].remove('wumpus')
                    if 'stench' in self.world[key]:
                        self.world[key].remove('stench')
                self.wumpus_alive = False
            else:
                self.wumpus_unique = True
                self.world[self._postion_ahead()].remove('wumpus')
            self.shot_arrow = False
        if bump:
            self.visited.remove(self.pos)
            self.moves -= 1
            if self.dir == 0:
                self.pos = (self.pos[0] + 1, self.pos[1])
            if self.dir == 1:
                self.pos = (self.pos[0], self.pos[1] + 1)
            if self.dir == 2:
                self.pos = (self.pos[0] - 1, self.pos[1])
                self.top_boundary = self.pos[0]
            if self.dir == 3:
                self.pos = (self.pos[0], self.pos[1] - 1)
                self.right_boundary = self.pos[1]
        else:
            if self.wumpus_alive:
                if stench:
                    self.world[self.pos].add('stench')
                else:
                    self._clear_danger('wumpus')
            if breeze:
                self.world[self.pos].add('breeze')
            else:
                self._clear_danger('pit')


    def _predict_danger(self, danger, sense):
        if danger == 'wumpus' and self.wumpus_unique:
            return
        for d in self._adjacent_rooms(self.pos):
            if not d in self.visited:
                excluded = False
                if d[0] not in range(1, self.top_boundary + 1) or d[1] not in range(1, self.right_boundary + 1):
                    excluded = True
                else:
                    for s in self._adjacent_rooms(d):
                        if s in self.visited:
                            if sense not in self.world[s]:
                                excluded = True
                if not excluded:
                    if danger == 'wumpus':
                        if danger in self.world[d]:
                            for v in self.world.values():
                                if danger in v:
                                    v.remove(danger)
                    self.world[d].add(danger)

    def _clear_danger(self, danger):
        for d in self._adjacent_rooms(self.pos):
            if d in self.world and danger in self.world[d]:
                self.world[d].remove(danger)

    def _turn(self):
        if self.dir < self.desired_dir:
            if self.dir == 0 and self.desired_dir == 3:
                action = Agent.Action.TURN_LEFT
            else:
                action = Agent.Action.TURN_RIGHT
        elif self.dir > self.desired_dir:
            if self.dir == 3 and self.desired_dir == 0:
                action = Agent.Action.TURN_RIGHT
            else:
                action = Agent.Action.TURN_LEFT
        if abs(self.dir - self.desired_dir) in (1, 3):
            self.turning = False
        return action


    def _update(self, action):
        if action == Agent.Action.GRAB:
            self.finished = True
        if action == Agent.Action.FORWARD:
            self.pos = self._postion_ahead()
        if action == Agent.Action.TURN_LEFT:
            self.dir = (self.dir - 1) % 4
        if action == Agent.Action.TURN_RIGHT:
            self.dir = (self.dir + 1) % 4
        if action == Agent.Action.SHOOT:
            self.has_arrow = False
        if not self.finished and action in self.move_types:
            self.moves += 1
            self.visited.add(self.pos)

    def _decide_dir(self, desired_pos = None):
        if not desired_pos:
            adjacent_unvisited = [room for room in self._adjacent_rooms(self.pos)
                                  if room not in self.visited and
                                  'wumpus' not in self.world[room] and 'pit' not in self.world[room]]
            adjacent_visited = [room for room in self._adjacent_rooms(self.pos)
                                if room in self.visited]
            if adjacent_unvisited:
                desired_pos = adjacent_unvisited[0]
            elif adjacent_visited:
                desired_pos = self.cheapest_dir(adjacent_visited)
            else:
                return False

        if desired_pos[0] > self.pos[0]:
            return 2
        elif desired_pos[0] < self.pos[0]:
            return 0
        elif desired_pos[1] > self.pos[1]:
            return 3
        else:
            return 1

    def cheapest_dir(self, ls : [(int, int)]):
        buffer = []
        dir_diff = {0 : 0, 1 : 1, 2 : 2, 3 : 1}
        for pos in ls:
            if pos[0] > self.pos[0]:
                buffer.append((dir_diff[abs(2 - self.dir)], pos))
            elif pos[0] < self.pos[0]:
                buffer.append((dir_diff[abs(0 - self.dir)], pos))
            elif pos[1] > self.pos[1]:
                buffer.append((dir_diff[abs(3 - self.dir)], pos))
            else:
                buffer.append((dir_diff[abs(1 - self.dir)], pos))
        return sorted(buffer)[0][1]

    def _go_home(self):
        if self.pos == (1, 1):
            return Agent.Action.CLIMB
        path = self._home_dir()
        self.desired_dir = self._decide_dir(path[1])
        if self.dir == self.desired_dir:
            return Agent.Action.FORWARD
        else:
            self.turning = True
            return self._turn()

    def _home_dir(self):
        frontier = PriorityQueue()
        frontier.put((0, self.pos, [self.pos]))
        visited = set()

        while frontier:
            cost, node, path = frontier.get()
            if node not in visited:
                visited.add(node)
                if node == (1, 1):
                    return path
                for n in [room for room in self._adjacent_rooms(node) if room in self.visited]:
                    if n not in visited:
                        new_path = [i for i in path]
                        new_path.append(n)
                        frontier.put((cost + 1, n, new_path))

    
    # ======================================================================
    # YOUR CODE ENDS
    # ======================================================================