import { HttpClient } from '@angular/common/http';
import { computed, inject, Injectable, signal } from '@angular/core';
import { Router } from '@angular/router';
import { map, Observable, tap } from 'rxjs';

import { environment } from '../../environments/environment';
import { LoginResponse, ProfileData, RegisterData, User } from '../models';

// Names of the values we keep in the browser's localStorage.
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const USER_KEY = 'user';

/**
 * Everything about the logged-in user: login, register, logout, profile.
 * Any component can read `auth.user()`, `auth.isLoggedIn()` or `auth.isAdmin()`.
 */
@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private url = `${environment.apiUrl}/auth`;

  /** The logged-in user, or null. Restored from localStorage after a page reload. */
  readonly user = signal<User | null>(readSavedUser());
  readonly isLoggedIn = computed(() => this.user() !== null);
  readonly isAdmin = computed(() => this.user()?.role === 'admin');

  login(username: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.url}/login/`, { username, password }).pipe(
      tap((response) => {
        localStorage.setItem(ACCESS_TOKEN_KEY, response.access);
        localStorage.setItem(REFRESH_TOKEN_KEY, response.refresh);
        this.saveUser(response.user);
      }),
    );
  }

  register(data: RegisterData): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.url}/register/`, data);
  }

  /** Ask for a new access token using the refresh token. Used by auth.interceptor.ts. */
  refreshAccessToken(): Observable<string> {
    return this.http
      .post<{ access: string }>(`${this.url}/refresh/`, { refresh: this.getRefreshToken() })
      .pipe(
        map((response) => response.access),
        tap((access) => localStorage.setItem(ACCESS_TOKEN_KEY, access)),
      );
  }

  updateProfile(data: ProfileData): Observable<User> {
    return this.http.put<User>(`${this.url}/me/`, data).pipe(tap((user) => this.saveUser(user)));
  }

  /** Forget the user and go to the login page. `reason` shows a message there. */
  logout(reason?: 'expired'): void {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    this.user.set(null);
    this.router.navigate(['/login'], { queryParams: reason ? { reason } : {} });
  }

  getAccessToken(): string | null {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  }

  private saveUser(user: User): void {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    this.user.set(user);
  }
}

function readSavedUser(): User | null {
  try {
    const saved = localStorage.getItem(USER_KEY);
    return saved ? JSON.parse(saved) : null;
  } catch {
    return null; // storage blocked or broken: just start logged out
  }
}
