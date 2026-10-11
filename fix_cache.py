p = "/data/data/com.termux/files/home/smm-new/app.py"
s = open(p).read()

# Purana load_data dhoondo aur hataao
import re

# Match load_data function
pattern = re.compile(r'def load_data\(force=False\):.*?(?=\ndef save_data)', re.DOTALL)

new_load = '''def load_data(force=False):
    """Always fetch from GitHub. No memory cache."""
    gh = gh_load()
    if gh:
        for k in ["payments","orders","users","services","announcements","tickets"]:
            if k not in gh:
                gh[k] = [] if k != "users" else {}
        _memory_cache["data"] = gh
        return gh
    # GitHub fail ho gaya - local fallback
    if _memory_cache["data"]:
        return _memory_cache["data"]
    try:
        with open(DATA_FILE) as f:
            d = json.load(f)
        for k in ["payments","orders","users","services","announcements","tickets"]:
            if k not in d:
                d[k] = [] if k != "users" else {}
        _memory_cache["data"] = d
        return d
    except:
        d = init_data()
        _memory_cache["data"] = d
        return d

'''

if pattern.search(s):
    s = pattern.sub(new_load, s)
    print("[+] load_data clean ho gaya")
else:
    print("[!] Pattern nahi mila")

# save_data ke liye retry already hai - confirm karo
if 'for i in range(3):' not in s:
    old_save = '''def save_data(d):
    _memory_cache["data"] = d
    gh_save(d)'''
    new_save = '''def save_data(d):
    _memory_cache["data"] = d
    for i in range(5):
        if gh_save(d):
            break
        _memory_cache["sha"] = None
        import time; time.sleep(1)'''
    s = s.replace(old_save, new_save)
    print("[+] save_data retry 5x")

open(p, "w").write(s)
print("[OK] app.py fix")
