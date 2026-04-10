
document.addEventListener("DOMContentLoaded", function () {

    // Fix TOC last item not highlighting
    const headings = document.querySelectorAll(".md-typeset h2, .md-typeset h3");
    const tocLinks = document.querySelectorAll(".md-nav__link");

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.id;

                tocLinks.forEach(link => {
                    if (link.getAttribute("href") === "#" + id) {
                        link.classList.add("md-nav__link--active");
                    } else {
                        link.classList.remove("md-nav__link--active");
                    }
                });
            }
        });
    }, {
        rootMargin: "0px 0px -80% 0px",
        threshold: 0.1
    });

    headings.forEach(h => observer.observe(h));
});
