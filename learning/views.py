from django.shortcuts import render, get_object_or_404
from .models import LearningTopic

def learning_center_view(request):
    """
    Ramonet Structured Learning Center Hub.
    """
    level = request.GET.get('level', '').strip()
    topics = LearningTopic.objects.all()

    if level:
        topics = topics.filter(level=level)

    context = {
        'topics': topics,
        'selected_level': level,
        'page_title': 'Learning Center',
    }
    return render(request, 'learning/center.html', context)

def topic_detail_view(request, slug):
    """
    Individual structured topic view with Simple/Technical explanations, diagrams, and exercises.
    """
    topic = get_object_or_404(LearningTopic, slug=slug)
    next_topic = LearningTopic.objects.filter(topic_number__gt=topic.topic_number).order_by('topic_number').first()
    prev_topic = LearningTopic.objects.filter(topic_number__lt=topic.topic_number).order_by('-topic_number').first()

    context = {
        'topic': topic,
        'next_topic': next_topic,
        'prev_topic': prev_topic,
        'page_title': f"Topic {topic.topic_number}: {topic.title}",
    }
    return render(request, 'learning/topic_detail.html', context)
