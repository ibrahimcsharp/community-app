"""
Tests for posts, comments and admin moderation.   Run with:  python manage.py test
"""
from rest_framework.test import APITestCase

from accounts.models import User

from .models import Category, Comment, ModerationLog, Post


class CommunityTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("boss", "boss@test.com", "x")
        self.sara = User.objects.create_user("sara", "sara@test.com", "x", status="approved")
        self.john = User.objects.create_user("john", "john@test.com", "x", status="approved")
        self.category = Category.objects.create(name="General", slug="general")

    def as_user(self, user):
        self.client.force_authenticate(user)

    def new_post(self, title="Hi", user=None):
        if user:
            self.as_user(user)
        return self.client.post("/api/posts/", {"title": title, "body": "Text",
                                                "category": self.category.id}, format="json")

    def feed_titles(self):
        return [p["title"] for p in self.client.get("/api/posts/").data]

    # ----- posts -----
    def test_new_post_is_pending_and_hidden_from_others(self):
        response = self.new_post("Sara's post", user=self.sara)
        self.assertEqual(response.data["status"], "pending")
        self.assertIn("Sara's post", self.feed_titles())        # author sees it

        self.as_user(self.john)
        self.assertNotIn("Sara's post", self.feed_titles())     # others don't

    def test_admin_approves_post_then_everyone_sees_it(self):
        post_id = self.new_post("Hello", user=self.sara).data["id"]

        self.as_user(self.admin)
        response = self.client.post(f"/api/admin/posts/{post_id}/approve/")
        self.assertEqual(response.data["status"], "approved")
        self.assertTrue(ModerationLog.objects.filter(target_type="post", target_id=post_id).exists())

        self.as_user(self.john)
        self.assertIn("Hello", self.feed_titles())

    def test_admin_post_is_approved_at_once(self):
        self.assertEqual(self.new_post(user=self.admin).data["status"], "approved")

    def test_editing_sends_post_back_to_pending(self):
        post = Post.objects.create(user=self.sara, category=self.category, title="A",
                                   body="B", status="approved")
        self.as_user(self.sara)
        response = self.client.put(f"/api/posts/{post.id}/", {"title": "A2"}, format="json")
        self.assertEqual(response.data["status"], "pending")

    def test_cannot_edit_or_delete_someone_elses_post(self):
        post = Post.objects.create(user=self.sara, category=self.category, title="A",
                                   body="B", status="approved")
        self.as_user(self.john)
        self.assertEqual(self.client.put(f"/api/posts/{post.id}/", {"title": "X"}, format="json").status_code, 403)
        self.assertEqual(self.client.delete(f"/api/posts/{post.id}/").status_code, 403)

    def test_reject_with_reason(self):
        post_id = self.new_post(user=self.sara).data["id"]
        self.as_user(self.admin)
        self.client.post(f"/api/admin/posts/{post_id}/reject/", {"reason": "Off topic"}, format="json")

        self.as_user(self.sara)
        response = self.client.get(f"/api/posts/{post_id}/")
        self.assertEqual(response.data["status"], "rejected")
        self.assertEqual(response.data["reject_reason"], "Off topic")

    # ----- comments -----
    def test_comment_flow(self):
        post = Post.objects.create(user=self.sara, category=self.category, title="A",
                                   body="B", status="approved")
        self.as_user(self.john)
        response = self.client.post(f"/api/posts/{post.id}/comments/", {"body": "Nice"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "pending")

        self.as_user(self.sara)  # not approved yet, so Sara can't see John's comment
        self.assertEqual(len(self.client.get(f"/api/posts/{post.id}/comments/").data), 0)

        self.as_user(self.admin)
        self.client.post(f"/api/admin/comments/{response.data['id']}/approve/")

        self.as_user(self.sara)
        self.assertEqual(len(self.client.get(f"/api/posts/{post.id}/comments/").data), 1)

    def test_cannot_comment_on_pending_post(self):
        post = Post.objects.create(user=self.sara, category=self.category, title="A", body="B")
        self.as_user(self.sara)
        response = self.client.post(f"/api/posts/{post.id}/comments/", {"body": "Hi"}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_edit_comment_goes_back_to_pending(self):
        post = Post.objects.create(user=self.sara, category=self.category, title="A",
                                   body="B", status="approved")
        comment = Comment.objects.create(post=post, user=self.john, body="Hi", status="approved")
        self.as_user(self.john)
        response = self.client.put(f"/api/comments/{comment.id}/", {"body": "Hi!"}, format="json")
        self.assertEqual(response.data["status"], "pending")

    # ----- admin -----
    def test_normal_user_cannot_use_admin_api(self):
        self.as_user(self.sara)
        self.assertEqual(self.client.get("/api/admin/stats/").status_code, 403)

    def test_admin_approves_user(self):
        maria = User.objects.create_user("maria", "maria@test.com", "x")
        self.as_user(self.admin)
        response = self.client.post(f"/api/admin/users/{maria.id}/approve/")
        self.assertEqual(response.data["status"], "approved")
        self.assertEqual(self.client.get("/api/admin/stats/").data["pending_users"], 0)

    def test_unknown_action(self):
        self.as_user(self.admin)
        self.assertEqual(self.client.post(f"/api/admin/users/{self.sara.id}/explode/").status_code, 400)
