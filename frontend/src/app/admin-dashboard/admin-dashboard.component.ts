import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AdminService } from '../services/admin.service';

@Component({
  selector: 'app-admin-dashboard',
  templateUrl: './admin-dashboard.component.html'
})
export class AdminDashboardComponent implements OnInit {
  activeTab: 'users' | 'exams' = 'users';
  username: string = '';
  
  users: any[] = [];
  showUserForm = false;
  userForm: any = {
    id: null,
    username: '',
    email: '',
    password: '',
    role: 'student',
    department: '',
    batch: ''
  };
  
  exams: any[] = [];
  showExamForm = false;
  examForm: any = {
    id: null,
    title: '',
    duration: 60,
    department: '',
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

  constructor(
    private adminService: AdminService,
    private router: Router
  ) {}

  ngOnInit() {
    this.username = localStorage.getItem('username') || 'Admin';
    this.loadUsers();
    this.loadExams();
  }

  logout() {
    localStorage.clear();
    this.router.navigate(['/']);
  }

  switchTab(tab: 'users' | 'exams') {
    this.activeTab = tab;
    this.resetForms();
  }

  loadUsers() {
    this.adminService.getUsers().subscribe({
      next: (data) => this.users = data,
      error: (err) => console.error('Error loading users:', err)
    });
  }

  openUserForm(user?: any) {
    if (user) {
      this.userForm = { ...user };
    } else {
      this.userForm = {
        id: null,
        username: '',
        email: '',
        password: '',
        role: 'student',
        department: '',
        batch: ''
      };
    }
    this.showUserForm = true;
  }

  saveUser() {
    if (this.userForm.id) {
      this.adminService.updateUser(this.userForm.id, this.userForm).subscribe({
        next: () => {
          this.loadUsers();
          this.closeUserForm();
          alert('User updated successfully!');
        },
        error: (err) => alert('Error: ' + (err.error.error || 'Update failed'))
      });
    } else {
      this.adminService.createUser(this.userForm).subscribe({
        next: () => {
          this.loadUsers();
          this.closeUserForm();
          alert('User created successfully!');
        },
        error: (err) => alert('Error: ' + (err.error.error || 'Creation failed'))
      });
    }
  }

  deleteUser(userId: number, username: string) {
    if (confirm(`Are you sure you want to delete user "${username}"?`)) {
      this.adminService.deleteUser(userId).subscribe({
        next: () => {
          this.loadUsers();
          alert('User deleted successfully!');
        },
        error: (err) => alert('Error: ' + (err.error.error || 'Deletion failed'))
      });
    }
  }

  closeUserForm() {
    this.showUserForm = false;
  }

  loadExams() {
    console.log('[Admin] Loading exams...');
    this.adminService.getExams().subscribe({
      next: (data) => {
        console.log('[Admin] Exams loaded:', data);
        this.exams = data;
      },
      error: (err) => {
        console.error('[Admin] Error loading exams:', err);
      }
    });
  }

  openExamForm(exam?: any) {
    console.log('[Admin] Opening exam form:', exam);
    
    if (exam) {
      let startTime = '';
      let endTime = '';
      
      if (exam.start_time) {
        startTime = this.formatDateForInput(new Date(exam.start_time));
      }
      
      if (exam.end_time) {
        endTime = this.formatDateForInput(new Date(exam.end_time));
      }
      
      this.examForm = {
        id: exam.id,
        title: exam.title,
        duration: exam.duration,
        department: exam.department,
        allowed_batch: exam.allowed_batch || '',
        start_time: startTime,
        end_time: endTime
      };
    } else {
      const now = new Date();
      const weekLater = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
      
      this.examForm = {
        id: null,
        title: '',
        duration: 60,
        department: '',
        allowed_batch: '',
        start_time: this.formatDateForInput(now),
        end_time: this.formatDateForInput(weekLater)
      };
    }
    
    console.log('[Admin] Exam form data:', this.examForm);
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
    console.log('[Admin] saveExam called with form:', this.examForm);
    
    if (!this.examForm.title || !this.examForm.title.trim()) {
      alert('Please enter exam title');
      return;
    }
    
    if (!this.examForm.department || !this.examForm.department.trim()) {
      alert('Please enter department');
      return;
    }
    
    if (!this.examForm.duration || this.examForm.duration < 1) {
      alert('Please enter valid duration');
      return;
    }
    
    if (!this.examForm.start_time || !this.examForm.end_time) {
      alert('Please set start and end times');
      return;
    }
    
    const examData: any = {
      title: this.examForm.title.trim(),
      duration: parseInt(this.examForm.duration.toString()),
      department: this.examForm.department.trim(),
      allowed_batch: this.examForm.allowed_batch ? this.examForm.allowed_batch.trim() : ''
    };
    
    try {
      examData.start_time = new Date(this.examForm.start_time).toISOString();
      examData.end_time = new Date(this.examForm.end_time).toISOString();
    } catch (error) {
      console.error('[Admin] Date conversion error:', error);
      alert('Invalid date format');
      return;
    }
    
    console.log('[Admin] Sending exam data:', examData);

    if (this.examForm.id) {
      console.log('[Admin] Updating exam ID:', this.examForm.id);
      this.adminService.updateExam(this.examForm.id, examData).subscribe({
        next: (response) => {
          console.log('[Admin] Update response:', response);
          this.loadExams();
          this.closeExamForm();
          alert('Exam updated successfully!');
        },
        error: (err) => {
          console.error('[Admin] Update error:', err);
          alert('Error: ' + (err.error?.error || err.message || 'Update failed'));
        }
      });
    } else {
      console.log('[Admin] Creating new exam');
      this.adminService.createExam(examData).subscribe({
        next: (response) => {
          console.log('[Admin] Create response:', response);
          this.loadExams();
          this.closeExamForm();
          alert('Exam created successfully!');
        },
        error: (err) => {
          console.error('[Admin] Create error:', err);
          alert('Error: ' + (err.error?.error || err.message || 'Creation failed'));
        }
      });
    }
  }

  deleteExam(examId: number, title: string) {
    console.log('[Admin] deleteExam called:', examId, title);
    
    if (confirm(`Are you sure you want to delete exam "${title}"? This will also delete all associated questions.`)) {
      this.adminService.deleteExam(examId).subscribe({
        next: (response) => {
          console.log('[Admin] Delete response:', response);
          this.loadExams();
          if (this.selectedExamId === examId) {
            this.selectedExamId = null;
            this.questions = [];
          }
          alert('Exam deleted successfully!');
        },
        error: (err) => {
          console.error('[Admin] Delete error:', err);
          alert('Error: ' + (err.error?.error || err.message || 'Deletion failed'));
        }
      });
    }
  }

  closeExamForm() {
    this.showExamForm = false;
  }

  selectExam(examId: number) {
    this.selectedExamId = examId;
    this.loadQuestions(examId);
  }

  loadQuestions(examId: number) {
    this.adminService.getQuestions(examId).subscribe({
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
      this.adminService.updateQuestion(this.questionForm.id, this.questionForm).subscribe({
        next: () => {
          this.loadQuestions(this.selectedExamId!);
          this.loadExams();
          this.closeQuestionForm();
          alert('Question updated successfully!');
        },
        error: (err) => alert('Error: ' + (err.error.error || 'Update failed'))
      });
    } else {
      this.adminService.createQuestion(this.selectedExamId, this.questionForm).subscribe({
        next: () => {
          this.loadQuestions(this.selectedExamId!);
          this.loadExams();
          this.closeQuestionForm();
          alert('Question created successfully!');
        },
        error: (err) => alert('Error: ' + (err.error.error || 'Creation failed'))
      });
    }
  }

  deleteQuestion(questionId: number) {
    if (confirm('Are you sure you want to delete this question?')) {
      this.adminService.deleteQuestion(questionId).subscribe({
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

  resetForms() {
    this.showUserForm = false;
    this.showExamForm = false;
    this.showQuestionForm = false;
    this.selectedExamId = null;
    this.questions = [];
  }
}