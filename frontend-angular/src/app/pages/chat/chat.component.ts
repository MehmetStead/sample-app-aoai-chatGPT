import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { ApiService } from '../../services/api.service';
import { AskResponse, Citation } from '../../models/api.models';
import { QuestionInputComponent } from '../../components/question-input/question-input.component';
import { AnswerComponent } from '../../components/answer/answer.component';
import { MaterialModule } from '../../material.module';

export interface ChatMessage extends AskResponse {
  id: string;
  role: string;
  content: string;
  date: string;
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css'],
  standalone: true,
  imports: [
    CommonModule,
    HttpClientModule,
    MaterialModule,
    QuestionInputComponent,
    AnswerComponent
  ],
  providers: [ApiService]
})
export class ChatComponent {
  isLoading = false;
  messages: ChatMessage[] = [];
  isCitationPanelOpen = false;
  activeCitation?: Citation;

  constructor(private apiService: ApiService) {}

  onSendMessage(message: string) {
    if (!message.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      answer: message,
      citations: [],
      generated_chart: null,
      date: new Date().toISOString()
    };
    this.messages.push(userMessage);

    this.isLoading = true;
    const abortController = new AbortController();

    // Call API
    this.apiService.conversation({
      messages: this.messages
    }, abortController.signal)
      .then(response => {
        console.log('API Response:', response);
        const assistantMessage: ChatMessage = {
          id: Date.now().toString(),
          role: 'assistant',
          content: typeof response.answer === 'string' ? response.answer : '',
          answer: response.answer,
          citations: response.citations,
          generated_chart: response.generated_chart,
          date: new Date().toISOString()
        };
        this.messages.push(assistantMessage);
      })
      .catch(error => {
        console.error('API Error:', error);
      })
      .finally(() => {
        this.isLoading = false;
      });
  }

  onCitationClick(citation: Citation) {
    this.activeCitation = citation;
    this.isCitationPanelOpen = true;
  }
} 