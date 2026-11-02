import { Location } from '@angular/common';
import { Component, computed, inject, input, OnInit, output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { errorMessage } from '../../error-message';
import { Category, Post } from '../../models';
import { AuthService } from '../../services/auth.service';
import { PostService } from '../../services/post.service';

/**
 * Create or edit a post. Used in three places:
 *   /posts/new        -> create, then open the new post
 *   /posts/:id/edit   -> edit,   then open the post
 *   inside the community page (embedded = true) -> create, then tell the page via (saved)
 */
@Component({
  selector: 'app-post-form',
  imports: [FormsModule],
  templateUrl: './post-form.html',
})
export class PostForm implements OnInit {
  private postService = inject(PostService);
  private router = inject(Router);
  private location = inject(Location);
  protected auth = inject(AuthService);

  /** From the URL /posts/:id/edit. Empty when creating a new post. */
  readonly id = input<string>();
  /** True when shown inside another page instead of on its own. */
  readonly embedded = input(false);

  readonly saved = output<Post>();
  readonly cancelled = output<void>();

  protected readonly isEdit = computed(() => !!this.id());
  protected form = { title: '', body: '', category: null as number | null };
  protected readonly categories = signal<Category[]>([]);
  protected readonly loading = signal(false);
  protected readonly busy = signal(false);
  protected readonly error = signal('');

  ngOnInit(): void {
    this.postService.getCategories().subscribe((categories) => this.categories.set(categories));

    // Editing: fill the form with the current post.
    const id = this.id();
    if (id) {
      this.loading.set(true);
      this.postService.getPost(id).subscribe({
        next: (post) => {
          this.form = { title: post.title, body: post.body, category: post.category };
          this.loading.set(false);
        },
        error: (err) => {
          this.error.set(errorMessage(err));
          this.loading.set(false);
        },
      });
    }
  }

  submit(): void {
    if (this.form.category === null) return;
    this.error.set('');
    this.busy.set(true);

    const data = { title: this.form.title, body: this.form.body, category: this.form.category };
    const id = this.id();
    const request = id ? this.postService.updatePost(id, data) : this.postService.createPost(data);

    request.subscribe({
      next: (post) => {
        this.busy.set(false);
        this.saved.emit(post);
        if (!this.embedded()) {
          this.router.navigate(['/posts', post.id]);
        }
      },
      error: (err) => {
        this.error.set(errorMessage(err));
        this.busy.set(false);
      },
    });
  }

  cancel(): void {
    if (this.embedded()) {
      this.cancelled.emit();
    } else {
      this.location.back();
    }
  }
}
