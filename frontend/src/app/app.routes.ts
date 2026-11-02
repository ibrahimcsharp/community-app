import { Routes } from '@angular/router';

import { adminGuard, authGuard } from './guards';
import { AdminPage } from './pages/admin/admin';
import { CommunityPage } from './pages/community/community';
import { LoginPage } from './pages/login/login';
import { PostDetailPage } from './pages/post-detail/post-detail';
import { PostForm } from './pages/post-form/post-form';
import { ProfilePage } from './pages/profile/profile';
import { RegisterPage } from './pages/register/register';

// Which page shows for which URL. To add a page: create it in pages/ and add a line here.
export const routes: Routes = [
  { path: '', redirectTo: 'community', pathMatch: 'full' },

  // Open to everyone
  { path: 'login', component: LoginPage, title: 'Log in' },
  { path: 'register', component: RegisterPage, title: 'Register' },

  // Logged-in users
  { path: 'community', component: CommunityPage, canActivate: [authGuard], title: 'Community' },
  { path: 'posts/new', component: PostForm, canActivate: [authGuard], title: 'New post' },
  { path: 'posts/:id', component: PostDetailPage, canActivate: [authGuard], title: 'Post' },
  { path: 'posts/:id/edit', component: PostForm, canActivate: [authGuard], title: 'Edit post' },
  { path: 'profile', component: ProfilePage, canActivate: [authGuard], title: 'My profile' },

  // Admins only
  { path: 'admin', component: AdminPage, canActivate: [authGuard, adminGuard], title: 'Admin' },

  // Unknown address -> community board
  { path: '**', redirectTo: 'community' },
];
