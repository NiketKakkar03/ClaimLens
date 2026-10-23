"""Domain values shared by generation, training, and serving."""

from __future__ import annotations

from enum import StrEnum


class ReviewPriority(StrEnum):
    STANDARD = "standard"
    ELEVATED = "elevated"
    URGENT = "urgent"


class ClaimType(StrEnum):
    COLLISION = "collision"
    THEFT = "theft"
    WEATHER = "weather"
    GLASS = "glass"
    LIABILITY = "liability"


class ReportingChannel(StrEnum):
    MOBILE = "mobile"
    WEB = "web"
    PHONE = "phone"
    BROKER = "broker"
