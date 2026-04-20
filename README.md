# Study_girl

Study_girl is a Python-first Django MVP for high school female students at Wesley High School in Dominica.

Motto: **SBS - Students Becoming Sisters**

The app helps girls preparing for CSEC find approved peer tutors, request study sessions, meet in a live study room, use solo study resources, and build safe ongoing Study Sister connections.

## What is included

- Django authentication: sign up, log in, log out, and password reset scaffolding.
- Student profiles with subjects needing help, learning style, study times, and preferred tutor traits.
- Tutor profiles and tutor applications with pending approval.
- Tutor discovery with filters for subject, personality trait, availability, school/parish, rating, and session count.
- Session request flow where tutors can accept or decline.
- Live study room MVP with WebRTC video/audio, screen sharing, chat, shared whiteboard, timer, and Focus Mode.
- Feedback system that can activate Study Sister connections after positive feedback from both people.
- Vibe badge logic after 5 completed sessions together.
- Solo study library with notes, video links, playlists, ambience links, and motivational quotes.
- Safety tools: community guidelines, user reporting, block connection option, and staff dashboard.
- Demo seed command for ministry/school presentation data.
- Tests for authentication, approval visibility, requests, room permissions, feedback, resources, and Vibe unlocks.

## MVP honesty

Some features are intentionally basic because this is a first version for student developers:

- WebRTC uses simple peer-to-peer browser media. For large groups or unreliable networks, a production app should use a media server or managed video service.
- Channels uses an in-memory channel layer for local/demo simplicity. A production multi-server deployment should use Redis.
- Focus Mode cannot block phone notifications or operating-system alerts. It encourages fullscreen, hides extra UI, detects tab switches/fullscreen exit, and recommends device Do Not Disturb.
- Music Mode does not bundle copyrighted music. It has a simple built-in focus tone and links to royalty-free ambience searches.

## Project structure

```text
study_girl/
  manage.py
  requirements.txt
  README.md
  .env.example
  Procfile
  render.yaml
  study_girl/       project settings, URLs, ASGI, WSGI
  accounts/         sign up and authentication helpers
  profiles/         students, tutors, subjects, applications, demo seed command
  tutoring/         session requests, study sessions, feedback, Study Sisters, Vibes
  sessions/         WebSocket consumer, chat messages, whiteboard events, room page
  resources/        solo study library and uploads
  moderation/       reports, guidelines, notification preferences
  dashboard/        home page, user dashboard, staff dashboard
  templates/        Django HTML templates
  static/           CSS, JavaScript, and placeholder artwork
```

## Local setup for students

1. Create and activate a virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
python -m pip install -r requirements.txt
```

3. Copy environment settings.

```powershell
Copy-Item .env.example .env
```

The app works with SQLite by default, so you do not need PostgreSQL for local practice.

4. Create the database tables.

```powershell
python manage.py makemigrations
python manage.py migrate
```

5. Create an admin user.

```powershell
python manage.py createsuperuser
```

6. Seed demo data for a presentation.

```powershell
python manage.py seed_demo
```

Demo accounts use password:

```text
demo12345
```

Examples: `student1`, `student2`, `tutor1`, `tutor2`.

7. Run the ASGI server.

```powershell
daphne study_girl.asgi:application
```

Open:

```text
http://127.0.0.1:8000/
```

You can also use Django's development server for normal pages:

```powershell
python manage.py runserver
```

For the live room WebSocket behavior, `daphne` is the better match because it runs the ASGI application.

## Running tests

```powershell
python manage.py test
```

## Render deployment

1. Push the project to GitHub.
2. Create a new Render Blueprint from `render.yaml`, or create a Web Service manually.
3. Add a PostgreSQL database on Render.
4. Set these environment variables:

```text
DEBUG=False
SECRET_KEY=<a long random secret>
ALLOWED_HOSTS=.onrender.com
DATABASE_URL=<Render PostgreSQL connection string>
```

5. Use this build command:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

6. Use this start command:

```bash
daphne study_girl.asgi:application --bind 0.0.0.0 --port $PORT
```

7. After deployment, run the `seed_demo` command from Render Shell if you want demo data.

## Admin workflow

- Create an admin with `python manage.py createsuperuser`.
- Visit `/admin/` to approve tutor profiles and review detailed records.
- Visit `/staff-dashboard/` for a presentation-friendly safety and activity summary.

For the MVP, tutor approval is controlled by `TutorProfile.approval_status`. Only profiles marked `approved` appear in tutor discovery.

## Future improvements

- Use Redis for Channels in production.
- Add email verification and stronger school identity checks.
- Add parent/teacher oversight workflows if required by school policy.
- Add richer tutor approval screens inside the app.
- Add CSEC curriculum mapping by topic and exam paper.
- Add Caribbean-wide location filters by island, parish, school, and timezone.
- Replace basic peer-to-peer WebRTC with a managed video infrastructure for reliability.
- Add resource review queues and file virus scanning before public release.
