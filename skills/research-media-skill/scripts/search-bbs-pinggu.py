"""
Read bbs.pinggu.org (经管之家) thread content via curl + cookie file.

This is the GENERIC fallback layer (works in any agent environment).
Hermes 主路线用 bsk（腾讯 BrowserSkill 真实浏览器登录态），见 SKILL.md。

Usage:
  python3 search-bbs-pinggu.py read <thread-url>     # Read thread (all reply floors)
  python3 search-bbs-pinggu.py check                 # Check cookie validity
"""
import os, sys, re, html as html_mod
import urllib.request

COOKIE_FILE = os.path.expanduser('~/.hermes/credentials/bbs-pinggu-cookies.txt')
AUTH_COOKIE_NAMES = ['Z9M6_79fc_auth', 'Z9M6_79fc_saltkey']
TEST_URL = 'https://bbs.pinggu.org/thread-7909828-1-1.html'


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


def cookies_valid():
    """Test if current cookies can read a thread. Returns bool."""
    cookies = read_cookies()
    if not cookies:
        print("  ⏭️  cookie 文件不存在或为空:", COOKIE_FILE)
        return False
    cookie_str = '; '.join(f'{k}={v}' for k, v in cookies.items())
    try:
        req = urllib.request.Request(
            TEST_URL,
            headers={'User-Agent': 'Mozilla/5.0', 'Cookie': cookie_str}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
        html_text = raw.decode('gbk', errors='replace')
        has_post = 'postmessage_' in html_text
        is_large = len(raw) > 100000
        return has_post and is_large
    except Exception:
        return False


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
    blocks = re.findall(r'(?:[\u4e00-\u9fff]{4,}[^<]*?)(?=<|$)', segment)
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
    if not cookies:
        print("❌ 无 cookie。请按 SKILL.md「Read via curl」指引配置经管之家登录 cookies。")
        return
    cookie_str = '; '.join(f'{k}={v}' for k, v in cookies.items())
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Cookie': cookie_str,
        })
        with urllib.request.urlopen(req, timeout=25) as resp:
            raw = resp.read()
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return
    html_text = raw.decode('gbk', errors='replace')
    if 'postmessage_' not in html_text:
        print("⚠️ 页面无帖子内容（登录墙？）。运行 check 验证 cookie，或改用 bsk 路线。")
        return
    posts = extract_post_content(html_text)
    if not posts:
        print("⚠️ 未提取到有效内容")
        return
    for i, p in enumerate(posts):
        print(f'--- 楼层 {i + 1} ---')
        print(p[:600])


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    action = sys.argv[1]
    if action == 'read':
        if len(sys.argv) < 3:
            print("用法: search-bbs-pinggu.py read <thread-url>")
            sys.exit(1)
        read_thread(sys.argv[2])
    elif action == 'check':
        ok = cookies_valid()
        print("✅ cookies 有效" if ok else "❌ cookies 无效或已过期")
        sys.exit(0 if ok else 1)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
