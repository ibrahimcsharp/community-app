import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import { Comment } from '../models';

/** Talks to /api/posts/<id>/comments/ and /api/comments/<id>/ */
@Injectable({ providedIn: 'root' })
export class CommentService {
  private http = inject(HttpClient);
  private url = environment.apiUrl;

  getComments(postId: number | string): Observable<Comment[]> {
    return this.http.get<Comment[]>(`${this.url}/posts/${postId}/comments/`);
  }

  addComment(postId: number | string, body: string): Observable<Comment> {
    return this.http.post<Comment>(`${this.url}/posts/${postId}/comments/`, { body });
  }

  updateComment(id: number, body: string): Observable<Comment> {
    return this.http.put<Comment>(`${this.url}/comments/${id}/`, { body });
  }

  deleteComment(id: number): Observable<void> {
    return this.http.delete<void>(`${this.url}/comments/${id}/`);
  }
}
