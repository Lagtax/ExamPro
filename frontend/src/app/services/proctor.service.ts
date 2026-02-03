import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ProctorService {
  baseUrl = 'http://127.0.0.1:8000/api/proctor';

  constructor(private http: HttpClient) {}

  logEvent(userId: string, examId: string, event: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/log/`, {
      user_id: userId,
      exam_id: examId,
      event: event
    });
  }

  getViolations(userId: string, examId: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/violations/`, {
      params: { user_id: userId, exam_id: examId }
    });
  }
}