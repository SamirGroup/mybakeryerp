// NovvoyERP — Sidebar toggle
(function () {
    function ready(fn) {
        if (document.readyState !== 'loading') { fn(); }
        else { document.addEventListener('DOMContentLoaded', fn); }
    }

    ready(function () {
        var sidebar  = document.getElementById('appSidebar');
        var overlay  = document.getElementById('sidebarOverlay');
        var openBtn  = document.getElementById('mobileMenuToggle');
        var closeBtn = document.getElementById('sidebarClose');

        if (!sidebar || !overlay || !openBtn) { return; }

        function open() {
            sidebar.classList.add('open');
            overlay.classList.add('active');
            document.body.classList.add('sidebar-open');
            openBtn.setAttribute('aria-expanded', 'true');
        }

        function close() {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
            document.body.classList.remove('sidebar-open');
            openBtn.setAttribute('aria-expanded', 'false');
        }

        openBtn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            sidebar.classList.contains('open') ? close() : open();
        });

        if (closeBtn) {
            closeBtn.addEventListener('click', function (e) {
                e.preventDefault();
                close();
            });
        }

        overlay.addEventListener('click', close);

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') { close(); }
        });

        var links = sidebar.querySelectorAll('a');
        for (var i = 0; i < links.length; i++) {
            links[i].addEventListener('click', function () {
                if (window.innerWidth <= 1080) { close(); }
            });
        }

        window.addEventListener('resize', function () {
            if (window.innerWidth > 1080) { close(); }
        });
    });
})();

// ── Toast notifications (Django messages) ─────────────────────────────────
(function () {
    var style = document.createElement('style');
    style.textContent =
        '@keyframes erpToastIn{from{opacity:0;transform:translateX(60px)}to{opacity:1;transform:translateX(0)}}' +
        '.erp-toast-wrap{position:fixed;top:20px;right:20px;z-index:99999;display:flex;flex-direction:column;gap:10px;pointer-events:none;}' +
        '.erp-toast{pointer-events:all;min-width:260px;max-width:380px;padding:14px 18px 14px 14px;border-radius:14px;' +
        'font-family:Manrope,sans-serif;font-size:14px;font-weight:700;display:flex;align-items:flex-start;gap:10px;' +
        'box-shadow:0 8px 28px rgba(0,0,0,0.14);animation:erpToastIn 0.3s ease both;}' +
        '.erp-toast.success{background:#d4edda;color:#155724;border:1px solid #b8dfc4;}' +
        '.erp-toast.error{background:#f8d7da;color:#721c24;border:1px solid #f1b0b7;}' +
        '.erp-toast.warning{background:#fff3cd;color:#856404;border:1px solid #ffe69c;}' +
        '.erp-toast.info{background:#d1ecf1;color:#0c5460;border:1px solid #b8daff;}' +
        '.erp-toast-icon{font-size:18px;flex-shrink:0;margin-top:1px;}' +
        '.erp-toast-close{margin-left:auto;background:none;border:none;cursor:pointer;font-size:18px;opacity:0.6;padding:0 0 0 8px;flex-shrink:0;line-height:1;}' +
        '.erp-toast-close:hover{opacity:1;}';
    document.head.appendChild(style);

    function makeWrap() {
        var w = document.getElementById('erp-toast-wrap');
        if (!w) {
            w = document.createElement('div');
            w.id = 'erp-toast-wrap';
            w.className = 'erp-toast-wrap';
            document.body.appendChild(w);
        }
        return w;
    }

    var ICONS = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };

    function showToast(msg, type, duration) {
        type = type || 'info';
        duration = duration || 4500;
        var wrap = makeWrap();
        var t = document.createElement('div');
        t.className = 'erp-toast ' + type;
        t.innerHTML =
            '<span class="erp-toast-icon">' + (ICONS[type] || ICONS.info) + '</span>' +
            '<span style="flex:1;">' + msg + '</span>' +
            '<button class="erp-toast-close" onclick="this.parentElement.remove()">&times;</button>';
        wrap.appendChild(t);
        setTimeout(function () {
            t.style.transition = 'opacity 0.4s, transform 0.4s';
            t.style.opacity = '0';
            t.style.transform = 'translateX(60px)';
            setTimeout(function () { if (t.parentElement) t.remove(); }, 420);
        }, duration);
    }

    window.showToast = showToast;

    function convertAlerts() {
        document.querySelectorAll('.alert').forEach(function (el) {
            var type = 'info';
            if (el.classList.contains('alert-success')) type = 'success';
            else if (el.classList.contains('alert-error') || el.classList.contains('alert-danger')) type = 'error';
            else if (el.classList.contains('alert-warning')) type = 'warning';
            var msg = el.textContent.trim();
            if (msg) showToast(msg, type);
            el.remove();
        });
    }

    if (document.readyState !== 'loading') { convertAlerts(); }
    else { document.addEventListener('DOMContentLoaded', convertAlerts); }
})();

// Buxgalteriya ichki menyu — URL hash bo'yicha faol holat
(function () {
    function accTabFromHash() {
        var h = (window.location.hash || '#overview').replace(/^#/, '').trim();
        if (!h) { h = 'overview'; }
        return h;
    }

    function syncAccountingSidebarHighlight() {
        var tab = accTabFromHash();
        var sub = document.querySelector('.nav-accounting-sub');
        if (!sub) { return; }
        var links = sub.querySelectorAll('a[href*="/accounting/#"]');
        links.forEach(function (a) {
            var m = a.getAttribute('href').match(/#(.+)$/);
            var t = m ? m[1] : '';
            a.classList.toggle('active', t === tab);
        });
    }

    function init() {
        syncAccountingSidebarHighlight();
    }

    window.addEventListener('hashchange', syncAccountingSidebarHighlight);
    document.addEventListener('DOMContentLoaded', init);
})();
