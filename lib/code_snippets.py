from typing import Dict

from todos.models import CodeSnippet


def get_navigation_objects(snippet: CodeSnippet) -> Dict[str, CodeSnippet]:
    prev = CodeSnippet.objects.filter(position__lt=snippet.position).order_by('-position').first()
    _next = CodeSnippet.objects.filter(position__gt=snippet.position).order_by('position').first()
    return {
        'prev': prev.pk if prev else None,
        'next': _next.pk if _next else None
    }
