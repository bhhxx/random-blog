from flask import Flask, render_template, request, jsonify, send_from_directory, url_for 
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse # Import urlparse directly
import re
import json
from datetime import datetime, timezone
import os

# Import config variables
from config import *

app = Flask(__name__)

# --- Translations ---
# Store backend messages here, keyed like the frontend
# --- Translations ---
MESSAGES = {
    'en': {
        'url_required': "URL cannot be empty",
        'password_required': "Password required",
        # 'access_denied': "ACCESS DENIED", # Keep the original simple one if needed elsewhere
        'access_denied_custom': "Password Incorrect.\nThis is a private website. If interested, please visit https://github.com/bhhxx/random-blog to build your own teleporter.", # NEW detailed message
        'invalid_url_format': "Invalid URL format (must start with http:// or https://)",
        'url_added_success': "URL successfully saved",
        'url_already_existed': "URL already existed",
        'add_error': "Internal server error while adding URL",
        'delete_url_required': "URL to delete cannot be empty",
        'url_delete_success': "URL successfully deleted",
        'url_not_found': "Coordinates not found",
        'delete_error': "Internal server error while deleting URL",
        'no_base_sites': "No base sites available",
        'no_valid_urls_db': "No valid URLs found in database",
        'fetch_links_failed': "Could not find any valid article links after checking several sites.",
        'fetch_internal_error': "Website crawl failed",
        'fetch_generic_error': "Unknown error during site processing",
        'bg_set_success': "Background image updated successfully.",
        'bg_set_error': "Error updating background image.",
        'bg_url_required': "Background image URL cannot be empty.",
        'bg_reset_success': "Background image reset to default.",
        'bg_reset_error': "Error resetting background image.",
        'invalid_bg_url': "Invalid background URL format.",
    },
    'zh': {
        'url_required': "URL 不能为空",
        'password_required': "需要提供密码",
        # 'access_denied': "访问被拒绝", # Keep original if needed
        'access_denied_custom': "密码错误。\n此网站为私人网站。\n若感兴趣，请访问 https://github.com/bhhxx/random-blog 构建你自己的超时空传送器。", # NEW detailed message
        'invalid_url_format': "URL 格式无效 (需要 http:// 或 https://)",
        'url_added_success': "URL 已成功保存",
        'url_already_existed': "URL 已存在",
        'add_error': "添加 URL 时发生内部错误",
        'delete_url_required': "要删除的 URL 不能为空",
        'url_delete_success': "URL 已成功删除",
        'url_not_found': "未找到坐标",
        'delete_error': "删除 URL 时发生内部错误",
        'no_base_sites': "没有可用的主站URL",
        'no_valid_urls_db': "数据库中没有有效的URL条目",
        'fetch_links_failed': "在检查了数个站点后未能找到任何有效的文章链接。",
        'fetch_internal_error': "网站抓取失败",
        'fetch_generic_error': "处理站点时发生未知错误",
        'bg_set_success': "背景图片更新成功。",
        'bg_set_error': "更新背景图片时出错。",
        'bg_url_required': "背景图片 URL 不能为空。",
        'bg_reset_success': "背景图片已重置为默认值。",
        'bg_reset_error': "重置背景图片时出错。",
        'invalid_bg_url': "背景图片 URL 格式无效。", # Optional
    }
}

# --- Helper Functions ---

def get_locale():
    """Detects language from 'X-App-Language' header, defaults to English."""
    lang = request.headers.get('X-App-Language', 'en') # Default to 'en'
    return lang if lang in MESSAGES else 'en'

def translate(key, lang=None):
    """Gets the translated message for a key and language."""
    if lang is None:
        lang = get_locale()
    # Fallback to English if key or lang is missing
    return MESSAGES.get(lang, MESSAGES['en']).get(key, MESSAGES['en'].get(key, key)) # Return key itself as last resort

# --- Data Handling Functions (JSON) ---

def load_urls_data():
    """Loads URL data from JSON file."""
    if not os.path.exists(URL_FILE): return []
    try:
        with open(URL_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            return json.loads(content) if content else []
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        print(f"Error loading URL data from {URL_FILE}: {e}")
        return []

def save_urls_data(data):
    """Saves URL data list to JSON file."""
    try:
        with open(URL_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except (IOError, Exception) as e:
        print(f"Error saving URL data to {URL_FILE}: {e}")

def add_url_entry(new_url):
    """Adds a new URL entry to the JSON data."""
    urls_data = load_urls_data()
    normalized_new_url = new_url.rstrip('/')
    existing_urls = {entry.get('url', '').rstrip('/') for entry in urls_data}

    if normalized_new_url in existing_urls:
        print(f"URL exists (ignoring trailing slash): {new_url}")
        # Use the key for translation
        return False, 'url_already_existed'

    timestamp = datetime.now(timezone.utc).isoformat()
    urls_data.append({"url": new_url, "added_at": timestamp})
    urls_data.sort(key=lambda x: x.get('url', ''))
    save_urls_data(urls_data)
    print(f"URL saved: {new_url} at {timestamp}")
    # Use the key for translation
    return True, 'url_added_success'

def delete_url_entry(url_to_delete):
    """Deletes a URL entry from the JSON data."""
    urls_data = load_urls_data()
    initial_length = len(urls_data)
    normalized_url_to_delete = url_to_delete.rstrip('/')
    updated_data = [entry for entry in urls_data if entry.get('url', '').rstrip('/') != normalized_url_to_delete]

    if len(updated_data) == initial_length:
        print(f"URL not found for deletion (ignoring trailing slash): {url_to_delete}")
        # Use the key for translation
        return False, 'url_not_found'

    save_urls_data(updated_data)
    print(f"URL deleted: {url_to_delete}")
    # Use the key for translation
    return True, 'url_delete_success'

# --- NEW: Background Setting Functions ---
def load_background_url():
    """Loads the current background URL setting, falling back to default."""
    try:
        if os.path.exists(BACKGROUND_CONFIG_FILE):
            with open(BACKGROUND_CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Return the stored URL if it exists and is a non-empty string
                if isinstance(data.get('background_url'), str) and data['background_url']:
                    print(f"Loaded background URL from config: {data['background_url']}")
                    return data['background_url']
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        print(f"Error loading background config file {BACKGROUND_CONFIG_FILE}: {e}")
    # Fallback to default from config.py if file doesn't exist, is empty, invalid, or URL is missing/empty
    print(f"Using default background URL: {DEFAULT_BACKGROUND_IMAGE}")
    return DEFAULT_BACKGROUND_IMAGE # Return default path

def save_background_url(new_bg_url=None):
    """Saves the new background URL or resets to default if None."""
    try:
        # If new_bg_url is None or empty string, effectively reset by removing/clearing the file
        if not new_bg_url:
            if os.path.exists(BACKGROUND_CONFIG_FILE):
                os.remove(BACKGROUND_CONFIG_FILE)
                print("Background setting file removed (reset to default).")
            return True # Resetting is considered success
        else:
             # Validate if it looks somewhat like a URL or path before saving
             if not (new_bg_url.startswith(('http://', 'https://', '/')) or '/' in new_bg_url or '.' in new_bg_url):
                 print(f"Refusing to save potentially invalid background URL: {new_bg_url}")
                 return False # Indicate save failure due to format

             data = {'background_url': new_bg_url}
             with open(BACKGROUND_CONFIG_FILE, 'w', encoding='utf-8') as f:
                 json.dump(data, f, indent=4)
             print(f"Saved new background URL: {new_bg_url}")
             return True # Indicate save success
    except (IOError, OSError, Exception) as e:
        print(f"Error saving background config file {BACKGROUND_CONFIG_FILE}: {e}")
        return False # Indicate save failure

# --- Web Scraping Functions ---

def fetch_links(url):
    """Fetches internal article links from a blog page."""
    print(f"Attempting to fetch links from: {url}")
    try:
        headers = {'User-Agent': f'RandomBlogBot/1.0 (+{UserAgent})'}
        response = requests.get(url, timeout=REQUEST_TIMEOUT, headers=headers, allow_redirects=True)
        response.raise_for_status()
        content_type = response.headers.get('content-type', '').lower()
        if 'html' not in content_type:
             print(f"Skipping non-HTML content ({content_type}) at: {url}")
             return []

        soup = BeautifulSoup(response.text, 'html.parser')
        parsed_base_url = urlparse(response.url)
        base_domain = f"{parsed_base_url.scheme}://{parsed_base_url.netloc}"
        if not parsed_base_url.scheme or not parsed_base_url.netloc:
             raise ValueError("Invalid base URL components")

        links = set()
        print(f"\n--- Processing links found on {response.url} ---") # Added divider
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            print(f"\n[DEBUG] Found href: '{href}'") # Debug href
            if not href or href.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
                print("[DEBUG] Skipping: Empty, fragment, mailto, tel, or javascript")
                continue

            try:
                full_url = urljoin(response.url, href)
                print(f"[DEBUG] Resolved full_url: '{full_url}'") # Debug full URL
            except ValueError:
                print("[DEBUG] Skipping: ValueError during urljoin")
                continue

            try:
                parsed_full_url = urlparse(full_url)
                if parsed_full_url.scheme not in ('http', 'https'):
                    print(f"[DEBUG] Skipping: Non-HTTP(S) scheme '{parsed_full_url.scheme}'")
                    continue
                link_base_domain = f"{parsed_full_url.scheme}://{parsed_full_url.netloc}"
                # Original path before normalization
                original_path = parsed_full_url.path
                # Normalize path: remove trailing slash unless it's the root '/'
                path_normalized = original_path.rstrip('/') if len(original_path) > 1 else original_path
                query = parsed_full_url.query # Get query string

                print(f"[DEBUG] Parsed components: Base='{link_base_domain}', OrigPath='{original_path}', NormPath='{path_normalized}', Query='{query}'")

            except ValueError:
                print("[DEBUG] Skipping: ValueError during URL parsing")
                continue

            # --- Domain Check ---
            if link_base_domain != base_domain:
                print(f"[DEBUG] Skipping: Domain mismatch ('{link_base_domain}' != '{base_domain}')")
                continue
            else:
                print("[DEBUG] Domain OK.")

            # --- Path Filter Check ---
            path_matched = False
            for rule in FILTER_RULES:
                match = re.search(rule, path_normalized, re.IGNORECASE)
                if match:
                    print(f"[DEBUG] FILTER RULE MATCH! Rule '{rule}' matched NormPath '{path_normalized}'. Skipping.")
                    path_matched = True
                    break # No need to check other rules for this link
            if path_matched:
                continue # Skip to next a_tag
            else:
                 print("[DEBUG] Path OK (No filter rule matched).")

            # --- Query Param Filter Check ---
            param_matched = False
            if query and EXCLUDE_PARAMS: # Only check if query and exclude list exist
                 for param_rule in EXCLUDE_PARAMS: # param_rule is like '=tag'
                     # Check if the rule exists as a substring in the query
                     if param_rule in query:
                         print(f"[DEBUG] EXCLUDE PARAM MATCH! Rule '{param_rule}' found in Query '{query}'. Skipping.")
                         param_matched = True
                         break
            if param_matched:
                 continue # Skip to next a_tag
            else:
                 print("[DEBUG] Query Params OK (No exclude param matched).")


            # If all checks passed:
            clean_url = parsed_full_url._replace(fragment="").geturl()
            print(f"[DEBUG] ADDING clean URL: {clean_url}")
            links.add(clean_url)

        print(f"\n--- Finished processing links for {response.url}. Found {len(links)} valid links ---")
        return sorted(list(links))

    # Keep existing except blocks
    except requests.exceptions.Timeout: print(f"Timeout fetching: {url}"); return []
    except requests.exceptions.RequestException as e: print(f"Request failed ({url}): {e}"); return []
    except ValueError as e: print(f"URL parsing error ({url}): {e}"); return []
    except Exception as e: print(f"Unknown error processing page ({url}): {e}"); return []

# --- Flask Routes ---

@app.route("/")
def index():
    """Renders the main page."""
    urls_data = load_urls_data()
    current_background_url = load_background_url()
    # Construct full URL for static files if it's a relative path
    if not current_background_url.startswith(('http://', 'https://')):
         # url_for needs endpoint name ('static') and filename parameter
         try:
              background_image_css_url = url_for('static', filename=current_background_url, _external=False) # Get relative URL
         except Exception as e:
              print(f"Warning: Could not generate URL for static background '{current_background_url}': {e}. Using raw path.")
              background_image_css_url = f'/static/{current_background_url}' # Fallback
    else:
        background_image_css_url = current_background_url # It's already a full URL

    print(f"Passing background URL to template: {background_image_css_url}")
    return render_template(MAXI_PAGE,
                           urls_data=urls_data,
                           background_image_url=background_image_css_url) # Pass URL to template

@app.route("/set_background", methods=["POST"])
def set_background():
    """Sets a new background URL or resets to default."""
    lang = get_locale()
    password = request.form.get("password")
    new_bg_url = request.form.get("url", "").strip() # URL for the new background
    action = request.form.get("action", "set") # "set" or "reset"

    if not password: return jsonify({"message": translate('password_required', lang)}), 401
    if password != SECRET_PASSWORD: return jsonify({"message": translate('access_denied', lang)}), 401 # Keep simple denial here

    if action == "reset":
        success = save_background_url(None) # Pass None to reset
        message_key = 'bg_reset_success' if success else 'bg_reset_error'
        status_code = 200 if success else 500
        return jsonify({"message": translate(message_key, lang)}), status_code
    elif action == "set":
        if not new_bg_url: return jsonify({"message": translate('bg_url_required', lang)}), 400
         # Basic validation if it looks like a URL or path
        if not (new_bg_url.startswith(('http://', 'https://', '/')) or '/' in new_bg_url or '.' in new_bg_url):
             return jsonify({"message": translate('invalid_bg_url', lang)}), 400

        success = save_background_url(new_bg_url)
        message_key = 'bg_set_success' if success else 'bg_set_error'
        status_code = 200 if success else 500
        return jsonify({"message": translate(message_key, lang)}), status_code
    else:
        return jsonify({"message": "Invalid action specified"}), 400

@app.route("/add_url", methods=["POST"])
def add_url():
    """Handles adding a URL."""
    lang = get_locale() # Detect language
    new_url = request.form.get("url", "").strip()
    password = request.form.get("password")

    if not new_url: return jsonify({"message": translate('url_required', lang)}), 400
    if not password: return jsonify({"message": translate('password_required', lang)}), 401
    if password != SECRET_PASSWORD:
        # Use the new, detailed message key
        return jsonify({"message": translate('access_denied_custom', lang)}), 401
    try:
        if not (new_url.startswith('http://') or new_url.startswith('https://')):
             return jsonify({"message": translate('invalid_url_format', lang)}), 400

        success, message_key = add_url_entry(new_url)
        status_code = 201 if success else 409 # Created or Conflict
        return jsonify({"message": translate(message_key, lang)}), status_code

    except Exception as e:
        print(f"Error adding URL: {e}")
        return jsonify({"message": translate('add_error', lang)}), 500

@app.route("/delete_url", methods=["POST"])
def delete_url():
    """Handles deleting a URL."""
    lang = get_locale() # Detect language
    url_to_delete = request.form.get("url", "").strip()
    password = request.form.get("password")

    if not url_to_delete: return jsonify({"message": translate('delete_url_required', lang)}), 400
    if not password: return jsonify({"message": translate('password_required', lang)}), 401
    if password != SECRET_PASSWORD:
        # Use the new, detailed message key
         return jsonify({"message": translate('access_denied_custom', lang)}), 401
    try:
        success, message_key = delete_url_entry(url_to_delete)
        status_code = 200 if success else 404 # OK or Not Found
        return jsonify({"message": translate(message_key, lang)}), status_code

    except Exception as e:
        print(f"Error deleting URL: {e}")
        return jsonify({"message": translate('delete_error', lang)}), 500

@app.route("/random_blog", methods=["GET"])
def random_blog():
    """Returns a random blog post URL."""
    lang = get_locale() # Detect language
    all_sites_data = load_urls_data()
    if not all_sites_data: return jsonify({"message": translate('no_base_sites', lang)}), 404

    all_sites_urls = [entry['url'] for entry in all_sites_data if 'url' in entry]
    if not all_sites_urls: return jsonify({"message": translate('no_valid_urls_db', lang)}), 404

    MAX_FETCH_ATTEMPTS = 5
    attempts = 0; selected_site = None; all_links = []
    sites_to_try = all_sites_urls[:] # Create a copy to modify

    while attempts < MAX_FETCH_ATTEMPTS and not all_links and sites_to_try:
         attempts += 1
         selected_site = random.choice(sites_to_try)
         sites_to_try.remove(selected_site) # Remove from list for this request
         print(f"Attempt {attempts}: Trying site {selected_site}")
         all_links = fetch_links(selected_site)
         if not all_links: print(f"No links found on {selected_site}.")

    if not all_links:
         print(f"Failed to find links after {attempts} attempts.")
         return jsonify({
             "message": translate('fetch_links_failed', lang),
             "source_site": selected_site # Report last attempted site
         }), 404

    final_url = random.choice(all_links)
    print(f"Success: Found link: {final_url} from {selected_site}")
    return jsonify({"blog_url": final_url, "source_site": selected_site}), 200


@app.route("/random_url", methods=["GET"])
def random_url():
    """Returns a random base blog URL."""
    lang = get_locale() # Detect language
    all_sites_data = load_urls_data()
    if not all_sites_data: return jsonify({"message": translate('no_base_sites', lang)}), 404

    all_sites_urls = [entry['url'] for entry in all_sites_data if 'url' in entry]
    if not all_sites_urls: return jsonify({"message": translate('no_valid_urls_db', lang)}), 404

    selected_site = random.choice(all_sites_urls)
    # No specific message needed on success here, just data
    return jsonify({"blog_url": selected_site, "source_site": selected_site}), 200

# --- Static File Serving ---
@app.route('/static/<path:filename>')
def static_files(filename):
    # Use safe_join to prevent directory traversal issues
    from werkzeug.utils import safe_join
    try:
        static_dir = os.path.abspath('static')
        file_path = safe_join(static_dir, filename)
        if not os.path.isfile(file_path):
             print(f"Static file not found: {file_path}")
             return jsonify({"message": "File not found"}), 404
        return send_from_directory('static', filename)
    except Exception as e:
         print(f"Error serving static file {filename}: {e}")
         return jsonify({"message": "Error serving file"}), 500

# --- Main Execution ---
if __name__ == "__main__":
    # Ensure the URL file exists
    if not os.path.exists(URL_FILE):
        print(f"URL file {URL_FILE} not found, creating empty file.")
        save_urls_data([])
    app.run(host=HOST, port=PORT, debug=DEBUG)