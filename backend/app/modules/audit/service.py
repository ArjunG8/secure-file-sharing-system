"""M6 public interface. Implementation notes: docs/security-design.md, section M6."""

import logging

from sqlalchemy.orm import Session

from app.core.errors import NotImplementedFeature
from app.models import AuditLog
from app.modules.audit import MODULE_INFO
from app.modules.audit.schemas import AuditEventIn, ChainVerification

logger = logging.getLogger(__name__)

GENESIS_HASH = "0" * 64


def record_event(db: Session, event: AuditEventIn) -> AuditLog | None:
    """Append an HMAC-chained entry to audit_logs.

    STUB BEHAVIOUR (until M6 implements it): the event is NOT persisted. A warning
    is logged so other modules can already call this without failing. Returns None.
    """
    logger.warning(
        "Audit logging not implemented (M6): event %r was NOT recorded.", event.event_type
    )
    return None


def compute_entry_hash(prev_hash: str, payload: dict) -> str:
    """HMAC-SHA256(AUDIT_HMAC_KEY, bytes.fromhex(prev_hash) || canonical_json(payload)), hex."""
    raise NotImplementedFeature(MODULE_INFO, "Audit hash computation")


def verify_chain(db: Session) -> ChainVerification:
    """Recompute every entry_hash in id order and report the first mismatch."""
    raise NotImplementedFeature(MODULE_INFO, "Audit chain verification")
