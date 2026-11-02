import { DatePipe } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { errorMessage } from '../../error-message';
import { AuthService } from '../../services/auth.service';
import { StatusBadge } from '../../status-badge/status-badge';

/** Shows your account info and lets you change email, full name and bio. */
@Component({
  selector: 'app-profile',
  imports: [DatePipe, FormsModule, StatusBadge],
  templateUrl: './profile.html',
})
export class ProfilePage {
  protected auth = inject(AuthService);

  // Start the form with the current values.
  protected form = {
    email: this.auth.user()?.email ?? '',
    full_name: this.auth.user()?.full_name ?? '',
    bio: this.auth.user()?.bio ?? '',
  };
  protected readonly busy = signal(false);
  protected readonly success = signal('');
  protected readonly error = signal('');

  save(): void {
    this.busy.set(true);
    this.success.set('');
    this.error.set('');

    this.auth.updateProfile(this.form).subscribe({
      next: () => {
        this.success.set('Profile saved.');
        this.busy.set(false);
      },
      error: (err) => {
        this.error.set(errorMessage(err));
        this.busy.set(false);
      },
    });
  }
}
