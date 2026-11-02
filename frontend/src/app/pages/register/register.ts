import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { errorMessage } from '../../error-message';
import { AuthService } from '../../services/auth.service';

/**
 * Registration form. The new account is 'pending' until an admin approves it,
 * so after signing up we send the user to the login page with a message.
 */
@Component({
  selector: 'app-register',
  imports: [FormsModule, RouterLink],
  templateUrl: './register.html',
})
export class RegisterPage {
  private auth = inject(AuthService);
  private router = inject(Router);

  protected form = { username: '', email: '', full_name: '', password: '', confirmPassword: '' };
  protected readonly error = signal('');
  protected readonly busy = signal(false);

  passwordsMatch(): boolean {
    return this.form.password === this.form.confirmPassword;
  }

  submit(): void {
    if (!this.passwordsMatch()) return;
    this.error.set('');
    this.busy.set(true);

    const { confirmPassword, ...data } = this.form; // confirmPassword is only for the screen
    this.auth.register(data).subscribe({
      next: () => this.router.navigate(['/login'], { queryParams: { reason: 'registered' } }),
      error: (err) => {
        this.error.set(errorMessage(err)); // e.g. "username: A user with that username already exists."
        this.busy.set(false);
      },
    });
  }
}
