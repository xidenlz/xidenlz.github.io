"""
Article body HTML for the site.

Each entry is the inner HTML that goes inside `<article class="prose">…</article>`.
Do not add opening/closing prose tags here, build.py wraps them.
Every technical claim (function name, hex value, struct field, path)
mirrors the original write-ups.
"""

BATTLEYE = r"""
<p>
  BattlEye keeps a running check on <em>where</em> code is executing from,
  not just <em>what</em> is loaded. The routine I want to describe here
  is the one that walks a thread’s call stack from the kernel, validates
  the return addresses against known image ranges, and reports the result
  through <code>BEDaisy</code>.
</p>

<p>
  The reason it matters: a manually mapped image never shows up in the PEB’s
  loader lists. Enumerating modules will miss it. But the manually mapped
  code still leaves return addresses on some thread’s stack. Walking that
  stack, then asking whether each frame lands inside a legitimately loaded
  image, is a different signal than enumerating modules, and a much harder
  one to hide from.
</p>

<div class="note">
  <span class="note-label">Core idea</span>
  <p>
    Stack walking asks where instructions are executing right now, not where
    the module list <em>says</em> they should be. An address that lands
    outside every known image range doesn’t prove a manual map. It’s a
    starting point for further checks.
  </p>
</div>

<h2>1. Getting a reference to the target thread</h2>
<p>
  The routine begins by resolving the target thread. If the ID doesn’t match
  the caller, it grabs an <code>ETHREAD</code> reference through
  <code>PsLookupThreadByThreadId</code>:
</p>

<div class="snippet">
  <div class="snippet-bar">
    <span class="snippet-lang">C · decompiled</span>
    <span class="snippet-name">thread lookup</span>
  </div>
  <pre><code><span class="syn-var">CurrentThreadId</span> <span class="syn-op">=</span> <span class="syn-fn">PsGetCurrentThreadId</span><span class="syn-op">();</span>

<span class="syn-kwd">if</span> <span class="syn-op">(</span><span class="syn-var">v20</span> <span class="syn-op">!=</span> <span class="syn-var">CurrentThreadId</span><span class="syn-op">)</span>
<span class="syn-op">{</span>
    <span class="syn-fn">LODWORD</span><span class="syn-op">(</span><span class="syn-var">CurrentThreadId</span><span class="syn-op">)</span> <span class="syn-op">=</span>
        <span class="syn-fn">PsLookupThreadByThreadId</span><span class="syn-op">(</span><span class="syn-var">v20</span><span class="syn-op">,</span> <span class="syn-op">&amp;</span><span class="syn-var">Thread</span><span class="syn-op">);</span>
<span class="syn-op">}</span></code></pre>
</div>

<p>
  With the <code>ETHREAD</code> in hand, the driver allocates a context in
  non-paged pool and sets up an APC:
</p>

<div class="snippet">
  <div class="snippet-bar">
    <span class="snippet-lang">C · decompiled</span>
    <span class="snippet-name">APC init and queue</span>
  </div>
  <pre><code><span class="syn-fn">KeInitializeApc</span><span class="syn-op">(</span>
    <span class="syn-var">AllocatedPool</span><span class="syn-op">,</span>
    <span class="syn-var">Thread</span><span class="syn-op">,</span>
    <span class="syn-num">0</span><span class="syn-op">,</span>
    <span class="syn-var">UpdateCurrnetStack</span><span class="syn-op">,</span>
    <span class="syn-num">0</span><span class="syn-op">,</span>
    <span class="syn-num">0</span><span class="syn-op">,</span>
    <span class="syn-num">0</span><span class="syn-op">,</span>
    <span class="syn-num">0</span>
<span class="syn-op">);</span>

<span class="syn-fn">KeInsertQueueApc</span><span class="syn-op">(</span>
    <span class="syn-var">AllocatedPool</span><span class="syn-op">,</span>
    <span class="syn-var">AllocatedPool</span><span class="syn-op">,</span>
    <span class="syn-num">0</span><span class="syn-op">,</span>
    <span class="syn-num">2</span>
<span class="syn-op">);</span></code></pre>
</div>

<p>
  The APC is the interesting choice. Instead of trying to walk another
  thread’s stack from outside its context, which would race with anything
  that thread was doing, the collection runs inside the target thread when
  the APC fires. The caller then just waits on a signaled event.
</p>

<p>
  (The typo <code>UpdateCurrnetStack</code> is theirs. I left it as it appears
  in the binary.)
</p>

<h2>2. Collecting frames with RtlWalkFrameChain</h2>
<p>
  When the APC lands in the target thread, it hits this callback:
</p>

<div class="snippet">
  <div class="snippet-bar">
    <span class="snippet-lang">C · decompiled</span>
    <span class="snippet-name">StackUpdater</span>
  </div>
  <pre><code><span class="syn-type">LONG</span> <span class="syn-kwd">__fastcall</span> <span class="syn-fn">StackUpdater</span><span class="syn-op">(</span>
    <span class="syn-type">__int64</span> <span class="syn-var">threadContext</span><span class="syn-op">,</span>
    <span class="syn-type">__int64</span> <span class="syn-var">flags</span><span class="syn-op">,</span>
    <span class="syn-type">__int64</span> <span class="syn-var">priority</span><span class="syn-op">,</span>
    <span class="syn-type">__int64</span> <span class="syn-op">*</span><span class="syn-var">frame_pointer</span><span class="syn-op">)</span>
<span class="syn-op">{</span>
    <span class="syn-type">__int64</span> <span class="syn-var">frame</span><span class="syn-op">;</span>

    <span class="syn-var">frame</span> <span class="syn-op">=</span> <span class="syn-op">*</span><span class="syn-var">frame_pointer</span><span class="syn-op">;</span>

    <span class="syn-op">*(</span><span class="syn-type">_DWORD</span> <span class="syn-op">*)(</span><span class="syn-var">frame</span> <span class="syn-op">+</span> <span class="syn-num">2160</span><span class="syn-op">)</span> <span class="syn-op">=</span>
        <span class="syn-fn">RtlWalkFrameChain</span><span class="syn-op">(</span>
            <span class="syn-op">(</span><span class="syn-type">PVOID</span> <span class="syn-op">*)(*</span><span class="syn-var">frame_pointer</span> <span class="syn-op">+</span> <span class="syn-num">0x70</span><span class="syn-op">),</span>
            <span class="syn-num">0x100</span><span class="syn-op">,</span>
            <span class="syn-num">0</span><span class="syn-op">);</span>

    <span class="syn-kwd">return</span> <span class="syn-fn">KeSetEvent</span><span class="syn-op">(</span>
        <span class="syn-op">(</span><span class="syn-type">PRKEVENT</span><span class="syn-op">)(</span><span class="syn-var">frame</span> <span class="syn-op">+</span> <span class="syn-num">0x58</span><span class="syn-op">),</span>
        <span class="syn-num">0</span><span class="syn-op">,</span>
        <span class="syn-num">0</span><span class="syn-op">);</span>
<span class="syn-op">}</span></code></pre>
</div>

<p>
  The important call is:
</p>

<div class="snippet">
  <div class="snippet-bar">
    <span class="snippet-lang">C</span>
    <span class="snippet-name">frame chain capture</span>
  </div>
  <pre><code><span class="syn-fn">RtlWalkFrameChain</span><span class="syn-op">(...,</span> <span class="syn-num">0x100</span><span class="syn-op">,</span> <span class="syn-num">0</span><span class="syn-op">);</span></code></pre>
</div>

<p>
  Up to <code>0x100</code> (256) frames get written into the context, the
  count goes into the same context at offset <code>+2160</code>, and
  <code>KeSetEvent</code> unblocks the collector thread.
</p>

<h2>3. Validating each frame against known image ranges</h2>
<p>
  Once the frames are back with the caller, each one is checked against a
  table of known image ranges. In decompiled form the check looks like this:
</p>

<div class="snippet">
  <div class="snippet-bar">
    <span class="snippet-lang">C · decompiled</span>
    <span class="snippet-name">range check</span>
  </div>
  <pre><code><span class="syn-var">_RDX</span> <span class="syn-op">=</span> <span class="syn-op">*(</span><span class="syn-type">_QWORD</span> <span class="syn-op">*)&amp;</span><span class="syn-var">AllocatedPool</span><span class="syn-op">[</span><span class="syn-num">2</span> <span class="syn-op">*</span> <span class="syn-var">v38</span> <span class="syn-op">+</span> <span class="syn-num">28</span><span class="syn-op">];</span>

<span class="syn-kwd">if</span> <span class="syn-op">(</span><span class="syn-var">_RDX</span> <span class="syn-op">&lt;</span> <span class="syn-var">_RCX</span> <span class="syn-op">||</span>
    <span class="syn-var">_RDX</span> <span class="syn-op">&gt;=</span> <span class="syn-op">*(</span><span class="syn-type">unsigned int</span> <span class="syn-op">*)(</span><span class="syn-var">qword_1400171D8</span> <span class="syn-op">+</span> <span class="syn-num">32</span><span class="syn-op">)</span> <span class="syn-op">+</span> <span class="syn-var">_RCX</span><span class="syn-op">)</span>
<span class="syn-op">{</span></code></pre>
</div>

<div class="note note-warn">
  <span class="note-label">Read it carefully</span>
  <p>
    A frame outside every known image range is <em>not</em> a “gotcha”.
    It’s an execution address that doesn’t sit in any expected module,
    which is enough to feed the report pipeline. What happens next is the
    interesting part.
  </p>
</div>

<h2>4. Reporting</h2>
<p>
  The results, frames, thread context, per-module offsets, get bundled up
  and passed to one of two report paths depending on how the routine got
  invoked:
</p>

<div class="snippet">
  <div class="snippet-bar">
    <span class="snippet-lang">C++ · decompiled</span>
    <span class="snippet-name">primary report path</span>
  </div>
  <pre><code><span class="syn-fn">BEDaisy::Report::ThreadStackReport</span><span class="syn-op">(</span>
    <span class="syn-var">v127</span><span class="syn-op">,</span>
    <span class="syn-var">v103</span>
<span class="syn-op">);</span></code></pre>
</div>

<div class="snippet">
  <div class="snippet-bar">
    <span class="snippet-lang">C · decompiled</span>
    <span class="snippet-name">alternate APC report path</span>
  </div>
  <pre><code><span class="syn-fn">FnThreadApcStackReport</span><span class="syn-op">(</span><span class="syn-var">v127</span><span class="syn-op">,</span> <span class="syn-var">v103</span><span class="syn-op">);</span></code></pre>
</div>

<h2>5. Full flow</h2>
<p>
  The six stages together:
</p>

<figure>
  <img src="../assets/diagrams/battleye_stack_flow.svg"
       alt="Six-stage flow: thread lookup, APC dispatch, frame capture, image bounds check, aggregation, report dispatch."
       loading="lazy" width="760" height="700">
  <figcaption>Kernel-side flow of the BattlEye stack-walking routine.</figcaption>
</figure>

<h2>Takeaway</h2>
<p>
  The routine is best described as <strong>execution-origin validation over
  a captured stack</strong>, not a manual-map detector. Manually mapped
  images are one thing it will catch; JIT’d code, shellcode, inline hooks,
  and generated trampolines can all leave frames outside every mapped
  image too.
</p>
<p>
  What made this worth writing up is the design choice, not the check
  itself. Running the collection inside the target thread on an APC lets
  the driver capture a coherent, atomic view of the stack without the
  synchronization mess of walking a foreign thread from outside. The
  boundary check that follows is almost mechanical once you have that view.
</p>
"""

KERNEL_CALLBACKS = r"""
<p>
  On 64-bit Windows, PatchGuard rules out most of the tricks security
  drivers used to reach for, SSDT hooks, inline patches on kernel code.
  What Microsoft gave everyone else in exchange is a small set of
  documented callback interfaces. Drivers register a function, the kernel
  calls it when the right thing happens, and that’s the whole surface.
</p>
<p>
  Two of these carry most of the weight for EDR and anti-cheat work: the
  process notification routines and the Object Manager callbacks. I want
  to look at both.
</p>

<h2>Process creation notifications</h2>
<p>
  A driver registers for process events with
  <code>PsSetCreateProcessNotifyRoutineEx</code>. The callback gets a
  <code>PS_CREATE_NOTIFY_INFO</code> pointer on creation, holding:
</p>
<ul>
  <li>Parent PID and creator thread ID.</li>
  <li>The full image path of the new executable.</li>
  <li>The command line.</li>
  <li>A writeable <code>CreationStatus</code> the driver can set to <code>STATUS_ACCESS_DENIED</code> to abort the launch.</li>
</ul>
<p>
  On termination the same callback fires with <code>CreateInfo == NULL</code>.
</p>

<div class="snippet">
  <div class="snippet-bar">
    <span class="snippet-lang">C</span>
    <span class="snippet-name">process notify callback</span>
  </div>
  <pre><code><span class="syn-type">VOID</span> <span class="syn-fn">ProcessNotifyCallbackEx</span><span class="syn-op">(</span>
    <span class="syn-type">PEPROCESS</span> <span class="syn-var">Process</span><span class="syn-op">,</span>
    <span class="syn-type">HANDLE</span> <span class="syn-var">ProcessId</span><span class="syn-op">,</span>
    <span class="syn-type">PPS_CREATE_NOTIFY_INFO</span> <span class="syn-var">CreateInfo</span>
<span class="syn-op">)</span> <span class="syn-op">{</span>
    <span class="syn-kwd">if</span> <span class="syn-op">(</span><span class="syn-var">CreateInfo</span> <span class="syn-op">!=</span> <span class="syn-num">NULL</span><span class="syn-op">)</span> <span class="syn-op">{</span>
        <span class="syn-com">// process is starting</span>
        <span class="syn-fn">KdPrint</span><span class="syn-op">((</span><span class="syn-str">"[+] spawn PID %llu | %wZ\n"</span><span class="syn-op">,</span>
            <span class="syn-op">(</span><span class="syn-type">ULONG_PTR</span><span class="syn-op">)</span><span class="syn-var">ProcessId</span><span class="syn-op">,</span> <span class="syn-var">CreateInfo</span><span class="syn-op">-&gt;</span><span class="syn-var">ImageFileName</span><span class="syn-op">));</span>

        <span class="syn-kwd">if</span> <span class="syn-op">(</span><span class="syn-fn">IsBlockedBinary</span><span class="syn-op">(</span><span class="syn-var">CreateInfo</span><span class="syn-op">-&gt;</span><span class="syn-var">ImageFileName</span><span class="syn-op">))</span> <span class="syn-op">{</span>
            <span class="syn-var">CreateInfo</span><span class="syn-op">-&gt;</span><span class="syn-var">CreationStatus</span> <span class="syn-op">=</span> <span class="syn-num">STATUS_ACCESS_DENIED</span><span class="syn-op">;</span>
        <span class="syn-op">}</span>
    <span class="syn-op">}</span> <span class="syn-kwd">else</span> <span class="syn-op">{</span>
        <span class="syn-fn">KdPrint</span><span class="syn-op">((</span><span class="syn-str">"[-] exit  PID %llu\n"</span><span class="syn-op">,</span> <span class="syn-op">(</span><span class="syn-type">ULONG_PTR</span><span class="syn-op">)</span><span class="syn-var">ProcessId</span><span class="syn-op">));</span>
    <span class="syn-op">}</span>
<span class="syn-op">}</span></code></pre>
</div>

<div class="note">
  <span class="note-label">Watch the IRQL</span>
  <p>
    The callback runs at <code>PASSIVE_LEVEL</code>, so paged memory is fair
    game, but the callback array is limited to 64 entries system-wide.
    Registering and unregistering blindly during driver load and unload is
    a fast way to leak slots on a busy system.
  </p>
</div>

<h2>Object Manager callbacks: ObRegisterCallbacks</h2>
<p>
  Process notifications tell you what happened. <code>ObRegisterCallbacks</code>
  lets you intervene <em>before</em> a handle to <code>*PsProcessType</code>
  or <code>*PsThreadType</code> is returned to the caller.
</p>
<p>
  In the pre-operation callback the driver reads
  <code>OperationInformation-&gt;Parameters-&gt;CreateHandleInformation.DesiredAccess</code>
  and can mask off rights before the Object Manager hands the handle back.
</p>

<div class="snippet">
  <div class="snippet-bar">
    <span class="snippet-lang">C</span>
    <span class="snippet-name">pre-op handle filter</span>
  </div>
  <pre><code><span class="syn-type">OB_PREOP_CALLBACK_STATUS</span> <span class="syn-fn">HandlePreCallback</span><span class="syn-op">(</span>
    <span class="syn-type">PVOID</span> <span class="syn-var">RegistrationContext</span><span class="syn-op">,</span>
    <span class="syn-type">POB_PRE_OPERATION_INFORMATION</span> <span class="syn-var">OpInfo</span>
<span class="syn-op">)</span> <span class="syn-op">{</span>
    <span class="syn-kwd">if</span> <span class="syn-op">(</span><span class="syn-var">OpInfo</span><span class="syn-op">-&gt;</span><span class="syn-var">ObjectType</span> <span class="syn-op">==</span> <span class="syn-op">*</span><span class="syn-type">PsProcessType</span><span class="syn-op">)</span> <span class="syn-op">{</span>
        <span class="syn-type">PEPROCESS</span> <span class="syn-var">TargetProcess</span> <span class="syn-op">=</span> <span class="syn-op">(</span><span class="syn-type">PEPROCESS</span><span class="syn-op">)</span><span class="syn-var">OpInfo</span><span class="syn-op">-&gt;</span><span class="syn-var">Object</span><span class="syn-op">;</span>

        <span class="syn-kwd">if</span> <span class="syn-op">(</span><span class="syn-fn">IsProtectedProcess</span><span class="syn-op">(</span><span class="syn-var">TargetProcess</span><span class="syn-op">))</span> <span class="syn-op">{</span>
            <span class="syn-com">// strip R/W/thread/dup rights before the handle is returned</span>
            <span class="syn-type">ACCESS_MASK</span> <span class="syn-var">MaskToStrip</span> <span class="syn-op">=</span> <span class="syn-num">PROCESS_VM_READ</span> <span class="syn-op">|</span>
                                      <span class="syn-num">PROCESS_VM_WRITE</span> <span class="syn-op">|</span>
                                      <span class="syn-num">PROCESS_VM_OPERATION</span> <span class="syn-op">|</span>
                                      <span class="syn-num">PROCESS_CREATE_THREAD</span> <span class="syn-op">|</span>
                                      <span class="syn-num">PROCESS_DUP_HANDLE</span><span class="syn-op">;</span>

            <span class="syn-var">OpInfo</span><span class="syn-op">-&gt;</span><span class="syn-var">Parameters</span><span class="syn-op">-&gt;</span><span class="syn-var">CreateHandleInformation</span><span class="syn-op">.</span><span class="syn-var">DesiredAccess</span> <span class="syn-op">&amp;=</span> <span class="syn-op">~</span><span class="syn-var">MaskToStrip</span><span class="syn-op">;</span>
        <span class="syn-op">}</span>
    <span class="syn-op">}</span>
    <span class="syn-kwd">return</span> <span class="syn-num">OB_PREOP_SUCCESS</span><span class="syn-op">;</span>
<span class="syn-op">}</span></code></pre>
</div>

<h2>What this closes off</h2>
<p>
  Once a driver is stripping rights on <code>PsProcessType</code>, user-mode
  code trying to <code>OpenProcess</code> a protected target for
  <code>VM_READ</code>/<code>VM_WRITE</code>/<code>CREATE_THREAD</code>
  gets a handle back. But not with those rights. Standard injection
  primitives, ordinary API hooks, most out-of-process debuggers: all
  neutered without any inline patching.
</p>
<p>
  What’s <em>still</em> interesting for anyone poking at these systems is
  the seams: how the driver decides which process to protect, whether that
  decision reads state a caller can influence, and whether an already-open
  handle from before protection kicked in can be duplicated back into
  something useful. That’s where the actual bugs tend to live.
</p>
"""

PE_HEADERS = r"""
<p>
  Every 32- and 64-bit Windows executable and DLL is a PE file. The DOS
  header and COFF file header handle the basic “yes this is a real image”
  check, but the parameters the Windows loader really cares about live in
  <code>IMAGE_OPTIONAL_HEADER</code>. Which, despite the name, is required.
</p>
<p>
  I want to walk through the parts of the optional header that come up
  most often when I’m reading a binary or writing a loader.
</p>

<h2>The 64-bit shape</h2>
<p>
  PE32+ (the 64-bit flavor) widens the fields that hold pointers.
  <code>ImageBase</code>, <code>SizeOfStackReserve</code>,
  <code>SizeOfHeapReserve</code>, and friends become <code>ULONGLONG</code>.
  Everything else keeps its width.
</p>

<div class="snippet">
  <div class="snippet-bar">
    <span class="snippet-lang">C · winnt.h</span>
    <span class="snippet-name">IMAGE_OPTIONAL_HEADER64</span>
  </div>
  <pre><code><span class="syn-kwd">typedef struct</span> <span class="syn-type">_IMAGE_OPTIONAL_HEADER64</span> <span class="syn-op">{</span>
    <span class="syn-type">WORD</span>        <span class="syn-var">Magic</span><span class="syn-op">;</span>                       <span class="syn-com">// 0x020b for PE32+ (x64)</span>
    <span class="syn-type">BYTE</span>        <span class="syn-var">MajorLinkerVersion</span><span class="syn-op">;</span>
    <span class="syn-type">BYTE</span>        <span class="syn-var">MinorLinkerVersion</span><span class="syn-op">;</span>
    <span class="syn-type">DWORD</span>       <span class="syn-var">SizeOfCode</span><span class="syn-op">;</span>
    <span class="syn-type">DWORD</span>       <span class="syn-var">SizeOfInitializedData</span><span class="syn-op">;</span>
    <span class="syn-type">DWORD</span>       <span class="syn-var">SizeOfUninitializedData</span><span class="syn-op">;</span>
    <span class="syn-type">DWORD</span>       <span class="syn-var">AddressOfEntryPoint</span><span class="syn-op">;</span>        <span class="syn-com">// RVA of entry point</span>
    <span class="syn-type">DWORD</span>       <span class="syn-var">BaseOfCode</span><span class="syn-op">;</span>                 <span class="syn-com">// RVA of code section</span>
    <span class="syn-type">ULONGLONG</span>   <span class="syn-var">ImageBase</span><span class="syn-op">;</span>                  <span class="syn-com">// preferred load address, e.g. 0x140000000</span>
    <span class="syn-type">DWORD</span>       <span class="syn-var">SectionAlignment</span><span class="syn-op">;</span>           <span class="syn-com">// in-memory page alignment, usually 0x1000</span>
    <span class="syn-type">DWORD</span>       <span class="syn-var">FileAlignment</span><span class="syn-op">;</span>              <span class="syn-com">// on-disk alignment, usually 0x200</span>
    <span class="syn-type">WORD</span>        <span class="syn-var">MajorOperatingSystemVersion</span><span class="syn-op">;</span>
    <span class="syn-com">// ... subsystem and DLL characteristics ...</span>
    <span class="syn-type">DWORD</span>       <span class="syn-var">NumberOfRvaAndSizes</span><span class="syn-op">;</span>        <span class="syn-com">// number of DataDirectory entries (16)</span>
    <span class="syn-type">IMAGE_DATA_DIRECTORY</span> <span class="syn-var">DataDirectory</span><span class="syn-op">[</span><span class="syn-num">16</span><span class="syn-op">];</span>
<span class="syn-op">}</span> <span class="syn-type">IMAGE_OPTIONAL_HEADER64</span><span class="syn-op">, *</span><span class="syn-type">PIMAGE_OPTIONAL_HEADER64</span><span class="syn-op">;</span></code></pre>
</div>

<h2>Section alignment versus file alignment</h2>
<p>
  These two fields catch people out, especially the first time they try
  to write a manual mapper.
</p>
<ul>
  <li><strong><code>FileAlignment</code></strong> is how sections are packed on disk. Commonly <code>0x200</code>.</li>
  <li><strong><code>SectionAlignment</code></strong> is how they end up in virtual memory. Commonly <code>0x1000</code>, one page.</li>
</ul>
<p>
  Because those numbers are different, an RVA doesn’t line up 1:1 with a
  file offset. To go from RVA to a raw offset you need to find which
  section contains the RVA, then subtract that section’s
  <code>VirtualAddress</code> and add its <code>PointerToRawData</code>:
</p>

<div class="snippet">
  <div class="snippet-bar">
    <span class="snippet-lang">C++</span>
    <span class="snippet-name">RVA -&gt; file offset</span>
  </div>
  <pre><code><span class="syn-type">DWORD</span> <span class="syn-fn">RvaToRawOffset</span><span class="syn-op">(</span><span class="syn-type">DWORD</span> <span class="syn-var">dwRva</span><span class="syn-op">,</span> <span class="syn-type">PIMAGE_NT_HEADERS</span> <span class="syn-var">pNtHeaders</span><span class="syn-op">)</span> <span class="syn-op">{</span>
    <span class="syn-type">PIMAGE_SECTION_HEADER</span> <span class="syn-var">pSection</span> <span class="syn-op">=</span> <span class="syn-fn">IMAGE_FIRST_SECTION</span><span class="syn-op">(</span><span class="syn-var">pNtHeaders</span><span class="syn-op">);</span>
    <span class="syn-kwd">for</span> <span class="syn-op">(</span><span class="syn-type">WORD</span> <span class="syn-var">i</span> <span class="syn-op">=</span> <span class="syn-num">0</span><span class="syn-op">;</span> <span class="syn-var">i</span> <span class="syn-op">&lt;</span> <span class="syn-var">pNtHeaders</span><span class="syn-op">-&gt;</span><span class="syn-var">FileHeader</span><span class="syn-op">.</span><span class="syn-var">NumberOfSections</span><span class="syn-op">;</span> <span class="syn-op">++</span><span class="syn-var">i</span><span class="syn-op">,</span> <span class="syn-op">++</span><span class="syn-var">pSection</span><span class="syn-op">)</span> <span class="syn-op">{</span>
        <span class="syn-kwd">if</span> <span class="syn-op">(</span><span class="syn-var">dwRva</span> <span class="syn-op">&gt;=</span> <span class="syn-var">pSection</span><span class="syn-op">-&gt;</span><span class="syn-var">VirtualAddress</span> <span class="syn-op">&amp;&amp;</span>
            <span class="syn-var">dwRva</span> <span class="syn-op">&lt;</span> <span class="syn-op">(</span><span class="syn-var">pSection</span><span class="syn-op">-&gt;</span><span class="syn-var">VirtualAddress</span> <span class="syn-op">+</span> <span class="syn-var">pSection</span><span class="syn-op">-&gt;</span><span class="syn-var">Misc</span><span class="syn-op">.</span><span class="syn-var">VirtualSize</span><span class="syn-op">))</span> <span class="syn-op">{</span>
            <span class="syn-kwd">return</span> <span class="syn-op">(</span><span class="syn-var">dwRva</span> <span class="syn-op">-</span> <span class="syn-var">pSection</span><span class="syn-op">-&gt;</span><span class="syn-var">VirtualAddress</span><span class="syn-op">)</span> <span class="syn-op">+</span> <span class="syn-var">pSection</span><span class="syn-op">-&gt;</span><span class="syn-var">PointerToRawData</span><span class="syn-op">;</span>
        <span class="syn-op">}</span>
    <span class="syn-op">}</span>
    <span class="syn-kwd">return</span> <span class="syn-num">0</span><span class="syn-op">;</span> <span class="syn-com">// not in any mapped section</span>
<span class="syn-op">}</span></code></pre>
</div>

<h2>The data directories</h2>
<p>
  The tail of the optional header is an array of 16
  <code>IMAGE_DATA_DIRECTORY</code> entries. Each is an RVA plus a size,
  pointing at a subsystem table. The first six are the ones you touch
  most often:
</p>

<div class="table-scroll">
  <table>
    <thead>
      <tr>
        <th>Index</th>
        <th>Directory</th>
        <th>What it points at</th>
      </tr>
    </thead>
    <tbody>
      <tr><td><code>0</code></td><td><code>EXPORT</code></td><td>Exports, functions this DLL makes available.</td></tr>
      <tr><td><code>1</code></td><td><code>IMPORT</code></td><td>Imports, external APIs this image needs.</td></tr>
      <tr><td><code>2</code></td><td><code>RESOURCE</code></td><td>Resources, icons, version info, dialogs.</td></tr>
      <tr><td><code>3</code></td><td><code>EXCEPTION</code></td><td><code>.pdata</code>, x64 SEH unwind data.</td></tr>
      <tr><td><code>4</code></td><td><code>SECURITY</code></td><td>Authenticode signatures (PKCS #7).</td></tr>
      <tr><td><code>5</code></td><td><code>BASERELOC</code></td><td>Relocation fixups if ASLR moves the image.</td></tr>
    </tbody>
  </table>
</div>

<h2>Why this matters in practice</h2>
<p>
  If you’re writing a loader, these fields are the whole contract with the
  OS loader: get the alignment right, walk the sections into memory, apply
  fixups from directory 5, resolve imports from directory 1, and honor
  the entry-point RVA. If you’re doing static analysis on an obfuscated
  sample, understanding what the loader trusts here is often the shortest
  path to figuring out what the sample is hiding.
</p>
"""

OVERLAYS = r"""
<p>
  There’s a set of Windows primitives that sit at the middle of everything
  interesting on the platform: DLL injection, thread hijacking, swap-chain
  hooking, APC-based execution, manual mapping. The same handful of tricks
  are used by Steam’s in-game overlay, Discord’s screen share, EDR agents,
  performance profilers, and every process-injection RAT you’ve ever
  read about.
</p>
<p>
  That’s the interesting bit. The primitives don’t care what you’re
  building. The intent lives at a higher layer.
</p>

<h2>Overlays inject DLLs the same way malware does</h2>
<p>
  When a game starts, <code>steam.exe</code> spawns a helper called
  <code>gameoverlayui64.exe</code> that injects
  <code>gameoverlayui.dll</code> into the game’s address space. The DLL
  then hooks into the graphics pipeline (typically
  <code>IDXGISwapChain::Present</code>) so it can draw friend lists,
  achievement toasts, and the browser over each frame.
</p>
<p>
  Discord does effectively the same thing for its overlay and low-latency
  screen share: inject a hook module, patch the presentation path, draw
  its own UI on top.
</p>

<div class="note">
  <span class="note-label">Dual-use</span>
  <p>
    The requirement is identical to a lot of malware: run custom code
    inside another process, then patch a frequently-called function to
    take control of a rendering (or logging, or input) pipeline. Context
    decides whether that’s an overlay or a keylogger.
  </p>
</div>

<h2>Thread hijacking, step by step</h2>
<p>
  One way to run code in another process without spawning a suspicious new
  thread is to grab an existing one, redirect its instruction pointer, and
  put it back. On x64 that’s <code>RIP</code>; on 32-bit
  <code>EIP</code>. The sequence looks like this:
</p>

<div class="snippet">
  <div class="snippet-bar">
    <span class="snippet-lang">flow</span>
    <span class="snippet-name">thread hijack</span>
  </div>
  <pre><code><span class="syn-var">1. SuspendThread</span>       :  <span class="syn-com">pause the target thread</span>
<span class="syn-var">2. GetThreadContext</span>    :  <span class="syn-com">read the register state (RIP, RSP, ...)</span>
<span class="syn-var">3. VirtualAllocEx</span>      :  <span class="syn-com">allocate memory in the target for the stub</span>
<span class="syn-var">4. SetThreadContext</span>    :  <span class="syn-com">point RIP at the stub</span>
<span class="syn-var">5. ResumeThread</span>        :  <span class="syn-com">stub runs; restores the original RIP when done</span></code></pre>
</div>

<p>
  It’s crude, but it works on anything that doesn’t inspect its own
  contexts, and it’s hard to catch from user mode without a driver watching
  handle rights on the target.
</p>

<h2>The rest of the landscape</h2>
<p>
  Beyond <code>CreateRemoteThread</code> and thread hijacking, the mainline
  Windows primitives that show up over and over:
</p>
<ul>
  <li>
    <strong>Native loader calls.</strong> Calling
    <code>LdrLoadDll</code> inside <code>ntdll.dll</code> directly instead
    of going through <code>LoadLibrary</code>, same effect, fewer hooks
    to trip.
  </li>
  <li>
    <strong>APC injection.</strong>
    <code>NtQueueApcThread</code>
    queues a routine to fire the next time a thread hits an alertable
    wait. Cheap, and it looks nothing like <code>CreateRemoteThread</code>.
  </li>
  <li>
    <strong>Manual / reflective mapping.</strong> Parsing the PE headers
    of an image already in memory, fixing relocations, resolving imports,
    calling the entry point, all without asking the loader to add the
    module to the PEB’s list.
  </li>
  <li>
    <strong>Kernel-mode loaders.</strong> Using a signed (or vulnerable)
    driver to map memory from ring 0, side-stepping every user-mode
    detection surface.
  </li>
</ul>

<h2>Why I keep coming back to this</h2>
<p>
  These aren’t offensive techniques or defensive techniques; they’re just
  Windows techniques. The same hook that renders a Discord overlay is the
  same hook a screenshot tool uses to grab a frame; the same
  <code>NtQueueApcThread</code> that lets a game overlay slot into the
  render thread is the one credential-stealer families reach for. Learning
  to read them at the byte level is what makes it possible to tell one
  from the other.
</p>
"""

XOR = r"""
<p>
  XOR is the cheapest string obfuscation in the book and the one you’ll
  see most often. Malware families use it for API names and C2 strings;
  binary protectors bake it into stub loaders; even some game hacks
  wrap their signature strings in a compile-time XOR macro to keep them
  out of a raw <code>strings</code> dump.
</p>
<p>
  In a decompiler the routines look loud, a wall of SSE loads and an
  <code>_mm_xor_ps</code>, but once you can see the pattern, undoing
  them takes a few seconds.
</p>

<h2>What the un-obfuscated call looks like</h2>
<p>
  Start with something boring. This is what you’d write:
</p>

<div class="snippet">
  <div class="snippet-bar">
    <span class="snippet-lang">C</span>
    <span class="snippet-name">source</span>
  </div>
  <pre><code><span class="syn-fn">printf</span><span class="syn-op">(</span><span class="syn-str">"Hello World!\n"</span><span class="syn-op">);</span></code></pre>
</div>

<p>
  In IDA, that decompiles to something you can read at a glance:
</p>

<div class="snippet">
  <div class="snippet-bar">
    <span class="snippet-lang">C · IDA</span>
    <span class="snippet-name">clean disassembly</span>
  </div>
  <pre><code><span class="syn-fn">sub_140001010</span><span class="syn-op">(</span><span class="syn-str">"Hello World!\n"</span><span class="syn-op">,</span> <span class="syn-var">argv</span><span class="syn-op">,</span> <span class="syn-var">envp</span><span class="syn-op">);</span></code></pre>
</div>

<h2>What the wrapped version looks like</h2>
<p>
  Now the same call, wrapped in a compile-time XOR macro. The compiler
  emits SSE loads for the encrypted bytes and the key, XORs them together,
  and passes the pointer to the resulting stack buffer:
</p>

<div class="snippet">
  <div class="snippet-bar">
    <span class="snippet-lang">C · IDA</span>
    <span class="snippet-name">SIMD-XORed string</span>
  </div>
  <pre><code><span class="syn-var">v5</span><span class="syn-op">.</span><span class="syn-var">m128_u64</span><span class="syn-op">[</span><span class="syn-num">0</span><span class="syn-op">]</span> <span class="syn-op">=</span> <span class="syn-num">0x3B48F9ABEEB37B3Bi64</span><span class="syn-op">;</span>
<span class="syn-var">v5</span><span class="syn-op">.</span><span class="syn-var">m128_u64</span><span class="syn-op">[</span><span class="syn-num">1</span><span class="syn-op">]</span> <span class="syn-op">=</span> <span class="syn-num">0x671AE6872EED461Ei64</span><span class="syn-op">;</span>
<span class="syn-var">v6</span><span class="syn-op">.</span><span class="syn-var">m128_u64</span><span class="syn-op">[</span><span class="syn-num">0</span><span class="syn-op">]</span> <span class="syn-op">=</span> <span class="syn-num">0x541FD9C482DF1E73i64</span><span class="syn-op">;</span>
<span class="syn-var">si128</span> <span class="syn-op">=</span> <span class="syn-op">(</span><span class="syn-type">__m128</span><span class="syn-op">)</span><span class="syn-fn">_mm_load_si128</span><span class="syn-op">((</span><span class="syn-kwd">const</span> <span class="syn-type">__m128i</span> <span class="syn-op">*)&amp;</span><span class="syn-var">v5</span><span class="syn-op">);</span>
<span class="syn-var">v6</span><span class="syn-op">.</span><span class="syn-var">m128_u64</span><span class="syn-op">[</span><span class="syn-num">1</span><span class="syn-op">]</span> <span class="syn-op">=</span> <span class="syn-num">0x671AE68D0F892A6Ci64</span><span class="syn-op">;</span>
<span class="syn-var">v5</span> <span class="syn-op">=</span> <span class="syn-fn">_mm_xor_ps</span><span class="syn-op">(</span><span class="syn-var">si128</span><span class="syn-op">,</span> <span class="syn-var">v6</span><span class="syn-op">);</span>
<span class="syn-fn">sub_140001010</span><span class="syn-op">(&amp;</span><span class="syn-var">v5</span><span class="syn-op">,</span> <span class="syn-var">argv</span><span class="syn-op">,</span> <span class="syn-var">envp</span><span class="syn-op">);</span></code></pre>
</div>

<p>
  <code>_mm_xor_ps</code> is the giveaway. The <code>sub_140001010</code>
  call at the end is the same <code>printf</code> from before, it doesn’t
  care whether the string came from <code>.rdata</code> or from a decoded
  stack buffer.
</p>

<h2>Undoing it by hand</h2>
<p>
  XOR is self-inverse: <code>A ^ B = C</code> implies <code>C ^ B = A</code>.
  Take the encrypted lane and the key lane and XOR them:
</p>

<div class="snippet">
  <div class="snippet-bar">
    <span class="snippet-lang">math</span>
    <span class="snippet-name">first 8 bytes</span>
  </div>
  <pre><code><span class="syn-var">encrypted</span> <span class="syn-op">=</span> <span class="syn-num">0x3B48F9ABEEB37B3B</span>
<span class="syn-var">key</span>       <span class="syn-op">=</span> <span class="syn-num">0x541FD9C482DF1E73</span>
<span class="syn-op">------------------------------</span>
<span class="syn-var">result</span>    <span class="syn-op">=</span> <span class="syn-num">0x6F57206F6C6C6548</span></code></pre>
</div>

<p>
  Read that little-endian:
</p>
<ul>
  <li><code>48 65 6C 6C 6F 20 57 6F</code> → <strong>“Hello Wo”</strong>.</li>
  <li>The second lane resolves to <strong>“rld!\n”</strong>, matching the source.</li>
</ul>

<h2>A tiny helper</h2>
<p>
  Doing this by hand for every string in a real sample gets old.
  I keep a small helper around for it:
</p>

<div class="snippet">
  <div class="snippet-bar">
    <span class="snippet-lang">Python</span>
    <span class="snippet-name">xor.py</span>
  </div>
  <pre><code><span class="syn-com"># hex helper</span>
<span class="syn-kwd">def</span> <span class="syn-fn">ToHex</span><span class="syn-op">(</span><span class="syn-var">Param</span><span class="syn-op">):</span>
    <span class="syn-kwd">return</span> <span class="syn-fn">hex</span><span class="syn-op">(</span><span class="syn-var">Param</span><span class="syn-op">)</span>

<span class="syn-com"># the actual work</span>
<span class="syn-kwd">def</span> <span class="syn-fn">XOR</span><span class="syn-op">(</span><span class="syn-var">Key</span><span class="syn-op">,</span> <span class="syn-var">Str</span><span class="syn-op">):</span>
    <span class="syn-kwd">return</span> <span class="syn-var">Key</span> <span class="syn-op">^</span> <span class="syn-var">Str</span>

<span class="syn-com"># little-endian order, reverse to read as ASCII</span>
<span class="syn-kwd">def</span> <span class="syn-fn">Translate</span><span class="syn-op">(</span><span class="syn-var">Result</span><span class="syn-op">):</span>
    <span class="syn-kwd">for</span> <span class="syn-var">i</span> <span class="syn-kwd">in</span> <span class="syn-fn">reversed</span><span class="syn-op">(</span><span class="syn-var">Result</span><span class="syn-op">):</span>
        <span class="syn-fn">print</span><span class="syn-op">(</span><span class="syn-var">i</span><span class="syn-op">)</span>

<span class="syn-kwd">def</span> <span class="syn-fn">Compare</span><span class="syn-op">(</span><span class="syn-var">Out</span><span class="syn-op">):</span>
    <span class="syn-kwd">return</span> <span class="syn-fn">int</span><span class="syn-op">(</span><span class="syn-var">Out</span><span class="syn-op">,</span> <span class="syn-num">16</span><span class="syn-op">)</span>

<span class="syn-var">Key</span>      <span class="syn-op">=</span> <span class="syn-fn">Compare</span><span class="syn-op">(</span><span class="syn-fn">input</span><span class="syn-op">(</span><span class="syn-str">'Key: '</span><span class="syn-op">))</span>
<span class="syn-var">StrValue</span> <span class="syn-op">=</span> <span class="syn-fn">Compare</span><span class="syn-op">(</span><span class="syn-fn">input</span><span class="syn-op">(</span><span class="syn-str">'String: '</span><span class="syn-op">))</span>

<span class="syn-var">Result</span> <span class="syn-op">=</span> <span class="syn-fn">XOR</span><span class="syn-op">(</span><span class="syn-var">Key</span><span class="syn-op">,</span> <span class="syn-var">StrValue</span><span class="syn-op">)</span>
<span class="syn-fn">print</span><span class="syn-op">(</span><span class="syn-str">'XOR:'</span><span class="syn-op">,</span> <span class="syn-fn">ToHex</span><span class="syn-op">(</span><span class="syn-var">Result</span><span class="syn-op">).</span><span class="syn-fn">upper</span><span class="syn-op">())</span>

<span class="syn-var">length</span> <span class="syn-op">=</span> <span class="syn-op">(</span><span class="syn-var">Result</span><span class="syn-op">.</span><span class="syn-fn">bit_length</span><span class="syn-op">()</span> <span class="syn-op">+</span> <span class="syn-num">7</span><span class="syn-op">)</span> <span class="syn-op">//</span> <span class="syn-num">8</span>
<span class="syn-kwd">try</span><span class="syn-op">:</span>
    <span class="syn-var">AsciiOut</span> <span class="syn-op">=</span> <span class="syn-var">Result</span><span class="syn-op">.</span><span class="syn-fn">to_bytes</span><span class="syn-op">(</span><span class="syn-var">length</span><span class="syn-op">,</span> <span class="syn-str">'big'</span><span class="syn-op">).</span><span class="syn-fn">decode</span><span class="syn-op">(</span><span class="syn-str">'ascii'</span><span class="syn-op">)</span>
    <span class="syn-fn">Translate</span><span class="syn-op">(</span><span class="syn-var">AsciiOut</span><span class="syn-op">)</span>
<span class="syn-kwd">except</span> <span class="syn-type">UnicodeDecodeError</span><span class="syn-op">:</span>
    <span class="syn-fn">print</span><span class="syn-op">(</span><span class="syn-str">'UnicodeDecodeError!'</span><span class="syn-op">)</span></code></pre>
</div>

<p>
  The whole thing is up at
  <a href="https://github.com/xidenlz/xor_calculator/blob/main/xor/Py/xor.py" rel="noopener">xor_calculator</a>.
  For any real sample I’d rather run it inside IDAPython so it can pull the
  constants straight out of the IDA database, but the standalone version is
  useful when you just want to sanity-check a lane by hand.
</p>

<h2>What to remember</h2>
<p>
  Once you can recognize <code>_mm_load_si128</code> paired with
  <code>_mm_xor_ps</code>, or the scalar equivalent of a wide load
  followed by a byte-wise XOR, the entire family of inline XOR
  obfuscations shrinks to a two-minute exercise. The keys are almost
  always right there in the same function, sometimes in the same
  basic block.
</p>
"""

QUASAR = r"""
<p>
  This one came out of routine community triage. An archive was submitted
  to a game-security board as “a working cheat”, and it got flagged for a
  closer look because it looked odd, three binaries, one of them written
  in Go, and an uploader account that was less than a week old.
</p>
<p>
  Static and dynamic passes both agreed: the archive was a decoy shell
  around a <strong>Quasar RAT</strong> reaching for a Portmap tunnel. This
  is what the check looked like.
</p>

<div class="note note-warn">
  <span class="note-label">Verdict</span>
  <p>
    <strong>Reject / malicious.</strong> Multi-stage social-engineering
    package: two decoy binaries, a Go dropper, and a Quasar RAT payload
    connecting to a dynamic C2 endpoint.
  </p>
</div>

<h2>The three binaries in the archive</h2>

<h3>1. The decoy DLL (Visual Basic)</h3>
<p>
  First binary was a VB-compiled DLL. Decompiling it showed nothing but
  dummy UI components, checkboxes, combo boxes, a couple of frames, with
  no hooks, no memory-reading code, and no game interaction of any kind.
  Its whole job was to look like a plausible cheat DLL on cursory inspection.
</p>

<h3>2. A 136 KB C++ stub</h3>
<p>
  Second was a 136 KB C++ executable. String analysis of the entry point
  turned up unreferenced hash-looking strings and a bunch of dead metadata.
  Padding, essentially. Enough to distract a fast heuristic scanner and
  push the overall file size up.
</p>

<h3>3. Run.exe (Go dropper)</h3>
<p>
  The interesting one. Three things stood out:
</p>
<ul>
  <li><strong>Language.</strong> Go, common in commodity droppers because the runtime bulks the binary out and blurs the surface, but very unusual for anything claiming to be a low-level game modification.</li>
  <li><strong>Size and entropy.</strong> Packed footprint with high-entropy sections.</li>
  <li><strong>VT ratio.</strong> Initial pass came back <strong>17/71</strong>. A solid chunk of engines already flagging generic trojan-dropper behavior.</li>
</ul>

<h2>Where it was calling home</h2>

<div class="snippet">
  <div class="snippet-bar">
    <span class="snippet-lang">indicator</span>
    <span class="snippet-name">network</span>
  </div>
  <pre><code><span class="syn-var">domain</span>   <span class="syn-op">=</span> <span class="syn-str">ramsadaye-38594.portmap.io</span>
<span class="syn-var">service</span>  <span class="syn-op">=</span> <span class="syn-type">Portmap.io (TCP tunneling)</span>
<span class="syn-var">note</span>     <span class="syn-op">=</span> <span class="syn-com">subdomain prefix matched an uploader handle</span>
                                <span class="syn-com">registered 5 days prior</span></code></pre>
</div>

<p>
  Portmap.io is a tunneling service, common in this kind of dropper because
  it lets whoever’s operating the RAT accept inbound connections without
  opening a port on their own ISP. The subdomain prefix lining up with an
  account created five days earlier tied the C2 to the uploader closely
  enough to make the decision easy.
</p>

<h2>Sandbox confirmation</h2>
<p>
  Detonated <code>Run.exe</code> in an interactive Any.Run sandbox to watch
  the process tree, the injections, and the sockets.
</p>
<ul>
  <li><strong>Payload.</strong> Memory dumped from the spawned child matched Quasar RAT’s configuration structure and its published YARA signatures. Quasar is a .NET-based open-source RAT, common in this ecosystem.</li>
  <li><strong>Capabilities observed.</strong> Keystroke logging, remote desktop streaming, browser credential theft, reverse shell.</li>
</ul>

<h2>Indicators</h2>

<div class="table-scroll">
  <table>
    <thead>
      <tr><th>Artifact</th><th>Type</th><th>Notes</th></tr>
    </thead>
    <tbody>
      <tr><td><code>Run.exe</code></td><td>file</td><td>Go-compiled Quasar RAT dropper (17/71 on VT).</td></tr>
      <tr><td><code>ramsadaye-38594.portmap.io</code></td><td>domain</td><td>TCP tunnel used for C2.</td></tr>
      <tr><td>Decoy DLL</td><td>file (VB)</td><td>Hollow UI, no functional logic.</td></tr>
    </tbody>
  </table>
</div>

<h2>What this one teaches</h2>
<p>
  The individual pieces here are ordinary. Quasar RAT is a decade old;
  Portmap tunneling is a standard C2 pattern; “disguise malware as a game
  cheat” is an old trick because the target audience is habituated to
  disabling AV. What made the triage clean was combining a compiler check
  on the dropper, a sandbox run, and a bit of correlation on the uploader
  metadata. None of those alone is decisive; together they took about
  fifteen minutes and left no doubt.
</p>
"""

FAST_TRIAGE = r"""
<p>
  Some weeks I look at a binary a day. Other weeks I sit with one file for
  a week. What I don’t do anymore is start every triage by loading the
  sample into IDA and reading disassembly. That reads well as a workflow
  when you’re doing it once. When you’re doing it every day, it burns
  hours before you’ve even decided whether the file is worth the time.
</p>
<p>
  What I do instead is a fast pass over the PE that answers three
  questions before I open a disassembler. If the answers push the sample
  past a threshold, I open IDA. If they don’t, I move on.
</p>

<h2>What the PE gives you for free</h2>
<p>
  The Portable Executable format is the header layout every Windows
  binary starts with. Think of it as the index of the book: everything the
  Windows loader needs to map, resolve, and run the file lives in there.
  Section table, entry point, imports, resources, compiler metadata, all
  of it. You can read all of that without executing anything, without
  running an unpacker, and without opening the file in a heavy tool.
</p>
<p>
  Three of those signals turn out to be enough to sort most triage into
  “look closer” or “close the file and move on”.
</p>

<h2>Flag 1: does it talk to the internet?</h2>
<p>
  The first pass is strings. A lot of malware falls into one of two
  archetypes at this stage, and both leak the same way.
</p>
<p>
  <strong>The naive author.</strong> URLs sit in <code>.rdata</code> as
  plaintext. C2 hostnames, Discord webhooks, port-forwarding tunnels,
  right there in a plain strings dump. If the sample is claiming to be a
  cracked build of a legitimate app that normally does license validation,
  seeing a POST to <code>discord.com/api/webhooks/…</code> is the whole
  story.
</p>
<p>
  <strong>The careful author.</strong> Strings are XOR-scrambled,
  stack-built, or resolved from constants at runtime. Nothing shows up in
  a plain strings pass. When that happens I run
  <a href="https://github.com/mandiant/flare-floss" rel="noopener">FLOSS</a>
  over the file. FLOSS resolves stack strings, decoded strings, and
  obfuscated constants without executing the binary. It’s noisy, but it
  usually surfaces the C2 anyway.
</p>
<p>
  Either way the question is the same: does this file want to reach the
  network, and where?
</p>

<h2>Flag 2: are its imports missing?</h2>
<p>
  Malware often resolves Win32 API names at runtime instead of listing
  them in the Import Address Table. That keeps
  <code>LoadLibrary</code>/<code>OpenProcess</code>/<code>VirtualAllocEx</code>
  from showing up in a static import listing, and it defeats the fastest
  form of triage.
</p>
<p>
  You can chase that resolution in IDA or in a debugger. That works, but
  it’s slow. I wrote a small tool on top of Zydis that follows the calls
  automatically and annotates each hit with the string that was almost
  certainly being resolved. Output looks like this:
</p>

<div class="snippet">
  <div class="snippet-bar">
    <span class="snippet-lang">tool output</span>
    <span class="snippet-name">dynamic import trace</span>
  </div>
  <pre><code>[CALL] RVA 0x0020D17B   call [0x00000000003C5218]
              0x0020D15D  jnz  0x000000000020D196
              0x0020D15F  lea  rcx, [0x0000000000535CA0]
            possible function arg: "ntdll.dll"
              0x0020D166  call [0x00000000003C5210]
              0x0020D16C  test rax, rax
              0x0020D16F  jz   0x000000000020D18A
              0x0020D171  lea  rdx, [0x0000000000535CB0]
            possible function arg: "RtlVerifyVersionInfo"
              0x0020D178  mov  rcx, rax</code></pre>
</div>

<p>
  Two <code>lea</code> loads of the same string reference right before a
  call: that’s almost always a <code>GetProcAddress</code> on
  <code>ntdll!RtlVerifyVersionInfo</code>. Doing that at scale by hand is
  what makes triage slow. Doing it with a Zydis pass over the code section
  takes seconds.
</p>
<p>
  The same tool also handles the common inline-XOR string obfuscation
  pattern. I wrote up how that pattern looks in
  <a href="../blog/defeating-malware-obfuscation-xor.html">defeating XOR
  string obfuscation</a>.
</p>

<h2>Flag 3: is there another binary inside it?</h2>
<p>
  This one catches a lot of cracked installers. The pitch is that
  <code>crack.exe</code> unlocks the legitimate app, and sometimes it
  actually does, so the user reports it as working. What they don’t see
  is a second executable dropped alongside the crack that gets run at
  first launch.
</p>
<p>
  The tell in the PE is straightforward: an entire second
  <code>MZ</code>/<code>PE</code> header sitting in a resource, in an
  overlay past the end of the last section, or inside a non-code section
  that shouldn’t hold one. My <code>pe_analyzer</code> script scans for
  those signatures and reports the offset and size of anything it finds.
</p>
<p>
  Extracting from a known offset is a few lines of Python:
</p>

<div class="snippet">
  <div class="snippet-bar">
    <span class="snippet-lang">Python</span>
    <span class="snippet-name">extract.py</span>
  </div>
  <pre><code><span class="syn-kwd">def</span> <span class="syn-fn">main</span><span class="syn-op">():</span>
    <span class="syn-kwd">if</span> <span class="syn-fn">len</span><span class="syn-op">(</span><span class="syn-var">sys</span><span class="syn-op">.</span><span class="syn-var">argv</span><span class="syn-op">)</span> <span class="syn-kwd">not in</span> <span class="syn-op">(</span><span class="syn-num">2</span><span class="syn-op">,</span> <span class="syn-num">3</span><span class="syn-op">):</span>
        <span class="syn-fn">print</span><span class="syn-op">(</span>
            <span class="syn-fn">f</span><span class="syn-str">"{R}Usage:{X} python {os.path.basename(sys.argv[0])} "</span>
            <span class="syn-str">"&lt;filename&gt; [output_file]"</span>
        <span class="syn-op">)</span>
        <span class="syn-var">sys</span><span class="syn-op">.</span><span class="syn-fn">exit</span><span class="syn-op">(</span><span class="syn-num">1</span><span class="syn-op">)</span>

    <span class="syn-var">filename</span> <span class="syn-op">=</span> <span class="syn-var">sys</span><span class="syn-op">.</span><span class="syn-var">argv</span><span class="syn-op">[</span><span class="syn-num">1</span><span class="syn-op">]</span>

    <span class="syn-kwd">if</span> <span class="syn-kwd">not</span> <span class="syn-var">os</span><span class="syn-op">.</span><span class="syn-var">path</span><span class="syn-op">.</span><span class="syn-fn">isfile</span><span class="syn-op">(</span><span class="syn-var">filename</span><span class="syn-op">):</span>
        <span class="syn-fn">print</span><span class="syn-op">(</span><span class="syn-fn">f</span><span class="syn-str">"{R}[-] File not found:{X} {filename}"</span><span class="syn-op">)</span>
        <span class="syn-var">sys</span><span class="syn-op">.</span><span class="syn-fn">exit</span><span class="syn-op">(</span><span class="syn-num">1</span><span class="syn-op">)</span>

    <span class="syn-kwd">try</span><span class="syn-op">:</span>
        <span class="syn-var">offset</span> <span class="syn-op">=</span> <span class="syn-fn">parse_num</span><span class="syn-op">(</span><span class="syn-fn">input</span><span class="syn-op">(</span><span class="syn-fn">f</span><span class="syn-str">"{Y}OFFSET:{X} "</span><span class="syn-op">))</span>
        <span class="syn-var">size</span>   <span class="syn-op">=</span> <span class="syn-fn">parse_num</span><span class="syn-op">(</span><span class="syn-fn">input</span><span class="syn-op">(</span><span class="syn-fn">f</span><span class="syn-str">"{Y}SIZE:{X} "</span><span class="syn-op">))</span>
    <span class="syn-kwd">except</span> <span class="syn-type">ValueError</span><span class="syn-op">:</span>
        <span class="syn-fn">print</span><span class="syn-op">(</span><span class="syn-fn">f</span><span class="syn-str">"{R}[-] Invalid number.{X}"</span><span class="syn-op">)</span>
        <span class="syn-var">sys</span><span class="syn-op">.</span><span class="syn-fn">exit</span><span class="syn-op">(</span><span class="syn-num">1</span><span class="syn-op">)</span>

    <span class="syn-var">output</span> <span class="syn-op">=</span> <span class="syn-op">(</span>
        <span class="syn-var">sys</span><span class="syn-op">.</span><span class="syn-var">argv</span><span class="syn-op">[</span><span class="syn-num">2</span><span class="syn-op">]</span> <span class="syn-kwd">if</span> <span class="syn-fn">len</span><span class="syn-op">(</span><span class="syn-var">sys</span><span class="syn-op">.</span><span class="syn-var">argv</span><span class="syn-op">)</span> <span class="syn-op">==</span> <span class="syn-num">3</span>
        <span class="syn-kwd">else</span> <span class="syn-var">os</span><span class="syn-op">.</span><span class="syn-var">path</span><span class="syn-op">.</span><span class="syn-fn">splitext</span><span class="syn-op">(</span><span class="syn-var">filename</span><span class="syn-op">)[</span><span class="syn-num">0</span><span class="syn-op">]</span> <span class="syn-op">+</span> <span class="syn-str">"_extracted.bin"</span>
    <span class="syn-op">)</span>

    <span class="syn-fn">print</span><span class="syn-op">(</span><span class="syn-fn">f</span><span class="syn-str">"\n{C}[*]{X} Extracting..."</span><span class="syn-op">)</span>

    <span class="syn-kwd">with</span> <span class="syn-fn">open</span><span class="syn-op">(</span><span class="syn-var">filename</span><span class="syn-op">,</span> <span class="syn-str">"rb"</span><span class="syn-op">)</span> <span class="syn-kwd">as</span> <span class="syn-var">f</span><span class="syn-op">:</span>
        <span class="syn-var">f</span><span class="syn-op">.</span><span class="syn-fn">seek</span><span class="syn-op">(</span><span class="syn-var">offset</span><span class="syn-op">)</span>
        <span class="syn-var">data</span> <span class="syn-op">=</span> <span class="syn-var">f</span><span class="syn-op">.</span><span class="syn-fn">read</span><span class="syn-op">(</span><span class="syn-var">size</span><span class="syn-op">)</span>

    <span class="syn-kwd">with</span> <span class="syn-fn">open</span><span class="syn-op">(</span><span class="syn-var">output</span><span class="syn-op">,</span> <span class="syn-str">"wb"</span><span class="syn-op">)</span> <span class="syn-kwd">as</span> <span class="syn-var">f</span><span class="syn-op">:</span>
        <span class="syn-var">f</span><span class="syn-op">.</span><span class="syn-fn">write</span><span class="syn-op">(</span><span class="syn-var">data</span><span class="syn-op">)</span>

    <span class="syn-fn">print</span><span class="syn-op">(</span><span class="syn-fn">f</span><span class="syn-str">"{G}[+]{X} Done"</span><span class="syn-op">)</span>
    <span class="syn-fn">print</span><span class="syn-op">(</span><span class="syn-fn">f</span><span class="syn-str">"{G}[+]{X} Saved: {output}"</span><span class="syn-op">)</span>
    <span class="syn-fn">print</span><span class="syn-op">(</span><span class="syn-fn">f</span><span class="syn-str">"{G}[+]{X} Size : {</span><span class="syn-fn">len</span><span class="syn-op">(</span><span class="syn-var">data</span><span class="syn-op">)</span><span class="syn-str">:,} bytes"</span><span class="syn-op">)</span></code></pre>
</div>

<p>
  The whole loop takes about a second per file. If the dropped payload
  looks worth a second look, that’s when I open IDA.
</p>

<h2>What this doesn’t catch</h2>
<p>
  This is a triage pass, not a verdict. A quiet PE with no interesting
  strings, no missing imports, and no embedded files can still be
  malicious. What flag ranking gets you is fast sorting: most samples
  fall out of the funnel at this stage, and the ones that stay are the
  ones worth the time it takes to reverse them properly.
</p>

<div class="note note-warn">
  <span class="note-label">If you’re here from a “free crack” site</span>
  <p>
    A “crack” of a legitimate app is a great cover for a payload. I’m
    writing up the popular crack-hosting sites and what they actually
    ship. The short version, do not run these binaries. Either pay for
    the software or use a free alternative. The arithmetic on the other
    path is very bad.
  </p>
</div>
"""

ARTICLE_BODIES = {
    "battleye-internals": BATTLEYE.strip(),
    "windows-kernel-callbacks": KERNEL_CALLBACKS.strip(),
    "pe-headers-deep-dive": PE_HEADERS.strip(),
    "overlays-and-malware-injection-mechanisms": OVERLAYS.strip(),
    "defeating-malware-obfuscation-xor": XOR.strip(),
    "triage-quasar-rat-case-study": QUASAR.strip(),
    "fast-triage-three-pe-flags": FAST_TRIAGE.strip(),
}
