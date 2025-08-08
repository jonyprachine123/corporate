# Corporate Website

A Flask-based corporate website with admin panel and content management.

## Features

- Public pages (Home, About, Services, Contact, etc.)
- Admin dashboard with login
- File upload functionality
- Responsive design
- Database integration

## Deployment

This project uses GitHub Actions for automatic deployment to cPanel.

### Setup GitHub Secrets

Add the following secrets to your GitHub repository:

1. Go to your GitHub repository
2. Click on Settings → Secrets and variables → Actions
3. Add these repository secrets:

```
FTP_SERVER: prachinbd.com
FTP_USERNAME: prachinbd
FTP_PASSWORD: your_cpanel_password
```

### Automatic Deployment

When you push to the `main` or `master` branch, GitHub Actions will:

1. Install Python dependencies
2. Deploy files to your cPanel server via FTP
3. Update your live website automatically

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Initialize database:
   ```bash
   python init_db.py
   ```

3. Run the application:
   ```bash
   python app.py
   ```

## File Structure

- `app.py` - Main Flask application
- `init_db.py` - Database initialization
- `passenger_wsgi.py` - WSGI configuration for cPanel
- `templates/` - HTML templates
- `static/` - CSS, JS, images, and uploads
- `database.db` - SQLite database

## cPanel Configuration

Ensure your cPanel is configured to:
- Support Python applications
- Point to `passenger_wsgi.py` as the startup file
- Set the correct Python version (3.9+)