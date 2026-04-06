import re

with open('templates/result.html', 'r', encoding='utf-8') as f:
    html = f.read()

new_section = r'''                <section class="result-timetable-section">
                    <!-- Section header -->
                    <div class="section-header">
                        <div>
                            <h2 class="section-title"><i class="fa-solid fa-calendar-week"></i> Weekly Timetable</h2>
                            <p class="section-sub">Your 7-day master schedule · scroll horizontally to view all days</p>
                        </div>
                    </div>

                    <!-- Weekly Calendar Grid -->
                    <div class="weekly-calendar-grid">
                        {% for day, day_entries in timetable.items() %}
                        <div class="calendar-day-col">
                            <div class="calendar-day-header">{{ day }}</div>
                            <div class="calendar-day-slots">
                                {% for entry in day_entries %}
                                <div class="cal-slot {{ entry.type }}">
                                    <!-- Top: Time & Icon -->
                                    <div class="cal-slot-top">
                                        <div class="cal-slot-time">{{ entry.time }}</div>
                                        <div class="cal-slot-icon">
                                            {% if entry.type == 'study' %}<i class="fa-solid fa-bolt"></i>
                                            {% elif entry.type == 'college' %}<i class="fa-solid fa-building-columns"></i>
                                            {% elif 'Sleep' in entry.task %}<i class="fa-solid fa-moon"></i>
                                            {% elif 'Lunch' in entry.task %}<i class="fa-solid fa-utensils"></i>
                                            {% elif 'Recap' in entry.task or 'Plan' in entry.task %}<i class="fa-solid fa-lightbulb"></i>
                                            {% else %}<i class="fa-solid fa-leaf"></i>{% endif %}
                                        </div>
                                    </div>
                                    <!-- Middle: Task -->
                                    <div class="cal-slot-task">{{ entry.task }}</div>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </section>'''

# regex to replace from <section class="result-timetable-section"> to </section>
html = re.sub(r'                <section class="result-timetable-section">.*?                </section>', new_section, html, flags=re.DOTALL)

with open('templates/result.html', 'w', encoding='utf-8') as f:
    f.write(html)
