import { DatePipe } from '@angular/common';
import { Component, inject, input, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { errorMessage } from '../../error-message';
import { Author, Comment, Post } from '../../models';
import { AuthService } from '../../services/auth.service';
import { CommentService } from '../../services/comment.service';
import { PostService } from '../../services/post.service';
import { StatusBadge } from '../../status-badge/status-badge';

/** One post with its comments. Authors (and admins) can edit or delete. */
@Component({
  selector: 'app-post-detail',
  imports: [DatePipe, FormsModule, RouterLink, StatusBadge],
  templateUrl: './post-detail.html',
})
export class PostDetailPage implements OnInit {
  private postService = inject(PostService);
  private commentService = inject(CommentService);
  private router = inject(Router);
  protected auth = inject(AuthService);

  /** From the URL /posts/:id */
  readonly id = input.required<string>();

  protected readonly post = signal<Post | null>(null);
  protected readonly comments = signal<Comment[]>([]);
  protected readonly error = signal('');
  protected readonly commentError = signal('');

  protected newComment = '';                                  // the "add a comment" box
  protected readonly editingId = signal<number | null>(null); // which comment is being edited
  protected editText = '';                                    // its text while editing

  ngOnInit(): void {
    this.postService.getPost(this.id()).subscribe({
      next: (post) => this.post.set(post),
      error: (err) => this.error.set(errorMessage(err)),
    });
    this.commentService.getComments(this.id()).subscribe((comments) => this.comments.set(comments));
  }

  /** Can the logged-in user edit/delete something written by `author`? */
  canChange(author: Author): boolean {
    const me = this.auth.user();
    return !!me && (me.id === author.id || me.role === 'admin');
  }

  // ----- post -----

  deletePost(): void {
    if (!confirm('Delete this post and all its comments?')) return;
    this.postService.deletePost(this.id()).subscribe({
      next: () => this.router.navigate(['/community']),
      error: (err) => this.error.set(errorMessage(err)),
    });
  }

  // ----- comments -----

  addComment(): void {
    this.commentError.set('');
    this.commentService.addComment(this.id(), this.newComment).subscribe({
      next: (comment) => {
        this.comments.update((list) => [...list, comment]);
        this.newComment = '';
      },
      error: (err) => this.commentError.set(errorMessage(err)),
    });
  }

  startEdit(comment: Comment): void {
    this.editingId.set(comment.id);
    this.editText = comment.body;
  }

  cancelEdit(): void {
    this.editingId.set(null);
  }

  saveEdit(comment: Comment): void {
    this.commentService.updateComment(comment.id, this.editText).subscribe({
      next: (updated) => {
        this.comments.update((list) => list.map((c) => (c.id === updated.id ? updated : c)));
        this.editingId.set(null);
      },
      error: (err) => this.commentError.set(errorMessage(err)),
    });
  }

  deleteComment(comment: Comment): void {
    if (!confirm('Delete this comment?')) return;
    this.commentService.deleteComment(comment.id).subscribe({
      next: () => this.comments.update((list) => list.filter((c) => c.id !== comment.id)),
      error: (err) => this.commentError.set(errorMessage(err)),
    });
  }
}
