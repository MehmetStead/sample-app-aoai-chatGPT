import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { LayoutComponent } from './pages/layout/layout.component';

@Component({
  selector: 'app-root',
  template: `
    <app-layout>
      <router-outlet></router-outlet>
    </app-layout>
  `,
  standalone: true,
  imports: [RouterModule, LayoutComponent]
})
export class AppComponent {
  title = 'chat-app';
} 