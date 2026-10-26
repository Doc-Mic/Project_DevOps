import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { FEATURES, Feature } from './feature-schema';
import { HealthResponse, PredictionResponse, PredictionService } from './prediction.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  readonly fields = FEATURES;
  readonly staticSite = !['localhost', '127.0.0.1'].includes(window.location.hostname);
  readonly api = inject(PredictionService);
  readonly loading = signal(false);
  readonly error = signal('');
  readonly result = signal<PredictionResponse | null>(null);
  readonly health = signal<HealthResponse | null>(null);
  readonly apiMessage = signal(this.staticSite ? 'Static demo' : 'Checking local API…');
  values: Record<string, number | null> = {};

  constructor() {
    for (const field of this.fields) this.values[field.name] = null;
    if (!this.staticSite) {
      this.api.health().subscribe({
        next: value => {
          this.health.set(value);
          this.apiMessage.set(value.model_loaded ? 'Local model ready' : 'Model not trained yet');
        },
        error: () => { this.apiMessage.set('Local API offline'); },
      });
    }
  }

  trackField(_index: number, field: Feature): string { return field.name; }

  submit(): void {
    this.error.set('');
    this.result.set(null);
    if (this.staticSite) {
      this.error.set('This GitHub Pages site is static. Run Flask and Angular on your computer to make predictions.');
      return;
    }
    const payload: Record<string, number> = {};
    for (const field of this.fields) {
      const value = this.values[field.name];
      if (value === null || value === undefined) {
        this.error.set(`Choose or enter a value for ${field.label}.`);
        return;
      }
      const numberValue = Number(value);
      if (!Number.isFinite(numberValue)) {
        this.error.set(`Enter a valid number for ${field.label}.`);
        return;
      }
      if (field.kind === 'category' && !(field.options ?? []).some(option => option.value === numberValue)) {
        this.error.set(`Choose a listed GTD code for ${field.label}.`);
        return;
      }
      if ((field.min !== undefined && numberValue < field.min) || (field.max !== undefined && numberValue > field.max)) {
        this.error.set(`${field.label} is outside the accepted range.`);
        return;
      }
      payload[field.name] = numberValue;
    }
    this.loading.set(true);
    this.api.predict(payload).subscribe({
      next: response => { this.result.set(response); this.loading.set(false); },
      error: err => {
        this.error.set(`API error ${err.status || ''}: ${err.error?.detail || err.error?.error || err.message || 'Check Flask.'}`);
        this.loading.set(false);
      },
    });
  }
}