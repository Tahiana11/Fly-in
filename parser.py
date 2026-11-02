from exception import ParserError
from typing import Any
import re


class Parser:
    def __init__(self, mapfile: str) -> None:
        self.mapfile = mapfile
        self.nb_drones: int = 0
        self.hubs: dict[str, dict[str, Any]] = {}
        self.connections: list[tuple[str, str, int]] = []
        self.start: dict[str, Any] | None = None
        self.end: dict[str, Any] | None = None
        self.links: set[frozenset[str]] = set()

        self.first_done: bool = False
        self.has_start: bool = False
        self.has_end: bool = False

    def read_line(self) -> list[str]:
        try:
            with open(self.mapfile, "r", encoding="utf-8") as file:
                return file.readlines()
        except OSError as e:
            raise ParserError(
                0,
                f"can't not read '{self.mapfile}': {e}"
            )

    def network(self) -> dict[str, Any]:
        lines = self.read_line()
        line_no: int = 0

        for line_no, raw_line in enumerate(lines, start=1):
            line_clean = raw_line.split("#", 1)[0].strip()
            if not line_clean:
                continue

            if not self.first_done:
                if not line_clean.startswith("nb_drones:"):
                    raise ParserError(line_no, "first line must be 'nb_drones: <n>'")
                self.first_done = True

            self.parse_line(line_clean, line_no)

        if not self.has_start:
            raise ParserError(
                line_no, "No 'start_hub' was found in the file."
            )
        if not self.has_end:
            raise ParserError(
                line_no, "No 'end_hub' was found in the file."
                )

        return {
            "nb_drones": self.nb_drones,
            "hubs": self.hubs,
            "connection": self.connections,
            "start": self.start,
            "end": self.end
        }

    def parse_line(self, line: str, line_no: int) -> None:
        if line.startswith("nb_drones:"):
            self.parse_nb_drones(line, line_no)
        elif line.startswith("start_hub:"):
            self.parse_hub(line, "start_hub", line_no)
        elif line.startswith("end_hub:"):
            self.parse_hub(line, "end_hub", line_no)
        elif line.startswith("hub:"):
            self.parse_hub(line, "hub", line_no)
        elif line.startswith("connection:"):
            self.parse_connection(line, line_no)
        else:
            raise ParserError(line_no, "Invalid instruction")

    def parse_hub(self, line: str, hub_type: str, line_no: int) -> None:
        pattern = (
            r"^(?:start_hub|end_hub|hub):\s+"
            r"([^\s-]+)\s+(-?\d+)\s+(-?\d+)"
            r"(?:\s+\[(.*?)\])?$"
        )
        match = re.match(pattern, line)
        if not match:
            raise ParserError(
                line_no,
                f"Invalid hub format: '{line}'"
            )
        name, x, y, meta = match.groups()
        hub = {
            "name": name,
            "x": int(x),
            "y": int(y),
            "metadata": self.parse_metadata(name, meta, line_no)
        }

        if name in self.hubs:
            raise ParserError(
                line_no,
                f"Hub '{name}' is already defined."
            )

        if hub_type == "start_hub":
            if self.has_start:
                raise ParserError(
                    line_no,
                    "Double definition of start_hub is prohibited."
                )
            self.start = hub
            self.has_start = True

        elif hub_type == "end_hub":
            if self.has_end:
                raise ParserError(
                    line_no,
                    "Double definition of end_hub is prohibited."
                )
            self.end = hub
            self.has_end = True
        self.hubs[name] = hub


    def parse_connection(self, line: str, line_no: int) -> None:
        pattern = r"^connection:\s+([^\s-]+)-([^\s-]+)" r"(?:\s+\[(.*?)\])?$"
        match = re.match(pattern, line)
        if not match:
            raise ParserError(line_no, f"Invalid connection format: '{line}'")
        hub1, hub2, meta = match.groups()
        for hub in (hub1, hub2):
            if hub not in self.hubs:
                raise ParserError(line_no, f"Unknown hub: '{hub}'")
        if hub1 == hub2:
            raise ParserError(line_no, "A hub cannot be connected to itself.")
        key = frozenset((hub1, hub2))
        if key in self.links:
            raise ParserError(line_no, f"Duplicate connection '{hub1}-{hub2}'.")

        capacity = 1
        if meta is not None:
            items = meta.split()
            if len(items) != 1 or not items[0].startswith("max_link_capacity="):
                raise ParserError(line_no, f"Invalid connection metadata: '{meta}'")
            capacity = self.check_positive(
                items[0].split("=", 1)[1], "max_link_capacity", line_no
            )
        self.links.add(key)
        self.connections.append((hub1, hub2, capacity))

    def parse_metadata(
        self, hub_type: str, meta: str | None, line_no: int
    ) -> dict[str, str]:
        metadata: dict[str, str] = {}
        if not meta:
            return metadata
        for item in meta.split():
            if "=" not in item:
                raise ParserError(
                    line_no,
                    f"Invalid metadata: '{item}'"
                )
            key, value = item.split("=", 1)
            if key in metadata:
                raise ParserError(
                    line_no,
                    f"Duplicate metadata key: '{key}'"
                )
            valid_keys = {
                "zone", "max_drones", "color"
            }
            if key not in valid_keys:
                raise ParserError(
                    line_no,
                    f"Unknown metadata key: '{key}'"
                )
            if key == "zone":
                valid_zones = {
                    "blocked",
                    "normal",
                    "restricted",
                    "priority"
                }

                if value not in valid_zones:
                    raise ParserError(
                        line_no,
                        f"Invalid zone value '{value}'"
                    )
            if key == "max_drones" and hub_type == "hub":
                self.check_positive(value, "max_drones", line_no)
            metadata[key] = value

        if "max_drones" not in metadata:
            if hub_type not in ("start", "end"):
                metadata["max_drones"] = "1"

        return metadata

    @staticmethod
    def check_positive(value: str, name: str, line_no: int) -> int:
        try:
            number = int(value)
        except ValueError as e:
            raise ParserError(
                line_no,
                f"{name} must be an integer."
            )
        if number <= 0:
            raise ParserError(
                line_no,
                f"{name} must be strictly positive integer."
            )
        return number

    def parse_nb_drones(self, line: str, line_no: int) -> None:
        value = line.split(":", 1)[1].strip()

        try:
            nb_drones = int(value)
        except ValueError:
            raise ParserError(
                line_no,
                "nb_drones must be an integer."
            )

        if nb_drones <= 0:
            raise ParserError(
                line_no,
                "nb_drones must be strictly positive."
            )

        if self.nb_drones != 0:
            raise ParserError(
                line_no,
                "nb_drones is already defined."
            )

        self.nb_drones = nb_drones
