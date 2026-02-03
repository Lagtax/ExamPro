import { TestBed } from '@angular/core/testing';

import { ProctorService } from './proctor.service';

describe('ProctorService', () => {
  let service: ProctorService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ProctorService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
