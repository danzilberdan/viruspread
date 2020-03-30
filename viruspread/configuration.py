import dataclasses


@dataclasses.dataclass
class Configuration:
    population_size: int = None
    starting_sick: int = None
    x_km: float = None
    y_km: float = None
    average_family_size: float = None
    stdv_family_size: int = None

    infection_probability_per_minute: float = None
    death_rate: float = None
    average_incubation_days: float = None
    stdv_incubation_days: float = None
    average_sickness_days: float = None
    stdv_sickness_days: float = None

    average_friend_group_count: float = None
    stdv_friend_group_count: float = None
    average_group_size: float = None
    stdv_group_size: float = None
    average_friend_meeting_minutes: float = None
    stdv_friend_meeting_minutes: float = None
    average_group_meetings_per_day: float = None
    stdv_group_meetings_per_day: float = None
    
    average_stranger_max_meeting_radius: float = None
    stdv_stranger_max_meeting_radius: float = None
    average_stranger_meeting_minutes: float = None
    stdv_stranger_meeting_minutes: float = None
    average_stranger_meetings_per_day: int = None
    stdv_stranger_meetings_per_day: int = None
