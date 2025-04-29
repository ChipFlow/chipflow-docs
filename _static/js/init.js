// Add cookieyes script
(function () {
  var script = document.createElement("script");
  script.id = "cookieyes";
  script.src = "https://cdn-cookieyes.com/client_data/58bb4c6a9878d62a6e5f8065/script.js";
  document.head.appendChild(script);
})()

// Google tag (gtag.js)
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-KSFS200Z8J');

(function () {
  var script = document.createElement("script");
  script.src = "https://www.googletagmanager.com/gtag/js?id=G-KSFS200Z8J";
  script.async = true;
  document.head.appendChild(script);

  // Track scrolling to h2 sections by id
  var sentIds = [];

  const observerCallback = (entries, observer, h2) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        // Get parent <section> of the h2, which has an id we can use to track
        var id = h2.closest("section").getAttribute("id");
        if (id && gtag && !sentIds.includes(id)) {
          gtag("event", "doc_section_view", {
            doc_section_view_id: id,
          });
          sentIds.push(id);
        }
      }
    });
  };

  var article = document.querySelector("[role=main]");
  article.querySelectorAll("h2").forEach((h2) => {
    if (h2) {
      const observer = new IntersectionObserver(
        (entries) => {
          observerCallback(entries, observer, h2);
        },
        { threshold: 1 }
      );
      observer.observe(h2);
    }
  });
})();
