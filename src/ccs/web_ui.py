"""Presentation-focused three-tab NetOps console."""
from ccs.studio_styles import STYLE
from ccs.studio_markup import BODY
from ccs.studio_script import SCRIPT


def document() -> str:
    return '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>NetOps Studio</title><style>'+STYLE+'</style></head><body>'+BODY+'<script>'+SCRIPT+'</script></body></html>'