import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { ChatMessage, Conversation } from '../models/chat.models';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private messages = new BehaviorSubject<ChatMessage[]>([]);
  private currentChat = new BehaviorSubject<Conversation | null>(null);

  constructor(private http: HttpClient) {}

  getMessages(): Observable<ChatMessage[]> {
    return this.messages.asObservable();
  }

  getCurrentChat(): Observable<Conversation | null> {
    return this.currentChat.asObservable();
  }

  setCurrentChat(chat: Conversation): void {
    this.currentChat.next(chat);
    this.messages.next(chat.messages);
  }

  sendMessage(message: string): Observable<any> {
    return this.http.post('/conversation', {
      messages: [{
        role: 'user',
        content: message
      }]
    });
  }

  getChatHistory(): Observable<Conversation[]> {
    return this.http.get<Conversation[]>('/history/list');
  }

  updateMessages(messages: ChatMessage[]): void {
    this.messages.next(messages);
  }
} 