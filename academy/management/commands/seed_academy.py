from django.core.management.base import BaseCommand
from academy.models import Course, Lesson, QuizQuestion, DeviceGuide, Achievement
from .courses_data import COURSES_DATA
from .devices_data import DEVICES_DATA

class Command(BaseCommand):
    help = 'Seeds Ramonet Academy with 14 courses, structured lessons (sections A-H), labs, quizzes, 27 device guides, and badges.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting Ramonet Academy database seeding...'))

        # 1. Seed Achievements / Badges
        achievements_data = [
            {'badge_code': 'first_lesson', 'title': 'First Steps', 'description': 'Completed your very first Ramonet Academy lesson.', 'icon': 'fa-shoe-prints', 'category': 'general', 'points': 50},
            {'badge_code': 'first_lab', 'title': 'Hands-on Engineer', 'description': 'Successfully completed your first practical simulation lab.', 'icon': 'fa-wrench', 'category': 'labs', 'points': 100},
            {'badge_code': 'perfect_quiz', 'title': 'Quiz Champion', 'description': 'Achieved a perfect 100% score on a knowledge assessment.', 'icon': 'fa-trophy', 'category': 'quiz', 'points': 100},
            {'badge_code': 'vlan_master', 'title': 'VLAN Architect', 'description': 'Successfully configured and verified 802.1Q VLAN broadcast isolation.', 'icon': 'fa-random', 'category': 'switching', 'points': 150},
            {'badge_code': 'routing_pro', 'title': 'Routing Professional', 'description': 'Mastered cross-subnet routing and default gateway forwarders.', 'icon': 'fa-route', 'category': 'routing', 'points': 150},
            {'badge_code': 'firewall_defender', 'title': 'Cyber Defender', 'description': 'Implemented stateful packet inspection and perimeter security rules.', 'icon': 'fa-shield-halved', 'category': 'security', 'points': 150},
            {'badge_code': 'streak_3', 'title': 'Consistent Learner', 'description': 'Maintained an active Academy study streak for 3 days.', 'icon': 'fa-fire', 'category': 'streak', 'points': 100},
            {'badge_code': 'rcna_certified', 'title': 'Ramonet Certified Network Architect', 'description': 'Passed the Capstone Enterprise Examination with flying colors.', 'icon': 'fa-certificate', 'category': 'certification', 'points': 500},
        ]
        ach_count = 0
        for ach in achievements_data:
            obj, created = Achievement.objects.update_or_create(
                badge_code=ach['badge_code'],
                defaults=ach
            )
            ach_count += 1
        self.stdout.write(self.style.SUCCESS(f'Seeded {ach_count} Academy Badges & Achievements.'))

        # 2. Seed 27 Device Guides (all 17 sections)
        dev_count = 0
        for dev in DEVICES_DATA:
            guide, created = DeviceGuide.objects.update_or_create(
                device_type=dev['device_type'],
                defaults=dev
            )
            dev_count += 1
        self.stdout.write(self.style.SUCCESS(f'Seeded {dev_count} Device-Specific Comprehensive Guides (17 sections each).'))

        # 3. Seed 14 Courses, Lessons (sections A-H), Labs, and Quizzes
        course_count = 0
        lesson_count = 0
        quiz_count = 0

        for c_data in COURSES_DATA:
            lessons_list = c_data.pop('lessons', [])
            course, _ = Course.objects.update_or_create(
                slug=c_data['slug'],
                defaults=c_data
            )
            course_count += 1

            for l_data in lessons_list:
                quizzes_list = l_data.pop('quizzes', [])
                lesson, _ = Lesson.objects.update_or_create(
                    course=course,
                    slug=l_data['slug'],
                    defaults=l_data
                )
                lesson_count += 1

                for q_idx, q_data in enumerate(quizzes_list, start=1):
                    q_data['order'] = q_idx
                    QuizQuestion.objects.update_or_create(
                        lesson=lesson,
                        order=q_idx,
                        defaults=q_data
                    )
                    quiz_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {course_count} Courses, {lesson_count} Practical Lessons, and {quiz_count} Quiz Questions.'
        ))
        self.stdout.write(self.style.SUCCESS('Ramonet Academy database seeding completed successfully!'))
