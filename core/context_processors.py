from . import settings

def simple_design(request):
    """Expose SIMPLE_DESIGN flag to templates."""
    return {
        'SIMPLE_DESIGN': getattr(settings, 'SIMPLE_DESIGN', False)
    }
