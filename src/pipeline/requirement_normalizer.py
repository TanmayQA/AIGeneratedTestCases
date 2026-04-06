from bs4 import BeautifulSoup
from src.models import NormalizedRequirement


def html_to_text(value: str) -> str:
    if not value:
        return ""

    soup = BeautifulSoup(value, "lxml")
    return soup.get_text("\n", strip=True)


def normalize_azure_work_item(raw: dict, source_url: str) -> NormalizedRequirement:
    fields = raw.get("fields", {})

    work_item_id = raw.get("id")
    title = fields.get("System.Title", "")

    description = html_to_text(fields.get("System.Description", ""))
    acceptance_criteria = html_to_text(
        fields.get("Microsoft.VSTS.Common.AcceptanceCriteria", "")
    )
    repro_steps = html_to_text(fields.get("Microsoft.VSTS.TCM.ReproSteps", ""))

    tags_raw = fields.get("System.Tags", "")
    tags = [tag.strip() for tag in tags_raw.split(";") if tag.strip()]

    if not acceptance_criteria:
        acceptance_criteria = description

    return NormalizedRequirement(
        requirement_id=str(work_item_id),
        title=title,
        description=description,
        acceptance_criteria=acceptance_criteria,
        repro_steps=repro_steps,
        tags=tags,
        source_url=source_url,
        source_type="azure"
    )