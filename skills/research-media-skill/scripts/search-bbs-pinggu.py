"""
Search bbs.pinggu.org (经管之家) and read full thread content.
Auto-refreshes cookies from Camofox browser session if expired (Hermes Agent).
Other agents: detect expiry and guide user to re-export.

Usage:
  python3 search-bbs-pinggu.py read <thread-url>     # Read thread (auto-refresh cookies)
  python3 search-bbs-pinggu.py check                  # Check cookie validity
  python3 search-bbs-pinggu.py login                  # Force cookie refresh from Camofox
"""
import os, sys, re, json, time, html as html_mod
import urllib.request, urllib.parse
import subprocess, shutil, sqlite3, tempfile

COOKIE_FILE = os.path.expanduser('~/.hermes/credentials/bbs-pinggu-cookies.txt')
AUTH_COOKIE_NAMES = ['Z9M6_79fc_auth', 'Z9M6_79fc_saltkey']
# Test thread used for cookie validity check (a well-known thread).
# If this thread is ever deleted, the check will fail and trigger refresh.
TEST_URL = 'https://bbs.pinggu.org/thread-7909828-1-1.html'

# ─── Cookie helpers ───────────────────────────────────────────

def read_cookies():
    if not os.path.exists(COOKIE_FILE):
        return {}
    cookies = {}
    with open(COOKIE_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                cookies[k.strip()] = v.strip()
    return cookies

def write_cookies(cookies_dict):
    """Write cookies dict to file."""
    os.makedirs(os.path.dirname(COOKIE_FILE), exist_ok=True)
    with open(COOKIE_FILE, 'w') as f:
        f.write(f"# bbs.pinggu.org login cookies\n")
        f.write(f"# 最后更新: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        for k, v in cookies_dict.items():
            f.write(f"{k}={v}\n")
    os.chmod(COOKIE_FILE, 0o600)

def cookies_valid():
    """Test if current cookies can read a thread. Returns bool."""
    cookies = read_cookies()
    if not cookies:
        return False
    cookie_str = '; '.join(f'{k}={v}' for k, v in cookies.items())
    try:
        req = urllib.request.Request(
            TEST_URL,
            headers={'User-Agent': 'Mozilla/5.0', 'Cookie': cookie_str}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
        html = raw.decode('gbk', errors='replace')
        # Valid: page contains post content (postmessage_) and is large.
        # Use byte length of raw response (login-wall page is ~5KB;
        # full thread is 100KB+). Decoded char count is unreliable for GBK.
        has_post = 'postmessage_' in html
        is_large = len(raw) > 100000
        return has_post and is_large
    except Exception:
        return False

# ─── Camofox session extraction ───────────────────────────────

def find_camofox_profile():
    """Find the Camofox Firefox profile directory from running processes."""
    try:
        out = subprocess.run(
            ['ps', 'aux'], capture_output=True, text=True, timeout=10
        ).stdout
        for line in out.split('\n'):
            low = line.lower()
            if 'camoufox' in low and '-profile' in low:
                m = re.search(r'-profile\s+(\S+)', line)
                if m:
                    return m.group(1)
    except Exception:
        pass
    return None

def extract_cookies_from_camofox():
    """
    Extract auth cookies from the running Camofox browser profile.
    Works because the user logs into bbs.pinggu.org in Camofox,
    and Firefox stores all cookies (incl. HttpOnly) in cookies.sqlite.
    Returns dict of cookies or None on failure.
    """
    profile = find_camofox_profile()
    if not profile:
        print("  ⏭️  Camofox not running. Cannot extract cookies.")
        return None

    db_path = os.path.join(profile, 'cookies.sqlite')
    if not os.path.exists(db_path):
        print(f"  ⏭️  cookies.sqlite not found at {db_path}")
        return None

    # Copy DB + WAL + SHM to temp dir (Firefox uses WAL mode: freshly
    # written cookies may still be in -wal, not checkpointed to main db)
    tmpdir = tempfile.mkdtemp(prefix='bbs-cookies-')
    try:
        for suffix in ['', '-wal', '-shm']:
            src = db_path + suffix
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(tmpdir, os.path.basename(src)))

        tmp_db = os.path.join(tmpdir, 'cookies.sqlite')
        conn = sqlite3.connect(tmp_db)
        cur = conn.cursor()
        placeholders = ','.join('?' for _ in AUTH_COOKIE_NAMES)
        cur.execute(
            f'SELECT name, value FROM moz_cookies WHERE host LIKE "%pinggu.org%" AND name IN ({placeholders})',
            AUTH_COOKIE_NAMES
        )
        rows = cur.fetchall()
        conn.close()

        if not rows:
            print("  ⏭️  Auth cookies not found in Camofox profile. "
                  "User must log in to bbs.pinggu.org in Camofox first.")
            return None

        cookies = dict(rows)
        missing = [n for n in AUTH_COOKIE_NAMES if n not in cookies]
        if missing:
            print(f"  ⏭️  Missing cookies in Camofox: {missing}")
            return None

        print(f"  ✅ Extracted {len(cookies)} auth cookies from Camofox session")
        return cookies
    except Exception as e:
        print(f"  ❌ Cookie extraction error: {e}")
        return None
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

# ─── Thread reader ────────────────────────────────────────────

def extract_post_content(html_text):
    post_ids = re.findall(r'id="postmessage_(\d+)"', html_text)
    if not post_ids:
        return []
    first_id = post_ids[0]
    idx = html_text.find(f'id="postmessage_{first_id}"')
    if idx < 0:
        return []
    td_end = html_text.find('</td>', idx)
    if td_end < 0:
        td_end = idx + 10000
    segment = html_text[idx:td_end]
    blocks = re.findall(r'(?:[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]{4,}[^<]*?)(?=<|$)', segment)
    meaningful = []
    for b in blocks:
        clean = re.sub(r'\s+', ' ', b).strip()
        clean = html_mod.unescape(clean)
        if len(clean) > 20 and '赵安豆' not in clean and '微信' not in clean and 'invite' not in clean:
            meaningful.append(clean)
    return meaningful

def read_thread(url):
    """Read a bbs.pinggu.org thread. Cookies must be valid before calling."""
    cookies = read_cookies()
    cookie_str = '; '.join(f'{k}={v}' for k, v in cookies.items())
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                     'Cookie': cookie_str}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read()
    except Exception as e:
        return {'error': str(e)}

    html_text = raw.decode('gbk', errors='replace')
    content = extract_post_content(html_text)
    title_match = re.search(r'<title>(.*?)</title>', html_text)
    title = html_mod.unescape(title_match.group(1)) if title_match else url

    return {
        'title': title,
        'url': url,
        'content': content,
        'total_paragraphs': len(content)
    }

# ─── Main ─────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  search-bbs-pinggu.py read <thread-url>   Read thread (auto-refresh cookies)")
        print("  search-bbs-pinggu.py check               Check cookie validity (exit 0=valid, 1=expired)")
        print("  search-bbs-pinggu.py login               Force cookie refresh from Camofox")
        sys.exit(1)

    action = sys.argv[1]

    if action == 'check':
        valid = cookies_valid()
        print(f"Cookies valid: {valid}")
        sys.exit(0 if valid else 1)

    elif action == 'login':
        print("🔄 Refreshing cookies from Camofox session...")
        cookies = extract_cookies_from_camofox()
        if cookies:
            write_cookies(cookies)
            if cookies_valid():
                print("✅ Cookies refreshed and verified!")
                sys.exit(0)
            else:
                print("❌ Extracted cookies failed verification")
                sys.exit(1)
        else:
            print("❌ Could not extract cookies. User must log in to bbs.pinggu.org in Camofox first.")
            sys.exit(1)

    elif action == 'read':
        url = sys.argv[2] if len(sys.argv) > 2 else input("URL: ")
        # Step 1: Check cookies, refresh from Camofox if needed
        if not cookies_valid():
            print("🔄 Cookies expired. Trying to refresh from Camofox session...")
            cookies = extract_cookies_from_camofox()
            if cookies:
                write_cookies(cookies)
                if not cookies_valid():
                    print("❌ Refreshed cookies failed verification")
                    sys.exit(1)
            else:
                print("❌ Cannot refresh cookies. Options:")
                print("   1. Open bbs.pinggu.org in Camofox, log in, then retry")
                print("   2. Re-export cookies from browser to " + COOKIE_FILE)
                sys.exit(1)
        result = read_thread(url)
        if 'error' in result:
            print(f"Error: {result['error']}")
            sys.exit(1)
        print(f"\n== {result['title']} ==")
        print(f"URL: {result['url']}")
        print(f"Total paragraphs: {result['total_paragraphs']}")
        print("\n--- Content ---")
        for p in result['content'][:30]:
            print(f"\n{p[:300]}")
        if result['total_paragraphs'] > 30:
            print(f"\n... ({result['total_paragraphs'] - 30} more paragraphs)")
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)
