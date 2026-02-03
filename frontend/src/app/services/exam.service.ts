import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({ providedIn: 'root' })
export class ExamService {
  baseUrl = 'http://127.0.0.1:8000/api/exams';

  constructor(private http: HttpClient) {}

  startExam(examId: string) {
    const userId = localStorage.getItem('user_id')!;
    return this.http.post(`${this.baseUrl}/${examId}/start/`, { user_id: userId });
  }

  getExams() {
    const userId = localStorage.getItem('user_id')!;
    return this.http.get<any[]>(`${this.baseUrl}?user_id=${userId}`);
  }

  getQuestions(examId: string, userId: string) {
    return this.http.get<any[]>(`${this.baseUrl}/${examId}/questions/?user_id=${userId}`);
  }

  submitExam(examId: string, payload: any) {
    return this.http.post(`${this.baseUrl}/${examId}/submit/`, payload);
  }

  getResult(examId: string) {
    const userId = localStorage.getItem('user_id')!;
    return this.http.get<any>(`${this.baseUrl}/${examId}/result/?user_id=${userId}`);
  }
}
