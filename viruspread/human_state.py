import dataclasses
from typing import Optional


@dataclasses.dataclass
class HumanState:
	is_alive: bool = True
	sick_since_day: Optional[int] = None
	incubation_days: int = 0
	sickness_days: int = 0
	will_survive: bool = True
	in_quarantine: bool = False

	def clone(self):
		return HumanState(
			is_alive=self.is_alive,
			sick_since_day=self.sick_since_day,
			incubation_days=self.incubation_days,
			sickness_days=self.sickness_days,
			will_survive=self.will_survive,
			in_quarantine=self.in_quarantine)
