"""
basemodel.py
----------
Defines canonical data schemas and source field mappings used for normalization.
"""

from pydantic import BaseModel, HttpUrl, Field, model_validator
from typing import List, Optional
from datetime import datetime

class Restaurant(BaseModel):
    place_id: str = Field(..., alias="id")
    name: str
    address: str = Field(..., alias="formattedAddress")
    website_url: Optional[HttpUrl] = Field(None, alias="websiteUri")
    google_maps_url: Optional[HttpUrl] = Field(None, alias="googleMapsUri")
    rating: Optional[float]
    
    @model_validator(mode="before")
    def flatten_nested_fields(cls, values):
        displayName = values.get("displayName", {})
        values["name"] = displayName.get("text")
        return values

class Review(BaseModel):
    author: Optional[str] = None
    url: Optional[HttpUrl] = Field(None, alias="googleMapsUri")
    rating: Optional[float] = None
    text: Optional[str] = None
    timestamp: Optional[int] = Field(None, alias="publishTime")

    original_lang: Optional[str] = None


    @model_validator(mode="before")
    def flatten_nested_fields(cls, values):
        """
        Extracts nested fields like:
          reviews[].authorAttribution.displayName
          reviews[].text.text
        from the raw JSON before validation.
        """
        author_attr = values.get("authorAttribution", {})
        text_obj = values.get("text", {})
        original_text = values.get("originalText", {})

        values["author"] = author_attr.get("displayName")
        values["url"] = author_attr.get("googleMapsUri")
        values["text"] = text_obj.get("text") if isinstance(text_obj, dict) else text_obj
        values["original_lang"] = original_text.get("languageCode")
    
        ts = values.get("publishTime")

        if isinstance(ts, str):
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                values["publishTime"] = int(dt.timestamp())
            except Exception:
                values["publishTime"] = None
        elif isinstance(ts, (int, float)):
            values["publishTime"] = int(ts)
        
        return values