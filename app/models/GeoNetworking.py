import json
import os
import datetime
import re
import math


from app.models.Packet import Packet


class GeoNetworking(Packet):
    """A class to represent a GeoNetworking packet

    Attributes:
        rhl (int): RHL
        src_pos_lat (float): Source position latitude
        src_pos_long (float): Source position longitude
        src_pos_speed (float): Source position speed
        stationID (int): Station ID
        seq_num (int): Sequence number
    """

    def __init__(
        self,
        src_mac,
        dst_mac,
        protocol,
        time,
        frame_number,
        frame_len,
        eth_type,
        rhl,
        src_pos_lat,
        src_pos_long,
        src_pos_speed,
        stationID,
        seq_num=0,
    ):
        """Create a GeoNetworking packet

        Args:
            src_mac (str): Source MAC address
            dst_mac (str): Destination MAC address
            protocol (str): Protocol
            time (str): Time
            frame_number (int): Frame number
            frame_len (int): Frame length
            eth_type (str): Ethernet type
            rhl (int): RHL
            src_pos_lat (float): Source position latitude
            src_pos_long (float): Source position longitude
            src_pos_speed (float): Source position speed
            stationID (int): Station ID
            seq_num (int): Sequence number
        """
        super().__init__(
            src_mac,
            dst_mac,
            protocol,
            time,
            frame_number,
            frame_len,
            eth_type,
        )
        self.rhl = rhl
        self.src_pos_lat = src_pos_lat
        self.src_pos_long = src_pos_long
        self.src_pos_speed = src_pos_speed
        self.stationID = stationID
        self.seq_num = seq_num

    def __str__(self):
        """To string method

        Returns:
            str: String of the GeoNetworking packet
        """
        return (
            f"GeoNetworking(SRC MAC: {self.src_mac}, DST MAC: {self.dst_mac}, Protocol: {self.protocol}, "
            f"Time: {self.time}, Frame Number: {self.frame_number}, Frame Length: {self.frame_len}, "
            f"Ethernet Type: {self.eth_type}, RHL: {self.rhl}, Source Position: ({self.src_pos_lat}, {self.src_pos_long}), "
            f"Source Speed: {self.src_pos_speed})"
        )

    def summary(self):
        """Summary of the GeoNetworking packet

        Returns:
            str: Summary of the GeoNetworking packet
        """
        return (
            f"From: {self.src_mac}, To: {self.dst_mac}, Protocol: {self.protocol}, "
            f"Frame Length: {self.frame_len}, Ethernet Type: {self.eth_type}, RHL: {self.rhl}, "
            f"Source Position: ({self.src_pos_lat}, {self.src_pos_long}), Source Speed: {self.src_pos_speed}"
        )

    def to_dict(self):
        """Convert the GeoNetworking packet to a dictionary

        Returns:
            dict: The GeoNetworking packet as a dictionary
        """
        packet_dict = super().to_dict()
        packet_dict.update(
            {
                "rhl": self.rhl,
                "src_pos_lat": self.src_pos_lat,
                "src_pos_long": self.src_pos_long,
                "src_pos_speed": self.src_pos_speed,
                "stationID": self.stationID,
                "seq_num": self.seq_num,
            }
        )
        return packet_dict

    @staticmethod
    def from_dict(packet_dict):
        """Create a GeoNetworking packet from a dictionary

        Args:
            packet_dict (dict): The GeoNetworking packet as a dictionary

        Returns:
            GeoNetworking: The GeoNetworking packet
        """
        try:
            src_pos_info = packet_dict["gnw"]["geonw.gbc"]["geonw.src_pos_tree"]
        except KeyError:
            src_pos_info = packet_dict["gnw"]["geonw.tsb"][
                "geonw.src_pos_tree"
            ]  # Alternative key for source position information

        try:
            seq_num = packet_dict["gnw"]["geonw.gbc"]["geonw.seq_num"]
        except KeyError:
            seq_num = 0

        return GeoNetworking(
            src_mac=packet_dict["eth"]["eth.src"],
            dst_mac=packet_dict["eth"]["eth.dst"],
            protocol=packet_dict["frame"]["frame.protocols"],
            time=packet_dict["frame"]["frame.time"],
            frame_number=packet_dict["frame"]["frame.number"],
            frame_len=packet_dict["frame"]["frame.len"],
            eth_type=packet_dict["eth"]["eth.type"],
            rhl=packet_dict["gnw"]["geonw.bh"]["geonw.bh.rhl"],
            src_pos_lat=src_pos_info["geonw.src_pos.lat"],
            src_pos_long=src_pos_info["geonw.src_pos.long"],
            src_pos_speed=src_pos_info["geonw.src_pos.speed"],
            # {Root}._source.layers.its.its.ItsPduHeader_element its.stationId
            stationID=packet_dict["its"]["its.ItsPduHeader_element"]["its.stationId"],
            seq_num=seq_num,
        )

    @staticmethod
    def from_json(packet_json):
        """Create a GeoNetworking packet from a JSON string

        Args:
            packet_json (str): The GeoNetworking packet as a JSON string

        Returns:
            GeoNetworking: The GeoNetworking packet
        """
        packet_dict = json.loads(packet_json)
        return GeoNetworking.from_dict(packet_dict)

    def get_formatted_protocol(self):
        """Get the formatted protocol

        Returns:
            str: The formatted protocol
        """
        return "GeoNetworking"

    def is_within_radius(self, lat, long, radius):
        """Check if the source position is within a certain radius

        Args:
            lat (float): The latitude
            long (float): The longitude
            radius (float): The radius

        Returns:
            bool: True if the source position is within the radius, False otherwise
        """
        return self.calculate_distance(lat, long) <= radius

    def calculate_distance(self, lat, long):
        """Calculate the distance between the source position and a given position

        Args:
            lat (float): The latitude
            long (float): The longitude

        Returns:
            float: The distance between the source position and the given position
        """
        return self.haversine(lat, long, self.src_pos_lat, self.src_pos_long)

    @staticmethod
    def haversine(lat1, long1, lat2, long2):
        """Calculate the haversine distance between two points

        Args:
            lat1 (float): The latitude of the first point
            long1 (float): The longitude of the first point
            lat2 (float): The latitude of the second point
            long2 (float): The longitude of the second point

        Returns:
            float: The haversine distance between the two points
        """
        # Convert latitude and longitude from degrees to radians
        lat1, long1, lat2, long2 = map(math.radians, [lat1, long1, lat2, long2])

        # Haversine formula
        dlat = lat2 - lat1
        dlong = long2 - long1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlong / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        r = 6371  # Radius of Earth in kilometers. Use 3956 for miles
        return c * r
