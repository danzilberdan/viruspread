import random
import os

import networkx as nx
from rtree import index
import numpy as np
import matplotlib.pyplot as plt

from viruspread.human import Human
from viruspread.family import Family
from viruspread.group import Group
from viruspread.simulator_state import SimulatorState
from viruspread.human_state import HumanState


class VirusSimulator:
    def __init__(self, configuration):
        self._config = configuration
        
        self._humans = [Human(human_index) for human_index in range(configuration.population_size)]
        self._families = list()
        self._groups = list()

        self._friend_graph = nx.Graph()
        self._family_graph = nx.Graph()

        self._family_geo_index = index.Index()
        self._group_geo_index = index.Index()

        self._init_family_graph()
        self._init_friends_graph()
        self._starting_state = self._get_starting_state()

    @property
    def starting_state(self):
        return self._starting_state
    
    def _init_family_graph(self):
        humans_iter = iter(self._humans)
        family_index = 0
        while True:
            random_family_size = np.random.normal(
                self._config.average_family_size, self._config.stdv_family_size)
            family_size = max(0, random_family_size)
            
            family = Family(index=family_index, location=(
                random.randrange(self._config.x_km), 
                random.randrange(self._config.y_km)))
            self._families.append(family)
            self._family_graph.add_node(family)
            x, y = family.location
            self._family_geo_index.insert(family_index, (x, y, x, y))

            try:
                for _ in range(int(np.around(family_size))):
                    human = next(humans_iter)
                    self._family_graph.add_node(human)
                    self._family_graph.add_edge(human, family)
            except StopIteration:
                break

            family_index += 1

    def _init_friends_graph(self):
        group_only_geo_index = index.Index()

        exact_group_count = (self._config.population_size * self._config.average_friend_group_count) / self._config.average_group_size
        group_count = int(np.around(exact_group_count))
        for group_index in range(group_count):
            new_group = Group(index=group_index, location=(
                random.randrange(self._config.x_km), 
                random.randrange(self._config.y_km)))
            self._groups.append(new_group)
            self._friend_graph.add_node(new_group)

            x, y = new_group.location
            self._group_geo_index.insert(group_index, (x, y, x, y))
            group_only_geo_index.insert(group_index, (x, y, x, y))

        for human in self._humans:
            self._friend_graph.add_node(human)
            exact_group_count = np.random.normal(
                self._config.average_friend_group_count, self._config.stdv_friend_group_count)
            group_count = max(0, int(np.around(exact_group_count)))
            family = next(self._family_graph.neighbors(human))
            family_x, family_y = family.location

            removed_groups = list()
            for family_member in self._family_graph.neighbors(family):
                if family_member in self._friend_graph:
                    for group in self._friend_graph.neighbors(family_member):
                        removed_groups.append(group)

            for removed_group in removed_groups:
                x, y = removed_group.location
                group_only_geo_index.delete(removed_group.index, (x, y, x, y))

            nearest_groups_indicies = group_only_geo_index.nearest((family_x, family_y, family_x, family_y), num_results=group_count)

            for removed_group in removed_groups:
                x, y = removed_group.location
                group_only_geo_index.insert(removed_group.index, (x, y, x, y))

            for group_to_add_human_index in nearest_groups_indicies:
                self._friend_graph.add_edge(human, self._groups[group_to_add_human_index])

    def _get_starting_state(self):
        human_states = [HumanState() for _ in self._humans]
        starting_state = SimulatorState(
            human_states=human_states,
            day=0)
        
        for _ in range(self._config.starting_sick):
            infected_index = random.randrange(len(self._humans))
            self._infect(starting_state, infected_index)

        return starting_state

    def _infect(self, simulator_state, human_index):
        if human_index not in simulator_state.sick_indicies:
            human_to_infect_state = simulator_state.human_states[human_index]
            human_to_infect_state.sick_since_day = simulator_state.day

            exact_incubation_days = np.random.normal(
                self._config.average_incubation_days, self._config.stdv_incubation_days)
            human_to_infect_state.incubation_days = int(np.around(max(0, exact_incubation_days)))

            exact_sickness_days = np.random.normal(
                self._config.average_sickness_days, self._config.stdv_sickness_days)
            human_to_infect_state.sickness_days = int(np.around(max(0, exact_sickness_days)))

            human_to_infect_state.will_survive = random.random() < self._config.death_rate

            simulator_state.sick_indicies.add(human_index)

    def _find_humans_to_heal(self, simulator_state):
        sick_human_indicies_to_remove = set()
        for sick_human_index in simulator_state.sick_indicies:
            sick_human_state = simulator_state.human_states[sick_human_index]
            if simulator_state.day >= sick_human_state.sick_since_day + sick_human_state.sickness_days:
                if sick_human_state.will_survive:
                    sick_human_state.sick_sinec_day = None
                    sick_human_state.incubation_days = 0
                    sick_human_state.sickness_days = 0
                    sick_human_state.will_survive = True
                    sick_human_indicies_to_remove.add(sick_human_index)
                else:
                    sick_human_state.is_alive = False

        simulator_state.sick_indicies -= sick_human_indicies_to_remove

    def _find_groups_to_infect(self, simulator_state):
        group_blacklist = set()
        to_infect = list()
        for sick_human_index in simulator_state.sick_indicies:
            human = self._humans[sick_human_index]
            for group in self._friend_graph.neighbors(human):
                if group in group_blacklist:
                    continue
                group_blacklist.add(group)

                # How many times did this group meet today?
                exact_meet_count = np.random.normal(
                    self._config.average_group_meetings_per_day, self._config.stdv_group_meetings_per_day)
                meet_count = int(np.around(max(0, exact_meet_count)))

                # For how long did they hang out together?
                total_time = 0
                for _ in range(meet_count):
                    exact_meet_time = np.random.normal(
                        self._config.average_friend_meeting_minutes, self._config.stdv_friend_meeting_minutes)
                    meet_time = max(0, exact_meet_time)
                    total_time += meet_time

                for friend in self._friend_graph.neighbors(group):
                    if friend.index in simulator_state.sick_indicies:
                        for friend in self._friend_graph.neighbors(group):
                            if friend.index not in simulator_state.sick_indicies:
                                # Did this human get infected by his friend?
                                not_getting_infected_probability_per_minute = 1 - self._config.infection_probability_per_minute
                                not_getting_infected_probability = not_getting_infected_probability_per_minute ** int(total_time)
                                if random.random() >= not_getting_infected_probability:
                                    to_infect.append(friend.index)
        for infect_index in to_infect:
            self._infect(simulator_state, infect_index)


    def simulate(self, old_state, mitigation):
        new_state = old_state.clone()
        new_state.day += 1
        self._find_humans_to_heal(new_state)
        self._find_groups_to_infect(new_state)
        return new_state

    def draw_family_graph(self):
        options = {
            "node_color": "black",
            "node_size": 30,
            "line_color": "grey",
            "linewidths": 0,
            "width": 0.1,
        }

        nx.draw(self._family_graph, **options)
        plt.savefig('family_graph.png')
        plt.clf()

    def draw(self, simulator_state):
        pos = {}
        for group in self._groups:
            x, y = group.location
            pos[group] = (x, y)

        for human in self._humans:
            family = next(self._family_graph.neighbors(human))
            x, y = family.location
            pos[human] = (x, y)

        colors = list()
        for node in self._friend_graph:
            if type(node) is Human:
                if simulator_state.human_states[node.index].sick_since_day:
                    colors.append('r')
                else:
                    colors.append('b')
            else:
                colors.append('y')

        options = {
            "node_color": colors,
            "node_size": 30,
            "line_color": "grey",
            "linewidths": 0,
            "width": 0.1,
            "pos": nx.kamada_kawai_layout(self._friend_graph)
        }

        plt.clf()
        nx.draw(self._friend_graph, **options)

        if not os.path.exists('output'):
            os.makedirs('output')
        plt.savefig(f'output/friend_graph_{simulator_state.day}.png')
