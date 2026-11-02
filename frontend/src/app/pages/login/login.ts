import { Component, computed, inject, input, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { errorMessage } from '../../error-message';
import { AuthService } from '../../services/auth.service';

// Messages that other pages can show here with /login?reason=...
const REASON_MESSAGES: Record<string, string> = {
  registered: 'Account created! An admin must approve it before you can log in.',
  expired: 'Your session has ended. Please log in again.',
};

/** Login form. On success it goes to the community board. */
@Component({
  selector: 'app-login',
  imports: [FormsModule, RouterLink],
  templateUrl: './login.html',
})
export class LoginPage {
  private auth = inject(AuthService);
  private router = inject(Router);

  /** From the URL: /login?reason=registered */
  readonly reason = input<string>();
  protected readonly infoMessage = computed(() => REASON_MESSAGES[this.reason() ?? ''] ?? '');

  protected form = { username: '', password: '' };
  protected readonly error = signal('');
  protected readonly busy = signal(false);

  constructor() {
    // Already logged in? Skip the form.
    if (this.auth.isLoggedIn()) {
      this.router.navigate(['/community']);
    }
  }

  submit(): void {
    this.error.set('');
    this.busy.set(true);

    this.auth.login(this.form.username, this.form.password).subscribe({
      next: () => this.router.navigate(['/community']),
      error: (err) => {
        this.error.set(errorMessage(err)); // e.g. "Your account is waiting for admin approval."
        this.busy.set(false);
      },
    });
  }
}
