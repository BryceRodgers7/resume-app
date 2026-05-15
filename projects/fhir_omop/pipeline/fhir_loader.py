"""Load synthetic FHIR R4 bundles from disk.

Reads Synthea-style FHIR Bundle JSON files from a directory and groups every
resource entry by its `resourceType`. Intentionally tiny — there is no
streaming parsing, validation, or reference resolution. Happy-path only.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Iterable, List

logger = logging.getLogger(__name__)


def discover_bundle_files(sample_data_dir: Path) -> List[Path]:
    """Return all *.json files in `sample_data_dir`, sorted for stable order."""
    return sorted(Path(sample_data_dir).glob("*.json"))


def load_bundle(bundle_path: Path) -> dict:
    """Parse a single FHIR Bundle JSON file."""
    with open(bundle_path, "r", encoding="utf-8") as f:
        return json.load(f)


def iter_resources(bundle: dict) -> Iterable[dict]:
    """Yield each `entry.resource` from a FHIR Bundle, skipping empty entries."""
    for entry in bundle.get("entry", []):
        resource = entry.get("resource")
        if resource:
            yield resource


def group_bundles_by_resource_type(bundles: Iterable[dict]) -> Dict[str, List[dict]]:
    """Group resources from a sequence of already-parsed FHIR Bundles.

    Used by both the file-on-disk path (`collect_resources_by_type`) and the
    in-memory upload path (Streamlit `file_uploader` → `json.loads`).
    """
    grouped: Dict[str, List[dict]] = {}
    for bundle in bundles:
        for resource in iter_resources(bundle):
            rtype = resource.get("resourceType", "Unknown")
            grouped.setdefault(rtype, []).append(resource)
    return grouped


def collect_resources_by_type(bundle_paths: Iterable[Path]) -> Dict[str, List[dict]]:
    """Parse every bundle file and group its resources by `resourceType`.

    Example return shape:
        {
            "Patient":            [ {..}, {..} ],
            "Encounter":          [ {..}, .. ],
            "Condition":          [ .. ],
            "Observation":        [ .. ],
            "MedicationRequest":  [ .. ],
        }
    """
    bundles: List[dict] = []
    for path in bundle_paths:
        bundles.append(load_bundle(path))
        logger.info("Parsed bundle %s", path.name)
    return group_bundles_by_resource_type(bundles)
