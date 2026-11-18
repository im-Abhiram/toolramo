from django.db import models
from django.contrib.auth.models import User
import uuid

class Course(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    CATEGORY_CHOICES = [
        ('foundations', 'Network Foundations'),
        ('switching_routing', 'Switching & Routing'),
        ('security', 'Network Security & Firewalls'),
        ('services_storage', 'Enterprise Services & Storage'),
        ('infrastructure', 'Infrastructure & Surveillance'),
        ('troubleshooting', 'Diagnostics & Troubleshooting'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default='foundations')
    estimated_hours = models.DecimalField(max_digits=4, decimal_places=1, default=4.0)
    icon = models.CharField(max_length=64, default='fa-graduation-cap')
    badge_name = models.CharField(max_length=100, default='Certified Network Associate')
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Academy Course'
        verbose_name_plural = 'Academy Courses'

    def __str__(self):
        return f"{self.title} ({self.get_level_display()})"

    @property
    def lesson_count(self):
        return self.lessons.count()

    @property
    def has_practical_labs(self):
        return self.lessons.filter(has_practical_lab=True).exists()


class Lesson(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    lesson_number = models.PositiveIntegerField(default=1)
    summary = models.TextField(blank=True, default='')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    estimated_minutes = models.PositiveIntegerField(default=25)

    # 8-Section Standard Educational Structure
    # SECTION A: Introduction
    section_a_intro = models.JSONField(
        default=dict,
        help_text="dict with: definition, purpose, why_needed, where_used, real_world_examples, advantages, limitations"
    )

    # SECTION B: How It Works
    section_b_how_it_works = models.JSONField(
        default=dict,
        help_text="dict with: architecture, protocols, interfaces, data_flow, device_interactions, osi_layers"
    )

    # SECTION C: Device Connection
    section_c_connection = models.JSONField(
        default=dict,
        help_text="dict with: required_devices, cable_types, port_selection, interface_compatibility, connection_diagram, ip_requirements, power_poe"
    )

    # SECTION D: Configuration
    section_d_configuration = models.JSONField(
        default=dict,
        help_text="dict with: device_setup, interface_config, ip_config, network_services, security_settings, verification"
    )

    # SECTION E: Command Training
    section_e_commands = models.JSONField(
        default=list,
        help_text="list of: {command, syntax, purpose, params, mode, expected_output, verification_commands, common_errors}"
    )

    # SECTION F: Practical Lab Specification
    has_practical_lab = models.BooleanField(default=True)
    lab_topology = models.JSONField(
        default=dict,
        help_text="Initial topology JSON {devices: [...], links: [...]}"
    )
    lab_tasks = models.JSONField(
        default=list,
        help_text="list of tasks: {task_id, title, instruction, target_device, expected_config, hints: [h1,h2,h3], show_me_steps: [...]}"
    )
    lab_solution_state = models.JSONField(
        default=dict,
        help_text="Target verification state: {devices: {...}, ping_tests: [...], checks: [...]}"
    )

    # SECTION G: Troubleshooting
    section_g_troubleshooting = models.JSONField(
        default=list,
        help_text="list of: {symptom, cause, diagnosis, fix}"
    )

    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'lesson_number']
        unique_together = ('course', 'slug')

    def __str__(self):
        return f"{self.course.title} - L{self.lesson_number}: {self.title}"


class QuizQuestion(models.Model):
    QUESTION_TYPES = [
        ('mcq', 'Multiple Choice'),
        ('true_false', 'True / False'),
        ('cli_identify', 'CLI Command Identification'),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='mcq')
    question_text = models.TextField()
    options = models.JSONField(default=list, help_text="List of choices: [{'id': 'A', 'text': '...'}]")
    correct_answer = models.CharField(max_length=200)
    explanation = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Quiz ({self.lesson.title}) Q{self.order}: {self.question_text[:50]}"


class DeviceGuide(models.Model):
    """
    27 Device-Specific In-Depth Courses covering all 17 required sections.
    """
    device_type = models.CharField(max_length=64, unique=True, help_text="e.g. router, layer2_switch, firewall")
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128, unique=True)
    category = models.CharField(max_length=64)
    icon = models.CharField(max_length=64, default='fa-server')
    summary = models.TextField()
    
    # 17 Standard Educational Sections
    section_1_intro = models.TextField(help_text="1. Device introduction")
    section_2_purpose = models.TextField(help_text="2. Purpose and function")
    section_3_applications = models.TextField(help_text="3. Real-world applications")
    section_4_appearance_ports = models.TextField(help_text="4. Physical appearance and ports")
    section_5_interfaces = models.TextField(help_text="5. Available interfaces")
    section_6_connection_methods = models.TextField(help_text="6. Connection methods")
    section_7_cables = models.TextField(help_text="7. Cable requirements")
    section_8_power_requirements = models.TextField(help_text="8. Power and PoE requirements")
    section_9_ip_configuration = models.TextField(help_text="9. IP configuration")
    section_10_device_settings = models.TextField(help_text="10. Device-specific settings")
    section_11_commands = models.JSONField(default=list, help_text="11. Supported commands")
    section_12_command_explanations = models.JSONField(default=list, help_text="12. Command explanations")
    section_13_verification = models.TextField(help_text="13. Verification procedures")
    section_14_common_mistakes = models.JSONField(default=list, help_text="14. Common mistakes")
    section_15_troubleshooting = models.JSONField(default=list, help_text="15. Troubleshooting")
    section_16_security_practices = models.JSONField(default=list, help_text="16. Security best practices")
    section_17_practical_project = models.JSONField(default=dict, help_text="17. Practical project topology & steps")
    
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f"Device Guide: {self.name}"


class UserCourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='course_progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='user_progress')
    completed_lessons = models.JSONField(default=list, help_text="List of lesson IDs completed")
    lab_scores = models.JSONField(default=dict, help_text="{lesson_id: score}")
    quiz_scores = models.JSONField(default=dict, help_text="{lesson_id: score}")
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    credential_id = models.CharField(max_length=64, blank=True, default='')
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        u = self.user.username if self.user else "Anonymous"
        return f"{u} - {self.course.title} ({len(self.completed_lessons)} completed)"

    def issue_credential(self):
        if not self.credential_id:
            self.credential_id = f"RAMONET-{uuid.uuid4().hex[:12].upper()}"
            self.save(update_fields=['credential_id'])
        return self.credential_id


class UserLearningProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='academy_profile')
    streak_days = models.PositiveIntegerField(default=1)
    last_activity_date = models.DateField(null=True, blank=True)
    total_points = models.PositiveIntegerField(default=0)
    earned_badges = models.JSONField(default=list)

    def __str__(self):
        u = self.user.username if self.user else "Guest Learner"
        return f"{u} Profile (Streak: {self.streak_days}d, {self.total_points} pts)"


class Achievement(models.Model):
    badge_code = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=128)
    description = models.TextField()
    icon = models.CharField(max_length=64, default='fa-award')
    category = models.CharField(max_length=64, default='general')
    points = models.PositiveIntegerField(default=50)

    def __str__(self):
        return f"{self.title} ({self.badge_code})"
