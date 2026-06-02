export interface Tag {
  id: string;
  slug: string;
  name: string;
  prompt_template_id: string | null;
  created_at: string;
}

export interface PromptTemplate {
  id: string;
  name: string;
  purpose: string;
  description: string | null;
  system_prompt: string;
  user_prompt_template: string;
  created_at: string;
  updated_at: string;
}

export interface FeedSource {
  id: string;
  tag_id: string;
  name: string;
  feed_url: string;
  is_active: boolean;
  fetch_interval_minutes: number;
  last_fetched_at: string | null;
}

export interface Article {
  id: string;
  tag_id: string;
  title: string;
  url: string;
  status: string;
  fetched_at: string;
  insight?: {
    short_news_md: string;
  };
}

export interface TagBrief {
  id: string;
  tag_id: string;
  tag_name: string | null;
  title: string;
  window_start: string;
  window_end: string;
  status: string;
  item_count: number;
  content_md?: string;
}
