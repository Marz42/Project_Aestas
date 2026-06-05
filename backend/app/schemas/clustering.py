from uuid import UUID

from pydantic import BaseModel


class ClusteringTaskResult(BaseModel):
    tag_id: UUID
    cluster_count: int
    article_count: int
    created: bool
