// The shapes of the data the Django API sends and receives.
// Field names match the JSON from backend/*/serializers.py exactly.

export type Role = 'user' | 'admin';
export type UserStatus = 'pending' | 'approved' | 'rejected' | 'blocked';
export type ContentStatus = 'pending' | 'approved' | 'rejected';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  bio: string;
  role: Role;
  status: UserStatus;
  approved_at: string | null;
  last_login: string | null;
  created_at: string;
}

/** The small user summary shown next to posts and comments. */
export interface Author {
  id: number;
  username: string;
  full_name: string;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
}

export interface Post {
  id: number;
  title: string;
  body: string;
  category: number;       // category id
  category_name: string;
  author: Author;
  status: ContentStatus;
  reject_reason: string;  // filled in when an admin rejects it
  comment_count: number;  // approved comments only
  created_at: string;
  updated_at: string;
}

export interface Comment {
  id: number;
  post: number;           // post id
  post_title: string;
  body: string;
  author: Author;
  status: ContentStatus;
  reject_reason: string;
  created_at: string;
  updated_at: string;
}

export interface ModerationLog {
  id: number;
  admin_username: string;
  target_type: 'user' | 'post' | 'comment';
  target_id: number;
  action: 'approve' | 'reject' | 'block' | 'unblock';
  note: string;
  created_at: string;
}

export interface AdminStats {
  pending_users: number;
  pending_posts: number;
  pending_comments: number;
  total_users: number;
  total_posts: number;
  total_comments: number;
}

// ----- What we send -----

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name: string;
}

export interface PostData {
  title: string;
  body: string;
  category: number;
}

export interface ProfileData {
  email: string;
  full_name: string;
  bio: string;
}

// ----- What login returns -----

export interface LoginResponse {
  access: string;   // short-lived token sent with every request
  refresh: string;  // long-lived token used to get a new access token
  user: User;
}
