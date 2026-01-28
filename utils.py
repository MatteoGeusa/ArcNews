import hashlib
import json
import html
import re
from bs4 import BeautifulSoup
from dateutil import parser
from markdownify import markdownify as md

def clean_html_to_markdown(raw_html):
    if not raw_html: return ""
    
    soup = BeautifulSoup(raw_html, 'html.parser')
    
    # 1. Rimozione tag inutili
    for tag in soup(["script", "style", "iframe", "noscript"]):
        tag.decompose()
        
    clean_html = str(soup)
    
    # 2. Conversione in Markdown
    markdown_text = md(
        clean_html, 
        heading_style="ATX", 
        newline_style="BACKSLASH",
        strong_em_symbol='*', 
        strip=['img']          
    )

    markdown_text = re.sub(r'^#+\s+(.*)$', r'*\1*', markdown_text, flags=re.MULTILINE)

    markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text).strip()
    
    return markdown_text

def convert_date_for_sqlite(date_string):
    try:
        return parser.parse(date_string).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return date_string

def calculate_checksum_id(title_text, content, photos_list):
    p_list = sorted(photos_list) if photos_list else []
    photos_str = json.dumps(p_list)
    raw_data = f"{title_text}||{content}||{photos_str}"
    return hashlib.md5(raw_data.encode('utf-8')).hexdigest()

def format_telegram_message_md(title, date, body_markdown, link):
    limit = 750
    if len(body_markdown) > limit:
        cut_index = body_markdown.rfind(' ', 0, limit)
        if cut_index == -1: cut_index = limit
        body_markdown = body_markdown[:cut_index] + " (...)"
        
    message = (
        f"*{title}*\n"          
        f"📅 _{date}_\n\n"     
        f"{body_markdown}\n\n"  
        f"[🔗 Continua a leggere sul sito ufficiale]({link})"
    )
    
    return message