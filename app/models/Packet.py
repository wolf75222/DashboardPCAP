import json
import os
import datetime
import re
from dateutil import parser


class Packet:
    """
    A class to represent a packet

    Attributes:
        src_mac (str): Source MAC address
        dst_mac (str): Destination MAC address
        protocol (str): Protocol
        time (str): Time
        frame_number (int): Frame number
        frame_len (int): Frame length
        eth_type (str): Ethernet type
    """

    def __init__(
        self, src_mac, dst_mac, protocol, time, frame_number, frame_len, eth_type
    ):
        """Create a packet

        Args:
            src_mac (str): Source MAC address
            dst_mac (str): Destination MAC address
            protocol (str): Protocol
            time (str): Time
            frame_number (int): Frame number
            frame_len (int): Frame length
            eth_type (str): Ethernet type
        """
        self.src_mac = src_mac
        self.dst_mac = dst_mac
        self.protocol = protocol
        self.time = self._format_time(time)
        self.frame_number = frame_number
        self.frame_len = frame_len
        self.eth_type = eth_type

    def __str__(self):
        """Summary of the packet

        Returns:
            str: Summary of the packet
        """
        return (
            f"Packet(SRC MAC: {self.src_mac}, DST MAC: {self.dst_mac}, Protocol: {self.protocol}, "
            f"Time: {self.time}, Frame Number: {self.frame_number}, Frame Length: {self.frame_len}, "
            f"Ethernet Type: {self.eth_type})"
        )

    def summary(self):
        """Summary of the packet

        Returns:
            str: Summary of the packet
        """
        return (
            f"From: {self.src_mac}, To: {self.dst_mac}, Protocol: {self.protocol}, "
            f"Frame Length: {self.frame_len}, Ethernet Type: {self.eth_type}"
        )

    def to_dict(self):
        """Convert the packet to a dictionary

        Returns:
            dict: The packet as a dictionary
        """
        return {
            "src_mac": self.src_mac,
            "dst_mac": self.dst_mac,
            "protocol": self.protocol,
            "time": self.time,
            "frame_number": self.frame_number,
            "frame_len": self.frame_len,
            "eth_type": self.eth_type,
        }

    @staticmethod
    def from_dict(packet_dict):
        """Create a packet from a dictionary

        Args:
            packet_dict (dict): The packet as a dictionary

        Returns:
            Packet: The packet
        """
        return Packet(
            src_mac=packet_dict["eth"]["eth.src"],
            dst_mac=packet_dict["eth"]["eth.dst"],
            protocol=packet_dict["frame"]["frame.protocols"],
            time=packet_dict["frame"]["frame.time"],
            frame_number=packet_dict["frame"]["frame.number"],
            frame_len=packet_dict["frame"]["frame.len"],
            eth_type=packet_dict["eth"]["eth.type"],
        )

    def _format_time(self, time_str):
        """Try to format the time string using dateutil parser and reformat it to the desired format.

        Args:
            time_str (str): The original time string.

        Returns:
            str: The formatted time string in '%b %d, %Y %H:%M:%S.%f000 %Z' format.
        """
        try:
            parsed_date = parser.parse(time_str)
            return parsed_date.strftime("%b %d, %Y %H:%M:%S.%f000 %Z")
        except (ValueError, TypeError) as e:
            print(f"Error parsing date: {e}")
            return "Invalid date format"

    @staticmethod
    def from_json(packet_json):
        """Create a packet from a JSON string

        Args:
            packet_json (str): The packet as a JSON string

        Returns:
            Packet: The packet
        """
        packet_dict = json.loads(packet_json)
        return Packet.from_dict(packet_dict)

    def _format_time(self, time_str):
        """Try to format the time string using dateutil parser.

        Args:
            time_str (str): The original time string.

        Returns:
            str: The formatted time string in 'YYYY-MM-DD HH:MM:SS' format.
        """
        try:
            parsed_date = parser.parse(time_str)
            return parsed_date.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError) as e:
            print(f"Error parsing date: {e}")
            return "Invalid date format"

    def get_formatted_protocol(self):
        """Get the formatted protocol

        Returns:
            str: The formatted protocol
        """
        # eth:ethertype:ipv6:ipv6.hopopts:icmpv6 -> ICMPv6
        return self.protocol.split(":")[-1].upper()

    def get_formatted_src_mac(self):
        """Get the formatted source MAC address

        Returns:
            str: The formatted source MAC address
        """
        if self.src_mac == "ff:ff:ff:ff:ff:ff":
            return "Broadcast"
        return self.src_mac

    def get_formatted_dst_mac(self):
        """Get the formatted destination MAC address

        Returns:
            str: The formatted destination MAC address
        """
        if self.dst_mac == "ff:ff:ff:ff:ff:ff":
            return "Broadcast"
        return self.dst_mac

    def get_formatted_eth_type(self):
        """Get the formatted Ethernet type

        Returns:
            str: The formatted Ethernet type
        """
        return self.eth_type.upper()

    def get_formatted_time(self):
        """Get the formatted time

        Returns:
            str: The formatted time
        """
        return self.time
