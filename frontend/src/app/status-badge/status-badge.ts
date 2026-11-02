import { Component, computed, input } from '@angular/core';

/**
 * A small coloured label for a status, used on many pages:
 *   <app-status-badge [status]="post.status" />
 */
@Component({
  selector: 'app-status-badge',
  templateUrl: './status-badge.html',
})
export class StatusBadge {
  readonly status = input.required<string>();

  // Bootstrap colour for each status. Change the colours here.
  protected readonly colorClass = computed(() => {
    switch (this.status()) {
      case 'approved': return 'text-bg-success';
      case 'pending':  return 'text-bg-warning';
      case 'rejected': return 'text-bg-danger';
      case 'blocked':  return 'text-bg-dark';
      default:         return 'text-bg-secondary';
    }
  });
}
