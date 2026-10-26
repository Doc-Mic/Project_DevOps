import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { App } from './app';
import { PredictionService } from './prediction.service';

describe('App', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [{
        provide: PredictionService,
        useValue: {
          health: () => of({ status: 'ok', model_loaded: true, features: 19, task: 'multiclass_classification', model_version: '1.0.0' }),
          predict: () => of({ prediction: 'Example group', task: 'multiclass_classification', probabilities: [], disclaimer: 'Research only.' }),
        },
      }],
    }).compileComponents();
  });

  it('creates the application', () => {
    const fixture = TestBed.createComponent(App);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('renders the research app heading', async () => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    await fixture.whenStable();
    expect((fixture.nativeElement as HTMLElement).querySelector('h1')?.textContent).toContain('Explore historical incident patterns');
  });
});