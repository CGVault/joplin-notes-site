
(function () {
    const OFFSET = 140;

    function getHeadings() {
        return Array.from(document.querySelectorAll(".md-content h1, .md-content h2, .md-content h3, .md-content h4"));
    }

    function getLinks() {
        return Array.from(document.querySelectorAll(".md-sidebar--secondary a, .md-nav--secondary a"));
    }

    function clear() {
        getLinks().forEach(l => l.classList.remove("toc-active"));
    }

    function activate(link) {
        if (link) link.classList.add("toc-active");
    }

    function findLink(id) {
        return document.querySelector(
            `.md-sidebar--secondary a[href="#${id}"], .md-nav--secondary a[href="#${id}"]`
        );
    }

    function getCurrent(headings, scrollPos) {
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

        const current = getCurrent(headings, scrollPos);

        clear();
        activate(findLink(current.id));

        // FIX: reliable bottom detection
        const docHeight = Math.max(
            document.body.scrollHeight,
            document.documentElement.scrollHeight
        );

        const atBottom = (window.innerHeight + window.scrollY) >= (docHeight - 10);

        if (atBottom) {
            const last = headings[headings.length - 1];
            clear();
            activate(findLink(last.id));
        }
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("load", onScroll);
    window.addEventListener("resize", onScroll);
    document.addEventListener("DOMContentLoaded", onScroll);
})();
