import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { StudentDashboardComponent } from './student-dashboard/student-dashboard.component';
import { AdminDashboardComponent } from './admin-dashboard/admin-dashboard.component';
import { RegisterComponent } from './register/register.component';
import { ExamPageComponent } from './exam-page/exam-page.component';
import { ResultPageComponent } from './result-page/result-page.component';
import { TeacherDashboardComponent } from './teacher-dashboard/teacher-dashboard.component';

const routes: Routes = [
  {path:'', component: LoginComponent},
  {path:'register', component: RegisterComponent},
  {path:'student', component: StudentDashboardComponent},
  {path:'admin', component: AdminDashboardComponent},
  {path: 'exam/:id', component: ExamPageComponent},
  {path: 'result/:id', component: ResultPageComponent},
  {path: 'teacher', component: TeacherDashboardComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
