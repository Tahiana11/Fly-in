from typing import Any, Optional


class Zone:
    """A zone (hub) of the network."""

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        kind: str = "normal",
        color: Optional[str] = None,
        max_drones: int = 1,
        is_start: bool = False,
        is_end: bool = False,
    ) -> None:
        """Create a zone.

        Args:
            name: Unique name of the zone.
            x: X coordinate.
            y: Y coordinate.
            kind: normal, blocked, restricted or priority.
            color: Optional color used for the display.
            max_drones: Max drones at the same time (ignored for start/end).
            is_start: True if this is the start hub.
            is_end: True if this is the end hub.
        """
        self.name = name
        self.x = x
        self.y = y
        self.kind = kind
        self.color = color
        self.max_drones = max_drones
        self.is_start = is_start
        self.is_end = is_end

    @property
    def is_blocked(self) -> bool:
        """Return True if drones can never enter this zone."""
        return self.kind == "blocked"

    @property
    def move_cost(self) -> int:
        """Return the number of turns needed to enter this zone."""
        return 2 if self.kind == "restricted" else 1

    def has_room(self, count: int) -> bool:
        """Tell if one more drone can enter when `count` are already there.

        Args:
            count: Number of drones currently in the zone.
        """
        if self.is_start or self.is_end:
            return True
        return count < self.max_drones

    def __repr__(self) -> str:
        """Return a readable representation."""
        return f"Zone({self.name}, {self.x}, {self.y}, {self.kind})"


class Link:
    """A bidirectional connection between two zones."""

    def __init__(self, a: str, b: str, capacity: int = 1) -> None:
        """Create a link.

        Args:
            a: Name of the first zone.
            b: Name of the second zone.
            capacity: Max drones crossing the link at the same time.
        """
        self.a = a
        self.b = b
        self.capacity = capacity

    def __repr__(self) -> str:
        """Return a readable representation."""
        return f"Link({self.a}-{self.b}, cap={self.capacity})"


class Network:
    """The whole graph: zones, links and simulation settings."""

    def __init__(self, nb_drones: int, start: str, end: str) -> None:
        """Create an empty network.

        Args:
            nb_drones: Number of drones to deliver.
            start: Name of the start zone.
            end: Name of the end zone.
        """
        self.nb_drones = nb_drones
        self.start = start
        self.end = end
        self.zones: dict[str, Zone] = {}
        self.links: dict[frozenset[str], Link] = {}
        self.adjacency: dict[str, list[str]] = {}

    def add_zone(self, zone: Zone) -> None:
        """Register a zone and prepare its neighbor list."""
        self.zones[zone.name] = zone
        self.adjacency[zone.name] = []

    def add_link(self, link: Link) -> None:
        """Register a link and update the adjacency of both zones."""
        self.links[frozenset((link.a, link.b))] = link
        self.adjacency[link.a].append(link.b)
        self.adjacency[link.b].append(link.a)

    def get_zone(self, name: str) -> Zone:
        """Return the zone called `name`."""
        return self.zones[name]

    def get_link(self, a: str, b: str) -> Link:
        """Return the link between `a` and `b` (order does not matter)."""
        return self.links[frozenset((a, b))]

    def neighbors(self, name: str) -> list[str]:
        """Return the zones reachable from `name` (blocked ones removed)."""
        return [n for n in self.adjacency[name] if not self.zones[n].is_blocked]

    @classmethod
    def build_network(cls, data: dict[str, Any]) -> "Network":
        """Build a Network from the dict returned by Parser.network().

        Args:
            data: Dict with nb_drones, hubs, connection, start and end.
        """
        start_name: str = data["start"]["name"]
        end_name: str = data["end"]["name"]
        network = cls(data["nb_drones"], start_name, end_name)

        for hub in data["hubs"].values():
            meta: dict[str, str] = hub["metadata"]
            is_start = hub["name"] == start_name
            is_end = hub["name"] == end_name
            max_drones = 1
            if not (is_start or is_end):
                max_drones = int(meta.get("max_drones", "1"))
            network.add_zone(
                Zone(
                    hub["name"],
                    hub["x"],
                    hub["y"],
                    meta.get("zone", "normal"),
                    meta.get("color"),
                    max_drones,
                    is_start,
                    is_end,
                )
            )

        for a, b, capacity in data["connection"]:
            network.add_link(Link(a, b, capacity))
        return network
