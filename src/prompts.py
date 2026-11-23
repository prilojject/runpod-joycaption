"""Official JoyCaption prompt templates and Extra Options.

Copied verbatim from fpgaminer/joycaption (gradio-app/app.py and the
root README "How to Prompt JoyCaption" section) at SHA
8445b2e55db7856d522e44ae84e7415fcf3413f6.

Copyright 2024 fpgaminer@bitcoin-mining.com
Licensed under the Apache License, Version 2.0 (see LICENSE.upstream).
Do not invent or "improve" these strings. The default formal-long prompt
used by this worker when no extras are set comes from the official
README example usage (also on that SHA).
"""

from __future__ import annotations

# Official default example (README "Example Usage" / worker default).
DEFAULT_PROMPT = "Write a long descriptive caption for this image in a formal tone."

CAPTION_TYPE_MAP = {
	"Descriptive": [
		"Write a detailed description for this image.",
		"Write a detailed description for this image in {word_count} words or less.",
		"Write a {length} detailed description for this image.",
	],
	"Descriptive (Casual)": [
		"Write a descriptive caption for this image in a casual tone.",
		"Write a descriptive caption for this image in a casual tone within {word_count} words.",
		"Write a {length} descriptive caption for this image in a casual tone.",
	],
	"Straightforward": [
		"Write a straightforward caption for this image. Begin with the main subject and medium. Mention pivotal elements—people, objects, scenery—using confident, definite language. Focus on concrete details like color, shape, texture, and spatial relationships. Show how elements interact. Omit mood and speculative wording. If text is present, quote it exactly. Note any watermarks, signatures, or compression artifacts. Never mention what's absent, resolution, or unobservable details. Vary your sentence structure and keep the description concise, without starting with “This image is…” or similar phrasing.",
		"Write a straightforward caption for this image within {word_count} words. Begin with the main subject and medium. Mention pivotal elements—people, objects, scenery—using confident, definite language. Focus on concrete details like color, shape, texture, and spatial relationships. Show how elements interact. Omit mood and speculative wording. If text is present, quote it exactly. Note any watermarks, signatures, or compression artifacts. Never mention what's absent, resolution, or unobservable details. Vary your sentence structure and keep the description concise, without starting with “This image is…” or similar phrasing.",
		"Write a {length} straightforward caption for this image. Begin with the main subject and medium. Mention pivotal elements—people, objects, scenery—using confident, definite language. Focus on concrete details like color, shape, texture, and spatial relationships. Show how elements interact. Omit mood and speculative wording. If text is present, quote it exactly. Note any watermarks, signatures, or compression artifacts. Never mention what's absent, resolution, or unobservable details. Vary your sentence structure and keep the description concise, without starting with “This image is…” or similar phrasing.",
	],
	"Stable Diffusion Prompt": [
		"Output a stable diffusion prompt that is indistinguishable from a real stable diffusion prompt.",
		"Output a stable diffusion prompt that is indistinguishable from a real stable diffusion prompt. {word_count} words or less.",
		"Output a {length} stable diffusion prompt that is indistinguishable from a real stable diffusion prompt.",
	],
	"MidJourney": [
		"Write a MidJourney prompt for this image.",
		"Write a MidJourney prompt for this image within {word_count} words.",
		"Write a {length} MidJourney prompt for this image.",
	],
	"Danbooru tag list": [
		"Generate only comma-separated Danbooru tags (lowercase_underscores). Strict order: `artist:`, `copyright:`, `character:`, `meta:`, then general tags. Include counts (1girl), appearance, clothing, accessories, pose, expression, actions, background. Use precise Danbooru syntax. No extra text.",
		"Generate only comma-separated Danbooru tags (lowercase_underscores). Strict order: `artist:`, `copyright:`, `character:`, `meta:`, then general tags. Include counts (1girl), appearance, clothing, accessories, pose, expression, actions, background. Use precise Danbooru syntax. No extra text. {word_count} words or less.",
		"Generate only comma-separated Danbooru tags (lowercase_underscores). Strict order: `artist:`, `copyright:`, `character:`, `meta:`, then general tags. Include counts (1girl), appearance, clothing, accessories, pose, expression, actions, background. Use precise Danbooru syntax. No extra text. {length} length.",
	],
	"e621 tag list": [
		"Write a comma-separated list of e621 tags in alphabetical order for this image. Start with the artist, copyright, character, species, meta, and lore tags (if any), prefixed by 'artist:', 'copyright:', 'character:', 'species:', 'meta:', and 'lore:'. Then all the general tags.",
		"Write a comma-separated list of e621 tags in alphabetical order for this image. Start with the artist, copyright, character, species, meta, and lore tags (if any), prefixed by 'artist:', 'copyright:', 'character:', 'species:', 'meta:', and 'lore:'. Then all the general tags. Keep it under {word_count} words.",
		"Write a {length} comma-separated list of e621 tags in alphabetical order for this image. Start with the artist, copyright, character, species, meta, and lore tags (if any), prefixed by 'artist:', 'copyright:', 'character:', 'species:', 'meta:', and 'lore:'. Then all the general tags.",
	],
	"Rule34 tag list": [
		"Write a comma-separated list of rule34 tags in alphabetical order for this image. Start with the artist, copyright, character, and meta tags (if any), prefixed by 'artist:', 'copyright:', 'character:', and 'meta:'. Then all the general tags.",
		"Write a comma-separated list of rule34 tags in alphabetical order for this image. Start with the artist, copyright, character, and meta tags (if any), prefixed by 'artist:', 'copyright:', 'character:', and 'meta:'. Then all the general tags. Keep it under {word_count} words.",
		"Write a {length} comma-separated list of rule34 tags in alphabetical order for this image. Start with the artist, copyright, character, and meta tags (if any), prefixed by 'artist:', 'copyright:', 'character:', and 'meta:'. Then all the general tags.",
	],
	"Booru-like tag list": [
		"Write a list of Booru-like tags for this image.",
		"Write a list of Booru-like tags for this image within {word_count} words.",
		"Write a {length} list of Booru-like tags for this image.",
	],
	"Art Critic": [
		"Analyze this image like an art critic would with information about its composition, style, symbolism, the use of color, light, any artistic movement it might belong to, etc.",
		"Analyze this image like an art critic would with information about its composition, style, symbolism, the use of color, light, any artistic movement it might belong to, etc. Keep it within {word_count} words.",
		"Analyze this image like an art critic would with information about its composition, style, symbolism, the use of color, light, any artistic movement it might belong to, etc. Keep it {length}.",
	],
	"Product Listing": [
		"Write a caption for this image as though it were a product listing.",
		"Write a caption for this image as though it were a product listing. Keep it under {word_count} words.",
		"Write a {length} caption for this image as though it were a product listing.",
	],
	"Social Media Post": [
		"Write a caption for this image as if it were being used for a social media post.",
		"Write a caption for this image as if it were being used for a social media post. Limit the caption to {word_count} words.",
		"Write a {length} caption for this image as if it were being used for a social media post.",
	],
}

NAME_OPTION = "If there is a person/character in the image you must refer to them as {name}."

EXTRA_OPTIONS: list[str] = [
    'If there is a person/character in the image you must refer to them as {name}.',
    'Do NOT include information about people/characters that cannot be changed (like ethnicity, gender, etc), but do still include changeable attributes (like hair style).',
    'Include information about lighting.',
    'Include information about camera angle.',
    'Include information about whether there is a watermark or not.',
    'Include information about whether there are JPEG artifacts or not.',
    'If it is a photo you MUST include information about what camera was likely used and details such as aperture, shutter speed, ISO, etc.',
    'Do NOT include anything sexual; keep it PG.',
    "Do NOT mention the image's resolution.",
    'You MUST include information about the subjective aesthetic quality of the image from low to very high.',
    "Include information on the image's composition style, such as leading lines, rule of thirds, or symmetry.",
    'Do NOT mention any text that is in the image.',
    'Specify the depth of field and whether the background is in focus or blurred.',
    'If applicable, mention the likely use of artificial or natural lighting sources.',
    'Do NOT use any ambiguous language.',
    'Include whether the image is sfw, suggestive, or nsfw.',
    'ONLY describe the most important elements of the image.',
    "If it is a work of art, do not include the artist's name or the title of the work.",
    'Identify the image orientation (portrait, landscape, or square) and aspect ratio if obvious.',
    'Use vulgar slang and profanity, such as (but not limited to) "fucking," "slut," "cock," etc.',
    'Do NOT use polite euphemisms—lean into blunt, casual phrasing.',
    'Include information about the ages of any people/characters when applicable.',
    'Mention whether the image depicts an extreme close-up, close-up, medium close-up, medium shot, cowboy shot, medium wide shot, wide shot, or extreme wide shot.',
    'Do not mention the mood/feeling/etc of the image.',
    'Explicitly specify the vantage height (eye-level, low-angle worm’s-eye, bird’s-eye, drone, rooftop, etc.).',
    'If there is a watermark, you must mention it.',
    'Your response will be used by a text-to-image model, so avoid useless meta phrases like “This image shows…”, "You are looking at...", etc.',
]

EXTRA_OPTIONS_SET = set(EXTRA_OPTIONS)

# Job `mode` values (lowercase) plus tone=casual for Descriptive.
MODE_TO_CAPTION_TYPE = {
    "descriptive": "Descriptive",
    "straightforward": "Straightforward",
    "sd_prompt": "Stable Diffusion Prompt",
    "stable_diffusion": "Stable Diffusion Prompt",
    "stable diffusion": "Stable Diffusion Prompt",
    "stable diffusion prompt": "Stable Diffusion Prompt",
    "midjourney": "MidJourney",
    "mid_journey": "MidJourney",
    "danbooru": "Danbooru tag list",
    "danbooru tag list": "Danbooru tag list",
    "e621": "e621 tag list",
    "e621 tag list": "e621 tag list",
    "rule34": "Rule34 tag list",
    "rule34 tag list": "Rule34 tag list",
    "booru": "Booru-like tag list",
    "booru-like": "Booru-like tag list",
    "booru-like tag list": "Booru-like tag list",
    "art_critic": "Art Critic",
    "art critic": "Art Critic",
    "product": "Product Listing",
    "product_listing": "Product Listing",
    "product listing": "Product Listing",
    "social": "Social Media Post",
    "social_media": "Social Media Post",
    "social media": "Social Media Post",
    "social media post": "Social Media Post",
}

# Official caption_length dropdown values, plus the worker's shorter aliases.
LENGTH_ALIASES = {
    "medium": "medium-length",
    "word_count": None,  # replaced by a numeric word_count
}

OFFICIAL_LENGTHS = {
    "any", "very short", "short", "medium-length", "long", "very long",
}

# Short slugs for Extra Options so jobs can pass names instead of the full sentence.
# Values are the official strings; unknown slugs are rejected.
EXTRA_OPTION_SLUGS: dict[str, str] = {
    'refer_to_name': 'If there is a person/character in the image you must refer to them as {name}.',
    'exclude_unchanging_personal_attributes': 'Do NOT include information about people/characters that cannot be changed (like ethnicity, gender, etc), but do still include changeable attributes (like hair style).',
    'lighting': 'Include information about lighting.',
    'camera_angle': 'Include information about camera angle.',
    'watermark': 'Include information about whether there is a watermark or not.',
    'jpeg_artifacts': 'Include information about whether there are JPEG artifacts or not.',
    'camera_metadata': 'If it is a photo you MUST include information about what camera was likely used and details such as aperture, shutter speed, ISO, etc.',
    'keep_pg': 'Do NOT include anything sexual; keep it PG.',
    'no_resolution': "Do NOT mention the image's resolution.",
    'aesthetic': 'You MUST include information about the subjective aesthetic quality of the image from low to very high.',
    'composition': "Include information on the image's composition style, such as leading lines, rule of thirds, or symmetry.",
    'no_text': 'Do NOT mention any text that is in the image.',
    'depth_of_field': 'Specify the depth of field and whether the background is in focus or blurred.',
    'lighting_sources': 'If applicable, mention the likely use of artificial or natural lighting sources.',
    'no_ambiguous_language': 'Do NOT use any ambiguous language.',
    'sfw_rating': 'Include whether the image is sfw, suggestive, or nsfw.',
    'important_elements_only': 'ONLY describe the most important elements of the image.',
    'no_artist_title': "If it is a work of art, do not include the artist's name or the title of the work.",
    'orientation': 'Identify the image orientation (portrait, landscape, or square) and aspect ratio if obvious.',
    'vulgar_slang': 'Use vulgar slang and profanity, such as (but not limited to) "fucking," "slut," "cock," etc.',
    'no_euphemisms': 'Do NOT use polite euphemisms—lean into blunt, casual phrasing.',
    'ages': 'Include information about the ages of any people/characters when applicable.',
    'shot_type': 'Mention whether the image depicts an extreme close-up, close-up, medium close-up, medium shot, cowboy shot, medium wide shot, wide shot, or extreme wide shot.',
    'no_mood': 'Do not mention the mood/feeling/etc of the image.',
    'vantage_height': 'Explicitly specify the vantage height (eye-level, low-angle worm’s-eye, bird’s-eye, drone, rooftop, etc.).',
    'mention_watermark': 'If there is a watermark, you must mention it.',
    'no_meta_phrases': 'Your response will be used by a text-to-image model, so avoid useless meta phrases like “This image shows…”, "You are looking at...", etc.',
}


def normalize_mode(mode: str, tone: str) -> str:
    """Return an official CAPTION_TYPE_MAP key."""
    key = (mode or "descriptive").strip().lower()
    # Allow passing the official UI names directly.
    for official in CAPTION_TYPE_MAP:
        if key == official.lower():
            if official == "Descriptive" and (tone or "formal").strip().lower() == "casual":
                return "Descriptive (Casual)"
            return official
    if key not in MODE_TO_CAPTION_TYPE:
        raise ValueError(
            f"mode: unknown value {mode!r}. Use descriptive, straightforward, "
            "or an official caption type name from the JoyCaption README."
        )
    official = MODE_TO_CAPTION_TYPE[key]
    if official == "Descriptive" and (tone or "formal").strip().lower() == "casual":
        return "Descriptive (Casual)"
    return official


def normalize_length(length: str | int | None, word_count: int | None = None) -> str | int:
    if word_count is not None and word_count > 0:
        return int(word_count)
    if length is None or length == "":
        return "long"
    if isinstance(length, int):
        return length
    raw = str(length).strip()
    if raw.isdigit():
        return int(raw)
    low = raw.lower().replace("_", "-")
    if low in LENGTH_ALIASES and LENGTH_ALIASES[low] is not None:
        return LENGTH_ALIASES[low]
    if low in OFFICIAL_LENGTHS:
        return low
    # accept "medium length"
    if low.replace(" ", "-") in OFFICIAL_LENGTHS:
        return low.replace(" ", "-")
    raise ValueError(
        f"length: expected any/very short/short/medium/long/very long or a word count, got {length!r}"
    )


def resolve_extra_options(items: list[str] | None) -> list[str]:
    """Map slugs or official phrases onto the official Extra Options strings."""
    if not items:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for raw in items:
        if not isinstance(raw, str) or not raw.strip():
            raise ValueError(f"extra_options: expected a non-empty string, got {raw!r}")
        text = raw.strip()
        if text in EXTRA_OPTIONS_SET:
            official = text
        elif text in EXTRA_OPTION_SLUGS:
            official = EXTRA_OPTION_SLUGS[text]
        else:
            # case-insensitive official match
            lowered = {s.lower(): s for s in EXTRA_OPTIONS}
            if text.lower() in lowered:
                official = lowered[text.lower()]
            else:
                raise ValueError(
                    "extra_options: unknown option "
                    f"{text!r}. Pass an official Extra Options sentence from the "
                    "JoyCaption README, or a documented slug such as 'lighting'."
                )
        if official not in seen:
            out.append(official)
            seen.add(official)
    return out


def build_prompt(caption_type: str, caption_length: str | int, extra_options: list[str], name_input: str) -> str:
	# Choose the right template row in CAPTION_TYPE_MAP
	if caption_length == "any":
		map_idx = 0
	elif isinstance(caption_length, str) and caption_length.isdigit():
		map_idx = 1  # numeric-word-count template
	else:
		map_idx = 2  # length descriptor template
	
	prompt = CAPTION_TYPE_MAP[caption_type][map_idx]

	if extra_options:
		prompt += " " + " ".join(extra_options)
	
	return prompt.format(
		name=name_input or "{NAME}",
		length=caption_length,
		word_count=caption_length,
	)


def assemble_prompt(
    mode: str = "descriptive",
    tone: str = "formal",
    length: str | int = "long",
    extra_options: list[str] | None = None,
    name: str = "",
    custom_prompt: str | None = None,
    word_count: int | None = None,
) -> tuple[str, list[str]]:
    """Build the prompt sent to official batch-caption.py.

    Returns (prompt, warnings). A custom prompt replaces the mode template
    and adds a warning that Beta One is not a general instruction follower.
    The default descriptive / formal / long combination with no extras uses
    the official README example prompt.
    """
    warnings: list[str] = []
    if custom_prompt and custom_prompt.strip():
        warnings.append(
            "custom prompt overrides mode/tone/length; Beta One is not a general instruction follower"
        )
        prompt = custom_prompt.strip()
        extras = resolve_extra_options(extra_options)
        if extras:
            prompt = prompt + " " + " ".join(extras)
            if name and "{name}" in " ".join(extras):
                prompt = prompt.format(name=name)
        return prompt, warnings

    caption_type = normalize_mode(mode, tone)
    caption_length = normalize_length(length, word_count)
    # Official build_prompt only treats a digit *string* as a word-count template
    # (the Gradio dropdown stores numbers as strings). Pass ints the same way.
    if isinstance(caption_length, int):
        caption_length = str(caption_length)
    extras = resolve_extra_options(extra_options)

    # Official README example is the worker default (not the CAPTION_TYPE_MAP
    # formal-long template, which says "detailed description").
    if (
        caption_type == "Descriptive"
        and caption_length == "long"
        and not extras
    ):
        return DEFAULT_PROMPT, warnings

    prompt = build_prompt(caption_type, caption_length, extras, name or "")
    return prompt, warnings
