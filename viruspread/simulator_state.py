import dataclasses
from typing import Set, List

from viruspread.human_state import HumanState


@dataclasses.dataclass
class SimulatorState:
	human_states: List[HumanState]
	day: int
	sick_indicies: Set[int] = dataclasses.field(default_factory=set)

	def clone(self):
		return SimulatorState(
			sick_indicies=set(self.sick_indicies),
			human_states=[human_state.clone() for human_state in self.human_states],
			day=self.day)
