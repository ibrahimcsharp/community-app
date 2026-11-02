import { DatePipe, SlicePipe } from '@angular/common';
import { Component, inject, signal, WritableSignal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Observable } from 'rxjs';

import { errorMessage } from '../../error-message';
import { AdminStats, Comment, ModerationLog, Post, User } from '../../models';
import { AdminService, ContentAction, UserAction } from '../../services/admin.service';
import { AuthService } from '../../services/auth.service';
import { StatusBadge } from '../../status-badge/status-badge';

type Tab = 'users' | 'posts' | 'comments' | 'logs';

/**
 * Admin panel with four tabs:
 *   Users    - approve / reject new sign-ups, block / unblock
 *   Posts    - approve / reject posts
 *   Comments - approve / reject comments
 *   Log      - history of all admin actions
 * The status filter starts on "pending", which is the to-do list.
 */
@Component({
  selector: 'app-admin',
  imports: [DatePipe, SlicePipe, FormsModule, RouterLink, StatusBadge],
  templateUrl: './admin.html',
})
export class AdminPage {
  private adminService = inject(AdminService);
  protected auth = inject(AuthService);

  protected readonly tab = signal<Tab>('users');
  protected statusFilter = 'pending'; // '' = all

  protected readonly stats = signal<AdminStats | null>(null);
  protected readonly users = signal<User[]>([]);
  protected readonly posts = signal<Post[]>([]);
  protected readonly comments = signal<Comment[]>([]);
  protected readonly logs = signal<ModerationLog[]>([]);

  protected readonly loading = signal(false);
  protected readonly message = signal(''); // green "done" message
  protected readonly error = signal('');

  constructor() {
    this.reload();
  }

  showTab(tab: Tab): void {
    this.tab.set(tab);
    this.message.set('');
    this.reload();
  }

  setStatusFilter(status: string): void {
    this.statusFilter = status;
    this.reload();
  }

  /** Load the numbers on the tabs and the list for the current tab. */
  reload(): void {
    this.error.set('');
    this.loading.set(true);
    this.adminService.getStats().subscribe((stats) => this.stats.set(stats));

    switch (this.tab()) {
      case 'users':
        this.load(this.adminService.getUsers(this.statusFilter), this.users);
        break;
      case 'posts':
        this.load(this.adminService.getPosts(this.statusFilter), this.posts);
        break;
      case 'comments':
        this.load(this.adminService.getComments(this.statusFilter), this.comments);
        break;
      case 'logs':
        this.load(this.adminService.getLogs(), this.logs);
        break;
    }
  }

  // ----- actions -----

  userAction(user: User, action: UserAction): void {
    const reason = this.askReason(action);
    if (reason === null) return; // admin pressed Cancel
    this.adminService.userAction(user.id, action, reason).subscribe({
      next: () => this.afterAction(`User "${user.username}": ${action} done.`),
      error: (err) => this.fail(err),
    });
  }

  postAction(post: Post, action: ContentAction): void {
    const reason = this.askReason(action);
    if (reason === null) return;
    this.adminService.postAction(post.id, action, reason).subscribe({
      next: () => this.afterAction(`Post "${post.title}": ${action} done.`),
      error: (err) => this.fail(err),
    });
  }

  commentAction(comment: Comment, action: ContentAction): void {
    const reason = this.askReason(action);
    if (reason === null) return;
    this.adminService.commentAction(comment.id, action, reason).subscribe({
      next: () => this.afterAction(`Comment by ${comment.author.username}: ${action} done.`),
      error: (err) => this.fail(err),
    });
  }

  // ----- helpers -----

  /** Run a list request and put the result into one of the signals above. */
  private load<T>(request: Observable<T[]>, list: WritableSignal<T[]>): void {
    request.subscribe({
      next: (items) => {
        list.set(items);
        this.loading.set(false);
      },
      error: (err) => this.fail(err),
    });
  }

  /** For reject/block, ask for an optional reason. Returns null if Cancel was pressed. */
  private askReason(action: string): string | null {
    if (action !== 'reject' && action !== 'block') return '';
    return prompt('Reason (optional, saved in the log and shown to the author):', '');
  }

  private afterAction(text: string): void {
    this.message.set(text);
    this.reload();
  }

  private fail(err: unknown): void {
    this.error.set(errorMessage(err));
    this.loading.set(false);
  }
}
