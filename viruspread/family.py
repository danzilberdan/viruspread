import dataclasses


@dataclasses.dataclass(eq=False)
class Family:
    index: int
    location: tuple
