from enter import GetMapsCategories
from parser import Parser
from network import Network
from exception import ParserError
import sys


def main() -> None:
    try:
        enter = GetMapsCategories()
        map_file = enter.get_target()

        data = Parser(map_file).network()
        network = Network.build_network(data)

    except (ParserError) as error:
        print(f"{error}")
        sys.exit(1)

    # for zone in network.zones.values():
    #     print(zone.name, zone.x, zone.y, zone.kind, zone.color, zone.max_drones, zone.is_start, zone.is_end)
    # print("\n\n\n\n")
    # print(network.links)
    # print("\n\n\n\n")
    # print(network.adjacency)
    # print("\n\n\n\n")


if __name__ == "__main__":
    main()
