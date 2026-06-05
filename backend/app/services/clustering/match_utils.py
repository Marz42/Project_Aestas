from app.models.article import Article
from app.models.story_cluster import StoryCluster
from app.models.tag import Tag
from app.services.clustering.text_utils import article_content_tags


def cluster_matches_tag(cluster: StoryCluster, tag: Tag) -> bool:
    if cluster.tag_id == tag.id:
        return True
    taxonomy = set(tag.taxonomy_slugs or [])
    if not taxonomy:
        return False
    for member in cluster.members:
        article = member.article
        if article is None:
            continue
        if article.tag_id == tag.id:
            return True
        if taxonomy.intersection(article_content_tags(article)):
            return True
    return False


def article_matches_tag(article: Article, tag: Tag) -> bool:
    if article.tag_id == tag.id:
        return True
    taxonomy = set(tag.taxonomy_slugs or [])
    return bool(taxonomy.intersection(article_content_tags(article)))
