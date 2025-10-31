from django.db import models
from accounts.models import CustomUser
from destinations.models import Destination


class ExplorePost(models.Model):
    """
    User-generated content: videos, photos, blogs.
    """
    
    POST_TYPE_CHOICES = [
        ('PHOTO', 'Photo'),
        ('VIDEO', 'Video'),
        ('BLOG', 'Blog'),
    ]
    
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    post_type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES)
    
    # Content
    title = models.CharField(max_length=255)
    caption = models.TextField(blank=True)
    
    # For photos
    image = models.ImageField(upload_to='explore/photos/', blank=True, null=True)
    
    # For videos
    video = models.FileField(upload_to='explore/videos/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)  # For YouTube, Vimeo links
    thumbnail = models.ImageField(upload_to='explore/thumbnails/', blank=True, null=True)
    
    # For blogs
    content = models.TextField(blank=True)  # Rich text content for blogs
    
    # Relations
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    
    # Engagement
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    
    # Moderation
    is_approved = models.BooleanField(default=True)  # Can be reviewed by admin
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_post_type_display()}: {self.title} by {self.author.email}"


class PostLike(models.Model):
    """
    Track likes on explore posts.
    Normalized to prevent duplicate likes.
    """
    post = models.ForeignKey(ExplorePost, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['post', 'user']

    def __str__(self):
        return f"{self.user.email} liked {self.post.title}"


class PostComment(models.Model):
    """
    Comments on explore posts.
    """
    post = models.ForeignKey(ExplorePost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.email} on {self.post.title}"