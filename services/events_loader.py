import os, glob, json
from typing import Optional

from sqlalchemy.orm import Session

from models import Event, EventRubric, Rubric


def get_latest_data_file(data_dir: str) -> Optional[str]:
    files = glob.glob(os.path.join(data_dir, "moscow_events*.json"))
    return max(files) if files else None


def _to_float_or_none(value):
    if value is None: return None
    try:
        return float(str(value).replace(",", ".").strip())
    except Exception:
        return None


def load_events_from_json(db: Session, filepath: str) -> None:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Expected JSON object mapping event_id -> event_data")

    visited_ids = set()

    for event_id, payload in data.items():
        visited_ids.add(event_id)

        event = db.query(Event).filter_by(id=event_id).first()
        if event:
            event.title = payload.get("title")
            event.image_url = payload.get("image_url")
            event.rating = _to_float_or_none(payload.get("rating"))
            event.price = payload.get("price")
            event.details = payload.get("details")
            event.archived = False
        else:
            event = Event(
                id=event_id,
                title=payload.get("title"),
                image_url=payload.get("image_url"),
                rating=_to_float_or_none(payload.get("rating")),
                price=payload.get("price"),
                details=payload.get("details"),
                archived=False
            )
            db.add(event)
            db.flush()

        # update rubrics
        db.query(EventRubric).filter(EventRubric.event_id == event_id).delete()
        for code in payload.get("rubrics", []):
            code = str(code).strip()
            if not code: continue
            rubric = db.query(Rubric).filter(Rubric.code == code).first()
            if not rubric:
                rubric = Rubric(code=code)
                db.add(rubric)
                db.flush()
            db.add(EventRubric(event_id=event_id, rubric_id=rubric.id))

    # archivate old events
    if visited_ids:
        db.query(Event).filter(~Event.id.in_(visited_ids)).update(
            {"archived": True}, synchronize_session=False
        )
    db.commit()
