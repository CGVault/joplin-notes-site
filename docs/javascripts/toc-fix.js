
(function () {
    const OFFSET = 140;

    function getHeadings() {
        return Array.from(document.querySelectorAll(".md-content h1, .md-content h2, .md-content h3, .md-content h4"));
    }

    function getTOCLinks() {
        return Array.from(document.querySelectorAll(".md-sidebar--secondary a, .md-nav--secondary a"));
    }

    function clear() {
        getTOCLinks().forEach(a => a.classList.remove("toc-active"));
    }

    function activate(link) {
        if (!link) return;
        link.classList.add("toc-active");
    }

    function findLinkById(id) {
        if (!id) return null;
        return document.querySelector(
            `.md-sidebar--secondary a[href="#${id}"], .md-nav--secondary a[href="#${id}"]`
        );
    }

    function getCurrentHeading(headings, scrollPos) {
        let current = headings[0];

        for (let h of headings) {
            const top = h.getBoundingClientRect().top + window.scrollY;
            if (top - OFFSET <= scrollPos) {
                current = h;
            }
        }

        return current;
    }

    function onScroll() {
        const headings = getHeadings();
        if (!headings.length) return;

        const scrollPos = window.scrollY;

        const current = getCurrentHeading(headings, scrollPos);

        clear();
        activate(findLinkById(current.id));

        // 🔥 FIX: robust bottom detection (not fragile scrollHeight check)
        const docHeight = Math.max(
            document.body.scrollHeight,
            document.documentElement.scrollHeight
        );

        const atBottom = (window.innerHeight + window.scrollY) >= (docHeight - 10);

        if (atBottom) {
            const last = headings[headings.length - 1];
            clear();
            activate(findLinkById(last.id));
        }
    }

    // run often enough for Material instant navigation
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("load", onScroll);
    window.addEventListener("resize", onScroll);

    // 🔥 FIX: Material instant reload support
    document.addEventListener("DOMContentLoaded", onScroll);
})();
