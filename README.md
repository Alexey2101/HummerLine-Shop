# HummerLine Shop

A Django-based e-commerce platform.

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd shop-college-main
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Copy `.env.example` to `.env` and configure your local settings.
   ```bash
   cp .env.example .env
   ```
   *Note: Ensure you set a unique `SECRET_KEY` and configure `DEBUG` accordingly.*

5. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Start the Development Server:**
   ```bash
   python manage.py runserver
   ```

## Technologies Used
- Django
- SQLite
- GSAP Animations

## GitHub Repository
To link this project to your GitHub repository:
```bash
gh repo create hummerline-shop --public --source=. --remote=origin --push
```
*Or use standard Git commands:*
```bash
git remote add origin <your-github-repo-url>
git branch -M main
git push -u origin main
```
