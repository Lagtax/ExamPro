import { Component, OnInit, OnDestroy, HostListener } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ExamService } from '../services/exam.service';
import { ProctorService } from '../services/proctor.service';

@Component({
  selector: 'app-exam-page',
  templateUrl: './exam-page.component.html'
})
export class ExamPageComponent implements OnInit, OnDestroy {
  examId!: string;
  userId!: string;

  questions: any[] = [];
  answers: any = {};

  remainingTime = 0;
  timer: any;

  // Proctoring
  violations = 0;
  maxViolations = 3;
  showWarning = false;
  warningMessage = '';
  
  // Webcam
  videoStream: MediaStream | null = null;
  isWebcamActive = false;

  constructor(
    private route: ActivatedRoute,
    private examService: ExamService,
    private proctorService: ProctorService,
    private router: Router
  ) {}

  ngOnInit() {
    this.examId = this.route.snapshot.paramMap.get('id')!;
    this.userId = localStorage.getItem('user_id')!;

    this.examService.startExam(this.examId).subscribe((res: any) => {
      this.startTimer(res.duration);
    });

    this.examService.getQuestions(this.examId, this.userId).subscribe(data => {
      this.questions = data;
    });

    this.proctorService.getViolations(this.userId, this.examId).subscribe((res: any) => {
      this.violations = res.violations;
      this.maxViolations = res.max_violations;
    });

    this.startWebcam();

    this.setupTabSwitchDetection();
  }

  startTimer(minutes: number) {
    this.remainingTime = minutes * 60;

    this.timer = setInterval(() => {
      this.remainingTime--;

      if (this.remainingTime <= 0) {
        clearInterval(this.timer);
        this.submitExam(true);
      }
    }, 1000);
  }

  formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  async startWebcam() {
    try {
      this.videoStream = await navigator.mediaDevices.getUserMedia({ 
        video: true, 
        audio: false 
      });
      
      const videoElement = document.getElementById('webcam') as HTMLVideoElement;
      if (videoElement) {
        videoElement.srcObject = this.videoStream;
        this.isWebcamActive = true;
      }
    } catch (error) {
      console.error('Webcam access denied:', error);
      this.logViolation('webcam_denied');
      alert('Webcam access is required for this exam. Please enable your webcam.');
    }
  }

  stopWebcam() {
    if (this.videoStream) {
      this.videoStream.getTracks().forEach(track => track.stop());
      this.videoStream = null;
      this.isWebcamActive = false;
    }
  }

  setupTabSwitchDetection() {
    document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
  }

  handleVisibilityChange() {
    if (document.hidden) {
      this.logViolation('tab_switch');
    }
  }

  @HostListener('window:blur', ['$event'])
  onWindowBlur(event: any) {
    this.logViolation('window_blur');
  }

  @HostListener('contextmenu', ['$event'])
  onRightClick(event: any) {
    event.preventDefault();
    this.showWarningMessage('Right-click is disabled during the exam.');
  }

  @HostListener('copy', ['$event'])
  @HostListener('paste', ['$event'])
  @HostListener('cut', ['$event'])
  blockCopyPaste(event: any) {
    event.preventDefault();
    this.showWarningMessage('Copy/Paste is disabled during the exam.');
  }

  logViolation(event: string) {
    this.proctorService.logEvent(this.userId, this.examId, event).subscribe({
      next: (res: any) => {
        this.violations = res.violations;
        
        if (res.auto_submitted) {
          alert('Maximum violations exceeded. Your exam has been automatically submitted.');
          this.stopWebcam();
          this.router.navigate(['/result', this.examId]);
        } else {
          const remaining = res.remaining;
          this.showWarningMessage(
            `Warning! Violation detected: ${event}. ${remaining} warning(s) remaining before auto-submission.`
          );
        }
      },
      error: (err) => {
        console.error('Error logging violation:', err);
      }
    });
  }

  showWarningMessage(message: string) {
    this.warningMessage = message;
    this.showWarning = true;
    
    setTimeout(() => {
      this.showWarning = false;
    }, 5000);
  }

  submitExam(auto = false) {
    clearInterval(this.timer);

    const payload = {
      user_id: this.userId,
      answers: Object.keys(this.answers).map(qid => ({
        question_id: qid,
        selected_option: this.answers[qid]
      }))
    };

    this.examService.submitExam(this.examId, payload).subscribe(() => {
      this.stopWebcam();
      this.router.navigate(['/result', this.examId]);
    });
  }

  ngOnDestroy() {
    if (this.timer) clearInterval(this.timer);
    this.stopWebcam();
    document.removeEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
  }
}