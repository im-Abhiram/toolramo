from django.db import models

class LearningTopic(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner Path'),
        ('intermediate', 'Intermediate Path'),
        ('advanced', 'Advanced Path'),
    ]

    topic_number = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    category = models.CharField(max_length=64, default='Fundamentals')
    
    simple_explanation = models.TextField(help_text="Clear, intuitive, real-world metaphor")
    technical_explanation = models.TextField(help_text="Rigorous engineering explanation")
    practical_example = models.TextField(help_text="Real enterprise use-case scenario")
    
    relevant_devices = models.JSONField(default=list, blank=True)
    relevant_commands = models.JSONField(default=list, blank=True)
    
    diagram_svg = models.TextField(blank=True, default='', help_text="Inline SVG diagram for visualization")
    common_mistakes = models.TextField(blank=True, default='')
    practice_exercise = models.TextField(blank=True, default='')
    
    quiz_questions = models.JSONField(default=list, blank=True, help_text="Interactive self-test questions")

    class Meta:
        ordering = ['topic_number']

    def __str__(self):
        return f"Topic {self.topic_number}: {self.title}"
