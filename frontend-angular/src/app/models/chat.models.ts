export interface ChatMessage {
  id: string;
  role: string;
  content: string | MessageContent[];
  end_turn?: boolean;
  date: string;
  feedback?: Feedback;
  context?: string;
  citations?: Citation[];
}

export interface MessageContent {
  type: string;
  text?: string;
  image_url?: {
    url: string;
  };
}

export interface Citation {
  content: string;
  id: string;
  title: string | null;
  filepath: string | null;
  url: string | null;
  metadata: string | null;
  chunk_id: string | null;
  reindex_id: string | null;
  part_index?: number;
}

export enum Feedback {
  Neutral = 'neutral',
  Positive = 'positive',
  Negative = 'negative'
}

export interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  date: string;
} 