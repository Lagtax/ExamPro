import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ExamService } from '../services/exam.service';

@Component({
  selector: 'app-student-dashboard',
  templateUrl: './student-dashboard.component.html'
})
export class StudentDashboardComponent implements OnInit {
  exams: any[] = [];
  username: string = '';

  constructor(
    private examService: ExamService,
    private router: Router
  ) {}

  ngOnInit() {
    this.username = localStorage.getItem('username') || 'Student';
    
    this.examService.getExams().subscribe({
      next: (data) => {
        this.exams = data;
      },
      error: (err) => {
        console.error('Error loading exams:', err);
      }
    });
  }

  startExam(examId: number) {
    this.router.navigate(['/exam', examId]);
  }

  logout() {
    localStorage.removeItem('user_id');
    localStorage.removeItem('role');
    localStorage.removeItem('username');
    
    this.router.navigate(['/']);
  }
}