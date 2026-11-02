from pathlib import Path
import sys


class GetMapsCategories:

    def __init__(self, maps_dir: str = "./maps") -> None:
        self.maps_dir = Path(maps_dir)
        self.target: list[Path] = []
        self._load_maps()

    def _load_maps(self) -> None:
        if not self.maps_dir.exists():
            print("There is no maps.")
            sys.exit(1)

        index = 0
        for category in sorted(self.maps_dir.iterdir()):
            if not category.is_dir():
                continue
            print(f"Maps: {category.name}:")
            for f in sorted(category.glob("*.txt")):
                print(f"[{index}] - {f.name}")
                self.target.append(f)
                index += 1
            print()

    def get_target(self) -> str:
        max_idx = len(self.target) - 1

        if max_idx < 0:
            print("No map files found.")
            sys.exit(1)

        while True:
            try:
                enter = input(
                    f"Please select the valid card between [0-{max_idx}]: "
                )
            except (EOFError, KeyboardInterrupt):
                print()
                sys.exit(0)
            try:
                choose = int(enter)
            except ValueError:
                print(f"Invalid choice: '{enter}' is not a number.")
                continue
            if choose < 0 or choose > max_idx:
                print(f"Invalid choice: enter a number between 0 and "
                      f"{max_idx}.")
                continue
            return str(self.target[choose])
