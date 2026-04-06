import re

with open('static/result.css', 'r', encoding='utf-8') as f:
    css = f.read()

new_css = r'''/* ── Weekly Calendar Grid ── */
.weekly-calendar-grid {
    display: flex;
    overflow-x: auto;
    border: 1px solid var(--border-strong);
    border-radius: 16px;
    background: var(--bg-sidebar);
    margin-bottom: 2rem;
    -ms-overflow-style: none;  /* IE and Edge */
    scrollbar-width: none;  /* Firefox */
}
.weekly-calendar-grid::-webkit-scrollbar {
    display: none;
}

.calendar-day-col {
    flex: 1;
    min-width: 260px; /* enough space for slots */
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
}
.calendar-day-col:last-child {
    border-right: none;
}

.calendar-day-header {
    background: rgba(255, 255, 255, 0.02);
    padding: 1.25rem 1rem;
    text-align: center;
    border-bottom: 1px solid var(--border-strong);
    color: var(--text-main);
    text-transform: uppercase;
    font-size: 0.85rem;
    font-weight: 800;
    letter-spacing: 0.05em;
}

.calendar-day-slots {
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    flex-grow: 1;
}

.cal-slot {
    background: var(--glass-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.cal-slot:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    border-color: var(--border-strong);
}

/* Color glowing accents for slots */
.cal-slot.study   { border-left: 3px solid var(--primary); }
.cal-slot.college { border-left: 3px solid #f97316; }
.cal-slot.rest    { border-left: 3px solid #10b981; }

.cal-slot.study:hover { box-shadow: 0 8px 24px rgba(99,102,241,0.15); border-color: var(--primary); }
.cal-slot.college:hover { box-shadow: 0 8px 24px rgba(249,115,22,0.15); border-color: #f97316; }
.cal-slot.rest:hover { box-shadow: 0 8px 24px rgba(16,185,129,0.15); border-color: #10b981; }

.cal-slot-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.cal-slot-time {
    font-size: 0.75rem;
    color: var(--text-muted);
    font-weight: 700;
    letter-spacing: 0.02em;
}
.cal-slot-icon {
    width: 28px; height: 28px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem;
    background: rgba(255, 255, 255, 0.05);
}
.cal-slot.study .cal-slot-icon   { background: rgba(99, 102, 241, 0.15); color: var(--primary); }
.cal-slot.college .cal-slot-icon { background: rgba(249, 115, 22, 0.15); color: #f97316; }
.cal-slot.rest .cal-slot-icon    { background: rgba(16, 185, 129, 0.15); color: #10b981; }

.cal-slot-task {
    font-size: 0.95rem;
    color: var(--text-main);
    font-weight: 700;
    line-height: 1.4;
}

/* Hide old result timetable related elements */
.tt-jump-pills, .edit-controls, .add-task-container { display: none !important; }
'''

# Use regex to find and replace everything from /* ── Daily Journey Carousel ── */ to /* ────────────────────────
css = re.sub(r'/\* ── Daily Journey Carousel ── \*/.*?/\* ────────────────────────', new_css + '\n/* ────────────────────────', css, flags=re.DOTALL)

with open('static/result.css', 'w', encoding='utf-8') as f:
    f.write(css)
