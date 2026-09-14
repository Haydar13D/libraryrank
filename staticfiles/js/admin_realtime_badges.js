document.addEventListener("DOMContentLoaded", function() {
    // Only run if we are inside the admin panel
    const sidebar = document.querySelector('aside');
    if (!sidebar) return;

    function updateBadges() {
        fetch('/api/admin/badges/')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Find the menu items
                    const links = document.querySelectorAll('aside a');
                    links.forEach(link => {
                        const href = link.getAttribute('href');
                        if (!href) return;

                        // Check for Redemption Claims
                        if (href.includes('leaderboard/redemptionclaim')) {
                            updateBadgeElement(link, data.pending_claims);
                        }
                        
                        // Check for Seminar Registrations
                        if (href.includes('leaderboard/seminarregistration')) {
                            updateBadgeElement(link, data.pending_registrations);
                        }
                    });
                }
            })
            .catch(error => console.error('Error fetching admin badges:', error));
    }

    function updateBadgeElement(linkElement, count) {
        // Unfold usually puts the badge in a specific span inside the link
        // Let's find the badge span or create one if it doesn't exist
        let badgeSpan = linkElement.querySelector('.bg-primary-600'); 
        
        if (!badgeSpan && count > 0) {
            // Need to create the badge span
            // Unfold structure: <a ...><span class="material-symbols-outlined">...</span><span class="flex-grow">Title</span><span class="...">Badge</span></a>
            badgeSpan = document.createElement('span');
            badgeSpan.className = 'bg-primary-600 text-white text-xs font-bold px-2 py-0.5 rounded-full ml-auto';
            linkElement.appendChild(badgeSpan);
        }

        if (badgeSpan) {
            if (count > 0) {
                badgeSpan.textContent = count;
                badgeSpan.style.display = 'inline-block';
            } else {
                badgeSpan.style.display = 'none';
            }
        }
    }

    // Run immediately
    updateBadges();

    // Poll every 15 seconds
    setInterval(updateBadges, 15000);
});
