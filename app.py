import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, make_response, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import firebase_admin
from firebase_admin import auth, credentials, firestore
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import json


# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback_secret_for_local_dev")

# --- Firebase & Firestore Setup ---
# Load environment variables
load_dotenv()

# Firebase Web Config (for frontend injection)
FIREBASE_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID")
}

# Initialize Firebase Admin
try:
    firebase_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if firebase_json:
        # Load from environment variable (Useful for Vercel)
        import json
        cred_dict = json.loads(firebase_json)
        cred = credentials.Certificate(cred_dict)
    else:
        # Load from file (Useful for local development)
        service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "service-account-file.json")
        cred = credentials.Certificate(service_account_path)
    
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    firebase_init_error = None
except Exception as e:
    print(f"Error: Firebase Admin failed to initialize. {e}")
    db = None
    firebase_init_error = str(e)

# Check database connection before doing anything
@app.before_request
def check_db_initialization():
    # Only block paths that aren't static to avoid breaking all assets
    if db is None and not request.path.startswith('/static'):
        return f"🔥 Firebase failed to initialize on Vercel Backend! Please ensure FIREBASE_SERVICE_ACCOUNT_JSON is pasted correctly in Vercel Environment Variables.<br><br><b>Exact Error:</b> {firebase_init_error}", 500

# --- Flask-Login Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- User Model (Firestore Helper) ---
class User(UserMixin):
    def __init__(self, uid, username, email):
        self.id = uid  # current_user.id in Flask-Login
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(uid):
    user_doc = db.collection('users').document(uid).get()
    if user_doc.exists:
        data = user_doc.to_dict()
        return User(uid, data.get('username'), data.get('email'))
    return None

# --- Master Achievement Definitions ---
BADGE_RULES = {
    "Master Planner": {"target": 1, "icon": "fa-graduation-cap", "desc": "Generated your first study plan!"},
    "Streak Warrior": {"target": 3, "icon": "fa-fire", "desc": "Maintained a 3-day study streak!"},
    "Productivity King": {"target": 90, "icon": "fa-rocket", "desc": "Achieved a productivity score of 90%+"},
    "Consistent Scholar": {"target": 5, "icon": "fa-bullseye", "desc": "Completed 5 total daily check-ins!"}
}

def unlock_badge(uid, name, icon, description):
    badge_ref = db.collection('users').document(uid).collection('achievements').document(name)
    if not badge_ref.get().exists:
        badge_ref.set({
            "name": name,
            "icon": icon,
            "description": description,
            "unlocked_at": firestore.SERVER_TIMESTAMP
        })
        return True
    return False

def get_streak(uid):
    from datetime import date, timedelta
    logs_ref = db.collection('users').document(uid).collection('logs')
    # Get logs ordered by date desc
    logs = logs_ref.order_by('date', direction=firestore.Query.DESCENDING).stream()
    
    log_dates = {doc.to_dict().get('date') for doc in logs}
    if not log_dates:
        return 0
        
    today = date.today()
    streak = 0
    current_date = today
    
    if today.isoformat() not in log_dates:
        current_date = today - timedelta(days=1)
        if current_date.isoformat() not in log_dates:
            return 0
            
    while current_date.isoformat() in log_dates:
        streak += 1
        current_date -= timedelta(days=1)
    return streak

def check_achievements(uid):
    user_ref = db.collection('users').document(uid)
    
    # 🎓 Master Planner: 1 plan
    plans_count = len(list(user_ref.collection('plans').limit(1).stream()))
    if plans_count >= BADGE_RULES["Master Planner"]["target"]:
        unlock_badge(uid, "Master Planner", BADGE_RULES["Master Planner"]["icon"], BADGE_RULES["Master Planner"]["desc"])

    # 🔥 Streak Warrior: 3-day streak
    streak = get_streak(uid)
    if streak >= BADGE_RULES["Streak Warrior"]["target"]:
        unlock_badge(uid, "Streak Warrior", BADGE_RULES["Streak Warrior"]["icon"], BADGE_RULES["Streak Warrior"]["desc"])

    # 🚀 Productivity King: Score >= 90%
    # Get best plan by productivity_score
    best_plans = user_ref.collection('plans').order_by('productivity_score', direction=firestore.Query.DESCENDING).limit(1).stream()
    for plan in best_plans:
        if plan.to_dict().get('productivity_score', 0) >= BADGE_RULES["Productivity King"]["target"]:
            unlock_badge(uid, "Productivity King", BADGE_RULES["Productivity King"]["icon"], BADGE_RULES["Productivity King"]["desc"])

    # 🎯 Consistent Scholar: 5 Check-ins
    check_ins = len(list(user_ref.collection('logs').where('completed', '==', True).stream()))
    if check_ins >= BADGE_RULES["Consistent Scholar"]["target"]:
        unlock_badge(uid, "Consistent Scholar", BADGE_RULES["Consistent Scholar"]["icon"], BADGE_RULES["Consistent Scholar"]["desc"])

# --- Plotting Helpers ---
def generate_graph(study_hours, distraction_hours, productivity_score):
    plt.figure(figsize=(6, 4))
    labels = ['Study Hours', 'Distraction Hours']
    values = [study_hours, distraction_hours]
    plt.bar(labels, values, color=['#4CAF50', '#F44336'])
    plt.title('Study vs Distraction')
    plt.ylabel('Hours')
    
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    return plot_url

def generate_gauge(score):
    plt.figure(figsize=(6, 2))
    plt.barh(['Productivity'], [score], color='#2196F3')
    plt.barh(['Productivity'], [100 - score], left=[score], color='#e0e0e0')
    plt.xlim(0, 100)
    plt.title(f'Productivity Score: {score}%')
    plt.yticks([])
    
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    return plot_url

# --- Auth Routes (Firebase Integration) ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        id_token = request.json.get('idToken')
        username = request.json.get('username')
        
        try:
            # Verify the token against Firebase
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            email = decoded_token['email']
            
            # Check if user already exists in Firestore
            user_ref = db.collection('users').document(uid)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                user_data = {
                    "username": username,
                    "email": email,
                    "created_at": firestore.SERVER_TIMESTAMP
                }
                user_ref.set(user_data)
                user = User(uid, username, email)
            else:
                data = user_doc.to_dict()
                user = User(uid, data.get('username'), data.get('email'))
            
            login_user(user)
            return {"status": "success", "message": "Account created!"}
        except Exception as e:
            return {"status": "error", "message": str(e)}, 401
            
    return render_template('register.html', firebase_config=FIREBASE_CONFIG)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        id_token = request.json.get('idToken')
        remember = request.json.get('remember', False)
        
        try:
            # Verify the token against Firebase
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            
            # Find user in Firestore
            user_ref = db.collection('users').document(uid)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                # Auto-register if not in Firestore (common for Google Sign-In)
                email = decoded_token.get('email', '')
                username = decoded_token.get('name', email.split('@')[0])
                user_data = {
                    "username": username,
                    "email": email,
                    "created_at": firestore.SERVER_TIMESTAMP
                }
                user_ref.set(user_data)
                user = User(uid, username, email)
            else:
                data = user_doc.to_dict()
                user = User(uid, data.get('username'), data.get('email'))
            
            login_user(user, remember=remember)
            return {"status": "success", "message": "Logged in!"}
        except Exception as e:
            return {"status": "error", "message": str(e)}, 401
            
    return render_template('login.html', firebase_config=FIREBASE_CONFIG)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user
    user_ref = db.collection('users').document(current_user.id)
    from datetime import date, datetime, time
    
    # Fetch plans (last 10)
    plans_stream = user_ref.collection('plans').order_by('created_at', direction=firestore.Query.DESCENDING).limit(10).stream()
    plans = []
    for p in plans_stream:
        p_data = p.to_dict()
        p_data['id'] = p.id
        plans.append(p_data)
        
    latest_plan = plans[0] if plans else None
    
    # Stats
    streak = get_streak(current_user.id)
    plans_count = len(list(user_ref.collection('plans').stream()))
    
    # Today's hours
    today_start = datetime.combine(date.today(), time.min)
    today_end = datetime.combine(date.today(), time.max)
    today_plans = user_ref.collection('plans') \
        .where('created_at', '>=', today_start) \
        .where('created_at', '<=', today_end) \
        .stream()
    today_study_hours = round(sum(p.to_dict().get('study_hours', 0) for p in today_plans), 1)
    
    # Total study hours (all-time)
    all_plans = user_ref.collection('plans').stream()
    total_study_hours = round(sum(p.to_dict().get('study_hours', 0) for p in all_plans), 1)
    
    # Overall progress and Check-in status
    overall_progress = int(latest_plan.get('syllabus_percentage', 0)) if latest_plan else 0
    
    today_str = date.today().isoformat()
    checked_in_today = user_ref.collection('logs').document(today_str).get().exists
    
    # Fetch achievements
    achievements = [doc.to_dict() for doc in user_ref.collection('achievements').stream()]

    return render_template('dashboard.html', 
                           user=current_user,
                           plans=plans,
                           latest_plan=latest_plan,
                           achievements=achievements,
                           streak=streak,
                           plans_count=plans_count,
                           total_study_hours=total_study_hours,
                           today_study_hours=today_study_hours,
                           overall_progress=overall_progress,
                           checked_in_today=checked_in_today)

@app.route('/check-in', methods=['POST'])
@login_required
def check_in():
    user_ref = db.collection('users').document(current_user.id)
    from datetime import date
    today_str = date.today().isoformat()
    
    log_ref = user_ref.collection('logs').document(today_str)
    if not log_ref.get().exists:
        log_ref.set({
            "date": today_str,
            "completed": True,
            "created_at": firestore.SERVER_TIMESTAMP
        })
    
    check_achievements(current_user.id)
    
    if request.is_json or request.headers.get('Accept') == 'application/json':
        return {"status": "success", "message": "Checked in successfully"}
    return redirect(url_for('dashboard'))

@app.route('/api/achievements')
@login_required
def api_achievements():
    user_ref = db.collection('users').document(current_user.id)
    check_achievements(current_user.id)
    
    plans_count = len(list(user_ref.collection('plans').stream()))
    streak = get_streak(current_user.id)
    
    # Max score
    best_plans = user_ref.collection('plans').order_by('productivity_score', direction=firestore.Query.DESCENDING).limit(1).stream()
    max_score = 0
    for p in best_plans:
        max_score = int(p.to_dict().get('productivity_score', 0))
        
    total_check_ins = len(list(user_ref.collection('logs').where('completed', '==', True).stream()))
    
    achievements = [doc.to_dict().get('name') for doc in user_ref.collection('achievements').stream()]
    
    return {
        "unlocked": achievements,
        "metrics": {
            "plans_created": plans_count,
            "streak": streak,
            "max_score": max_score,
            "total_check_ins": total_check_ins
        },
        "definitions": BADGE_RULES
    }

@app.route('/planner')
@login_required
def planner():
    return render_template('planner.html')

@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    user = current_user
    subject_names = request.form.getlist('subject_names[]')
    difficulties  = request.form.getlist('difficulties[]')

    study_total_hours  = float(request.form.get('study_hours', 0))
    exam_date_str      = request.form.get('exam_date')
    syllabus_completion= float(request.form.get('syllabus_percentage', 0))
    distraction_hours  = float(request.form.get('distraction_hours', 0))
    sleep_hours_input  = float(request.form.get('sleep_hours', 7))
    college_hours_input= float(request.form.get('college_hours', 0))

    # ── Input Validation ──────────────────────────────────────────
    if study_total_hours <= 0:
        flash("Please enter valid study hours greater than 0")
        return redirect(url_for('planner'))

    total_day_hours = study_total_hours + distraction_hours + sleep_hours_input + college_hours_input
    if total_day_hours > 24:
        flash(f"Unrealistic schedule: Total daily hours ({total_day_hours}h) cannot exceed 24 hours!")
        return redirect(url_for('planner'))

    if not exam_date_str:
        flash("Target exam date is required.")
        return redirect(url_for('planner'))

    exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d')
    today = datetime.now()
    if exam_date < today.replace(hour=0, minute=0, second=0, microsecond=0):
        flash("Target exam date cannot be in the past.")
        return redirect(url_for('planner'))

    days_left = (exam_date - today).days

    # ── Productivity Score ─────────────────────────────────────────
    productivity_score = (study_total_hours * 10) - (distraction_hours * 5) + syllabus_completion
    if sleep_hours_input < 6:
        productivity_score -= 10
    productivity_score = max(0, min(100, productivity_score))

    # ── Risk & Warnings ───────────────────────────────────────────
    risk_level  = "Low"
    warnings    = []
    suggestions = []

    if syllabus_completion < 50 and days_left < 10:
        risk_level = "High"
        warnings.append("⚠️ HIGH RISK: Very close to exam with less than 50% syllabus completed!")
    elif days_left < 15 or syllabus_completion < 60:
        risk_level = "Medium"

    if study_total_hours < 3:
        suggestions.append("Increase daily study hours to at least 4–5 hours.")
    if distraction_hours > 4:
        warnings.append("🛑 WARNING: High distraction hours detected!")
    if sleep_hours_input < 7:
        warnings.append("😴 SLEEP ALERT: Health experts recommend at least 7–8 hours of sleep.")

    # ── Subject Allocation ────────────────────────────────────────
    weight_map = {"Hard": 3, "Medium": 2, "Easy": 1}
    total_weight = sum(weight_map[d] for d in difficulties)

    subjects_to_schedule = []
    for name, diff in zip(subject_names, difficulties):
        weight = weight_map[diff]
        allocated = round((weight / total_weight) * study_total_hours, 1) if total_weight > 0 else 0
        subjects_to_schedule.append({"name": name, "difficulty": diff, "time": allocated})

    order = {"Hard": 0, "Medium": 1, "Easy": 2}
    subjects_to_schedule.sort(key=lambda x: order[x["difficulty"]])

    # ── Time Helpers ──────────────────────────────────────────────
    def m2s(total_minutes):
        """Convert minutes-since-midnight to a 12-hour time string."""
        total_minutes = int(total_minutes) % (24 * 60)
        h = total_minutes // 60
        m = total_minutes % 60
        period = "AM" if h < 12 else "PM"
        h12 = h % 12 or 12
        return f"{h12:02d}:{m:02d} {period}"

    def slot_str(start, end):
        return f"{m2s(start)} - {m2s(end)}"

    # ── Build Ordered Day Events for 7 Days ───────────────────────
    import random
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekly_timetable = {}

    WAKE_UP   = 6 * 60          # 06:00 AM in minutes
    MORNING_ROUTINE = 60        # 1 h
    sleep_mins = int(sleep_hours_input * 60)
    bed_time   = WAKE_UP - sleep_mins
    bed_time_display = (bed_time % (24 * 60))

    for day in days_of_week:
        is_weekend = (day in ["Saturday", "Sunday"])
        daily_college_hours = 0 if is_weekend else college_hours_input

        COLLEGE_START = 10 * 60 + 30               # 10:30 AM
        COLLEGE_END   = COLLEGE_START + int(daily_college_hours * 60)
        RETURN_HOME   = COLLEGE_END + 30           # 30-min travel

        blocked = []
        if daily_college_hours > 0:
            blocked.append((COLLEGE_START, RETURN_HOME))

        raw = []

        # Sleep
        if bed_time < 0:
            raw.append((bed_time % (24*60), 24*60-1, f"😴 Sleep ({sleep_hours_input:.0f} hrs)", "rest"))
            raw.append((0, WAKE_UP, f"😴 Sleep (cont.)", "rest"))
        else:
            raw.append((bed_time_display, WAKE_UP, f"😴 Sleep ({sleep_hours_input:.0f} hrs)", "rest"))

        # Morning routine
        raw.append((WAKE_UP, WAKE_UP + MORNING_ROUTINE, "🌅 Morning Routine & Quick Refresh", "rest"))

        # College (if any)
        if daily_college_hours > 0:
            raw.append((COLLEGE_START, COLLEGE_END, "🏫 College / Classes (Fixed)", "college"))
            raw.append((COLLEGE_END, RETURN_HOME, "🏠 Return Home & Relax", "rest"))

        # ── Distribute Study Blocks intelligently ─────────────────────
        WIND_DOWN_START = 22 * 60   # 10:00 PM
        LUNCH_START     = 13 * 60   # 1:00 PM
        LUNCH_END       = 13 * 60 + 45
        CHUNK_MAX   = 90
        SHORT_BREAK = 10
        LONG_BREAK  = 45

        if daily_college_hours > 0:
            free_windows = [
                (WAKE_UP + MORNING_ROUTINE, COLLEGE_START),
                (RETURN_HOME, WIND_DOWN_START),
            ]
        else:
            free_windows = [
                (WAKE_UP + MORNING_ROUTINE, WIND_DOWN_START),
            ]

        # Interleave & Shuffle subjects for daily variety
        day_subjects = list(subjects_to_schedule)
        random.shuffle(day_subjects) 
        hard_subjs = [s for s in day_subjects if s["difficulty"] == "Hard"]
        other_subjs = [s for s in day_subjects if s["difficulty"] != "Hard"]
        
        interleaved = []
        while hard_subjs or other_subjs:
            if hard_subjs: interleaved.append(hard_subjs.pop(0))
            if other_subjs: interleaved.append(other_subjs.pop(0))

        study_queue = []
        for subj in interleaved:
            subj_mins = subj["time"] * 60
            chunk_max = 60 if subj["difficulty"] == "Hard" else 90
            while subj_mins > 0:
                chunk = min(chunk_max, subj_mins)
                study_queue.append((subj["name"], subj["difficulty"], chunk))
                subj_mins -= chunk

        study_blocks = []
        q_idx = 0

        for win_start, win_end in free_windows:
            cur = win_start

            # Insert lunch if window crosses 13:00 and no college
            if daily_college_hours == 0 and win_start < LUNCH_START < win_end:
                while q_idx < len(study_queue) and cur < LUNCH_START:
                    name, diff, chunk_mins = study_queue[q_idx]
                    available = LUNCH_START - cur
                    actual = min(chunk_mins, available)
                    if actual >= 20:
                        icon = "⚡ Focus" if diff == "Hard" else "📖 Study"
                        study_blocks.append((cur, cur + actual, f"{icon}: {name}", "study"))
                        cur += actual
                        if actual >= chunk_mins:
                            q_idx += 1
                            if q_idx < len(study_queue) and cur + SHORT_BREAK < LUNCH_START:
                                study_blocks.append((cur, cur + SHORT_BREAK, "🥤 Refresh", "rest"))
                                cur += SHORT_BREAK
                        else:
                            study_queue[q_idx] = (name, diff, chunk_mins - actual)
                            break
                    else: break

                if cur <= LUNCH_START: cur = LUNCH_START
                study_blocks.append((cur, cur + LONG_BREAK, "🥗 Lunch", "rest"))
                cur += LONG_BREAK

            # Main study loop for the window
            while q_idx < len(study_queue) and cur < win_end:
                name, diff, chunk_mins = study_queue[q_idx]
                available = win_end - cur
                actual = min(chunk_mins, available)
                
                if actual < 20: break 
                
                icon = "⚡ Focus" if diff == "Hard" else "📖 Study"
                study_blocks.append((cur, cur + actual, f"{icon}: {name}", "study"))
                cur += actual

                if actual >= chunk_mins:
                    q_idx += 1
                    if q_idx < len(study_queue) and cur + SHORT_BREAK <= win_end:
                        study_blocks.append((cur, cur + SHORT_BREAK, "⏱ Stretch", "rest"))
                        cur += SHORT_BREAK
                else:
                    study_queue[q_idx] = (name, diff, chunk_mins - actual)
                    break

            # Daily Recap
            if cur < win_end and win_end == WIND_DOWN_START:
                recap_mins = 20
                if cur + recap_mins <= win_end:
                    study_blocks.append((win_end - recap_mins, win_end, "💡 Recap", "study"))
                    cur = win_end - recap_mins

            if cur < win_end:
                study_blocks.append((cur, win_end, "🌟 Free Time", "rest"))

        raw.extend(study_blocks)
        raw.append((WIND_DOWN_START, WIND_DOWN_START + 30, "📝 Plan Tomorrow", "rest"))
        
        raw.sort(key=lambda x: x[0])

        day_timetable = []
        for item in raw:
            start, end, task, typ = item
            day_timetable.append({
                "time": slot_str(start, end),
                "task": task,
                "type": typ,
            })
        weekly_timetable[day] = day_timetable

    timetable = weekly_timetable

    # ── Motivation ────────────────────────────────────────────────
    if productivity_score > 80:
        motivation = "Excellent work! Your plan is solid. Go crush it! 🚀"
    elif productivity_score > 50:
        motivation = "Good plan! Stay disciplined to finish all subjects. 💪"
    else:
        motivation = "It's a start! Focus on hard subjects first to gain momentum. 🔥"

    # ── Save to Firestore ─────────────────────────────────────────
    plan_data = {
        "exam_date": exam_date_str,
        "syllabus_percentage": syllabus_completion,
        "distraction_hours": distraction_hours,
        "sleep_hours": sleep_hours_input,
        "college_hours": college_hours_input,
        "study_hours": study_total_hours,
        "productivity_score": productivity_score,
        "risk_level": risk_level,
        "warnings": warnings,
        "suggestions": suggestions,
        "timetable": timetable,
        "motivation": motivation,
        "subjects": subjects_to_schedule,
        "created_at": firestore.SERVER_TIMESTAMP
    }
    
    user_ref = db.collection('users').document(current_user.id)
    new_plan_ref = user_ref.collection('plans').document()
    new_plan_ref.set(plan_data)
    
    check_achievements(current_user.id)
    return redirect(url_for('view_plan', plan_id=new_plan_ref.id))


@app.route('/plan/<plan_id>')
@login_required
def view_plan(plan_id):
    user_ref = db.collection('users').document(current_user.id)
    plan_doc = user_ref.collection('plans').document(plan_id).get()
    
    if not plan_doc.exists:
        return "Plan not found", 404
        
    plan = plan_doc.to_dict()
    plan['id'] = plan_doc.id
    
    exam_date = datetime.strptime(plan['exam_date'], '%Y-%m-%d')
    days_left = (exam_date - datetime.now()).days

    study_distraction_plot = generate_graph(plan['study_hours'], plan['distraction_hours'], plan['productivity_score'])
    productivity_plot = generate_gauge(plan['productivity_score'])

    warnings = plan.get('warnings', [])
    suggestions = plan.get('suggestions', [])
    timetable = plan.get('timetable', [])

    subjects_data = []
    for s in plan.get('subjects', []):
        subjects_data.append({
            "name": s['name'],
            "difficulty": s['difficulty'],
            "time": s['time'],
            "reason": "Allocated based on difficulty weighting."
        })

    return render_template('result.html',
                           score=int(plan['productivity_score']),
                           risk_level=plan['risk_level'],
                           warnings=warnings,
                           suggestions=suggestions,
                           timetable=timetable,
                           subjects_data=subjects_data,
                           study_distraction_plot=study_distraction_plot,
                           productivity_plot=productivity_plot,
                           days_left=days_left,
                           motivation=plan['motivation'],
                           sleep_hours=plan['sleep_hours'],
                           college_hours=plan['college_hours'],
                           plan=plan)

@app.route('/export/<plan_id>')
@login_required
def export_pdf(plan_id):
    user_ref = db.collection('users').document(current_user.id)
    plan_doc = user_ref.collection('plans').document(plan_id).get()
    
    if not plan_doc.exists:
        return "Plan not found", 404
        
    plan = plan_doc.to_dict()
    timetable = plan.get('timetable', [])
    
    # Just render the HTML template directly. The template will use window.print().
    return render_template('export_pdf.html', plan=plan, timetable=timetable)

@app.route('/update_timetable/<plan_id>', methods=['POST'])
@login_required
def update_timetable(plan_id):
    new_timetable = request.json.get('timetable')
    if not new_timetable:
        return {"status": "error", "message": "No data provided"}, 400
        
    user_ref = db.collection('users').document(current_user.id)
    user_ref.collection('plans').document(plan_id).update({
        "timetable": new_timetable
    })
    
    return {"status": "success", "message": "Timetable updated successfully"}

@app.route('/api/weekly_stats')
@login_required
def weekly_stats():
    from datetime import date, timedelta, datetime
    user_id = current_user.id
    today = date.today()

    DAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    result = []

    user_ref = db.collection('users').document(user_id)
    
    for offset in range(6, -1, -1):          # 6 days ago → today
        target_date = today - timedelta(days=offset)
        date_str    = target_date.isoformat()
        label       = DAY_LABELS[target_date.weekday()]

        # Query plans created on this calendar day
        start_time = datetime.combine(target_date, datetime.min.time())
        end_time = datetime.combine(target_date, datetime.max.time())
        
        day_plans = user_ref.collection('plans') \
            .where('created_at', '>=', start_time) \
            .where('created_at', '<=', end_time) \
            .stream()

        hours = sum(p.to_dict().get('study_hours', 0) for p in day_plans)
        hours = round(hours, 1)

        result.append({
            'date'    : date_str,
            'label'   : label,
            'hours'   : hours,
            'is_today': offset == 0,
        })

    # Also compute aggregate stats
    all_hours   = [r['hours'] for r in result]
    total_hours = round(sum(all_hours), 1)
    days_with_data = sum(1 for h in all_hours if h > 0)
    avg_hours   = round(total_hours / days_with_data, 1) if days_with_data else 0

    return {
        'days'       : result,
        'total_hours': total_hours,
        'avg_hours'  : avg_hours,
        'today_label': DAY_LABELS[today.weekday()],
    }


if __name__ == '__main__':
    app.run(debug=True)

