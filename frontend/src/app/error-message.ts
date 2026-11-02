import { HttpErrorResponse } from '@angular/common/http';

/**
 * Turns any API error into one readable sentence to show on screen.
 *
 * Django sends errors in two shapes:
 *   { "detail": "Wrong username or password." }
 *   { "username": ["A user with that username already exists."] }
 */
export function errorMessage(error: unknown): string {
  if (!(error instanceof HttpErrorResponse)) {
    return 'Something went wrong.';
  }
  if (error.status === 0) {
    return 'Cannot reach the server. Is the Django backend running?';
  }

  const body = error.error;
  if (body?.detail) {
    return body.detail;
  }
  if (body && typeof body === 'object') {
    return Object.entries(body)
      .map(([field, messages]) => {
        const text = Array.isArray(messages) ? messages.join(' ') : String(messages);
        return field === 'non_field_errors' ? text : `${field.replace('_', ' ')}: ${text}`;
      })
      .join(' ');
  }
  return `Error ${error.status}.`;
}
