"""PersonaPlex audio gateway for WebRTC/RTP and Priority Interruption flags."""
from __future__ import annotations

import base64
import dataclasses
import logging
import struct
import time
from typing import Optional


RTP_HEADER_FMT = "!BBHII"
RTP_HEADER_SIZE = 12
PRIORITY_EXTENSION_ID = 0xA11A

logger = logging.getLogger("arabella.audio_gateway")


@dataclasses.dataclass
class RtpHeader:
    version: int
    padding: int
    extension: int
    cc: int
    marker: int
    payload_type: int
    sequence: int
    timestamp: int
    ssrc: int


@dataclasses.dataclass
class AudioFrame:
    payload: bytes
    header: RtpHeader
    priority_interruption: bool
    received_at: float

    def to_sense_packet_payload(self) -> dict:
        return {
            "codec": "pcm_s16le",
            "sample_rate_hz": 16000,
            "channels": 1,
            "priority_interruption": self.priority_interruption,
            "rtp_header": {
                "sequence": self.header.sequence,
                "timestamp": self.header.timestamp,
                "ssrc": self.header.ssrc,
                "extension": {
                    "id": PRIORITY_EXTENSION_ID,
                    "priority_interruption": self.priority_interruption,
                },
            },
            "frame_bytes": base64.b64encode(self.payload).decode("ascii"),
        }


class AudioGateway:
    """Minimal RTP parsing with a Priority Interruption header extension.

    This is a lightweight stub so GPU-1 can normalize audio packets
    before routing them into Sense-Packets and Letta jitter buffers.
    """

    def __init__(self) -> None:
        self.last_sequence: Optional[int] = None

    def parse_rtp_packet(self, packet: bytes) -> AudioFrame:
        if len(packet) < RTP_HEADER_SIZE:
            raise ValueError("RTP packet too short")

        b1, b2, sequence, timestamp, ssrc = struct.unpack(
            RTP_HEADER_FMT, packet[:RTP_HEADER_SIZE]
        )
        version = b1 >> 6
        padding = (b1 >> 5) & 1
        extension = (b1 >> 4) & 1
        cc = b1 & 0x0F
        marker = (b2 >> 7) & 1
        payload_type = b2 & 0x7F

        header = RtpHeader(
            version=version,
            padding=padding,
            extension=extension,
            cc=cc,
            marker=marker,
            payload_type=payload_type,
            sequence=sequence,
            timestamp=timestamp,
            ssrc=ssrc,
        )

        offset = RTP_HEADER_SIZE + (cc * 4)
        priority_interruption = False

        if extension:
            if len(packet) < offset + 4:
                raise ValueError("RTP header extension missing")
            ext_profile, ext_length = struct.unpack("!HH", packet[offset : offset + 4])
            offset += 4
            ext_bytes = ext_length * 4
            extension_payload = packet[offset : offset + ext_bytes]
            offset += ext_bytes
            if ext_profile == PRIORITY_EXTENSION_ID and extension_payload:
                priority_interruption = bool(extension_payload[0])

        payload = packet[offset:]

        if self.last_sequence is not None and sequence != (self.last_sequence + 1) % 65536:
            logger.warning(
                "RTP sequence discontinuity: last=%s current=%s",
                self.last_sequence,
                sequence,
            )
        self.last_sequence = sequence

        return AudioFrame(
            payload=payload,
            header=header,
            priority_interruption=priority_interruption,
            received_at=time.time(),
        )

    def build_priority_extension(self, priority_interruption: bool) -> bytes:
        payload = b"\x01" if priority_interruption else b"\x00"
        # Pad to 32-bit boundary for RTP header extension.
        padding = (4 - (len(payload) % 4)) % 4
        payload += b"\x00" * padding
        length_words = len(payload) // 4
        return struct.pack("!HH", PRIORITY_EXTENSION_ID, length_words) + payload


__all__ = ["AudioGateway", "AudioFrame", "RtpHeader"]
