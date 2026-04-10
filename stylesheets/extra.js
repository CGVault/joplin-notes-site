
document.addEventListener("DOMContentLoaded", function () {

    const headings = document.querySelectorAll(".md-typeset h2, .md-typeset h3");
    const tocLinks = document.querySelectorAll(".md-nav__link");

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const id = entry.target.id;

            tocLinks.forEach(link => {
                if (link.getAttribute("href") === "#" + id && entry.isIntersecting) {
                    link.classList.add("md-nav__link--active");
                }
            });
        });
    }, {
        rootMargin: "0px 0px -80% 0px",
        threshold: 0.1
    });

    headings.forEach(h => observer.observe(h));
});
