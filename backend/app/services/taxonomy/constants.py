"""Coarse taxonomy slugs for content_tags (15–30 categories)."""

TAXONOMY_ENTRIES: list[tuple[str, str]] = [
    ("politics", "政治"),
    ("economy", "经济财经"),
    ("technology", "科技"),
    ("military_conflict", "军事与冲突"),
    ("disaster", "灾害事故"),
    ("sports", "体育"),
    ("entertainment", "文娱"),
    ("crime_law", "法治犯罪"),
    ("health_science", "健康科学"),
    ("society", "社会民生"),
    ("energy", "能源"),
    ("automotive", "汽车交通"),
    ("real_estate", "房地产"),
    ("trade", "贸易"),
    ("diplomacy", "外交"),
    ("environment", "环境气候"),
    ("education", "教育"),
    ("labor", "劳动就业"),
    ("cyber", "网络信息安全"),
    ("other", "其他"),
]

TAXONOMY_SLUGS: frozenset[str] = frozenset(slug for slug, _ in TAXONOMY_ENTRIES)

TAG_TAXONOMY_MAP: dict[str, list[str]] = {
    "military": ["military_conflict", "politics", "diplomacy"],
    "tech": ["technology", "cyber", "economy"],
    "auto": ["automotive", "technology", "economy"],
}


def format_taxonomy_for_prompt() -> str:
    return ", ".join(f"{slug}（{name}）" for slug, name in TAXONOMY_ENTRIES)
