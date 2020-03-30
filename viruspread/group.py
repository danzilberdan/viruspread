import dataclasses


@dataclasses.dataclass(eq=False)
class Group:
	index: int
	location: tuple
