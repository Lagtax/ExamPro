import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { TeacherService } from '../services/teacher.service';

@Component({
  selector: 'app-teacher-dashboard',
  templateUrl: './teacher-dashboard.component.html'
})
export class TeacherDashboardComponent implements OnInit {
  activeTab: 'exams' | 'performance' = 'exams';
  username: string = '';
  userId: string = '';
  department: string = '';
  
  exams: any[] = [];
  showExamForm = false;
  examForm: any = {
    id: null,
    title: '',
    duration: 60,
    allowed_batch: '',
    start_time: '',
    end_time: ''
  };
  
  selectedExamId: number | null = null;
  questions: any[] = [];
  showQuestionForm = false;
  questionForm: any = {
    id: null,
    question_text: '',
    option_a: '',
    option_b: '',
    option_c: '',
    option_d: '',
    correct_option: 'A'
  };

  performanceData: any = null;
  selectedPerformanceExamId: number | null = null;

  constructor(
    private teacherService: TeacherService,
    private router: Router
  ) {}

  ngOnInit() {
    this.username = localStorage.getItem('username') || 'Teacher';
    this.userId = localStorage.getItem('user_id') || '';
    this.department = localStorage.getItem('department') || '';
    
    this.loadExams();
  }

  logout() {
    localStorage.clear();
    this.router.navigate(['/']);
  }

  switchTab(tab: 'exams' | 'performance') {
    this.activeTab = tab;
    if (tab === 'performance') {
      this.loadPerformance();
    }
  }

  loadExams() {
    this.teacherService.getExams(this.userId).subscribe({
      next: (data) => this.exams = data,
      error: (err) => console.error('Error loading exams:', err)
    });
  }

  openExamForm(exam?: any) {
    if (exam) {
      const startDate = new Date(exam.start_time);
      const endDate = new Date(exam.end_time);
      
      this.examForm = {
        id: exam.id,
        title: exam.title,
        duration: exam.duration,
        allowed_batch: exam.allowed_batch,
        start_time: this.formatDateForInput(startDate),
        end_time: this.formatDateForInput(endDate)
      };
    } else {
      const now = new Date();
      const weekLater = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
      
      this.examForm = {
        id: null,
        title: '',
        duration: 60,
        allowed_batch: '',
        start_time: this.formatDateForInput(now),
        end_time: this.formatDateForInput(weekLater)
      };
    }
    this.showExamForm = true;
  }

  formatDateForInput(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  }

  saveExam() {
    const examData = {
      ...this.examForm,
      start_time: new Date(this.examForm.start_time).toISOString(),
      end_time: new Date(this.examForm.end_time).toISOString()
    };

    if (this.examForm.id) {
      this.teacherService.updateExam(this.userId, this.examForm.id, examData).subscribe({
        next: () => {
          this.loadExams();
          this.closeExamForm();
          alert('Exam updated successfully!');
        },
        error: (err) => alert('Error: ' + (err.error.error || 'Update failed'))
      });
    } else {
      this.teacherService.createExam(this.userId, examData).subscribe({
        next: () => {
          this.loadExams();
          this.closeExamForm();
          alert('Exam created successfully!');
        },
        error: (err) => alert('Error: ' + (err.error.error || 'Creation failed'))
      });
    }
  }

  deleteExam(examId: number, title: string) {
    if (confirm(`Delete exam "${title}"? This will also delete all questions.`)) {
      this.teacherService.deleteExam(this.userId, examId).subscribe({
        next: () => {
          this.loadExams();
          alert('Exam deleted successfully!');
        },
        error: (err) => alert('Error: ' + (err.error.error || 'Deletion failed'))
      });
    }
  }

  closeExamForm() {
    this.showExamForm = false;
  }

  getExamStatus(exam: any): string {
    if (exam.is_active) return 'Active';
    if (exam.is_upcoming) return 'Upcoming';
    if (exam.is_expired) return 'Expired';
    return 'Unknown';
  }

  getExamStatusColor(exam: any): string {
    if (exam.is_active) return '#4CAF50';
    if (exam.is_upcoming) return '#2196F3';
    if (exam.is_expired) return '#9E9E9E';
    return '#000';
  }

  // ============ QUESTION MANAGEMENT ============
  selectExam(examId: number) {
    this.selectedExamId = examId;
    this.loadQuestions(examId);
  }

  loadQuestions(examId: number) {
    this.teacherService.getQuestions(examId).subscribe({
      next: (data) => this.questions = data,
      error: (err) => console.error('Error loading questions:', err)
    });
  }

  openQuestionForm(question?: any) {
    if (question) {
      this.questionForm = { ...question };
    } else {
      this.questionForm = {
        id: null,
        question_text: '',
        option_a: '',
        option_b: '',
        option_c: '',
        option_d: '',
        correct_option: 'A'
      };
    }
    this.showQuestionForm = true;
  }

  saveQuestion() {
    if (!this.selectedExamId) {
      alert('Please select an exam first!');
      return;
    }

    if (this.questionForm.id) {
      // Update
      this.teacherService.updateQuestion(this.questionForm.id, this.questionForm).subscribe({
        next: () => {
          this.loadQuestions(this.selectedExamId!);
          this.loadExams();
          this.closeQuestionForm();
          alert('Question updated successfully!');
        },
        error: (err) => alert('Error: ' + (err.error.error || 'Update failed'))
      });
    } else {
      // Create
      this.teacherService.createQuestion(this.selectedExamId, this.questionForm).subscribe({
        next: () => {
          this.loadQuestions(this.selectedExamId!);
          this.loadExams();
          this.closeQuestionForm();
          alert('Question added successfully!');
        },
        error: (err) => alert('Error: ' + (err.error.error || 'Creation failed'))
      });
    }
  }

  deleteQuestion(questionId: number) {
    if (confirm('Delete this question?')) {
      this.teacherService.deleteQuestion(questionId).subscribe({
        next: () => {
          this.loadQuestions(this.selectedExamId!);
          this.loadExams();
          alert('Question deleted successfully!');
        },
        error: (err) => alert('Error: ' + (err.error.error || 'Deletion failed'))
      });
    }
  }

  closeQuestionForm() {
    this.showQuestionForm = false;
  }

  // ============ PERFORMANCE TRACKING ============
  loadPerformance(examId?: number) {
    this.teacherService.getStudentPerformance(this.userId, examId).subscribe({
      next: (data) => {
        this.performanceData = data;
        this.selectedPerformanceExamId = examId || null;
      },
      error: (err) => console.error('Error loading performance:', err)
    });
  }

  viewExamPerformance(examId: number) {
    this.loadPerformance(examId);
  }

  viewOverallPerformance() {
    this.loadPerformance();
  }

  // ============ HELPER METHODS FOR PERFORMANCE DISPLAY ============
  
  getStatusColor(status: string): string {
    switch(status) {
      case 'submitted': return '#4CAF50';
      case 'absent': return '#f44336';
      case 'not_attempted': return '#9E9E9E';
      case 'in_progress': return '#FF9800';
      default: return '#666';
    }
  }

  getPercentageColor(percentage: number): string {
    if (percentage >= 80) return '#4CAF50';
    if (percentage >= 60) return '#2196F3';
    if (percentage >= 40) return '#FF9800';
    return '#f44336';
  }

  getTimeTaken(startTime: string, endTime: string): string {
    if (!startTime || !endTime) return '-';
    
    const start = new Date(startTime);
    const end = new Date(endTime);
    const diff = end.getTime() - start.getTime();
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 60) {
      return `${minutes} min`;
    } else {
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;
      return `${hours}h ${mins}m`;
    }
  }

  toggleStudentExams(student: any) {
    student.showExams = !student.showExams;
  }
}