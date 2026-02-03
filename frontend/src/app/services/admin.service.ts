import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AdminService {
  baseUrl = 'http://127.0.0.1:8000/api/admin';

  constructor(private http: HttpClient) {}

  getUsers(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/users/`);
  }

  createUser(userData: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/users/create/`, userData);
  }

  updateUser(userId: number, userData: any): Observable<any> {
    return this.http.put(`${this.baseUrl}/users/${userId}/update/`, userData);
  }

  deleteUser(userId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/users/${userId}/delete/`);
  }

  getExams(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/exams/`);
  }

  createExam(examData: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/exams/create/`, examData);
  }

  updateExam(examId: number, examData: any): Observable<any> {
    return this.http.put(`${this.baseUrl}/exams/${examId}/update/`, examData);
  }

  deleteExam(examId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/exams/${examId}/delete/`);
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
}