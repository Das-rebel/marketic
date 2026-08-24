"""
Design Templates — Platform-specific visual content templates.
"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class Platform(str, Enum):
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"


@dataclass
class BrandTokens:
    """
    Brand-as-data: the entire visual identity as configuration, not code.
    Templates reference tokens ({{brand.primary}}); any brand renders correctly.
    Load from brand_memory or a brand kit file — never hardcode in templates.
    """
    name: str = "Brand"
    tagline: str = ""
    handle: str = "@brand"
    primary_color: str = "#1A1A1A"      # {{brand.primary}}
    background_color: str = "#FFFFFF"   # {{brand.background}}
    accent_color: str = "#FF6600"       # {{brand.accent}}
    secondary_color: str = "#008000"    # {{brand.secondary}}
    font_primary: str = "Helvetica"     # {{brand.font}}

    def to_substitution_map(self) -> Dict[str, str]:
        return {
            "{{brand.primary}}": self.primary_color,
            "{{brand.background}}": self.background_color,
            "{{brand.accent}}": self.accent_color,
            "{{brand.secondary}}": self.secondary_color,
            "{{brand.font}}": self.font_primary,
            "{{brand.handle}}": self.handle,
            "{{brand.name}}": self.name.upper(),
            "{{brand.tagline}}": self.tagline.upper(),
        }

    @classmethod
    def from_image(cls, image_url: str, brand_name: str = "", api_key: str = None) -> "BrandTokens":
        """
        Bootstrap tokens from one reference image (screenshot/logo/post).
        Vault-sourced: @EXM7777 style-cloning - vision model extracts the
        style descriptor; we map it onto tokens.
        Falls back to defaults when no vision API is configured.
        """
        import base64 as _b64
        key = api_key or os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if not key:
            return cls(name=brand_name or "Brand")

        prompt = (
            'Extract this brand\'s visual identity as strict JSON only: '
            '{"primary_color": "#hex", "background_color": "#hex", '
            '"accent_color": "#hex", "secondary_color": "#hex", '
            '"font_primary": "closest common font name", "tagline": "any visible tagline"}'
        )
        try:
            import httpx
            headers = {"Authorization": f"Bearer {key}"}
            content: Any = [{"type": "text", "text": prompt}]
            if image_url.startswith("http"):
                content.append({"type": "image_url", "image_url": {"url": image_url}})
            else:  # local file -> base64 data URL
                with open(image_url, "rb") as f:
                    b64 = _b64.b64encode(f.read()).decode()
                content.append({"type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{b64}"}})

            base = ("https://openrouter.ai/api/v1" if key.startswith("sk-or-")
                    else "https://api.openai.com/v1")
            resp = httpx.post(
                f"{base}/chat/completions",
                headers=headers,
                json={"model": "openai/gpt-4o-mini" if key.startswith("sk-or-") else "gpt-4o-mini",
                      "messages": [{"role": "user", "content": content}], "max_tokens": 300},
                timeout=60.0,
            )
            if resp.status_code == 200:
                text = resp.json()["choices"][0]["message"]["content"]
                text = text[text.find("{"): text.rfind("}") + 1]
                data = json.loads(text)
                return cls(
                    name=brand_name or "Brand",
                    tagline=data.get("tagline", ""),
                    primary_color=data.get("primary_color", cls.primary_color),
                    background_color=data.get("background_color", cls.background_color),
                    accent_color=data.get("accent_color", cls.accent_color),
                    secondary_color=data.get("secondary_color", cls.secondary_color),
                    font_primary=data.get("font_primary", cls.font_primary),
                )
        except Exception as e:
            print(f"[BrandTokens.from_image] extraction failed: {e}")
        return cls(name=brand_name or "Brand")

    @classmethod
    def from_brand_memory(cls, brand_record: Dict[str, Any]) -> "BrandTokens":
        """Load tokens from the brand_memory store."""
        return cls(
            name=brand_record.get("name", "Brand"),
            tagline=brand_record.get("tagline", ""),
            handle=brand_record.get("handle", "@brand"),
            primary_color=brand_record.get("primary_color", "#1A1A1A"),
            background_color=brand_record.get("background_color", "#FFFFFF"),
            accent_color=brand_record.get("accent_color", "#FF6600"),
            secondary_color=brand_record.get("secondary_color", "#008000"),
            font_primary=brand_record.get("font_primary", "Helvetica"),
        )


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
    """Brand-agnostic design templates. Render against BrandTokens."""

    def __init__(self, tokens: Optional[BrandTokens] = None):
        self.tokens = tokens or BrandTokens()
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
                    content="linear-gradient(transparent, {{brand.background}})",
                    position={"x": 0, "y": 540, "width": 1080, "height": 540},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[LABEL]",
                    font="{{brand.font}}",
                    font_size=11,
                    color="{{brand.accent}}",
                    tracking=0.15,
                    position={"x": 40, "y": 700},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[TITLE]",
                    font="{{brand.font}}",
                    font_size=56,
                    color="{{brand.primary}}",
                    tracking=-0.05,
                    position={"x": 40, "y": 750},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[DESCRIPTION]",
                    font="{{brand.font}}",
                    font_size=16,
                    color="{{brand.primary}}",
                    opacity=0.6,
                    position={"x": 40, "y": 830},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[BRAND_NAME]",
                    font="{{brand.font}}",
                    font_size=14,
                    color="{{brand.primary}}",
                    position={"x": 40, "y": 1000},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="{{brand.handle}}",
                    font="{{brand.font}}",
                    font_size=14,
                    color="{{brand.primary}}",
                    position={"x": 860, "y": 1000},
                ),
            ],
            background_color="{{brand.background}}",
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
                    font="{{brand.font}}",
                    font_size=11,
                    color="{{brand.accent}}",
                    tracking=0.15,
                    position={"x": 40, "y": 650},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[HEADLINE]",
                    font="{{brand.font}}",
                    font_size=64,
                    color="{{brand.background}}",
                    position={"x": 40, "y": 720},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[SUBTEXT]",
                    font="{{brand.font}}",
                    font_size=14,
                    color="{{brand.background}}",
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
                    content="{{brand.background}}",
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[DATE]",
                    font="{{brand.font}}",
                    font_size=14,
                    color="{{brand.accent}}",
                    position={"x": 40, "y": 100},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[TIME]",
                    font="{{brand.font}}",
                    font_size=14,
                    color="{{brand.primary}}",
                    position={"x": 800, "y": 100},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[EVENT NAME]",
                    font="{{brand.font}}",
                    font_size=96,
                    color="{{brand.primary}}",
                    line_height=0.9,
                    position={"x": 40, "y": 200},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[DESCRIPTION]",
                    font="{{brand.font}}",
                    font_size=16,
                    color="{{brand.primary}}",
                    opacity=0.6,
                    position={"x": 40, "y": 700},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[PRICE]",
                    font="{{brand.font}}",
                    font_size=14,
                    color="{{brand.secondary}}",
                    position={"x": 40, "y": 800},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[BRAND_NAME]",
                    font="{{brand.font}}",
                    font_size=14,
                    color="{{brand.primary}}",
                    position={"x": 40, "y": 950},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[TAGLINE]",
                    font="{{brand.font}}",
                    font_size=14,
                    color="{{brand.primary}}",
                    position={"x": 800, "y": 950},
                ),
            ],
            background_color="{{brand.background}}",
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
                    font="{{brand.font}}",
                    font_size=12,
                    color="{{brand.accent}}",
                    position={"x": 0, "y": 1300, "width": 1080, "align": "center"},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[TITLE]",
                    font="{{brand.font}}",
                    font_size=72,
                    color="{{brand.background}}",
                    position={"x": 0, "y": 1400, "width": 1080, "align": "center"},
                ),
                TemplateLayer(
                    layer_type="divider",
                    content="{{brand.accent}}",
                    position={"x": 490, "y": 1520, "width": 60, "height": 2},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[DESCRIPTION]",
                    font="{{brand.font}}",
                    font_size=16,
                    color="{{brand.background}}",
                    opacity=0.7,
                    position={"x": 0, "y": 1580, "width": 1080, "align": "center"},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[PRICE]",
                    font="{{brand.font}}",
                    font_size=28,
                    color="{{brand.accent}}",
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
                    content="{{brand.background}}",
                ),
                TemplateLayer(
                    layer_type="image",
                    content="[CUSTOMER_PHOTO]",
                    position={"x": 0, "y": 0, "width": 1080, "height": 810},
                ),
                TemplateLayer(
                    layer_type="gradient",
                    content="linear-gradient(transparent, {{brand.background}})",
                    position={"x": 0, "y": 680, "width": 1080, "height": 400},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="SHARED BY @[USERNAME]",
                    font="{{brand.font}}",
                    font_size=11,
                    color="{{brand.accent}}",
                    tracking=0.15,
                    position={"x": 40, "y": 820},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[CAPTION]",
                    font="{{brand.font}}",
                    font_size=14,
                    color="{{brand.primary}}",
                    opacity=0.6,
                    position={"x": 40, "y": 870},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[BRAND_NAME]",
                    font="{{brand.font}}",
                    font_size=11,
                    color="{{brand.primary}}",
                    position={"x": 40, "y": 1000},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="#PARADISEWITHFANGS",
                    font="{{brand.font}}",
                    font_size=11,
                    color="{{brand.primary}}",
                    position={"x": 760, "y": 1000},
                ),
            ],
            background_color="{{brand.background}}",
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
                    content="{{brand.background}}",
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[HEADLINE]",
                    font="{{brand.font}}",
                    font_size=32,
                    color="{{brand.primary}}",
                    position={"x": 60, "y": 200},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[BODY]",
                    font="{{brand.font}}",
                    font_size=18,
                    color="{{brand.primary}}",
                    opacity=0.8,
                    position={"x": 60, "y": 320},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[CTA]",
                    font="{{brand.font}}",
                    font_size=16,
                    color="{{brand.accent}}",
                    position={"x": 60, "y": 480},
                ),
            ],
            background_color="{{brand.background}}",
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
                    content="{{brand.background}}",
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[COMPANY LOGO]",
                    position={"x": 60, "y": 60},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[HEADLINE]",
                    font="{{brand.font}}",
                    font_size=28,
                    color="{{brand.primary}}",
                    position={"x": 60, "y": 140},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[BODY]",
                    font="{{brand.font}}",
                    font_size=16,
                    color="{{brand.primary}}",
                    opacity=0.85,
                    position={"x": 60, "y": 220},
                ),
                TemplateLayer(
                    layer_type="text",
                    content="[HASHTAGS]",
                    font="{{brand.font}}",
                    font_size=12,
                    color="{{brand.accent}}",
                    position={"x": 60, "y": 540},
                ),
            ],
            background_color="{{brand.background}}",
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

        # Resolve brand tokens + placeholders
        substitutions = self.tokens.to_substitution_map()
        substitutions.update({f"[{k}]": v for k, v in placeholders.items()})

        def resolve(text: str) -> str:
            for key, value in substitutions.items():
                text = text.replace(key, value)
            return text

        rendered = {
            "template_id": template.template_id,
            "name": template.name,
            "platform": template.platform.value,
            "dimensions": template.dimensions,
            "layers": [],
            "background_color": template.background_color,
        }

        for layer in template.layers:
            content = resolve(layer.content)

            # Handle photo placeholder
            if content in ("[PHOTO]", "[CUSTOMER_PHOTO]") and photo_path:
                content = photo_path

            rendered_layer = {
                "type": layer.layer_type,
                "content": content,
            }

            if layer.font:
                rendered_layer["font"] = resolve(layer.font)
            if layer.font_size:
                rendered_layer["font_size"] = layer.font_size
            if layer.color:
                rendered_layer["color"] = resolve(layer.color)
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
        bg = rendered.get("background_color", "{{brand.background}}")

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
