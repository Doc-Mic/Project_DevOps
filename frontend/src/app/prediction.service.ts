import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ClassProbability {
  group: string;
  probability: number;
}

export interface PredictionResponse {
  prediction: string;
  task: string;
  probabilities: ClassProbability[];
  disclaimer: string;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  features: number;
  task: string;
  model_version: string | null;
}

@Injectable({ providedIn: 'root' })
export class PredictionService {
  private readonly http = inject(HttpClient);

  health(): Observable<HealthResponse> {
    return this.http.get<HealthResponse>('/api/health');
  }

  predict(payload: Record<string, number>): Observable<PredictionResponse> {
    return this.http.post<PredictionResponse>('/api/predict', payload);
  }
}