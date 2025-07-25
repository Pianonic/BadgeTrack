from pydantic import BaseModel, Field
from typing import Annotated

class BadgeParams(BaseModel):
    tag: Annotated[str, Field(strip_whitespace=True, min_length=1, max_length=200)]
    label: Annotated[str, Field(strip_whitespace=True, min_length=1, max_length=20)] = "visits"
    color: Annotated[str, Field(strip_whitespace=True, min_length=3, max_length=10)] = "4ade80"
    style: Annotated[str, Field(strip_whitespace=True, min_length=2, max_length=10)] = "flat"
    logo: Annotated[str, Field(strip_whitespace=True, max_length=20)] = ""

class TagStatsResponse(BaseModel):
    tag: str
    visit_count: int
    last_updated: int

class SystemStatsResponse(BaseModel):
    total_tracked_tags: int
    total_visits: int
    new_badges_today: int

class AppInfoResponse(BaseModel):
    version: str
    environment: str
