"""
Design Templates — Platform-specific visual content templates.
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class Platform(str, Enum):
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"


class TemplateType(str, Enum):
    STATIC_POST = "static_post"
    STORY = "story"
    REEL = "reel"
    CAROUSEL = "carousel"
    EVENT_POSTER = "event_poster"
    MENU_HIGHLIGHT = "menu_highlight"
    VIBE_POST = "vibe_post"
    UGC_REPOST = "ugc_repost"


@dataclass
class TemplateLayer:
    """A single layer in a design template."""
    layer_type: str  # text, image, background, gradient
    content: str
    font: Optional[str] = None
    font_size: Optional[int] = None
    color: Optional[str] = None
    position: Optional[Dict[str, int]] = None  # x, y, width, height
    opacity: Optional[float] = None
    tracking: Optional[float] = None  # letter-spacing
    line_height: Optional[float] = None


@dataclass
class DesignTemplate:
    """A complete design template."""
    template_id: str
    name: str
    platform: Platform
    template_type: TemplateType
    dimensions: Dict[str, int]  # width, height
    layers: List[TemplateLayer]
    background_color: Optional[str] = None
    background_image: Optional[str] = None
    gradient: Optional[Dict[str, Any]] = None
    brand_rules: Optional[Dict[str, Any]] = None


# Platform dimensions
PLATFORM_DIMENSIONS = {
    Platform.INSTAGRAM: {
        "post": {"width": 1080, "height": 1080},
        "story": {"width": 1080, "height": 1920},
        "reel": {"width": 1080, "height": 1920},
    },
    Platform.FACEBOOK: {
        "post": {"width": 1200, "height": 630},
        "story": {"width": 1080, "height": 1920},
    },
    Platform.TWITTER: {
        "post": {"width": 1200, "height": 675},
        "header": {"width": 1500, "height": 500},
    },
    Platform.LINKEDIN: {
        "post": {"width": 1200, "height": 627},
        "cover": {"width": 1584, "height": 396},
    },
    Platform.TIKTOK: {
        "video": {"width": 1080, "height": 1920},
        "cover": {"width": 1080, "height": 1920},
    },
}


class TemplateLibrary:
    """Pre-built design templates for marketing content."""

    def __init__(self):
        self.templates: Dict[str, DesignTemplate] = {}
        self._load_default_templates()

    def _load_default_templates(self):
        """Load default templates."""

        # Menu Highlight — Instagram Post
        self.templates["ig_menu_highlight"] = DesignTemplate(
            template_id="ig_menu_highlight",
            name="Menu Highlight",
            platform=Platform.INSTAGRAM,
            template_type=TemplateType.MENU_HIGHLIGHT,
            dimensions=PLATFORM_DIMENSIONS[Platform.INSTAGRAM]["post"],
            layers=[
                TemplateLayer(
                    layer_type="image",
                    content="[PHOTO]",  # Will be replaced with actual photo
                    position={"x": 0, "y": 0, "width": 1080, "height": 680},
                ),
                TemplateLayer(
                    layer_type="gradient",
                    content="linear-gradient(transparent, #F8F5EA)",
                    position={"x": 0, "y": 540, "width": 1080, "height": 540},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[LABEL]",
                    font="Kisrre",
                    font_size=11,
                    color="#E67E32",
                    tracking=0.15,
                    position={"x": 40, "y": 700},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[TITLE]",
                    font="Kisrre",
                    font_size=56,
                    color="#6D0000",
                    tracking=-0.05,
                    position={"x": 40, "y": 750},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[DESCRIPTION]",
                    font="Kisrre",
                    font_size=16,
                    color="#6D0000",
                    opacity=0.6,
                    position={"x": 40, "y": 830},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="BUKITO",
                    font="Kisrre",
                    font_size=14,
                    color="#6D0000",
                    position={"x": 40, "y": 1000},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="@BUKITO.SUMBAWA",
                    font="Kisrre",
                    font_size=14,
                    color="#6D0000",
                    position={"x": 860, "y": 1000},
                ),
            ],
            background_color="#F8F5EA",
        )

        # Vibe Post — Instagram Post
        self.templates["ig_vibe_post"] = DesignTemplate(
            template_id="ig_vibe_post",
            name="Vibe Post",
            platform=Platform.INSTAGRAM,
            template_type=TemplateType.VIBE_POST,
            dimensions=PLATFORM_DIMENSIONS[Platform.INSTAGRAM]["post"],
            layers=[
                TemplateLayer(
                    layer_type="background",
                    content="#1A1A1A",
                ),
                TemplateLayer(
                    layer_type="image",
                    content="[PHOTO]",
                    position={"x": 0, "y": 0, "width": 1080, "height": 1080},
                ),
                TemplateLayer(
                    layer_type="gradient",
                    content="linear-gradient(transparent, rgba(0,0,0,0.7))",
                    position={"x": 0, "y": 600, "width": 1080, "height": 480},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[LABEL]",
                    font="Kisrre",
                    font_size=11,
                    color="#E67E32",
                    tracking=0.15,
                    position={"x": 40, "y": 650},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[HEADLINE]",
                    font="Kisrre",
                    font_size=64,
                    color="#F8F5EA",
                    position={"x": 40, "y": 720},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[SUBTEXT]",
                    font="Kisrre",
                    font_size=14,
                    color="#F8F5EA",
                    opacity=0.6,
                    position={"x": 40, "y": 830},
                ),
            ],
        )

        # Event Poster — Instagram Post
        self.templates["ig_event_poster"] = DesignTemplate(
            template_id="ig_event_poster",
            name="Event Poster",
            platform=Platform.INSTAGRAM,
            template_type=TemplateType.EVENT_POSTER,
            dimensions=PLATFORM_DIMENSIONS[Platform.INSTAGRAM]["post"],
            layers=[
                TemplateLayer(
                    layer_type="background",
                    content="#F8F5EA",
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[DATE]",
                    font="Kisrre",
                    font_size=14,
                    color="#E67E32",
                    position={"x": 40, "y": 100},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[TIME]",
                    font="Kisrre",
                    font_size=14,
                    color="#6D0000",
                    position={"x": 800, "y": 100},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[EVENT NAME]",
                    font="Kisrre",
                    font_size=96,
                    color="#6D0000",
                    line_height=0.9,
                    position={"x": 40, "y": 200},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[DESCRIPTION]",
                    font="Kisrre",
                    font_size=16,
                    color="#6D0000",
                    opacity=0.6,
                    position={"x": 40, "y": 700},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[PRICE]",
                    font="Kisrre",
                    font_size=14,
                    color="#008134",
                    position={"x": 40, "y": 800},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="BUKITO",
                    font="Kisrre",
                    font_size=14,
                    color="#6D0000",
                    position={"x": 40, "y": 950},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="PARADISE WITH FANGS",
                    font="Kisrre",
                    font_size=14,
                    color="#6D0000",
                    position={"x": 800, "y": 950},
                ),
            ],
            background_color="#F8F5EA",
        )

        # Story — Weekly Special
        self.templates["ig_story_weekly"] = DesignTemplate(
            template_id="ig_story_weekly",
            name="Weekly Special Story",
            platform=Platform.INSTAGRAM,
            template_type=TemplateType.STORY,
            dimensions=PLATFORM_DIMENSIONS[Platform.INSTAGRAM]["story"],
            layers=[
                TemplateLayer(
                    layer_type="background",
                    content="#000000",
                ),
                TemplateLayer(
                    layer_type="image",
                    content="[PHOTO]",
                    position={"x": 0, "y": 0, "width": 1080, "height": 1920},
                ),
                TemplateLayer(
                    layer_type="gradient",
                    content="linear-gradient(transparent, #000000)",
                    position={"x": 0, "y": 1200, "width": 1080, "height": 720},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[LABEL]",
                    font="Kisrre",
                    font_size=12,
                    color="#E67E32",
                    position={"x": 0, "y": 1300, "width": 1080, "align": "center"},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[TITLE]",
                    font="Kisrre",
                    font_size=72,
                    color="#F8F5EA",
                    position={"x": 0, "y": 1400, "width": 1080, "align": "center"},
                ),
                TemplateLayer(
                    layer_type="divider",
                    content="#E67E32",
                    position={"x": 490, "y": 1520, "width": 60, "height": 2},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[DESCRIPTION]",
                    font="Kisrre",
                    font_size=16,
                    color="#F8F5EA",
                    opacity=0.7,
                    position={"x": 0, "y": 1580, "width": 1080, "align": "center"},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[PRICE]",
                    font="Kisrre",
                    font_size=28,
                    color="#E67E32",
                    position={"x": 0, "y": 1700, "width": 1080, "align": "center"},
                ),
            ],
        )

        # UGC Repost — Instagram Post
        self.templates["ig_ugc_repost"] = DesignTemplate(
            template_id="ig_ugc_repost",
            name="UGC Repost",
            platform=Platform.INSTAGRAM,
            template_type=TemplateType.UGC_REPOST,
            dimensions=PLATFORM_DIMENSIONS[Platform.INSTAGRAM]["post"],
            layers=[
                TemplateLayer(
                    layer_type="background",
                    content="#F8F5EA",
                ),
                TemplateLayer(
                    layer_type="image",
                    content="[CUSTOMER_PHOTO]",
                    position={"x": 0, "y": 0, "width": 1080, "height": 810},
                ),
                TemplateLayer(
                    layer_type="gradient",
                    content="linear-gradient(transparent, #F8F5EA)",
                    position={"x": 0, "y": 680, "width": 1080, "height": 400},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="SHARED BY @[USERNAME]",
                    font="Kisrre",
                    font_size=11,
                    color="#E67E32",
                    tracking=0.15,
                    position={"x": 40, "y": 820},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[CAPTION]",
                    font="Kisrre",
                    font_size=14,
                    color="#6D0000",
                    opacity=0.6,
                    position={"x": 40, "y": 870},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="BUKITO",
                    font="Kisrre",
                    font_size=11,
                    color="#6D0000",
                    position={"x": 40, "y": 1000},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="#PARADISEWITHFANGS",
                    font="Kisrre",
                    font_size=11,
                    color="#6D0000",
                    position={"x": 760, "y": 1000},
                ),
            ],
            background_color="#F8F5EA",
        )

        # Twitter Post
        self.templates["twitter_announcement"] = DesignTemplate(
            template_id="twitter_announcement",
            name="Brand Announcement",
            platform=Platform.TWITTER,
            template_type=TemplateType.STATIC_POST,
            dimensions=PLATFORM_DIMENSIONS[Platform.TWITTER]["post"],
            layers=[
                TemplateLayer(
                    layer_type="background",
                    content="#F8F5EA",
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[HEADLINE]",
                    font="Kisrre",
                    font_size=32,
                    color="#6D0000",
                    position={"x": 60, "y": 200},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[BODY]",
                    font="Kisrre",
                    font_size=18,
                    color="#6D0000",
                    opacity=0.8,
                    position={"x": 60, "y": 320},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[CTA]",
                    font="Kisrre",
                    font_size=16,
                    color="#E67E32",
                    position={"x": 60, "y": 480},
                ),
            ],
            background_color="#F8F5EA",
        )

        # LinkedIn Post
        self.templates["linkedin_thought_leadership"] = DesignTemplate(
            template_id="linkedin_thought_leadership",
            name="Thought Leadership",
            platform=Platform.LINKEDIN,
            template_type=TemplateType.STATIC_POST,
            dimensions=PLATFORM_DIMENSIONS[Platform.LINKEDIN]["post"],
            layers=[
                TemplateLayer(
                    layer_type="background",
                    content="#F8F5EA",
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[COMPANY LOGO]",
                    position={"x": 60, "y": 60},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[HEADLINE]",
                    font="Kisrre",
                    font_size=28,
                    color="#6D0000",
                    position={"x": 60, "y": 140},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[BODY]",
                    font="Kisrre",
                    font_size=16,
                    color="#6D0000",
                    opacity=0.85,
                    position={"x": 60, "y": 220},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[HASHTAGS]",
                    font="Kisrre",
                    font_size=12,
                    color="#E67E32",
                    position={"x": 60, "y": 540},
                ),
            ],
            background_color="#F8F5EA",
        )

    def get_template(self, template_id: str) -> Optional[DesignTemplate]:
        """Get a template by ID."""
        return self.templates.get(template_id)

    def get_templates_by_platform(self, platform: Platform) -> List[DesignTemplate]:
        """Get all templates for a platform."""
        return [t for t in self.templates.values() if t.platform == platform]

    def get_templates_by_type(self, template_type: TemplateType) -> List[DesignTemplate]:
        """Get all templates of a specific type."""
        return [t for t in self.templates.values() if t.template_type == template_type]

    def render_template(
        self,
        template_id: str,
        placeholders: Dict[str, str],
        photo_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Render a template with filled placeholders.
        Returns a dict with all layers and their resolved values.
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")

        rendered = {
            "template_id": template.template_id,
            "name": template.name,
            "platform": template.platform.value,
            "dimensions": template.dimensions,
            "layers": [],
            "background_color": template.background_color,
        }

        for layer in template.layers:
            content = layer.content

            # Replace placeholders
            for key, value in placeholders.items():
                placeholder = f"[{key}]"
                if placeholder in content:
                    content = content.replace(placeholder, value)

            # Handle photo placeholder
            if content == "[PHOTO]" and photo_path:
                content = photo_path
            elif content == "[CUSTOMER_PHOTO]" and photo_path:
                content = photo_path

            rendered_layer = {
                "type": layer.layer_type,
                "content": content,
            }

            if layer.font:
                rendered_layer["font"] = layer.font
            if layer.font_size:
                rendered_layer["font_size"] = layer.font_size
            if layer.color:
                rendered_layer["color"] = layer.color
            if layer.position:
                rendered_layer["position"] = layer.position
            if layer.opacity is not None:
                rendered_layer["opacity"] = layer.opacity

            rendered["layers"].append(rendered_layer)

        return rendered


class TemplateRenderer:
    """Renders templates to various formats."""

    def __init__(self):
        self.library = TemplateLibrary()

    def render_for_paper_mcp(
        self,
        template_id: str,
        placeholders: Dict[str, str],
        photo_path: Optional[str] = None,
    ) -> str:
        """
        Render template as Paper MCP script.
        Paper MCP is a design canvas tool.
        """
        rendered = self.library.render_template(template_id, placeholders, photo_path)

        # Generate Paper MCP script
        script_lines = [
            f"// Template: {rendered['name']}",
            f"// Platform: {rendered['platform']}",
            f"// Dimensions: {rendered['dimensions']['width']}x{rendered['dimensions']['height']}",
            "",
            f"canvas.setSize({rendered['dimensions']['width']}, {rendered['dimensions']['height']})",
            "",
        ]

        if rendered.get("background_color"):
            script_lines.append(f"canvas.setBackground('{rendered['background_color']}')")

        for i, layer in enumerate(rendered["layers"]):
            layer_id = f"layer_{i}"

            if layer["type"] == "background":
                script_lines.append(f"canvas.setBackground('{layer['content']}')")

            elif layer["type"] == "image":
                script_lines.append(f"const {layer_id} = canvas.addImage('{layer['content']}')")
                if layer.get("position"):
                    pos = layer["position"]
                    script_lines.append(f"{layer_id}.setPosition({pos['x']}, {pos['y']})")

            elif layer["type"] == "text":
                script_lines.append(f"const {layer_id} = canvas.addText('{layer['content']}', {{")
                if layer.get("font"):
                    script_lines.append(f"  fontFamily: '{layer['font']}',")
                if layer.get("font_size"):
                    script_lines.append(f"  fontSize: {layer['font_size']},")
                if layer.get("color"):
                    script_lines.append(f"  fill: '{layer['color']}',")
                if layer.get("tracking") is not None:
                    script_lines.append(f"  letterSpacing: {layer['tracking']},")
                if layer.get("position"):
                    pos = layer["position"]
                    script_lines.append(f"  x: {pos['x']}, y: {pos['y']},")
                script_lines.append("})")

            elif layer["type"] == "gradient":
                script_lines.append(f"// Gradient layer at y={layer.get('position', {}).get('y', 0)}")

        script_lines.append("")
        script_lines.append("canvas.render()")

        return "\n".join(script_lines)

    def render_for_cli(
        self,
        template_id: str,
        placeholders: Dict[str, str],
        photo_path: Optional[str] = None,
    ) -> str:
        """
        Render template as CLI command for imagemagick or similar.
        """
        rendered = self.library.render_template(template_id, placeholders, photo_path)

        commands = [
            f"# Template: {rendered['name']}",
            f"# Platform: {rendered['platform']}",
            "",
        ]

        dims = rendered["dimensions"]
        bg = rendered.get("background_color", "#F8F5EA")

        # Base image creation
        commands.append(f"# Create base image")
        commands.append(
            f"convert -size {dims['width']}x{dims['height']} xc:{bg} template.png"
        )

        for i, layer in enumerate(rendered["layers"]):
            if layer["type"] == "text":
                pos = layer.get("position", {"x": 0, "y": 0})
                font = layer.get("font", "Helvetica")
                size = layer.get("font_size", 24)
                color = layer.get("color", "#000000")

                commands.append(
                    f"convert template.png -font {font} -pointsize {size} "
                    f"-fill '{color}' -annotate +{pos['x']}+{pos['y']} "
                    f"'{layer['content']}' template.png"
                )

            elif layer["type"] == "image":
                commands.append(f"# Image layer: {layer['content']}")

        return "\n".join(commands)
