"""
Dynamic SEO XML Sitemaps for Ramonet Platform.
Indexes all public learning topics, academy courses, guided lessons, device guides,
and interactive high-value networking tools.
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from learning.models import LearningTopic
from academy.models import Course, Lesson, DeviceGuide


class StaticViewSitemap(Sitemap):
    priority = 0.9
    changefreq = 'weekly'

    def items(self):
        return [
            'dashboard',
            'topology:designer',
            'topology:rack_designer',
            'networktools:toolbox',
            'networktools:subnet_calculator',
            'networktools:ports_cheatsheet',
            'networktools:osi_model',
            'networktools:discovery',
            'networktools:capacity_cost',
            'commands:library',
            'troubleshooting:incident_simulator',
            'troubleshooting:lab',
            'monitoring:dashboard',
            'projects:scenarios',
            'projects:documentation',
            'configuration:automation_studio',
            'configuration:compliance_centre',
            'learning:center',
            'academy:dashboard',
            'academy:device_guides',
        ]

    def location(self, item):
        return reverse(item)


class TopicSitemap(Sitemap):
    priority = 0.85
    changefreq = 'weekly'

    def items(self):
        return LearningTopic.objects.all().order_by('topic_number')

    def location(self, item):
        return reverse('learning:topic_detail', kwargs={'slug': item.slug})


class CourseSitemap(Sitemap):
    priority = 0.85
    changefreq = 'weekly'

    def items(self):
        return Course.objects.filter(is_published=True).order_by('order')

    def location(self, item):
        return reverse('academy:course_detail', kwargs={'slug': item.slug})

    def lastmod(self, item):
        return item.updated_at


class LessonSitemap(Sitemap):
    priority = 0.80
    changefreq = 'weekly'

    def items(self):
        return Lesson.objects.filter(course__is_published=True).select_related('course').order_by('order')

    def location(self, item):
        return reverse('academy:lesson_reader', kwargs={
            'course_slug': item.course.slug,
            'lesson_slug': item.slug
        })

    def lastmod(self, item):
        return item.created_at


class DeviceGuideSitemap(Sitemap):
    priority = 0.75
    changefreq = 'monthly'

    def items(self):
        return DeviceGuide.objects.all().order_by('order')

    def location(self, item):
        return reverse('academy:device_guide_detail', kwargs={'slug': item.slug})
