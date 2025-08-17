#!/usr/bin/env python3
"""
Generate dummy agriculture reports (CSV, Excel, PDF) into the reports/ folder.

This script does not call external services. It uses static sample data
formatted similarly to crew results to exercise the reporting pipeline.
"""

import os
from pathlib import Path
from datetime import datetime

from utils.reporting import (
    build_report_dict,
    build_csv_bytes,
    build_excel_bytes,
    build_pdf_bytes,
)


def sample_crew_result() -> dict:
    # Minimal structure aligned with AgriculturalCrew.process_comprehensive_query output
    return {
        "success": True,
        "source": "Agricultural Crew (Dummy)",
        "confidence": 0.82,
        "data": {
            "mcp_data": {
                "weather": {
                    "temperature": 29.5,
                    "humidity": 62,
                    "description": "partly cloudy",
                    "wind_speed": 4.7,
                    "pressure": 1012,
                    "forecast": [
                        {"time": "2025-08-17 12:00:00", "temperature": 29.5, "humidity": 62, "description": "clouds"},
                        {"time": "2025-08-17 15:00:00", "temperature": 30.2, "humidity": 58, "description": "clear"},
                    ],
                },
                "soil": {"soil_moisture": "Moderate", "ph": 6.8, "type": "Alluvial"},
                "market": {"crop": "Wheat", "current_price": 2100, "trend": "Rising"},
                "policies": [
                    {"name": "PM-KISAN", "benefit": "₹6,000/year", "eligibility": "Small/Marginal"}
                ],
            },
            "agent_insights": {
                "weather": {
                    "success": True,
                    "confidence": 0.9,
                    "data": {
                        "current_weather": {
                            "temperature": 29.5,
                            "humidity": 62,
                            "description": "partly cloudy",
                            "wind_speed": 4.7,
                            "pressure": 1012,
                        },
                        "forecast": {
                            "forecast": [
                                {"time": "2025-08-17 12:00:00", "temperature": 29.5, "humidity": 62, "description": "clouds"},
                                {"time": "2025-08-17 15:00:00", "temperature": 30.2, "humidity": 58, "description": "clear"},
                            ]
                        },
                        "irrigation_recommendation": {
                            "recommendation": "Moderate irrigation recommended",
                            "priority": "Medium",
                            "next_irrigation": "Within 48 hours",
                        },
                    },
                },
                "crop": {
                    "success": True,
                    "confidence": 0.78,
                    "data": {
                        "recommendations": [
                            {"name": "Wheat", "varieties": ["HD-2967", "PBW-343"], "duration": 140, "water_need": "Medium"},
                            {"name": "Mustard", "varieties": ["Pusa Bold"], "duration": 120, "water_need": "Low"},
                        ],
                        "suitability_analysis": {
                            "Wheat": {"suitability_score": 85, "factors": ["Favorable temperature", "Market demand"], "recommendation": "Highly Recommended"},
                            "Mustard": {"suitability_score": 72, "factors": ["Low water requirement"], "recommendation": "Recommended"},
                        },
                        "market_data": {"Wheat": {"current_price": 2100, "trend": "Rising"}},
                        "crop_calendar": {
                            "planting_start": "October",
                            "planting_end": "December",
                            "harvest_start": "March",
                            "harvest_end": "May",
                        },
                    },
                },
                "finance": {
                    "success": True,
                    "confidence": 0.74,
                    "data": {
                        "loan_options": [
                            {"name": "Kisan Credit Card (KCC)", "interest_rate": "7.0%", "max_amount": "₹3,00,000"},
                            {"name": "Agricultural Term Loan", "interest_rate": "8.5%", "max_amount": "₹10,00,000"},
                        ],
                        "government_schemes": [
                            {"name": "PM Fasal Bima Yojana", "coverage": "Yield & weather risk"},
                            {"name": "PM-KISAN", "benefit": "₹6,000/year"},
                        ],
                        "insurance_options": [
                            {"name": "PMFBY", "premium_rate": "2% Kharif"},
                        ],
                        "loan_eligibility": {"eligible_amount": "₹80,000", "factors": ["Land area: 1.6 ha"]},
                    },
                },
            },
            "recommendations": {
                "immediate_actions": ["Irrigate within 48 hours"],
                "short_term_plan": ["Apply nitrogen fertilizer per schedule"],
                "long_term_strategy": ["Consider crop diversification"],
                "risk_mitigation": ["Monitor for rust diseases"],
                "opportunities": ["Rising wheat prices in local mandi"],
            },
        },
    }


def main():
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    query = "Dummy agricultural advisory report"
    context = {"location": "Mumbai", "crop_type": "Wheat", "season": "Rabi", "soil_type": "Alluvial"}
    crew_result = sample_crew_result()

    report_dict = build_report_dict(query, context, crew_result, language="en")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # CSV
    csv_bytes = build_csv_bytes(report_dict)
    (reports_dir / f"dummy_report_{ts}.csv").write_bytes(csv_bytes)

    # Excel
    try:
        xlsx_bytes = build_excel_bytes(report_dict)
        (reports_dir / f"dummy_report_{ts}.xlsx").write_bytes(xlsx_bytes)
    except Exception as e:
        print(f"Excel generation skipped: {e}")

    # PDF
    try:
        pdf_bytes = build_pdf_bytes(report_dict)
        (reports_dir / f"dummy_report_{ts}.pdf").write_bytes(pdf_bytes)
    except Exception as e:
        print(f"PDF generation skipped: {e}")

    print(f"Dummy reports created in: {reports_dir.resolve()}")


if __name__ == "__main__":
    main()


