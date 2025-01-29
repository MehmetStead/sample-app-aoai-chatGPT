import { Component, Input, Output, EventEmitter, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { AskResponse, Citation } from '../../models/api.models';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { MaterialModule } from '../../material.module';

@Component({
  selector: 'app-answer',
  templateUrl: './answer.component.html',
  styleUrls: ['./answer.component.css'],
  standalone: true,
  imports: [
    CommonModule,
    MaterialModule
  ]
})
export class AnswerComponent implements OnChanges {
  @Input() answer!: AskResponse;
  @Output() citationClicked = new EventEmitter<Citation>();

  isReferencesOpen = false;
  parsedAnswer: SafeHtml = '';

  constructor(private sanitizer: DomSanitizer) {
    marked.setOptions({
      gfm: true,
      breaks: true
    });
  }

  async ngOnChanges(changes: SimpleChanges) {
    if (changes['answer'] && typeof this.answer?.answer === 'string') {
      console.log('Received new answer:', this.answer.answer); // Debug log
      try {
        const parsedMarkdown = await marked(this.answer.answer);
        console.log('Parsed markdown:', parsedMarkdown); // Debug log
        const cleanHtml = DOMPurify.sanitize(parsedMarkdown);
        this.parsedAnswer = this.sanitizer.bypassSecurityTrustHtml(cleanHtml);
      } catch (error) {
        console.error('Error in answer processing:', error);
        // Fallback to plain text
        this.parsedAnswer = this.sanitizer.bypassSecurityTrustHtml(
          `<p>${this.answer.answer}</p>`
        );
      }
    }
  }

  toggleReferences(): void {
    this.isReferencesOpen = !this.isReferencesOpen;
  }

  onCitationClick(citation: Citation): void {
    this.citationClicked.emit(citation);
  }
} 