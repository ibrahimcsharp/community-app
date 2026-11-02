import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import { AdminStats, Comment, ModerationLog, Post, User } from '../models';

export type UserAction = 'approve' | 'reject' | 'block' | 'unblock';
export type ContentAction = 'approve' | 'reject';

/** Talks to /api/admin/... (admins only). */
@Injectable({ providedIn: 'root' })
export class AdminService {
  private http = inject(HttpClient);
  private url = `${environment.apiUrl}/admin`;

  getStats(): Observable<AdminStats> {
    return this.http.get<AdminStats>(`${this.url}/stats/`);
  }

  // ----- users -----
  getUsers(status = ''): Observable<User[]> {
    return this.http.get<User[]>(`${this.url}/users/`, { params: statusParam(status) });
  }

  userAction(id: number, action: UserAction, reason = ''): Observable<User> {
    return this.http.post<User>(`${this.url}/users/${id}/${action}/`, { reason });
  }

  // ----- posts -----
  getPosts(status = ''): Observable<Post[]> {
    return this.http.get<Post[]>(`${this.url}/posts/`, { params: statusParam(status) });
  }

  postAction(id: number, action: ContentAction, reason = ''): Observable<Post> {
    return this.http.post<Post>(`${this.url}/posts/${id}/${action}/`, { reason });
  }

  // ----- comments -----
  getComments(status = ''): Observable<Comment[]> {
    return this.http.get<Comment[]>(`${this.url}/comments/`, { params: statusParam(status) });
  }

  commentAction(id: number, action: ContentAction, reason = ''): Observable<Comment> {
    return this.http.post<Comment>(`${this.url}/comments/${id}/${action}/`, { reason });
  }

  // ----- history -----
  getLogs(): Observable<ModerationLog[]> {
    return this.http.get<ModerationLog[]>(`${this.url}/logs/`);
  }
}

/** ?status=pending, or nothing when status is '' (= all). */
function statusParam(status: string): HttpParams {
  return status ? new HttpParams().set('status', status) : new HttpParams();
}
