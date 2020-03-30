import dataclasses


@dataclasses.dataclass
class Mitigation:
    max_group_size: int
    quarantine_days: int
    inspections_per_day: int
