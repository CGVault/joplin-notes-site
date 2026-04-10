
(function () {
    const OFFSET = 120;

    function getHeadings() {
        return Array.from(document.querySelectorAll("h1, h2, h3, h4"));
    }

    function getLinks() {
        return Array.from(document.querySelectorAll(".md-nav--secondary a"));
    }

    function setActive(link) {
        getLinks().forEach(l => l.classList.remove("toc-active"));
        if (link) link.classList.add("toc-active");
    }

    function onScroll() {
        const scrollPos = window.scrollY + OFFSET;
        const headings = getHeadings();

        let current = headings[0];

        for (let h of headings) {
            if (h.offsetTop <= scrollPos) current = h;
        }

        const id = current.id;
        const link = document.querySelector(`.md-nav--secondary a[href="#${id}"]`);
        setActive(link);

        // FORCE LAST HEADING ACTIVE AT BOTTOM
        const bottom = window.innerHeight + window.scrollY >= document.body.scrollHeight - 2;

        if (bottom && headings.length > 0) {
            const last = headings[headings.length - 1];
            const lastLink = document.querySelector(`.md-nav--secondary a[href="#${last.id}"]`);
            setActive(lastLink);
        }
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("load", onScroll);
})();
