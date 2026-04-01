document.addEventListener('DOMContentLoaded', () => {
    // --- PREMIUM THEME ENGINE ---
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;
    
    // Initialize Theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    htmlElement.setAttribute('data-theme', savedTheme);
    updateThemeUI(savedTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            htmlElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeUI(newTheme);
            
            // Add a subtle click animation
            themeToggle.style.transform = 'scale(0.9)';
            setTimeout(() => themeToggle.style.transform = 'scale(1)', 100);
        });
    }

    function updateThemeUI(theme) {
        if (!themeToggle) return;
        const icon = themeToggle.querySelector('i');
        const span = themeToggle.querySelector('span');
        if (icon) {
            if (theme === 'dark') {
                icon.className = 'fa-solid fa-sun';
                if (span) span.textContent = 'Light Mode';
            } else {
                icon.className = 'fa-solid fa-moon';
                if (span) span.textContent = 'Dark Mode';
            }
        }
    }

    // --- MOBILE MENU TOGGLE ---
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const navMenu = document.getElementById('nav-menu');
    
    if (mobileMenuToggle && navMenu) {
        mobileMenuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (navMenu.classList.contains('active') && !navMenu.contains(e.target) && !mobileMenuToggle.contains(e.target)) {
                navMenu.classList.remove('active');
            }
        });
    }

    // --- SIDEBAR NAV HIGHLIGHTER ---
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    // --- FOCUS MODE LOGIC (REFINED) ---
    let timer;
    let timeLeft = 25 * 60; 
    let isRunning = false;
    
    const timerDisplay = document.getElementById('timer-display');
    const timerLabel = document.getElementById('timer-label');
    const startBtn = document.getElementById('start-timer');
    const resetBtn = document.getElementById('reset-timer');

    if (startBtn && timerDisplay) {
        startBtn.addEventListener('click', () => {
            if (isRunning) {
                clearInterval(timer);
                startBtn.textContent = 'Resume';
            } else {
                timer = setInterval(() => {
                    if (timeLeft > 0) {
                        timeLeft--;
                        updateTimer();
                    } else {
                        clearInterval(timer);
                        alert("Focus Session Finished!");
                    }
                }, 1000);
                startBtn.textContent = 'Pause';
            }
            isRunning = !isRunning;
        });

        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                clearInterval(timer);
                timeLeft = 25 * 60;
                updateTimer();
                startBtn.textContent = 'Start Focus';
                isRunning = false;
            });
        }

        function updateTimer() {
            const mins = Math.floor(timeLeft / 60);
            const secs = timeLeft % 60;
            timerDisplay.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
    }

    // --- HELPER: SCROLL TO ACTIVE SESSION ---
    // If on results page, highlight current time slot
    if (window.location.pathname.includes('/plan/')) {
        const slots = document.querySelectorAll('.timeline-slot');
        const now = new Date();
        const currentMin = now.getHours() * 60 + now.getMinutes();

        slots.forEach(slot => {
            const timeStr = slot.querySelector('.slot-block div div').textContent; // e.g. "07:00 AM - 08:30 AM"
            if (timeStr.includes(' - ')) {
                const [start, end] = timeStr.split(' - ');
                const startMin = parseTimeToMin(start);
                const endMin = parseTimeToMin(end);

                if (currentMin >= startMin && currentMin <= endMin) {
                    slot.querySelector('.slot-block').style.borderColor = 'var(--primary)';
                    slot.querySelector('.slot-block').style.boxShadow = 'var(--shadow-primary)';
                    slot.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
    }

    function parseTimeToMin(timeStr) {
        if (!timeStr) return 0;
        const parts = timeStr.trim().split(' ');
        if (parts.length < 2) return 0;
        const [hms, period] = parts;
        let [h, m] = hms.split(':').map(Number);
        if (period === 'PM' && h !== 12) h += 12;
        if (period === 'AM' && h === 12) h = 0;
        return h * 60 + m;
    }

    // --- REVEAL ON SCROLL ---
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, { threshold: 0.15 });

    document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));
});
