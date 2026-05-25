"""
Different small and distinct helper functions
"""

import html
import html.parser
import re
from pathlib import Path

import i18n

HTML_BLOCK_LEVEL_ELEMENTS = {
    "p",
    "div",
    "ul",
    "ol",
    "li",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
}
REGEX_DETECT_TIMESTAMP = re.compile(r"\[\d\d:\d\d:\d\d\]")


def str_to_ms(time_str: str) -> int:
    """
    Convert a "hh:mm:ss" time string to milliseconds.

    Args:
        time_str (str): The time string in "hh:mm:ss" format.

    Returns:
        int: The time in milliseconds.

    Raises:
        ValueError: If the input time string is invalid.
        TypeError: If the input is not a string.
    """

    try:
        # See https://stackoverflow.com/a/6402859
        h, m, s = time_str.split(":")
        ret = (int(h) * 3600 + int(m) * 60 + int(s)) * 1000
    except ValueError as e:
        raise ValueError(
            "time string is invalid", i18n.t("err_invalid_time_string"), time_str
        ) from e
    except AttributeError as e:
        raise TypeError(
            "time string is not of type str",
            i18n.t("err_invalid_time_string"),
            type(time_str),
            time_str,
        ) from e

    return ret


def create_unique_filenames(path_inputs: [Path]) -> Path:
    """
    Creates a list of unique filenames from a list of input paths.

    This function takes a list of file paths and generates a list of unique
    filenames. It handles potential filename collisions by incrementing a counter
    and appending it to the filename until a unique name is found.

    Args:
        path_inputs (list of Path): A list of file paths.

    Returns:
        list of Path: A list of unique filenames.

    Raises:
        RuntimeError: If a unique filename cannot be found after multiple attempts.
    """

    ret = []

    for item in path_inputs:
        new = item

        # Increment possible file names.
        for i in range(1, 1000):
            # There are several possibilities, we need to catch:
            # 1. A file with the given name already exists.
            # 2. There is already such a named file in `ret`.
            if new in ret or new.exists():
                new = _build_inc_filename(item, i)
            else:
                ret.append(new)
                break

        # Check here whether a new filename was found and raise error if not.
        if len(ret) == 0 or new != ret[-1]:
            raise RuntimeError("could not find an unique filename", new)

    return ret


def _build_inc_filename(path_input: Path, inc: int) -> Path:
    """
    Builds a new path with filename increment.

    This function constructs a new path by taking an input path and a given
    increment as filename addition. The original path and suffix is preserved.

    Args:
        path_input (Path): The original path to build upon.
        inc (int): An integer used to create the incremented filename.

    Returns:
        A new path representing the updated file path.
    """

    path_output = path_input.parent / f"{path_input.stem}_{inc}{path_input.suffix}"
    return path_output


def ms_to_str(milliseconds: int, include_ms: bool = False) -> str:
    """
    Convert milliseconds to a formatted timestamp string in "HH:MM:SS" format.

    Args:
        milliseconds (float): The number of milliseconds to convert.
        include_ms (bool, optional): Whether to include milliseconds in the
        output ("HH:MM:SS.mmm"). Defaults to False.

    Returns:
        str: A formatted timestamp string.
    """

    if milliseconds > 86400000:
        raise ValueError("milliseconds are larger than 24 hours", milliseconds)
    if milliseconds < 0:
        raise ValueError("milliseconds smaller than zero", milliseconds)

    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    if include_ms:
        formatted += f".{milliseconds:03d}"

    return formatted


def _ms_to_webvtt(milliseconds: int) -> str:
    """
    Converts milliseconds to a WebVTT timestamp string (HH:MM:SS.mmm).

    Args:
        milliseconds: The time in milliseconds.

    Returns:
        A string representing the timestamp in the format HH:MM:SS.mmm.
    """

    return ms_to_str(milliseconds, include_ms=True)


def html_to_text(html_str: str, use_only_body=False) -> str:
    """
    Recursively extracts text content from an HTML node and its children.

    Args:
        node: An HTML node to extract text from.

    Returns:
        A string containing the extracted text.
    """

    # Define the parser class. See
    # https://stackoverflow.com/questions/14694482/converting-html-to-text-with-python
    # for more information on this approach.
    #
    # TODO: move this function and class to its own module.
    class MyHTMLParser(html.parser.HTMLParser):
        def __init__(self, use_only_body=False):
            super().__init__()
            self.result = []
            self.body_found = not use_only_body

        def handle_starttag(self, tag, attrs):
            if self.body_found:
                if tag in HTML_BLOCK_LEVEL_ELEMENTS or tag == "br":
                    self.result.append("\n")
            else:
                if tag == "body":
                    self.body_found = True

        def handle_endtag(self, tag):
            if self.body_found and tag in HTML_BLOCK_LEVEL_ELEMENTS:
                self.result.append("\n")

        def handle_data(self, data):
            if self.body_found:
                text = html.unescape(data).strip()
                if text:
                    self.result.append(text)

        def get_text(self):
            ret = ""

            for item in self.result:
                if ret and not ret[-1].isspace() and not item.isspace():
                    ret += " "

                ret += item

            return ret.strip()

    parser = MyHTMLParser(use_only_body)
    parser.feed(html_str)

    return parser.get_text()


def _vtt_escape(txt: str) -> str:
    """
    Escapes a string and normalizes newline characters.

    This function takes a string as input, escapes HTML special characters
    using html.escape, and then normalizes consecutive newline characters
    into single newlines.

    Args:
        txt: The input string to be processed.

    Returns:
        The processed string with escaped HTML characters and normalized newlines.
    """

    txt = html.escape(txt, quote=False)

    # Make sure to replace all double newlines with a single newline. Use a
    # while loop to find repetitive occurences.
    #
    # This could also be done using a regular expression. But I'm not sure
    # what's faster and this is probably easier and doesn't require an
    # additional library.
    while "\n\n" in txt:
        txt = txt.replace("\n\n", "\n")

    return txt


# AI-Generated Feature: Centralized HTML Parser
# Extracts structural data (title, info, segments) from the HTML transcript to feed other export formats.
def parse_transcript_html(html_string: str) -> tuple[str, str, list[dict]]:
    """
    Parses an HTML transcript and extracts title, info, and segments.
    Returns: (title, info, list_of_segments)
    """
    class TranscriptHTMLParser(html.parser.HTMLParser):
        def __init__(self):
            super().__init__()
            self.body_found = False
            self.segments = []

        def handle_starttag(self, tag, attrs):
            if tag == "body":
                self.body_found = True
                return

            if not self.body_found:
                return

            if tag == "p":
                self.segments.append({
                    "text": "",
                    "speaker": None,
                    "time_start": None,
                    "time_end": None,
                })
            elif tag == "a" and self.segments:
                tmp = None
                for item in attrs:
                    if item[0] == "name":
                        tmp = item[1].split("_")
                if tmp and len(tmp) >= 4:
                    self.segments[-1]["time_start"] = tmp[1]
                    self.segments[-1]["time_end"] = tmp[2]
                    self.segments[-1]["speaker"] = tmp[3]

        def handle_endtag(self, tag):
            pass

        def handle_data(self, data):
            if not self.body_found or not self.segments:
                return

            if not data or data.isspace():
                return

            if self.segments[-1]["speaker"] and data.strip().replace(":", "") == self.segments[-1]["speaker"]:
                return

            if REGEX_DETECT_TIMESTAMP.match(data.strip()):
                return

            if self.segments[-1]["text"] and not self.segments[-1]["text"][-1].isspace():
                self.segments[-1]["text"] += " "

            self.segments[-1]["text"] += html.unescape(data).strip()

        def get_title(self):
            return self.segments[0]["text"] if len(self.segments) > 0 else ""

        def get_info(self):
            return self.segments[1]["text"] if len(self.segments) > 1 else ""

        def get_segments(self):
            for item in self.segments[2:]:
                if item["text"] and not item["text"].isspace():
                    yield item

    parser = TranscriptHTMLParser()
    parser.feed(html_string)
    return parser.get_title(), parser.get_info(), list(parser.get_segments())


# AI-Generated Feature: Extended Export (Markdown)
# Formats segments to a markdown string.
def html_to_markdown(html_string: str) -> str:
    """
    Converts an HTML transcript to Markdown format.
    """
    title, info, segments = parse_transcript_html(html_string)
    
    lines = []
    if title:
        lines.append(f"# {title}")
    if info:
        lines.append(f"*{info}*")
        lines.append("---")
        lines.append("")
        
    for item in segments:
        header = ""
        if item["speaker"]:
            header += f"**{item['speaker']}** "
        
        if item["time_start"]:
            start = ms_to_str(int(item["time_start"]))
            header += f"(*{start}*):"
        
        if header:
            lines.append(header)
        lines.append(item["text"])
        lines.append("")
        
    return "\n".join(lines)


# AI-Generated Feature: Extended Export (ODT)
# Uses odfpy to build a formatted OpenDocument Text document.
def html_to_odt(html_string: str) -> bytes:
    """
    Converts an HTML transcript to an ODT file (returned as bytes).
    """
    import io
    from odf.opendocument import OpenDocumentText
    from odf.text import P, Span
    from odf.style import Style, TextProperties, ParagraphProperties
    
    doc = OpenDocumentText()
    
    # Create bold and italic styles
    bold_style = Style(name="Bold", family="text")
    bold_style.addElement(TextProperties(fontweight="bold"))
    doc.automaticstyles.addElement(bold_style)
    
    italic_style = Style(name="Italic", family="text")
    italic_style.addElement(TextProperties(fontstyle="italic"))
    doc.automaticstyles.addElement(italic_style)
    
    # Title style
    title_style = Style(name="TitleStyle", family="paragraph")
    title_style.addElement(ParagraphProperties(marginbottom="0.5cm"))
    title_style.addElement(TextProperties(fontweight="bold", fontsize="18pt"))
    doc.automaticstyles.addElement(title_style)
    
    title, info, segments = parse_transcript_html(html_string)
    
    if title:
        doc.text.addElement(P(stylename=title_style, text=title))
    if info:
        doc.text.addElement(P(text=info))
        doc.text.addElement(P(text=""))
        
    for item in segments:
        p = P()
        if item["speaker"] or item["time_start"]:
            if item["speaker"]:
                p.addElement(Span(stylename=bold_style, text=item["speaker"] + " "))
            if item["time_start"]:
                start = ms_to_str(int(item["time_start"]))
                p.addElement(Span(stylename=italic_style, text=f"[{start}] "))
        p.addElement(Span(text=item["text"]))
        doc.text.addElement(p)
        doc.text.addElement(P(text=""))
        
    out = io.BytesIO()
    doc.save(out)
    return out.getvalue()


# AI-Generated Feature: Extended Export (PDF)
# Uses fpdf2 to output a PDF with custom margins and true physical line numbers.
def html_to_pdf(html_string: str, with_line_numbers: bool = True) -> bytes:
    """
    Converts an HTML transcript to a PDF file (returned as bytes).
    """
    from fpdf import FPDF
    
    title, info, segments = parse_transcript_html(html_string)
    
    def safe_pdf_str(s: str) -> str:
        if not s:
            return ""
        # The character '꞉' (U+A789) is used in noScribe to avoid breaking WebVTT/MAXQDA
        # But standard PDF fonts don't support it, so we revert it to a standard colon.
        s = s.replace('꞉', ':')
        # fpdf2 built-in fonts support windows-1252. Replace unsupported chars to avoid crashes.
        return s.encode('windows-1252', 'replace').decode('windows-1252')
        
    class TranscriptPDF(FPDF):
        def header(self):
            self.set_font("helvetica", "B", 14)
            if hasattr(self, "transcript_title") and self.transcript_title:
                self.cell(0, 10, safe_pdf_str(self.transcript_title), new_x="LMARGIN", new_y="NEXT", align="L")
                
        def footer(self):
            self.set_y(-15)
            self.set_font("helvetica", "I", 8)
            self.cell(0, 10, str(self.page_no()), align="C")
            
    pdf = TranscriptPDF()
    pdf.transcript_title = title
    pdf.add_page()
    pdf.set_font("helvetica", size=10)
    
    if info:
        pdf.set_font("helvetica", "I", 9)
        pdf.multi_cell(0, 5, safe_pdf_str(info))
        pdf.ln(5)
    
    line_counter = 1
    
    for item in segments:
        # Construct header block (Speaker + Time)
        header_text = ""
        if item["speaker"]:
            header_text += item["speaker"] + " "
        if item["time_start"]:
            start = ms_to_str(int(item["time_start"]))
            header_text += f"[{start}] "
            
        margin_x = 20 if with_line_numbers else 10
        
        # Split header text if present
        header_lines = []
        if header_text:
            pdf.set_x(margin_x)
            pdf.set_font("helvetica", "B", 11)
            # Use multi_cell dry_run to split it (usually 1 line, but just in case)
            header_lines = pdf.multi_cell(0, 6, safe_pdf_str(header_text), dry_run=True, output="LINES")
            
        # Split body text
        body_lines = []
        if item["text"]:
            pdf.set_x(margin_x)
            pdf.set_font("helvetica", "", 11)
            body_lines = pdf.multi_cell(0, 6, safe_pdf_str(item["text"]), dry_run=True, output="LINES")
            
        # Print header lines
        if header_lines:
            pdf.set_font("helvetica", "B", 11)
            for line in header_lines:
                if pdf.y + 6 > pdf.page_break_trigger:
                    pdf.add_page()
                pdf.set_x(margin_x)
                if with_line_numbers:
                    pdf.set_font("helvetica", "I", 8)
                    pdf.set_text_color(150, 150, 150)
                    pdf.cell(10, 6, str(line_counter))
                    pdf.set_text_color(0, 0, 0)
                    pdf.set_font("helvetica", "B", 11)
                    line_counter += 1
                pdf.cell(0, 6, line, new_x="LMARGIN", new_y="NEXT")
                
        # Print body lines
        if body_lines:
            pdf.set_font("helvetica", "", 11)
            for line in body_lines:
                if pdf.y + 6 > pdf.page_break_trigger:
                    pdf.add_page()
                pdf.set_x(margin_x)
                if with_line_numbers:
                    pdf.set_font("helvetica", "I", 8)
                    pdf.set_text_color(150, 150, 150)
                    pdf.cell(10, 6, str(line_counter))
                    pdf.set_text_color(0, 0, 0)
                    pdf.set_font("helvetica", "", 11)
                    line_counter += 1
                pdf.cell(0, 6, line, new_x="LMARGIN", new_y="NEXT")
                
        # Add an empty line between segments
        if pdf.y + 4 > pdf.page_break_trigger:
            pdf.add_page()
        else:
            pdf.ln(4)
            
    return pdf.output()


# AI-Generated Refactored Feature: WebVTT Export
# Modified to use the new centralized HTML parser.
def html_to_webvtt(html_string: str) -> str:
    """
    Converts an HTML interview output file to a WebVTT transcript.

    This function extracts text from an HTML interview output file and
    transforms it into a WebVTT format. Each segment is converted into a WebVTT
    cue with start and end times, speaker information, and the text content.

    Args:
        html_string: The input string to be processed.

    Returns:
        A string containing the WebVTT transcript.
    """
    title, info, segments = parse_transcript_html(html_string)

    ret = "WEBVTT "
    ret += _vtt_escape(title) + "\n\n"
    ret += _vtt_escape("NOTE\n" + info) + "\n\n"

    for index, item in enumerate(segments):
        ret += f"{index + 1}\n"

        start = _ms_to_webvtt(int(item["time_start"]))
        end = _ms_to_webvtt(int(item["time_end"]))
        ret += f"{start} --> {end}\n"

        if item["speaker"]:
            ret += f"<v {item['speaker']}>"

        ret += _vtt_escape(item["text"])
        ret += "\n\n"

    return ret


# AI-Generated Feature: Custom Dictionary support
# Combines the default language prompt/hotwords with custom dictionary terms.
def combine_prompt_and_dictionary(prompt: str, custom_dictionary: str) -> str:
    prompt = (prompt or "").strip()
    custom_dict = (custom_dictionary or "").strip()
    if custom_dict:
        if prompt:
            return prompt.rstrip(".,?!") + ", " + custom_dict
        else:
            return custom_dict
    return prompt