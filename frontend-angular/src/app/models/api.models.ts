export type AskResponse = {
  answer: string | []
  citations: Citation[]
  generated_chart: string | null
  error?: string
  message_id?: string
}

export type Citation = {
  content: string
  id: string
  title: string | null
  filepath: string | null
  url: string | null
}

export type ChatMessage = {
  id: string
  role: string
  content: string | [{ type: string; text: string }, { type: string; image_url: { url: string } }]
  date: string
}

export type ConversationRequest = {
  messages: ChatMessage[]
}

export type UserInfo = {
  access_token: string
  expires_on: string
  id_token: string
  provider_name: string
  user_claims: any[]
  user_id: string
}

export type FrontendSettings = {
  auth_enabled?: string | null
  ui?: {
    title: string
    chat_title: string
    chat_description: string
    logo?: string
    chat_logo?: string
    show_share_button?: boolean
  }
  sanitize_answer?: boolean
} 