import io
from typing import Any, Dict, List, Tuple
from datetime import datetime

import pandas as pd

try:
    # Optional import for PDF generation; validated at runtime
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas
except Exception:  # pragma: no cover
    A4 = None
    cm = None
    canvas = None


def _safe_get(dct: Dict[str, Any], path: List[str], default: Any = None) -> Any:
    current: Any = dct
    for key in path:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


def build_report_dict(
    query: str,
    context: Dict[str, Any],
    crew_result: Dict[str, Any],
    language: str = "en",
) -> Dict[str, Any]:
    now_iso = datetime.utcnow().isoformat()

    data = crew_result.get("data", {}) if isinstance(crew_result, dict) else {}
    mcp = data.get("mcp_data", {})
    insights = data.get("agent_insights", {})

    weather_insight = insights.get("weather", {})
    crop_insight = insights.get("crop", {})
    finance_insight = insights.get("finance", {})

    report: Dict[str, Any] = {
        "metadata": {
            "generated_at": now_iso,
            "query": query,
            "language": language,
            "location": (context or {}).get("location", ""),
            "crop": (context or {}).get("crop_type", ""),
            "confidence": crew_result.get("confidence", 0.0),
            "source": crew_result.get("source", "KrishiSetu"),
        },
        "weather": _safe_get(weather_insight, ["data"], {}) or mcp.get("weather", {}),
        "soil": mcp.get("soil", {}),
        "market": mcp.get("market", {}),
        "policies": mcp.get("policies", []),
        "crop": _safe_get(crop_insight, ["data"], {}),
        "finance": _safe_get(finance_insight, ["data"], {}),
        "recommendations": data.get("recommendations", {}),
    }

    return report


def build_csv_bytes(report: Dict[str, Any]) -> bytes:
    rows: List[Dict[str, Any]] = []

    # Metadata
    for k, v in report.get("metadata", {}).items():
        rows.append({"Section": "Metadata", "Key": k, "Value": v})

    # Weather snapshot
    weather = report.get("weather", {})
    if isinstance(weather, dict):
        for k, v in weather.items():
            if k == "forecast" and isinstance(v, list):
                # Include first 5 forecast rows flattened
                for i, item in enumerate(v[:5]):
                    rows.append({
                        "Section": "WeatherForecast",
                        "Key": f"row_{i}",
                        "Value": item,
                    })
            else:
                rows.append({"Section": "Weather", "Key": k, "Value": v})

    # Crop recommendations
    crop = report.get("crop", {})
    if isinstance(crop, dict):
        recs = crop.get("recommendations") or []
        if isinstance(recs, list):
            for item in recs:
                rows.append({"Section": "CropRecommendations", "Key": item.get("name", ""), "Value": item})

        # Suitability analysis (flatten)
        suitability = crop.get("suitability_analysis") or {}
        if isinstance(suitability, dict):
            for name, entry in suitability.items():
                rows.append({"Section": "CropSuitability", "Key": name, "Value": entry})

    # Finance
    finance = report.get("finance", {})
    for key in ["loan_options", "government_schemes", "insurance_options"]:
        items = finance.get(key) or []
        if isinstance(items, list):
            for item in items[:20]:
                rows.append({"Section": key, "Key": item.get("name", ""), "Value": item})
    if finance.get("loan_eligibility"):
        rows.append({"Section": "loan_eligibility", "Key": "eligible_amount", "Value": finance["loan_eligibility"].get("eligible_amount")})

    # Recommendations
    recs = report.get("recommendations", {})
    if isinstance(recs, dict):
        for category, items in recs.items():
            if isinstance(items, list):
                for item in items:
                    rows.append({"Section": f"Recommendations:{category}", "Key": "item", "Value": item})

    df = pd.DataFrame(rows)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")


def build_excel_bytes(report: Dict[str, Any]) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Overview sheet
        overview_items = report.get("metadata", {})
        pd.DataFrame(list(overview_items.items()), columns=["Field", "Value"]).to_excel(writer, sheet_name="Overview", index=False)

        # Weather sheet
        weather = report.get("weather", {})
        if isinstance(weather, dict):
            snapshot = {k: v for k, v in weather.items() if k != "forecast"}
            if snapshot:
                pd.DataFrame(list(snapshot.items()), columns=["Metric", "Value"]).to_excel(writer, sheet_name="Weather", index=False)
            forecast = weather.get("forecast", [])
            if isinstance(forecast, list) and forecast:
                pd.DataFrame(forecast).to_excel(writer, sheet_name="Forecast", index=False)

        # Crop sheets
        crop = report.get("crop", {})
        if isinstance(crop, dict):
            recs = crop.get("recommendations") or []
            if isinstance(recs, list) and recs:
                pd.DataFrame(recs).to_excel(writer, sheet_name="CropRecs", index=False)
            suit = crop.get("suitability_analysis") or {}
            if isinstance(suit, dict) and suit:
                suit_rows: List[Dict[str, Any]] = []
                for name, entry in suit.items():
                    row = {"crop": name}
                    row.update(entry)
                    suit_rows.append(row)
                pd.DataFrame(suit_rows).to_excel(writer, sheet_name="Suitability", index=False)

        # Finance sheets
        finance = report.get("finance", {})
        for key, sheet in [("loan_options", "Loans"), ("government_schemes", "Schemes"), ("insurance_options", "Insurance")]:
            items = finance.get(key) or []
            if isinstance(items, list) and items:
                pd.DataFrame(items).to_excel(writer, sheet_name=sheet, index=False)
        if finance.get("loan_eligibility"):
            pd.DataFrame(list(finance["loan_eligibility"].items()), columns=["Metric", "Value"]).to_excel(writer, sheet_name="Eligibility", index=False)

        # MCP data
        for key, sheet in [("soil", "Soil"), ("market", "Market"), ("policies", "Policies")]:
            value = report.get(key)
            if isinstance(value, dict) and value:
                pd.DataFrame(list(value.items()), columns=["Key", "Value"]).to_excel(writer, sheet_name=sheet, index=False)
            elif isinstance(value, list) and value:
                pd.DataFrame(value).to_excel(writer, sheet_name=sheet, index=False)

        # Recommendations
        recs = report.get("recommendations", {})
        if isinstance(recs, dict) and recs:
            rec_rows: List[Dict[str, Any]] = []
            for category, items in recs.items():
                if isinstance(items, list):
                    for item in items:
                        rec_rows.append({"category": category, "item": item})
            if rec_rows:
                pd.DataFrame(rec_rows).to_excel(writer, sheet_name="Recommendations", index=False)

    return output.getvalue()


def build_pdf_bytes(report: Dict[str, Any]) -> bytes:
    if canvas is None or A4 is None or cm is None:
        raise RuntimeError("PDF generation dependencies are missing. Please install reportlab.")

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    def draw_title(text: str, y: float) -> float:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2 * cm, y, text)
        return y - 0.7 * cm

    def draw_kv_block(title: str, data: Dict[str, Any], y: float) -> float:
        y = draw_title(title, y)
        c.setFont("Helvetica", 10)
        for k, v in data.items():
            text = f"- {k}: {v}"
            if y < 2 * cm:
                c.showPage()
                y = height - 2 * cm
                c.setFont("Helvetica", 10)
            c.drawString(2.2 * cm, y, str(text)[:150])
            y -= 0.5 * cm
        return y

    def draw_list_block(title: str, items: List[Any], y: float) -> float:
        y = draw_title(title, y)
        c.setFont("Helvetica", 10)
        for item in items:
            if y < 2 * cm:
                c.showPage()
                y = height - 2 * cm
                c.setFont("Helvetica", 10)
            c.drawString(2.2 * cm, y, f"- {str(item)[:150]}")
            y -= 0.5 * cm
        return y

    y = height - 2 * cm
    meta = report.get("metadata", {})
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, y, "KrishiSetu Agriculture Report")
    y -= 1 * cm
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, f"Generated: {meta.get('generated_at', '')}")
    y -= 0.5 * cm
    c.drawString(2 * cm, y, f"Query: {meta.get('query', '')}")
    y -= 0.5 * cm
    c.drawString(2 * cm, y, f"Location: {meta.get('location', '')}  |  Crop: {meta.get('crop', '')}")
    y -= 0.5 * cm
    c.drawString(2 * cm, y, f"Confidence: {meta.get('confidence', 0.0)}  |  Source: {meta.get('source', '')}")
    y -= 0.8 * cm

    # Weather
    weather = report.get("weather", {})
    if isinstance(weather, dict) and weather:
        snap = {k: v for k, v in weather.items() if k != "forecast"}
        if snap:
            y = draw_kv_block("Weather", snap, y)
        forecast = weather.get("forecast", [])
        if isinstance(forecast, list) and forecast:
            y = draw_list_block("Forecast (next 5)", [str(item) for item in forecast[:5]], y)

    # Crop
    crop = report.get("crop", {})
    if isinstance(crop, dict) and crop:
        recs = crop.get("recommendations") or []
        if recs:
            y = draw_list_block("Crop Recommendations", [item.get("name", str(item)) for item in recs[:10]], y)
        suit = crop.get("suitability_analysis") or {}
        if suit:
            y = draw_list_block("Suitability (top)", [f"{name}: {entry.get('suitability_score', '')}" for name, entry in list(suit.items())[:10]], y)

    # Finance
    finance = report.get("finance", {})
    if isinstance(finance, dict) and finance:
        loans = finance.get("loan_options") or []
        if loans:
            y = draw_list_block("Loan Options", [lo.get("name", "") for lo in loans[:10]], y)
        schemes = finance.get("government_schemes") or []
        if schemes:
            y = draw_list_block("Schemes", [sc.get("name", "") for sc in schemes[:10]], y)
        eligibility = finance.get("loan_eligibility") or {}
        if eligibility:
            y = draw_kv_block("Loan Eligibility", eligibility, y)

    # Recommendations
    recs = report.get("recommendations", {})
    if isinstance(recs, dict) and recs:
        y = draw_title("Recommendations", y)
        c.setFont("Helvetica", 10)
        for category, items in recs.items():
            if y < 2 * cm:
                c.showPage()
                y = height - 2 * cm
                c.setFont("Helvetica", 10)
            c.drawString(2 * cm, y, f"- {category}")
            y -= 0.5 * cm
            for item in items[:5]:
                if y < 2 * cm:
                    c.showPage()
                    y = height - 2 * cm
                    c.setFont("Helvetica", 10)
                c.drawString(2.8 * cm, y, f"• {str(item)[:140]}")
                y -= 0.45 * cm

    c.showPage()
    c.save()
    return buffer.getvalue()


