import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import { Category, Post, PostData } from '../models';

/** Talks to /api/categories/ and /api/posts/ */
@Injectable({ providedIn: 'root' })
export class PostService {
  private http = inject(HttpClient);
  private url = environment.apiUrl;

  getCategories(): Observable<Category[]> {
    return this.http.get<Category[]>(`${this.url}/categories/`);
  }

  /** The community board. `category` = category id, `mine` = only my own posts. */
  getPosts(filters: { category?: string; mine?: boolean } = {}): Observable<Post[]> {
    let params = new HttpParams();
    if (filters.category) params = params.set('category', filters.category);
    if (filters.mine) params = params.set('mine', '1');
    return this.http.get<Post[]>(`${this.url}/posts/`, { params });
  }

  getPost(id: number | string): Observable<Post> {
    return this.http.get<Post>(`${this.url}/posts/${id}/`);
  }

  createPost(data: PostData): Observable<Post> {
    return this.http.post<Post>(`${this.url}/posts/`, data);
  }

  updatePost(id: number | string, data: PostData): Observable<Post> {
    return this.http.put<Post>(`${this.url}/posts/${id}/`, data);
  }

  deletePost(id: number | string): Observable<void> {
    return this.http.delete<void>(`${this.url}/posts/${id}/`);
  }
}
