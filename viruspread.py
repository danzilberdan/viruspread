from viruspread.configuration import Configuration
from viruspread.virus_simulator import VirusSimulator
from viruspread.mitigation import Mitigation


def main():
	config = Configuration(
		population_size=100,
		starting_sick=2,
		death_rate=0.03,
		average_incubation_days=5.1,
		stdv_incubation_days=1.52,
		average_sickness_days=14,
		stdv_sickness_days=3,
		average_family_size=3.1,
		stdv_family_size=2,
		x_km=20,
		y_km=30,
		average_friend_group_count=2,
		stdv_friend_group_count=0.3,
		average_group_size=3,
		stdv_group_size=1,
		average_group_meetings_per_day=0.7,
		stdv_group_meetings_per_day=0.2,
		average_friend_meeting_minutes=60,
		stdv_friend_meeting_minutes=20,
		infection_probability_per_minute=0.001)
	virus_simulator = VirusSimulator(config)
	virus_simulator.draw(virus_simulator.starting_state)
	new_state = virus_simulator.starting_state
	for _ in range(30):
		new_state = virus_simulator.simulate(new_state, Mitigation(max_group_size=20, quarantine_days=14, inspections_per_day=1000))
		virus_simulator.draw(new_state)


if __name__ == '__main__':
	main()
