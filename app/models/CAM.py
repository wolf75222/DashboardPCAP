import json
import os
import datetime
import re

from app.models.GeoNetworking import GeoNetworking


class CAM(GeoNetworking):
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
        generation_delta_time,
        station_type,
        latitude,
        longitude,
        semi_major_confidence,
        semi_minor_confidence,
        semi_major_orientation,
        altitude_value,
        altitude_confidence,
        stationID,
        seq_num=0,
    ):
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
        self.generation_delta_time = generation_delta_time
        self.station_type = station_type
        self.latitude = latitude
        self.longitude = longitude
        self.semi_major_confidence = semi_major_confidence
        self.semi_minor_confidence = semi_minor_confidence
        self.semi_major_orientation = semi_major_orientation
        self.altitude_value = altitude_value
        self.altitude_confidence = altitude_confidence

    def __str__(self):
        return (
            super().__str__()
            + f", Generation Delta Time: {self.generation_delta_time}, Station Type: {self.station_type}, Latitude: {self.latitude}, Longitude: {self.longitude}, Confidence Ellipse: ({self.semi_major_confidence}, {self.semi_minor_confidence}, {self.semi_major_orientation}), Altitude: {self.altitude_value} ({self.altitude_confidence})"
        )

    def to_dict(self):
        """Convert the CAM packet to a dictionary

        Returns:
            dict: The CAM packet as a dictionary
        """
        cam_dict = super().to_dict()
        cam_dict.update(
            {
                "generation_delta_time": self.generation_delta_time,
                "station_type": self.station_type,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "semi_major_confidence": self.semi_major_confidence,
                "semi_minor_confidence": self.semi_minor_confidence,
                "semi_major_orientation": self.semi_major_orientation,
                "altitude_value": self.altitude_value,
                "altitude_confidence": self.altitude_confidence,
            }
        )
        return cam_dict

    @staticmethod
    def from_dict(packet_dict):
        """Create a CAM packet from a dictionary

        Args:
            packet_dict (dict): The CAM packet as a dictionary

        Returns:
            CAM: The CAM packet
        """
        geo_packet = GeoNetworking.from_dict(packet_dict)
        cam_info = packet_dict["its"]["cam.CamPayload_element"]
        cam_params = cam_info["cam.camParameters_element"]
        basic_container = cam_params["cam.basicContainer_element"]
        ref_pos = basic_container["its.referencePosition_element"]
        pos_conf_ellipse = ref_pos["its.positionConfidenceEllipse_element"]
        altitude_info = ref_pos["its.altitude_element"]

        return CAM(
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
            stationID=geo_packet.stationID,
            seq_num=geo_packet.seq_num,
            generation_delta_time=cam_info["cam.generationDeltaTime"],
            station_type=basic_container["its.stationType"],
            latitude=ref_pos["its.latitude"],
            longitude=ref_pos["its.longitude"],
            semi_major_confidence=pos_conf_ellipse["its.semiMajorAxisLength"],
            semi_minor_confidence=pos_conf_ellipse["its.semiMinorAxisLength"],
            semi_major_orientation=pos_conf_ellipse["its.semiMajorAxisOrientation"],
            altitude_value=altitude_info["its.altitudeValue"],
            altitude_confidence=altitude_info["its.altitudeConfidence"],
        )

    def get_formatted_protocol(self):
        """Get the formatted protocol

        Returns:
            str: The formatted protocol
        """
        return "CAM"

    def is_within_radius_cam(self, lat, long, radius):
        """Check if a given position is within a certain radius of the CAM's position

        Args:
            lat (float): The latitude of the point to check
            long (float): The longitude of the point to check
            radius (float): The radius in kilometers

        Returns:
            bool: True if the point is within the radius, False otherwise
        """
        return self.haversine(self.latitude, self.longitude, lat, long) <= radius
