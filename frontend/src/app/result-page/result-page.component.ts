import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ExamService } from '../services/exam.service';

@Component({
  selector: 'app-result-page',
  templateUrl: './result-page.component.html'
})
export class ResultPageComponent implements OnInit {
  examId!: string;
  userId!: string;

  score!: number;
  totalQuestions!: number;
  submitted!: boolean;
  percentage!: number;
  loading = true;
  error = '';

  constructor(
    private route: ActivatedRoute, 
    private examService: ExamService, 
    private router: Router
  ) {}

  ngOnInit() {
    this.examId = this.route.snapshot.paramMap.get('id')!;
    this.userId = localStorage.getItem('user_id')!;

    this.examService.getResult(this.examId).subscribe({
      next: (res: any) => {
        this.score = res.score;
        this.totalQuestions = res.total_questions;
        this.submitted = res.submitted;
        this.percentage = (this.score / this.totalQuestions) * 100;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load results';
        this.loading = false;
        console.error(err);
      }
    });
  }

  goHome() {
    this.router.navigate(['/student']);
  }
}