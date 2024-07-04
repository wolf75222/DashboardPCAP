import json
import os
from datetime import datetime, timedelta
import time
import requests
from dateutil import parser
import copy

import re
from typing import List
from itertools import groupby
from collections import defaultdict

from app.models.GeoNetworking import GeoNetworking
from app.models.Packet import Packet
from app.models.DENM import DENM
from app.models.CAM import CAM
from haversine import haversine, Unit
from math import radians, cos, sin, sqrt, atan2


class Packets:
    """
    A class to represent a collection of packets

    Attributes:
        file_path (str): The path to the JSON file
        packets (List[Packet]): The list of packets
    """

    def __init__(self, file_path: str):
        """Create a collection of packets from a JSON file

        Args:
            file_path (str): The path to the JSON file

        Raises:
            FileNotFoundError: If the file is not found
            ValueError: If the file is not a JSON file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} was not found.")
        if not file_path.endswith(".json"):
            raise ValueError("The file must be a JSON file.")

        self.file_path = file_path

        self.packets: List[Packet] = []
        self.load_packets()

    def load_packets(self):
        """
        Load packets from a JSON file
        """
        try:
            with open(self.file_path, "r") as file:
                data = json.load(file)
                for packet_data in data:
                    packet = self.determine_packet_type(
                        packet_data["_source"]["layers"]
                    )
                    if packet:
                        self.packets.append(packet)
        except FileNotFoundError:
            print(f"Error: The file {self.file_path} was not found.")
        except json.JSONDecodeError:
            print("Error: Failed to decode JSON.")

    def determine_packet_type(self, packet_dict):
        """Determines the type of packet based on the protocol.

        Args:
            packet_dict (dict): The packet as a dictionary

        Returns:
            Packet: The packet object
        """
        protocol = packet_dict["frame"]["frame.protocols"]
        if "eth:ethertype:gnw:btpb:its" in protocol:
            its_layer = packet_dict.get("its", {})
            if "cam.CamPayload_element" in its_layer:
                return CAM.from_dict(packet_dict)
            elif "denm.DenmPayload_element" in its_layer:
                return DENM.from_dict(packet_dict)
            else:
                return GeoNetworking.from_dict(packet_dict)
        return Packet.from_dict(packet_dict)

    def __str__(self):
        """String representation of the packets collection.

        Returns:
            str: The string representation of the packets collection
        """
        return f"Packets Collection: {len(self.packets)} packets loaded from {self.file_path}"

    def summary(self):
        """Summarizes the packets.

        Returns:
            str: The summary of the packets
        """
        return "\n".join([packet.summary() for packet in self.packets])

    def count_type(self, packet_type):
        """Counts the number of packets of a specific type.

        Args:
            packet_type (_type_): The type of packet to count

        Returns:
            int: The number of packets of the specified type
        """
        return sum(isinstance(packet, packet_type) for packet in self.packets)

    def statistics(self):
        """Generates statistics about the packets, including the total number of packets and the number of each type.

        Returns:
            dict: The statistics
        """
        stats = {
            "total_packets": len(self.packets),
            "total_cam": self.count_type(CAM),
            "total_denm": self.count_type(DENM),
            "total_geo": self.count_type(GeoNetworking),
            "total_other": self.count_type(Packet)
            - (self.count_type(CAM) + self.count_type(DENM)),
        }
        return stats

    def get_packets(self, page: int, per_page: int):
        """Get a subset of packets for pagination.

        Args:
            page (int): The page number
            per_page (int): The number of packets per page

        Returns:
            List[Packet]: The list of packets for the specified page
        """
        start = (page - 1) * per_page
        end = start + per_page
        return self.packets[start:end]

    def get_packet(self, frame_number: int):
        """Get a packet by frame number.

        Args:
            frame_number (int): The frame number

        Returns:
            Packet: The packet with the specified frame number
        """
        for packet in self.packets:
            if packet.frame_number == frame_number:
                return packet
        return None

    def get_packet_by_time(self, time: datetime):
        """Get a packet by time.

        Args:
            time (datetime): The time

        Returns:
            Packet: The packet with the specified time
        """
        for packet in self.packets:
            if packet.time == time:
                return packet
        return None

    def search_packets(self, search_term: str):
        """Search for packets by a search term.

        Args:
            search_term (str): The search term

        Returns:
            List[Packet]: The list of packets that match the search term
        """
        return [
            packet
            for packet in self.packets
            if re.search(search_term, packet.summary())
        ]

    def get_packet_types(self):
        """Get the unique packet types.

        Returns:
            List[str]: The list of unique packet types
        """
        return list(set([type(packet).__name__ for packet in self.packets]))

    def get_time_range(self):
        """Get the time range of the packets.

        Returns:
            Tuple[datetime, datetime]: The time range
        """
        times = [packet.time for packet in self.packets]
        return min(times), max(times)

    def get_packets_by_type(self, packet_type):
        """Get packets by type.

        Args:
            packet_type (str): The packet type

        Returns:
            List[Packet]: The list of packets of the specified type
        """
        return [packet for packet in self.packets if isinstance(packet, packet_type)]

    def get_packets_by_time_range(self, start_time: datetime, end_time: datetime):
        """Get packets within a time range.

        Args:
            start_time (datetime): The start time
            end_time (datetime): The end time

        Returns:
            List[Packet]: The list of packets within the time range
        """
        return [
            packet for packet in self.packets if start_time <= packet.time <= end_time
        ]

    def get_packets_by_src_mac(self, src_mac: str):
        """Get packets by source MAC address.

        Args:
            src_mac (str): The source MAC address

        Returns:
            List[Packet]: The list of packets with the specified source MAC address
        """
        return [packet for packet in self.packets if packet.src_mac == src_mac]

    def get_packets_by_dst_mac(self, dst_mac: str):
        """Get packets by destination MAC address.

        Args:
            dst_mac (str): The destination MAC address

        Returns:
            List[Packet]: The list of packets with the specified destination MAC address
        """
        return [packet for packet in self.packets if packet.dst_mac == dst_mac]

    def get_packets_by_location(self, latitude: float, longitude: float, radius: float):
        """Get packets by location.

        Args:
            latitude (float): The latitude
            longitude (float): The longitude
            radius (float): The radius

        Returns:
            List[Packet]: The list of packets within the specified location
        """
        return [
            packet
            for packet in self.packets
            if packet.is_within_radius(latitude, longitude, radius)
        ]

    def round_time(self, dt, interval):
        """Round time to the nearest interval.

        Args:
            dt (datetime): The time
            interval (int): The interval

        Returns:
            datetime: The rounded time
        """
        new_minute = (dt.minute // interval) * interval
        return dt.replace(minute=new_minute, second=0, microsecond=0)

    def time_series_data(self):
        """Generates time series data for the packets.

        Returns:
            dict: The time series data for the packets
        """
        # Deux formats de date à essayer
        formats = ["%Y-%m-%d %H:%M:%S", "%b %d, %Y %H:%M:%S.%f000 %Z"]
        # Format de sortie des dates
        output_format = "%Y-%m-%d %H:%M:%S"
        # Regroupez les paquets par intervalles de temps prédéfinis (par exemple, toutes les 15 minutes)
        grouped_data = defaultdict(lambda: {"CAM": 0, "DENM": 0, "Autres": 0})

        for packet in self.packets:
            parsed_time = None
            for fmt in formats:
                try:
                    # Essayer de convertir la chaîne de caractères en datetime
                    parsed_time = datetime.strptime(packet.time, fmt)
                    break  # Si la conversion réussit, sortir de la boucle
                except ValueError:
                    continue  # Si la conversion échoue, essayer le format suivant

            if parsed_time is None:
                try:
                    parsed_time = parser.parse(packet.time)
                except (ValueError, TypeError) as e:
                    print(f"Error parsing date: {e}")
                    continue  # Passer au paquet suivant en cas d'erreur

            rounded_time = self.round_time(parsed_time, 1)
            rounded_time_str = rounded_time.strftime(output_format)

            if isinstance(packet, CAM):
                grouped_data[rounded_time_str]["CAM"] += 1
            elif isinstance(packet, DENM):
                grouped_data[rounded_time_str]["DENM"] += 1
            else:
                grouped_data[rounded_time_str]["Autres"] += 1

        times = sorted(grouped_data.keys())
        cam_counts = [grouped_data[time]["CAM"] for time in times]
        denm_counts = [grouped_data[time]["DENM"] for time in times]
        other_counts = [grouped_data[time]["Autres"] for time in times]

        return {
            "times": times,
            "cam_counts": cam_counts,
            "denm_counts": denm_counts,
            "other_counts": other_counts,
        }

    def get_src_traffic(self):
        """Get the source traffic.

        Returns:
            dict: The source traffic
        """
        src_traffic = {}
        for packet in self.packets:
            if packet.src_mac not in src_traffic:
                src_traffic[packet.src_mac] = 0
            src_traffic[packet.src_mac] += 1
        return src_traffic

    def get_dst_traffic(self):
        """Get the destination traffic.

        Returns:
            dict: The destination traffic
        """
        dst_traffic = {}
        for packet in self.packets:
            if packet.dst_mac not in dst_traffic:
                dst_traffic[packet.dst_mac] = 0
            dst_traffic[packet.dst_mac] += 1
        return dst_traffic

    def get_traffic_details(self):
        """Get the traffic details.

        Returns:
            dict: The traffic details
        """
        traffic_details = {}
        for packet in self.packets:
            if packet.src_mac not in traffic_details:
                traffic_details[packet.src_mac] = {
                    "total_packets": 0,
                    "cam_packets": 0,
                    "denm_packets": 0,
                    "other_packets": 0,
                }
            traffic_details[packet.src_mac]["total_packets"] += 1
            if isinstance(packet, CAM):
                traffic_details[packet.src_mac]["cam_packets"] += 1
            elif isinstance(packet, DENM):
                traffic_details[packet.src_mac]["denm_packets"] += 1
            else:
                traffic_details[packet.src_mac]["other_packets"] += 1
        return traffic_details

    def get_first_last_time(self):
        """Get the first and last time of the packets.

        Returns:
            Tuple[int, int]: The first and last time
        """
        times = [packet.time for packet in self.packets]
        return min(times), max(times)

    def get_first_position(self):
        """Get the first position of the packets.

        Returns:
            dict: (latitude, longitude) of the first position
        """
        for packet in self.packets:
            if isinstance(packet, GeoNetworking):
                return {
                    "latitude": float(packet.src_pos_lat) / 1e7,
                    "longitude": float(packet.src_pos_long) / 1e7,
                }
            elif isinstance(packet, CAM):
                return {
                    "latitude": float(packet.latitude) / 1e7,
                    "longitude": float(packet.longitude) / 1e7,
                }
            elif isinstance(packet, DENM):
                return {
                    "latitude": float(packet.latitude) / 1e7,
                    "longitude": float(packet.longitude) / 1e7,
                }
        return None

    def parse_time(self, time_str):
        """Parse a time string.

        Args:
            time_str (str): The time string

        Returns:
            datetime: The parsed time
        """
        # Deux formats de date à essayer
        formats = ["%Y-%m-%d %H:%M:%S", "%b %d, %Y %H:%M:%S.%f000 %Z"]

        for fmt in formats:
            try:
                return datetime.strptime(time_str, fmt)
            except ValueError:
                continue  # Si la conversion échoue, essayer le format suivant

        # Si aucun des formats ne correspond, essayer d'utiliser parser.parse
        try:
            return parser.parse(time_str)
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Time data '{time_str}' does not match any expected format"
            ) from e

    def get_denm_cam_association(self, filter_stations=None):
        cams = defaultdict(list)
        for packet in self.packets:
            if isinstance(packet, CAM):
                packet_time = self.parse_time(packet.time)
                packet.latitude = float(packet.latitude) / 1e7
                packet.longitude = float(packet.longitude) / 1e7
                cams[packet.station_type].append((packet, packet_time))

        denm_cam_data = defaultdict(list)
        packets_by_station = defaultdict(lambda: defaultdict(list))

        for packet in self.packets:
            if isinstance(packet, DENM):
                if (
                    filter_stations
                    and packet.originating_station_id not in filter_stations
                ):
                    continue  # Skip this packet if it's not from a filtered station
                key = (packet.originating_station_id, packet.sequence_number)
                packets_by_station[packet.originating_station_id][
                    packet.sequence_number
                ].append(packet)

        for station_id, sequences in packets_by_station.items():
            for sequence_number, packets in sequences.items():
                filtered_packets = {}
                for packet in packets:
                    if packet.seq_num not in filtered_packets:
                        filtered_packets[packet.seq_num] = packet

                rhl_seen = set()  # Track RHL values to ensure we only count unique hops
                hop_count = 0
                passage_details = defaultdict(int)
                passage_path = []

                for packet in filtered_packets.values():
                    denm_time = self.parse_time(packet.time)
                    denm_pos = (
                        float(packet.latitude) / 1e7,
                        float(packet.longitude) / 1e7,
                    )

                    # Use a bounding box to limit the CAMs considered
                    time_window_start = denm_time - timedelta(seconds=60)
                    time_window_end = denm_time + timedelta(seconds=60)
                    closest_cam = None
                    min_distance = float("inf")

                    for cam, cam_time in cams.get(packet.station_type, []):
                        if not (time_window_start <= cam_time <= time_window_end):
                            continue
                        cam_pos = (cam.latitude, cam.longitude)
                        distance = haversine(denm_pos, cam_pos)
                        if distance < min_distance:
                            min_distance = distance
                            closest_cam = cam

                    if closest_cam and packet.rhl not in rhl_seen:
                        rhl_seen.add(packet.rhl)
                        hop_count += 1

                        # Collect passage details
                        station_id_from_mac = self.get_station_by_mac(packet.src_mac)
                        if station_id_from_mac:
                            passage_details[station_id_from_mac] += 1
                            passage_path.append(station_id_from_mac)

                        key = (
                            f"{packet.originating_station_id}-{packet.sequence_number}"
                        )
                        denm_cam_data[key].append(
                            {
                                "time": denm_time,
                                "rhl": packet.rhl,
                                "position": (
                                    closest_cam.latitude,
                                    closest_cam.longitude,
                                ),
                                "hop_count": hop_count,
                                "passage_details": passage_details,
                                "passage_path": passage_path,
                            }
                        )

        return denm_cam_data

    def get_denm_stations(self):
        """Get the stations that have sent DENM packets.

        Returns:
            List[str]: The list of stations that have sent DENM packets
        """
        stations = set()
        for packet in self.packets:
            if isinstance(packet, DENM):
                stations.add(packet.originating_station_id)
        return list(stations)

    def get_station_by_mac(self, mac_address):
        """Get the station ID by MAC address.

        Args:
            mac_address (str): The MAC address

        Returns:
            str: The station ID
        """
        for packet in self.packets:
            if isinstance(packet, CAM) and packet.src_mac == mac_address:
                return packet.stationID
        return None

    def get_reception_distribution(self):
        """Get the reception distribution.

        Returns:
            defaultdict: The reception distribution
        """
        hops_data = defaultdict(list)

        # Collect packets by station and sequence number
        packets_by_station = defaultdict(lambda: defaultdict(list))
        for packet in self.packets:
            if isinstance(packet, DENM):
                key = (packet.originating_station_id, packet.sequence_number)
                packets_by_station[packet.originating_station_id][
                    packet.sequence_number
                ].append(packet)

        # Calculate the number of hops for each packet and store passage details
        for station_id, sequences in packets_by_station.items():
            for sequence_number, packets in sequences.items():
                # Filter to include only the first occurrence of each packet by seq_num
                filtered_packets = {}
                for packet in packets:
                    if packet.seq_num not in filtered_packets:
                        filtered_packets[packet.seq_num] = packet

                # Calculate hop count
                hop_count = (
                    len(filtered_packets) - 1
                )  # Number of hops is the number of unique seq_num minus one
                passage_details = defaultdict(int)

                # Accumulate passage details for each packet in the sequence
                for packet in filtered_packets.values():
                    station_id_from_mac = self.get_station_by_mac(packet.src_mac)
                    if station_id_from_mac:
                        passage_details[station_id_from_mac] += 1

                hops_data[station_id].append(
                    {"hop_count": hop_count, "passage_details": passage_details}
                )

        return hops_data

    def get_repetition_distribution(self):
        """Get the repetition distribution.

        Returns:
            defaultdict: The repetition distribution
        """
        hops_data = defaultdict(list)

        # Collect packets by station and sequence number
        packets_by_station = defaultdict(lambda: defaultdict(list))
        for packet in self.packets:
            if isinstance(packet, DENM):
                key = (packet.originating_station_id, packet.sequence_number)
                packets_by_station[packet.originating_station_id][
                    packet.sequence_number
                ].append(packet)

        # Calculate the number of hops for each packet and store passage details
        for station_id, sequences in packets_by_station.items():
            for seq_num, packets in sequences.items():
                hop_count = (
                    len(packets) - 1
                )  # Number of hops is the number of appearances minus one
                passage_details = defaultdict(int)
                for packet in packets:
                    # Get the station ID using the MAC address of the packet
                    station_id = self.get_station_by_mac(packet.src_mac)
                    if station_id:
                        passage_details[station_id] += 1

                hops_data[station_id].append(
                    {"hop_count": hop_count, "passage_details": passage_details}
                )

        return hops_data

    def get_hops_distribution(self):
        """Get the hops distribution.

        Returns:
            defaultdict: The hops distribution
        """
        hops_data = defaultdict(list)

        # Collect packets by station and sequence number
        packets_by_station = defaultdict(lambda: defaultdict(list))
        for packet in self.packets:
            if isinstance(packet, DENM):
                key = (packet.originating_station_id, packet.sequence_number)
                packets_by_station[packet.originating_station_id][
                    packet.sequence_number
                ].append(packet)

        # Calculate the number of hops for each packet and store passage details
        for station_id, sequences in packets_by_station.items():
            for sequence_number, packets in sequences.items():
                # Track RHL values to ensure we only count unique hops
                rhl_seen = set()
                hop_count = 0
                passage_details = defaultdict(int)
                passage_path = []

                for packet in packets:
                    if packet.rhl not in rhl_seen:
                        rhl_seen.add(packet.rhl)
                        hop_count += 1

                        # Collect passage details
                        station_id_from_mac = self.get_station_by_mac(packet.src_mac)
                        if station_id_from_mac:
                            passage_details[station_id_from_mac] += 1
                            passage_path.append(station_id_from_mac)

                hops_data[station_id].append(
                    {
                        "hop_count": hop_count,
                        "passage_details": passage_details,
                        "passage_path": passage_path,
                    }
                )

        return hops_data

    def get_weather_data(self):
        """Get the weather data.

        Returns:
            dict: The weather data
        """
        weather_data = {}
        base_url = "https://archive-api.open-meteo.com/v1/era5"

        for packet in self.packets:
            if isinstance(packet, CAM):
                lat = float(packet.latitude) / 1e7
                lon = float(packet.longitude) / 1e7

                # Convert time to the required format
                time = datetime.strptime(packet.time, "%b %d, %Y %H:%M:%S.%f000 %Z")
                start_date = time.strftime("%Y-%m-%d")
                end_date = (time + timedelta(days=1)).strftime(
                    "%Y-%m-%d"
                )  # Example: next day

                # Build the API request URL
                url = (
                    f"{base_url}?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}"
                    "&hourly=temperature_2m,weathercode"
                )

                # Make the request to the weather API
                print(f"Retrieving weather data for packet at {start_date}")
                response = requests.get(url)
                if response.status_code == 200:
                    weather_info = response.json()
                    weather_data[start_date] = weather_info
                    print(f"Retrieved weather data for packet at {start_date}")
                    print(weather_info)
                    return weather_info
                else:
                    print(
                        f"Failed to retrieve weather data for packet at {start_date}: {response.status_code}"
                    )

                # Pause to avoid hitting the rate limit
                # time.sleep(1)  # Adjust the sleep time as needed

    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        # Calcul de la distance en utilisant la formule de Haversine
        R = 6373000.0  # Rayon de la Terre en mètres

        lat1, lon1, lat2, lon2 = (
            radians(lat1),
            radians(lon1),
            radians(lat2),
            radians(lon2),
        )
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance

    def get_furthest_station_distance(self):
        packets = copy.deepcopy(
            self.packets
        )  # Deep copy the packets to avoid mutation issues
        cams = defaultdict(list)
        for packet in packets:
            if isinstance(packet, CAM):
                packet_time = self.parse_time(packet.time)
                packet.latitude = float(packet.latitude) / 1e7
                packet.longitude = float(packet.longitude) / 1e7
                cams[packet.stationID].append((packet, packet_time))

        furthest_distances = defaultdict(list)
        for packet in packets:
            if isinstance(packet, DENM):
                source_id = packet.originating_station_id
                denm_pos = (float(packet.latitude) / 1e7, float(packet.longitude) / 1e7)
                denm_time = self.parse_time(packet.time)
                min_time_diff = float("inf")
                closest_cam = None

                for cam, cam_time in cams[source_id]:
                    time_diff = abs((denm_time - cam_time).total_seconds())
                    if time_diff < min_time_diff:
                        min_time_diff = time_diff
                        closest_cam = cam

                if closest_cam:
                    cam_pos = (closest_cam.latitude, closest_cam.longitude)
                    distance = self.calculate_distance(
                        denm_pos[0], denm_pos[1], cam_pos[0], cam_pos[1]
                    )
                    furthest_distances[source_id].append(distance)

        max_distances = {
            station: int(round(max(distances))) if distances else 0
            for station, distances in furthest_distances.items()
        }
        print("Max Distances (rounded and converted to int):", max_distances)
        return max_distances

    def get_distance_distribution(self):
        packets = copy.deepcopy(
            self.packets
        )  # Deep copy the packets to avoid mutation issues
        cams = defaultdict(list)
        for packet in packets:
            if isinstance(packet, CAM):
                packet_time = self.parse_time(packet.time)
                packet.latitude = float(packet.latitude) / 1e7
                packet.longitude = float(packet.longitude) / 1e7
                cams[packet.stationID].append((packet, packet_time))

        distances = []
        packet_info = []  # To store additional packet information
        for packet in packets:
            if isinstance(packet, DENM):
                source_id = packet.originating_station_id
                denm_pos = (float(packet.latitude) / 1e7, float(packet.longitude) / 1e7)
                denm_time = self.parse_time(packet.time)
                min_time_diff = float("inf")
                closest_cam = None

                for cam, cam_time in cams[source_id]:
                    time_diff = abs((denm_time - cam_time).total_seconds())
                    if time_diff < min_time_diff:
                        min_time_diff = time_diff
                        closest_cam = cam

                if closest_cam:
                    cam_pos = (closest_cam.latitude, closest_cam.longitude)
                    distance = self.calculate_distance(
                        denm_pos[0], denm_pos[1], cam_pos[0], cam_pos[1]
                    )
                    distances.append(distance)
                    packet_info.append(
                        {
                            "distance": distance,
                            "station_id": source_id,
                            "denm_pos": denm_pos,
                            "denm_time": denm_time,
                        }
                    )

        print("Distances:", distances)  # Debugging line

        # Calculate the distribution as percentages
        total_distances = len(distances)
        distance_distribution = defaultdict(
            lambda: {"count": 0, "stations": defaultdict(int)}
        )
        bin_edges = list(
            range(0, int(max(distances)) + 200, 200)
        )  # Example: 0-200m, 200-400m, etc.

        for info in packet_info:
            distance = info["distance"]
            station_id = info["station_id"]
            for i in range(len(bin_edges) - 1):
                if bin_edges[i] <= distance < bin_edges[i + 1]:
                    bin_key = f"{bin_edges[i]}-{bin_edges[i+1]}"
                    distance_distribution[bin_key]["count"] += 1
                    distance_distribution[bin_key]["stations"][station_id] += 1
                    break

        # Convert counts to percentages
        for bin_key, data in distance_distribution.items():
            data["percentage"] = (data["count"] / total_distances) * 100

        print("Distance Distribution:", distance_distribution)  # Debugging line
        return distance_distribution

    def test(self):
        """
        Test the class methods
        """
        print("Get Furthest Station Distance : ")
        print(self.get_furthest_station_distance())
        print("Get Distance Distribution : ")
        print(self.get_distance_distribution())
        return self.get_furthest_station_distance()
