import { DatePipe, SlicePipe } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { errorMessage } from '../../error-message';
import { Category, Post } from '../../models';
import { PostService } from '../../services/post.service';
import { StatusBadge } from '../../status-badge/status-badge';
import { PostForm } from '../post-form/post-form';

/**
 * The community board: a list of posts with a category filter,
 * an "All / My posts" switch, and a button that opens the new-post form.
 */
@Component({
  selector: 'app-community',
  imports: [DatePipe, SlicePipe, FormsModule, RouterLink, StatusBadge, PostForm],
  templateUrl: './community.html',
})
export class CommunityPage {
  private postService = inject(PostService);

  protected readonly posts = signal<Post[]>([]);
  protected readonly categories = signal<Category[]>([]);
  protected readonly loading = signal(true);
  protected readonly error = signal('');
  protected readonly showNewPostForm = signal(false);

  // Filters. category = category id as text ('' = all).
  protected filters = { category: '', mine: false };

  constructor() {
    this.postService.getCategories().subscribe((categories) => this.categories.set(categories));
    this.loadPosts();
  }

  loadPosts(): void {
    this.loading.set(true);
    this.error.set('');
    this.postService.getPosts(this.filters).subscribe({
      next: (posts) => {
        this.posts.set(posts);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(errorMessage(err));
        this.loading.set(false);
      },
    });
  }

  setCategory(categoryId: string): void {
    this.filters.category = categoryId;
    this.loadPosts();
  }

  setMine(mine: boolean): void {
    this.filters.mine = mine;
    this.loadPosts();
  }

  /** Called by the embedded <app-post-form> after a post was saved. */
  onPostSaved(): void {
    this.showNewPostForm.set(false);
    this.loadPosts();
  }
}
