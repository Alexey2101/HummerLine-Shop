import os
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def icon(name, className="", id="", aria_hidden="true"):
    icon_path = os.path.join(settings.BASE_DIR, 'static', 'svg', 'icons', f"{name}.svg")
    
    if not os.path.exists(icon_path):
        return mark_safe(f"<!-- Icon {name} not found -->")
        
    with open(icon_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()
    
    # Inject attributes into the <svg> tag
    attrs = []
    full_class = f"icon-svg {className}".strip()
    if full_class: attrs.append(f'class="{full_class}"')
    if id: attrs.append(f'id="{id}"')
    if aria_hidden: attrs.append(f'aria-hidden="{aria_hidden}"')
    attrs.append(f'data-icon-name="{name}"')
    
    if attrs:
        import re
        # Find the opening <svg> tag
        match = re.search(r'<svg[^>]*>', svg_content)
        if match:
            svg_tag = match.group(0)
            new_svg_tag = svg_tag
            
            for attr in attrs:
                # attr is in format 'name="value"'
                name_match = re.match(r'([a-zA-Z0-9_-]+)="', attr)
                if name_match:
                    attr_name = name_match.group(1)
                    # Extract value correctly even if it contains quotes (though unlikely here)
                    attr_value = attr[len(attr_name)+2:-1]
                    
                    # Helper to inject or replace attribute within the tag
                    pattern = rf'{attr_name}="[^"]*"'
                    if re.search(pattern, new_svg_tag):
                        new_svg_tag = re.sub(pattern, f'{attr_name}="{attr_value}"', new_svg_tag)
                    else:
                        new_svg_tag = new_svg_tag.replace('<svg', f'<svg {attr_name}="{attr_value}"')
            
            svg_content = svg_content.replace(svg_tag, new_svg_tag, 1)
        
    return mark_safe(svg_content)
