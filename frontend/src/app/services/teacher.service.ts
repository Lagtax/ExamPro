import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class TeacherService {
  baseUrl = 'http://127.0.0.1:8000/api/teacher';

  constructor(private http: HttpClient) {}

  getExams(userId: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/exams/`, {
      params: { user_id: userId }
    });
  }

  createExam(userId: string, examData: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/exams/create/`, {
      ...examData,
      user_id: userId
    });
  }

  updateExam(userId: string, examId: number, examData: any): Observable<any> {
    return this.http.put(`${this.baseUrl}/exams/${examId}/update/`, {
      ...examData,
      user_id: userId
    });
  }

  deleteExam(userId: string, examId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/exams/${examId}/delete/`, {
      params: { user_id: userId }
    });
  }

  getQuestions(examId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/exams/${examId}/questions/`);
  }

  createQuestion(examId: number, questionData: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/exams/${examId}/questions/create/`, questionData);
  }

  updateQuestion(questionId: number, questionData: any): Observable<any> {
    return this.http.put(`${this.baseUrl}/questions/${questionId}/update/`, questionData);
  }

  deleteQuestion(questionId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/questions/${questionId}/delete/`);
  }

  getStudentPerformance(userId: string, examId?: number): Observable<any> {
    const params: any = { user_id: userId };
    if (examId) {
      params.exam_id = examId;
    }
    return this.http.get(`${this.baseUrl}/performance/`, { params });
  }

  getStudentDetail(userId: string, studentId: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/students/${studentId}/`, {
      params: { user_id: userId }
    });
  }
}