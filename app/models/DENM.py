import json
import os
import datetime
import re

from app.models.GeoNetworking import GeoNetworking


class DENM(GeoNetworking):
    """
    A class to represent a DENM packet
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
        originating_station_id,
        sequence_number,
        detection_time,
        reference_time,
        latitude,
        longitude,
        semi_major_confidence,
        semi_minor_confidence,
        semi_major_orientation,
        altitude,
        altitude_confidence,
        validity_duration,
        station_type,
        stationID,
        seq_num=0,
    ):
        """Create a DENM packet

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
            originating_station_id (int): Originating station ID
            sequence_number (int): Sequence number
            detection_time (str): Detection time
            reference_time (str): Reference time
            latitude (float): Latitude
            longitude (float): Longitude
            semi_major_confidence (float): Semi-major confidence
            semi_minor_confidence (float): Semi-minor confidence
            semi_major_orientation (float): Semi-major orientation
            altitude (float): Altitude
            altitude_confidence (float): Altitude confidence
            validity_duration (int): Validity duration
            station_type (int): Station type
            stationID (int): Station ID
        """
        super().__init__(
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
            seq_num,
        )
        self.originating_station_id = originating_station_id
        self.sequence_number = sequence_number
        self.detection_time = detection_time
        self.reference_time = reference_time
        self.latitude = latitude
        self.longitude = longitude
        self.semi_major_confidence = semi_major_confidence
        self.semi_minor_confidence = semi_minor_confidence
        self.semi_major_orientation = semi_major_orientation
        self.altitude = altitude
        self.altitude_confidence = altitude_confidence
        self.validity_duration = validity_duration
        self.station_type = station_type

    def __str__(self):
        """To string method

        Returns:
            str: String of the DENM packet
        """
        return (
            super().__str__()
            + f", Originating Station ID: {self.originating_station_id}, Sequence Number: {self.sequence_number}, "
            f"Detection Time: {self.detection_time}, Reference Time: {self.reference_time}, "
            f"Event Position: ({self.latitude}, {self.longitude}), "
            f"Position Confidence: ({self.semi_major_confidence}, {self.semi_minor_confidence}, {self.semi_major_orientation}), "
            f"Altitude: {self.altitude} ({self.altitude_confidence}), Validity Duration: {self.validity_duration}, "
            f"Station Type: {self.station_type}"
        )

    def to_dict(self):
        """Convert the DENM packet to a dictionary

        Returns:
            dict: The DENM packet as a dictionary
        """
        denm_dict = super().to_dict()
        denm_dict.update(
            {
                "originating_station_id": self.originating_station_id,
                "sequence_number": self.sequence_number,
                "detection_time": self.detection_time,
                "reference_time": self.reference_time,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "semi_major_confidence": self.semi_major_confidence,
                "semi_minor_confidence": self.semi_minor_confidence,
                "semi_major_orientation": self.semi_major_orientation,
                "altitude": self.altitude,
                "altitude_confidence": self.altitude_confidence,
                "validity_duration": self.validity_duration,
                "station_type": self.station_type,
            }
        )
        return denm_dict

    @staticmethod
    def from_dict(packet_dict):
        """Create a DENM packet from a dictionary

        Args:
            packet_dict (dict): The DENM packet as a dictionary

        Returns:
            DENM: The DENM packet
        """
        geo_packet = GeoNetworking.from_dict(packet_dict)
        denm_info = packet_dict["its"]["denm.DenmPayload_element"][
            "denm.management_element"
        ]
        event_position = denm_info["denm.eventPosition_element"]
        pos_conf_ellipse = event_position["its.positionConfidenceEllipse_element"]
        altitude_info = event_position["its.altitude_element"]

        return DENM(
            src_mac=geo_packet.src_mac,
            dst_mac=geo_packet.dst_mac,
            protocol=geo_packet.protocol,
            time=geo_packet.time,
            frame_number=geo_packet.frame_number,
            frame_len=geo_packet.frame_len,
            eth_type=geo_packet.eth_type,
            rhl=geo_packet.rhl,
            src_pos_lat=geo_packet.src_pos_lat,
            src_pos_long=geo_packet.src_pos_long,
            src_pos_speed=geo_packet.src_pos_speed,
            originating_station_id=denm_info["denm.actionId_element"][
                "its.originatingStationId"
            ],
            stationID=geo_packet.stationID,
            seq_num=geo_packet.seq_num,
            sequence_number=denm_info["denm.actionId_element"]["its.sequenceNumber"],
            detection_time=denm_info["denm.detectionTime"],
            reference_time=denm_info["denm.referenceTime"],
            latitude=event_position["its.latitude"],
            longitude=event_position["its.longitude"],
            semi_major_confidence=pos_conf_ellipse["its.semiMajorConfidence"],
            semi_minor_confidence=pos_conf_ellipse["its.semiMinorConfidence"],
            semi_major_orientation=pos_conf_ellipse["its.semiMajorOrientation"],
            altitude=altitude_info["its.altitudeValue"],
            altitude_confidence=altitude_info["its.altitudeConfidence"],
            validity_duration=denm_info["denm.validityDuration"],
            station_type=denm_info["denm.stationType"],
        )

    def get_formatted_protocol(self):
        """Get the formatted protocol

        Returns:
            str: The formatted protocol
        """
        return "DENM"

    def is_within_radius_denm(self, lat, long, radius):
        """Check if a given position is within a certain radius of the DENM's event position

        Args:
            lat (float): The latitude of the point to check
            long (float): The longitude of the point to check
            radius (float): The radius in kilometers

        Returns:
            bool: True if the point is within the radius, False otherwise
        """
        return self.haversine(self.latitude, self.longitude, lat, long) <= radius
