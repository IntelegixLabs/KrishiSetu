from typing import List, Optional, Any
from pydantic import BaseModel, Field, field_validator


class RangeValue(BaseModel):
    average: float = Field(..., description="Average value")
    range: str = Field(..., description="Range string, e.g., '6.2 - 8.0'")

    @field_validator("range", mode="before")
    @classmethod
    def coerce_range(cls, v: Any) -> str:
        # Accept dicts like {min: x, max: y} or lists/tuples [x, y] and coerce to "x - y"
        if isinstance(v, dict):
            min_v = v.get("min") if "min" in v else v.get("low") or v.get("minimum")
            max_v = v.get("max") if "max" in v else v.get("high") or v.get("maximum")
            if min_v is not None and max_v is not None:
                return f"{min_v} - {max_v}"
        if isinstance(v, (list, tuple)) and len(v) == 2:
            return f"{v[0]} - {v[1]}"
        return v


class NutrientStats(BaseModel):
    nitrogen_kg_per_ha: RangeValue
    phosphorus_kg_per_ha: RangeValue
    potassium_kg_per_ha: RangeValue


class Soil(BaseModel):
    type: str
    ph: RangeValue
    moisture_percentage: RangeValue
    organic_carbon_percentage: RangeValue
    nutrients: NutrientStats


class Crop(BaseModel):
    types: List[str]
    season: str
    growth_stages: List[str]


class Rainfall(BaseModel):
    last_24h: RangeValue
    forecast_24h: RangeValue


class Weather(BaseModel):
    temperature_c: RangeValue
    humidity_pct: RangeValue
    rainfall_mm: Rainfall
    wind_speed_mps: RangeValue


class Finance(BaseModel):
    market_price_inr_per_quintal: RangeValue
    market_trend: str
    applicable_schemes: List[str]


class PestRisk(BaseModel):
    average: str
    notable_risks: List[str]


class IrrigationNeed(BaseModel):
    average: str
    specific_needs: List[str]


class Risks(BaseModel):
    pest_risk: PestRisk
    irrigation_need: IrrigationNeed


class SpecificAction(BaseModel):
    crop: str
    action: str


class IrrigationRecommendations(BaseModel):
    general: str
    specific: List[SpecificAction]


class CropManagement(BaseModel):
    general: str
    specific: List[SpecificAction]


class Recommendations(BaseModel):
    irrigation: IrrigationRecommendations
    crop_management: CropManagement


class AgriculturalAnalysis(BaseModel):
    soil: Soil
    crop: Crop
    weather: Weather
    finance: Finance
    risks: Risks
    recommendations: Recommendations
    summary: str


