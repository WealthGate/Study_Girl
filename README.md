# Study Girl

Study Girl is a Python-first Django MVP for high school female students at Wesley High School in Dominica.

Motto: **SBS - Students Becoming Sisters**

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/WealthGate/Study_Girl)
[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?type=git&builder=dockerfile&repository=github.com/WealthGate/Study_Girl&branch=main&name=studygirl&ports=8000;http;/&env[DEBUG]=False&env[ALLOWED_HOSTS]=.koyeb.app,localhost,127.0.0.1)

Planned public test URL after Koyeb deployment:

```text
https://studygirl-<your-koyeb-org>.koyeb.app
```

Koyeb assigns the exact `*.koyeb.app` URL after deployment.

Planned public test URL after Render deployment, if using Render:

```text
https://studygirl.onrender.com
```

If Render says the name is already taken, keep the service name close, such as `studygirl-dominica`. Render will show the final public URL after deployment.

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

## Temporary public test link

Use this option when students need to test from different locations before the app is permanently deployed. It runs the app on your computer and creates a temporary public HTTPS link through Cloudflare Tunnel.

This is best for short demonstrations. Keep the PowerShell window open while students are testing; closing it closes the public link.

```powershell
.\scripts\start-public-demo.ps1
```

The script will:

- run database migrations,
- refresh demo data,
- start the Daphne ASGI server if it is not already running,
- create a public `https://...trycloudflare.com` link that can be shared with students.

Demo accounts:

```text
student1 / demo12345
student2 / demo12345
tutor1 / demo12345
tutor2 / demo12345
```

Firebase Hosting and Netlify static hosting are not a good match for this app because Study Girl is a Django ASGI app with WebSockets. For a more permanent free or low-cost public link, use a Python/container host such as Koyeb or Render.

## Render deployment

The repository includes `render.yaml`, so Render can create the web service and PostgreSQL database from GitHub.

1. Open the GitHub repository:

```text
https://github.com/WealthGate/Study_Girl
```

2. Click the **Deploy to Render** button near the top of this README.
3. Sign in to Render and approve the Blueprint.
4. Keep the service name as `studygirl` if Render allows it.
5. Deploy.

The Blueprint sets these environment variables automatically:

```text
DEBUG=False
SECRET_KEY=<generated by Render>
ALLOWED_HOSTS=.onrender.com
DATABASE_URL=<connected to the Render PostgreSQL database>
```

The Blueprint uses this build command:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py seed_demo
```

The `seed_demo` step creates demo users so students can test the app immediately.

Demo accounts:

```text
student1 / demo12345
student2 / demo12345
tutor1 / demo12345
tutor2 / demo12345
```

The Blueprint uses this start command:

```bash
daphne study_girl.asgi:application --bind 0.0.0.0 --port $PORT
```

After deployment, Render will show the public app URL. If the `studygirl` service name is available, it should be:

```text
https://studygirl.onrender.com
```

If the public site shows an error after first deploy, open the Render service logs. Most first-deploy issues are missing environment variables or a database that has not finished provisioning yet.

## Free Koyeb deployment

If Render asks for payment, use Koyeb for the school testing link. This repository includes a `Dockerfile` and `start-koyeb.sh` for Koyeb.

1. Open the GitHub repository:

```text
https://github.com/WealthGate/Study_Girl
```

2. Click the **Deploy to Koyeb** button near the top of this README.
3. Sign in to Koyeb and connect GitHub if asked.
4. Keep the app name as:

```text
studygirl
```

5. Choose the free web service instance if Koyeb offers multiple choices.
6. Deploy.

Koyeb will show the public student testing URL after deployment. It will look similar to:

```text
https://studygirl-<your-koyeb-org>.koyeb.app
```

For this free test deployment, the app uses SQLite inside the service. The startup script runs migrations and `seed_demo` automatically, so demo accounts are available after each deployment:

```text
student1 / demo12345
student2 / demo12345
tutor1 / demo12345
tutor2 / demo12345
```

Important limitation: if the free service restarts from a fresh filesystem, demo data is recreated. This is acceptable for student testing, but a long-term school rollout should use PostgreSQL.

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
