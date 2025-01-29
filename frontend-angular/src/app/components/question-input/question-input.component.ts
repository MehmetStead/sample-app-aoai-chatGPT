import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormControl, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from '../../material.module';

@Component({
  selector: 'app-question-input',
  templateUrl: './question-input.component.html',
  styleUrls: ['./question-input.component.css'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MaterialModule
  ]
})
export class QuestionInputComponent {
  @Input() disabled = false;
  @Input() placeholder = 'Type a message...';
  @Output() sendMessage = new EventEmitter<string>();

  messageControl = new FormControl('');
  base64Image: string | null = null;

  onSend(): void {
    if (this.disabled || !this.messageControl.value?.trim()) {
      return;
    }
    this.sendMessage.emit(this.messageControl.value);
    this.messageControl.reset();
    this.base64Image = null;
  }

  async onImageUpload(event: Event): Promise<void> {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) {
      try {
        this.base64Image = await this.resizeImage(file, 800, 800);
      } catch (error) {
        console.error('Error resizing image:', error);
      }
    }
  }

  private resizeImage(file: Blob, maxWidth: number, maxHeight: number): Promise<string> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      const reader = new FileReader();

      reader.onload = (e) => {
        img.src = e.target?.result as string;
        img.onload = () => {
          const canvas = document.createElement('canvas');
          let { width, height } = img;

          if (width > maxWidth || height > maxHeight) {
            if (width > height) {
              height = (maxWidth / width) * height;
              width = maxWidth;
            } else {
              width = (maxHeight / height) * width;
              height = maxHeight;
            }
          }

          canvas.width = width;
          canvas.height = height;
          const ctx = canvas.getContext('2d');
          ctx?.drawImage(img, 0, 0, width, height);
          resolve(canvas.toDataURL('image/jpeg', 0.8));
        };
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  handleEnterKey(event: any): void {
    const kbEvent = event as KeyboardEvent;
    if (!kbEvent.shiftKey) {
      kbEvent.preventDefault();
      this.onSend();
    }
  }
} 