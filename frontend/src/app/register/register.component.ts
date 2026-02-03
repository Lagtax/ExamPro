import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html'
})
export class RegisterComponent {
  username = '';
  password = '';
  email = '';
  department = '';
  batch = '';
  role = 'student';

  constructor(private http: HttpClient, private router: Router) {}

  register() {
    if (!this.username || !this.password) {
      alert('Username and password are required');
      return;
    }

    if (this.role === 'student' && (!this.department || !this.batch)) {
      alert('Students must provide department and batch');
      return;
    }
    
    if (this.role === 'teacher' && !this.department) {
      alert('Teachers must provide department');
      return;
    }

    const payload: any = {
      username: this.username,
      password: this.password,
      email: this.email,
      role: this.role
    };

    if (this.role === 'student' || this.role === 'teacher') {
      payload.department = this.department;
    }
    
    if (this.role === 'student') {
      payload.batch = this.batch;
    }

    this.http.post('http://127.0.0.1:8000/api/auth/register/', payload).subscribe({
      next: (res: any) => {
        console.log('Registered:', res);
        localStorage.setItem('user_id', res.user_id);
        localStorage.setItem('role', res.role);
        localStorage.setItem('username', this.username);
        
        if (res.role === 'admin') {
          this.router.navigate(['/admin']);
        } else if (res.role === 'teacher') {
          this.router.navigate(['/teacher']);
        } else {
          this.router.navigate(['/student']);
        }
      },
      error: (err) => {
        console.error(err);
        alert(err.error.error || 'Registration failed');
      }
    });
  }
}