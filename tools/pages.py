"""
Content for xidenlz.github.io.

Text lives here. Layout lives in build.py.
"""
from datetime import date
from articles import ARTICLE_BODIES

SITE_URL = "https://xidenlz.github.io/xidenlz/"
AUTHOR = "Musaed"

NAV = [
    ("Home",     "index.html"),
    ("About",    "about.html"),
    ("Research", "research.html"),
    ("Projects", "projects.html"),
    ("Blog",     "blog.html"),
    ("Contact",  "contact.html"),
]

# ---------------------------------------------------------------------------
# top-level pages
# ---------------------------------------------------------------------------

HOME = {
    "root": True,
    "slug": "index",
    "title": "Musaed, reverse engineering and Windows internals",
    "description": "CS student at KFU. Reverse engineering, kernel internals, and anti-cheat research.",
    "og": "home",
}

ABOUT = {
    "slug": "about",
    "title": "About",
    "description": "About Musaed, CS student at KFU, low-level and security research.",
    "subtitle": "CS student at KFU. I read binaries and write about what I find.",
    "crumbs": [("home", "index.html"), ("about", "about.html")],
    "og": "about",
    "background": (
        "I'm a Computer Science and Data Analysis student at "
        "<strong>King Faisal University</strong>, graduating February 2027. "
        "I spend most of my time reading disassembly, mostly Windows binaries, "
        "mostly the parts that touch the kernel. The write-ups here are the "
        "record of that work: what I looked at, what I found, and what I got wrong."
    ),
    "focus": (
        "Right now I'm working on Windows internals and anti-cheat research. "
        "I'm looking for a security or reverse-engineering internship for 2026, "
        "if that overlaps with what your team does, "
        "<a href=\"contact.html\">reach out</a>."
    ),
    "skills": [
        {
            "title": "Analysis",
            "items": [
                "Static and dynamic binary analysis",
                "x86 / x64 disassembly",
                "PE and ELF structure",
                "Memory analysis and pattern scanning",
                "Malware triage",
            ],
        },
        {
            "title": "Tools",
            "items": [
                "IDA Pro, Ghidra",
                "x64dbg, x32dbg",
                "WinDbg, kernel and user",
                "Zydis",
                "Sysinternals, Any.Run",
            ],
        },
        {
            "title": "Languages",
            "items": [
                "C / C++",
                "Python",
                "x86 / x64 assembly",
                "Windows API and NT native API",
                "SQL",
            ],
        },
        {
            "title": "Systems",
            "items": [
                "Windows internals and kernel callbacks",
                "Anti-cheat drivers",
                "Hooking and detection",
                "Process injection primitives",
                "Authenticode and digital signatures",
            ],
        },
    ],
    "record": [
        {
            "when": "6+ years",
            "role": "VirusTotal community contributor",
            "where": "Independent volunteer",
            "note": (
                "Triaging suspicious files submitted to the community, static "
                "and dynamic passes, verdicts, and short notes for other analysts."
            ),
        },
        {
            "when": "Ongoing",
            "role": "UnknownCheats staff / contributor",
            "where": "Reverse engineering community",
            "note": (
                "Discussion and analysis around game security, anti-cheat drivers, "
                "memory protection, and low-level Windows development."
            ),
        },
    ],
}

RESEARCH_INDEX = {
    "slug": "research",
    "title": "Research",
    "description": "Long-form reverse-engineering write-ups.",
    "subtitle": "Long-form write-ups. Fewer, longer, more careful than the blog.",
    "crumbs": [("home", "index.html"), ("research", "research.html")],
    "og": "research",
    "pending": [
        {
            "category": "In progress",
            "when": "Working on it",
            "title": "Anti-Cheat Expert (ACE), kernel side",
            "dek": (
                "Ongoing look at Tencent's Anti-Cheat Expert: driver callbacks, "
                "memory-protection primitives, integrity heartbeats, and how "
                "the client authenticates its kernel component."
            ),
            "tags": ["ACE", "Kernel", "Integrity", "In progress"],
        },
    ],
}

PROJECTS_INDEX = {
    "slug": "projects",
    "title": "Projects",
    "description": "Windows injection, hooking utilities, and binary triage tools.",
    "subtitle": "Injection, hooking, and triage code.",
    "crumbs": [("home", "index.html"), ("projects", "projects.html")],
    "og": "projects",
}

BLOG_INDEX = {
    "slug": "blog",
    "title": "Blog",
    "description": "Short notes on reverse engineering, kernel work, and malware triage.",
    "subtitle": "Short notes. Things I want to write down before I forget them.",
    "crumbs": [("home", "index.html"), ("blog", "blog.html")],
    "og": "blog",
}

CONTACT = {
    "slug": "contact",
    "title": "Contact",
    "description": "Email, GitHub, and Discord.",
    "subtitle": "The best ways to reach me for research, collaboration, or internships.",
    "crumbs": [("home", "index.html"), ("contact", "contact.html")],
    "og": "contact",
    "intro": (
        "I'm happy to talk about anti-cheat, kernel work, malware triage, "
        "or an internship opportunity. Email is the fastest way to reach me; "
        "Discord works too."
    ),
    "channels": [
        {
            "label": "Email",
            "value": '<a href="mailto:uint64_t@hotmail.com">uint64_t@hotmail.com</a>',
            "note": "First choice. I read it every day.",
            "icon": (
                '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" '
                'stroke="currentColor" stroke-width="1.6" aria-hidden="true">'
                '<rect x="3" y="5" width="18" height="14" rx="2"/>'
                '<path d="M3 7l9 6 9-6"/>'
                '</svg>'
            ),
        },
        {
            "label": "GitHub",
            "value": '<a href="https://github.com/xidenlz" rel="noopener">github.com/xidenlz</a>',
            "note": "Public code, tooling, and repositories.",
            "icon": (
                '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" '
                'stroke="currentColor" stroke-width="1.6" aria-hidden="true">'
                '<path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>'
                '</svg>'
            ),
        },
        {
            "label": "Discord",
            "value": "xdenlz",
            "note": "For quick questions or research chatter.",
            "icon": (
                '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" '
                'stroke="currentColor" stroke-width="1.6" aria-hidden="true">'
                '<path d="M18 5a15 15 0 0 0-4-1l-.2.4a12 12 0 0 0-3.6 0L10 4a15 15 0 0 0-4 1c-2 3-3 6-2.7 9 1.6 1.2 3.1 2 4.6 2.4l1-1.4a9 9 0 0 1-1.6-.8l.4-.3a10 10 0 0 0 8.6 0l.4.3a9 9 0 0 1-1.6.8l1 1.4c1.5-.5 3-1.2 4.6-2.4C21 11 20 8 18 5z"/>'
                '<circle cx="9.5" cy="12" r="1.2" fill="currentColor" stroke="none"/>'
                '<circle cx="14.5" cy="12" r="1.2" fill="currentColor" stroke="none"/>'
                '</svg>'
            ),
        },
    ],
}

NOT_FOUND = {
    "slug": "404",
    "title": "Not found",
    "description": "This URL doesn’t resolve to a page on the site.",
    "og": "home",
    "root": True,
}

# ---------------------------------------------------------------------------
# projects, long form (used by projects.html and homepage cards)
# ---------------------------------------------------------------------------

PROJECTS = {
    "nt-injector": {
        "slug": "nt-injector",
        "category": "Injection framework",
        "status": None,
        "stack": "C++17 · NT native API · driver",
        "title": "NtInjector (NtLoader)",
        "dek": (
            "Windows injection framework built on NT native APIs, no static "
            "IAT footprint, imports resolved by PEB walking. User-mode and "
            "driver dispatch modes."
        ),
        "long_dek": (
            "A Windows injection framework that avoids the Win32 wrapper "
            "layer entirely, no static IAT entries, every function pointer "
            "resolved at runtime by walking the PEB and parsing exports. "
            "Configuration is JSON-driven (<code>ntcfg.json</code>) and the "
            "same binary drives both user-mode and driver-backed injection paths."
        ),
        "primitives": [
            ("Manual map",
             "In-memory PE mapping with relocations, imports, TLS callbacks, "
             "and SEH, without registering the module in the PEB loader lists. "
             "Optional header and section wipe (<code>.pdata</code>, <code>.rsrc</code>, <code>.reloc</code>)."),
            ("LdrLoadDll stub",
             "Writes a small stub plus <code>LDR_DATA</code> into the target "
             "and runs it via <code>NtCreateThreadEx</code>."),
            ("User-mode APC",
             "Enumerates threads with <code>NtQuerySystemInformation</code> "
             "and queues <code>LdrLoadDll</code> with <code>NtQueueApcThread</code> "
             "so it fires the next time the target hits an alertable wait."),
            ("Kernel driver",
             "Dispatches injection through a custom driver "
             "(<code>\\??\\NtKrnldrv</code>) and unloads once it's done."),
        ],
        "tags": ["C++17", "NT native API", "Kernel driver", "Manual map",
                 "PEB walk", "LdrLoadDll"],
        "link_url": "https://www.unknowncheats.me/forum/general-programming-and-reversing/735809-ntldr-windowsnt-injector.html",
        "link_label": "Thread on UnknownCheats",
    },
    "screenshot-bypass": {
        "slug": "screenshot-bypass",
        "category": "Graphics hooking",
        "status": None,
        "stack": "C++ · MinHook · GDI",
        "title": "Screenshot detection bypass",
        "dek": (
            "Hooks <code>gdi32!BitBlt</code> to return a clean framebuffer to "
            "screenshot-based scanners while overlays keep rendering."
        ),
        "long_dek": (
            "A hook on <code>gdi32!BitBlt</code> that returns a clean copy of "
            "the framebuffer to screenshot-based scanners while overlays keep "
            "rendering in test builds. Small research toy, not a product, "
            "the interesting part is how many anti-cheat capture paths still "
            "rely on GDI."
        ),
        "primitives": [
            ("BitBlt hook",
             "Filters overlay layers out of screen-capture buffers."),
            ("Test target",
             "Ships with a dummy overlay process to reproduce the capture path."),
        ],
        "tags": ["C++", "MinHook", "GDI32", "BitBlt", "Anti-cheat"],
        "link_url": "https://github.com/xidenlz/Screenshot-Detection-Bypass",
        "link_label": "Source on GitHub",
    },
    "pe-analyzer": {
        "slug": "pe-analyzer",
        "category": "Binary triage",
        "status": "Private tooling",
        "stack": "Python · C++ · Zydis",
        "title": "PE Analyzer Suite",
        "dek": (
            "Sample-triage tooling, Python for PE/ELF inspection and payload "
            "extraction, C++/Zydis for instruction-level tracing."
        ),
        "long_dek": (
            "Tooling I use for sample triage. Python scripts do the boring "
            "part, parsing PE/ELF headers, dumping embedded binaries by "
            "computing exact offset and size, running heuristic scans over "
            "strings and section entropy. A separate C++ tool uses Zydis to "
            "trace dynamic import resolution when I need to look at how a "
            "sample resolves <code>GetProcAddress</code>."
        ),
        "primitives": [
            ("Embedded binary extraction",
             "Finds nested executables inside a host binary and dumps them "
             "by the exact raw offset and size, no scanning heuristics after "
             "the header is located."),
            ("Heuristics",
             "Section entropy anomalies, string scans for C2 patterns, "
             "Discord webhooks, port-forwarding tunnels, common loader markers."),
            ("Disassembly",
             "Zydis-backed x86/x64 pass for tracing dynamic import "
             "resolution and following calls to <code>GetProcAddress</code>."),
        ],
        "tags": ["Python", "C++", "Zydis", "PE/ELF", "Triage"],
        "link_url": None,
    },
}

# ---------------------------------------------------------------------------
# articles, index metadata; bodies live in articles.py
# ---------------------------------------------------------------------------

def _art(slug, kind, category, title, dek, short_dek, meta_desc, tags,
         when, body):
    words = len(body.split())
    return {
        "kind": kind,
        "slug": slug,
        "parent": "research" if kind == "research" else "blog",
        "category": category,
        "title": title,
        "dek": dek,
        "short_dek": short_dek,
        "meta_description": meta_desc,
        "tags": tags,
        "date": when,
        "date_display": when.strftime("%B %-d, %Y") if hasattr(when, "strftime") else when,
        "word_count": words,
        "body": body,
    }

# Windows doesn't support %-d in strftime, swap for manual formatting.
def _fmt(d):
    return d.strftime("%B ") + str(d.day) + d.strftime(", %Y")


ARTICLES = {
    "battleye-internals": {
        "kind": "research",
        "slug": "battleye-internals",
        "parent": "research",
        "category": "Anti-cheat · Kernel",
        "title": "BattlEye: kernel-side stack walking",
        "dek": (
            "How BattlEye walks a thread's call stack from kernel mode. "
            "Traces thread lookup with <code>PsLookupThreadByThreadId</code>, "
            "APC-driven collection with <code>RtlWalkFrameChain</code>, "
            "image-range validation, and how findings reach "
            "<code>BEDaisy::Report::ThreadStackReport</code>."
        ),
        "short_dek": (
            "How BattlEye walks a thread's stack from kernel mode: "
            "<code>PsLookupThreadByThreadId</code>, an APC, "
            "<code>RtlWalkFrameChain</code>, and the report path."
        ),
        "meta_description": (
            "BattlEye kernel-side stack walking, thread lookup, APC-driven "
            "capture with RtlWalkFrameChain, image-boundary checks, and "
            "report dispatch."
        ),
        "tags": ["Kernel", "APC", "RtlWalkFrameChain", "Anti-cheat",
                 "Stack walking", "Reverse engineering"],
        "date": date(2026, 6, 12),
        "date_display": _fmt(date(2026, 6, 12)),
        "word_count": len(ARTICLE_BODIES["battleye-internals"].split()),
        "body": ARTICLE_BODIES["battleye-internals"],
    },
    "windows-kernel-callbacks": {
        "kind": "post",
        "slug": "windows-kernel-callbacks",
        "parent": "blog",
        "category": "Kernel",
        "title": "Windows kernel process and thread callbacks",
        "dek": (
            "How security drivers watch process lifecycles and strip access "
            "with <code>PsSetCreateProcessNotifyRoutineEx</code> and "
            "<code>ObRegisterCallbacks</code>."
        ),
        "short_dek": (
            "How drivers watch process lifecycles and strip handle access "
            "using <code>PsSetCreateProcessNotifyRoutineEx</code> and "
            "<code>ObRegisterCallbacks</code>."
        ),
        "meta_description": (
            "Windows kernel process and thread notification callbacks, "
            "PsSetCreateProcessNotifyRoutineEx and ObRegisterCallbacks in "
            "practice."
        ),
        "tags": ["Windows kernel", "Callbacks", "Security drivers", "x64"],
        "date": date(2026, 2, 18),
        "date_display": _fmt(date(2026, 2, 18)),
        "word_count": len(ARTICLE_BODIES["windows-kernel-callbacks"].split()),
        "body": ARTICLE_BODIES["windows-kernel-callbacks"],
    },
    "pe-headers-deep-dive": {
        "kind": "post",
        "slug": "pe-headers-deep-dive",
        "parent": "blog",
        "category": "PE format",
        "title": "PE optional headers and data directories",
        "dek": (
            "A walk through <code>IMAGE_OPTIONAL_HEADER64</code>: section "
            "alignment, RVA-to-offset math, and the data directories the "
            "Windows loader actually reads."
        ),
        "short_dek": (
            "<code>IMAGE_OPTIONAL_HEADER64</code>, section alignment, "
            "RVA-to-file-offset math, and the 16 data directories."
        ),
        "meta_description": (
            "The PE Optional Header explained, IMAGE_OPTIONAL_HEADER64, "
            "section alignment, RVA to file-offset conversion, data directories."
        ),
        "tags": ["PE32+", "Windows loader", "Virtual memory", "C/C++"],
        "date": date(2026, 3, 1),
        "date_display": _fmt(date(2026, 3, 1)),
        "word_count": len(ARTICLE_BODIES["pe-headers-deep-dive"].split()),
        "body": ARTICLE_BODIES["pe-headers-deep-dive"],
    },
    "overlays-and-malware-injection-mechanisms": {
        "kind": "post",
        "slug": "overlays-and-malware-injection-mechanisms",
        "parent": "blog",
        "category": "Windows internals",
        "title": "Overlays and malware share the same primitives",
        "dek": (
            "Steam and Discord overlays, EDR agents, and process-injection "
            "malware all reach for the same handful of Windows APIs. Notes "
            "on the shared surface."
        ),
        "short_dek": (
            "Steam, Discord, EDRs, and injectors all use the same handful "
            "of Windows primitives. Notes on the shared surface."
        ),
        "meta_description": (
            "Overlays, EDR agents, and process-injection malware share the "
            "same Windows primitives, DLL injection, thread hijacking, "
            "LdrLoadDll, swap-chain hooks."
        ),
        "tags": ["Process injection", "Thread hijacking", "DirectX",
                 "LdrLoadDll"],
        "date": date(2025, 11, 6),
        "date_display": _fmt(date(2025, 11, 6)),
        "word_count": len(ARTICLE_BODIES["overlays-and-malware-injection-mechanisms"].split()),
        "body": ARTICLE_BODIES["overlays-and-malware-injection-mechanisms"],
    },
    "defeating-malware-obfuscation-xor": {
        "kind": "post",
        "slug": "defeating-malware-obfuscation-xor",
        "parent": "blog",
        "category": "Reverse engineering",
        "title": "XOR string de-obfuscation, in practice",
        "dek": (
            "Recognizing SSE-vectorized XOR routines in IDA, working the "
            "key out by hand, and a small Python helper for doing it in bulk."
        ),
        "short_dek": (
            "Recognizing <code>_mm_xor_ps</code> in IDA, working out the "
            "key, and a small Python helper for doing it in bulk."
        ),
        "meta_description": (
            "Undoing inline XOR string obfuscation, reading vectorized "
            "_mm_xor_ps in IDA, computing the XOR key, and automating with Python."
        ),
        "tags": ["Reverse engineering", "XOR", "IDA Pro", "Python"],
        "date": date(2025, 9, 14),
        "date_display": _fmt(date(2025, 9, 14)),
        "word_count": len(ARTICLE_BODIES["defeating-malware-obfuscation-xor"].split()),
        "body": ARTICLE_BODIES["defeating-malware-obfuscation-xor"],
    },
    "fast-triage-three-pe-flags": {
        "kind": "post",
        "slug": "fast-triage-three-pe-flags",
        "parent": "blog",
        "category": "Malware triage",
        "title": "Fast triage: three PE flags before I open IDA",
        "dek": (
            "A faster pass than opening IDA every time. Three questions I "
            "answer from the PE first: does it talk to the network, does "
            "it have real imports, and does it drop another binary."
        ),
        "short_dek": (
            "Three questions I answer from the PE first: does it talk to "
            "the network, does it have real imports, and does it drop "
            "another binary."
        ),
        "meta_description": (
            "How I triage Windows binaries fast by reading the PE first. "
            "Three flags I check before opening a disassembler: internet "
            "activity, dynamic import resolution, and embedded payloads."
        ),
        "tags": ["Malware triage", "PE format", "Static analysis",
                 "Zydis", "FLOSS"],
        "date": date(2026, 8, 28),
        "date_display": _fmt(date(2026, 8, 28)),
        "word_count": len(ARTICLE_BODIES["fast-triage-three-pe-flags"].split()),
        "body": ARTICLE_BODIES["fast-triage-three-pe-flags"],
    },
    "triage-quasar-rat-case-study": {
        "kind": "post",
        "slug": "triage-quasar-rat-case-study",
        "parent": "blog",
        "category": "Malware triage",
        "title": "Quasar RAT dressed as a game cheat",
        "dek": (
            "A community submission that looked like a cheat: a hollow VB DLL, "
            "a Go dropper, and a Quasar RAT calling home over a Portmap tunnel."
        ),
        "short_dek": (
            "A hollow VB DLL, a Go dropper, and a Quasar RAT reaching a "
            "Portmap tunnel, a submission I flagged during triage."
        ),
        "meta_description": (
            "Triage of a Quasar RAT submitted as a game cheat, decoy VB DLL, "
            "Go dropper, Portmap C2, and how it was caught."
        ),
        "tags": ["Malware triage", "Quasar RAT", "Any.Run", "Threat intel"],
        "date": date(2025, 5, 22),
        "date_display": _fmt(date(2025, 5, 22)),
        "word_count": len(ARTICLE_BODIES["triage-quasar-rat-case-study"].split()),
        "body": ARTICLE_BODIES["triage-quasar-rat-case-study"],
    },
}
