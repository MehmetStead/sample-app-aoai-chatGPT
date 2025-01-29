import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, catchError, of, from } from 'rxjs';
import { 
  AskResponse,
  ConversationRequest, 
  UserInfo,
  FrontendSettings 
} from '../models/api.models';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private headers = new HttpHeaders().set('Content-Type', 'application/json');

  constructor(private http: HttpClient) {}

  /**
   * Sends a conversation request to the OpenAI service
   */
  async conversation(options: ConversationRequest, abortSignal: AbortSignal): Promise<AskResponse> {
    const response = await fetch('/conversation', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: options.messages
      }),
      signal: abortSignal
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No reader available');
    }

    let finalAnswer = '';
    let citations: any[] = [];
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Convert chunk to text and add to buffer
        const chunk = new TextDecoder().decode(value);
        console.log('Received chunk:', chunk); // Debug log
        buffer += chunk;

        // Process complete lines from buffer
        const lines = buffer.split('\n');
        // Keep the last potentially incomplete line in buffer
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.trim() || line === '{}') continue;

          try {
            const jsonResponse = JSON.parse(line);
            console.log('Parsed JSON:', jsonResponse); // Debug log
            if (jsonResponse.choices?.[0]?.messages) {
              for (const message of jsonResponse.choices[0].messages) {
                if (message.role === 'assistant') {
                  finalAnswer += message.content; // Changed back to concatenation
                  console.log('Current answer:', finalAnswer); // Debug log
                } else if (message.role === 'tool') {
                  try {
                    const toolContent = JSON.parse(message.content);
                    if (toolContent.citations) {
                      citations = toolContent.citations;
                    }
                  } catch (e) {
                    console.warn('Error parsing tool content:', e);
                  }
                }
              }
            }
          } catch (e) {
            console.warn('Error parsing JSON line:', e);
          }
        }
      }
    } finally {
      reader.releaseLock();
    }

    console.log('Final response:', { answer: finalAnswer, citations }); // Debug log
    return {
      answer: finalAnswer,
      citations: citations,
      generated_chart: null,
      message_id: Date.now().toString()
    };
  }

  /**
   * Gets the current user's authentication info
   */
  getUserInfo(): Observable<UserInfo[]> {
    return this.http.get<UserInfo[]>('/.auth/me').pipe(
      catchError(() => {
        console.log('No identity provider found. Access to chat will be blocked.');
        return of([]);
      })
    );
  }

  /**
   * Gets frontend configuration settings
   */
  frontendSettings(): Observable<FrontendSettings | null> {
    return this.http.get<FrontendSettings>('/frontend_settings').pipe(
      catchError(() => {
        console.error('There was an issue fetching frontend settings.');
        return of(null);
      })
    );
  }
} 