import logging
from enum import StrEnum

import click
import typed_settings as ts
from bs4 import BeautifulSoup
from sh import pandoc, xclip

xclip = xclip.bake("-selection", "clipboard")

logger = logging.getLogger()


class Format(StrEnum):
    html = "html"
    markdown = "markdown"
    rst = "rst"
    org = "org"


@ts.settings
class Settings:
    format: Format = Format.org
    debug: bool = False


@click.command()
@ts.click_options(Settings, "clip2x")
def main(settings: Settings):
    """Converts HTML in the clipboard to Org, Markdown or RST format"""
    if settings.debug:
        logger.setLevel(logging.DEBUG)
    logging.debug(f"Format: {settings.format}")
    logging.debug(f"Targets: {clip_targets()}")
    if "text/html" in clip_targets():
        try:
            html = clip_get_html()
            logging.debug(f"HTML: {html}")
        except Exception:
            logging.debug("Getting HTML failed")
            html = None
    else:
        html = None
    if html:
        if settings.format == Format.html:
            logging.debug("Outputing HTML format")
            print(html)
        else:
            html = html[:-1]  # remove ^@ at end of string
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup():
                for attribute in ["class", "id", "name", "style"]:
                    del tag[attribute]
            print(
                pandoc(
                    "--wrap=none",
                    "-f",
                    "html-native_divs-native_spans",
                    "-t",
                    settings.format,
                    _in=str(soup),
                )
            )
    else:
        print(clip_get_text())


def clip_targets():
    return xclip("-o", "-t", "TARGETS").split()


def clip_get_html():
    return xclip("-o", "-t", "text/html")


def clip_get_text():
    try:
        return xclip("-o", "-t", "UTF8_STRING")
    except Exception:
        pass
    return xclip("-o", "-t", "text/plain")
