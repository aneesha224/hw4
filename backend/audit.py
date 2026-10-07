import json
from datetime import datetime, timezone
from pathlib import Path
from models import AuditEntry

AUDIT_FILE = Path(__file__).resolve().parents[1] / "output" / "audit_trail.json"

def audit(event: str, tool_name: str, arguments: object, result: object, stop_reason: str | None = None) -> None:
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    entries = []
    if AUDIT_FILE.exists():
        try: entries = json.loads(AUDIT_FILE.read_text())
        except json.JSONDecodeError: entries = []
    entry = AuditEntry(time=datetime.now(timezone.utc).isoformat(), event=event, tool_name=tool_name, arguments=str(arguments)[:500], result=str(result)[:500], stop_reason=stop_reason)
    AUDIT_FILE.write_text(json.dumps(entries + [entry.model_dump()], indent=2) + "\n")
