import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html'
})
export class LoginComponent {
  username = '';
  password = '';
  errorMsg = '';

  constructor(private router: Router, private http: HttpClient) {}

  login() {
    if (!this.username || !this.password) {
      this.errorMsg = 'Enter username and password';
      return;
    }

    this.http.post<any>('http://127.0.0.1:8000/api/auth/login/', {
      username: this.username,
      password: this.password
    }).subscribe({
      next: (res) => {
        localStorage.setItem('user_id', res.user_id);
        localStorage.setItem('role', res.role);
        localStorage.setItem('username', this.username);
        localStorage.setItem('department', res.department || '');
        
        // Route based on role from backend
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
        this.errorMsg = err.error?.error || 'Login failed';
      }
    });
  }
}