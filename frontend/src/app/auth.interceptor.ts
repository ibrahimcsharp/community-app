import { HttpErrorResponse, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';

import { AuthService } from './services/auth.service';

/**
 * Runs for every HTTP request the app makes.
 *
 *  1. Adds "Authorization: Bearer <access token>" so Django knows who we are.
 *  2. If Django answers 401 (token expired), it gets a new access token with
 *     the refresh token and tries the request once more.
 *  3. If that fails too, the user is logged out.
 */
export const authInterceptor: HttpInterceptorFn = (request, next) => {
  const auth = inject(AuthService);

  // Login, register and refresh don't need (and must not retry with) a token.
  const isAuthCall = /\/auth\/(login|register|refresh)\/$/.test(request.url);
  if (isAuthCall) {
    return next(request);
  }

  const token = auth.getAccessToken();
  return next(token ? withToken(request, token) : request).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status !== 401) {
        return throwError(() => error); // not a login problem: let the page show it
      }
      if (!auth.getRefreshToken()) {
        auth.logout('expired');
        return throwError(() => error);
      }
      return auth.refreshAccessToken().pipe(
        switchMap((newToken) => next(withToken(request, newToken))),
        catchError((retryError: HttpErrorResponse) => {
          if (retryError.status === 401) auth.logout('expired');
          return throwError(() => retryError);
        }),
      );
    }),
  );
};

function withToken(request: HttpRequest<unknown>, token: string): HttpRequest<unknown> {
  return request.clone({ setHeaders: { Authorization: `Bearer ${token}` } });
}
