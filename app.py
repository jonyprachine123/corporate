import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, g, send_from_directory
from werkzeug.utils import secure_filename

# --- App Configuration ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key_here' # Change this!
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.config['ALLOWED_IMAGE_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'webp'}
app.config['DATABASE'] = 'database.db'

# --- Helper Functions ---

def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row # Allows accessing columns by name
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()

def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def allowed_image_file(filename):
    """Checks if the image file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_IMAGE_EXTENSIONS']

# --- Public-Facing Routes ---

@app.route('/')
def home():
    db = get_db()
    gallery_images = db.execute('SELECT id, title, filename FROM gallery WHERE is_active = 1 ORDER BY sort_order ASC, timestamp DESC').fetchall()
    return render_template('public/index.html', gallery_images=gallery_images)

@app.route('/about')
def about():
    return render_template('public/about.html')

@app.route('/about/founder')
def founder():
    return render_template('public/founder.html')

@app.route('/about/cofounder')
def cofounder():
    return render_template('public/cofounder.html')

@app.route('/about/chairman')
def chairman():
    return render_template('public/chairman.html')

@app.route('/about/board-of-directors')
def board_of_directors():
    return render_template('public/board_of_directors.html')

@app.route('/about/company-profile')
def company_profile():
    return render_template('public/company_profile.html')

@app.route('/about/managing-director')
def managing_director():
    return render_template('public/managing_director.html')

@app.route('/services')
def services():
    return render_template('public/services.html')

@app.route('/enterprise')
def enterprise():
    return render_template('public/enterprise.html')

@app.route('/notices')
def notices():
    db = get_db()
    all_notices = db.execute('SELECT id, title, filename, timestamp FROM notices ORDER BY timestamp DESC').fetchall()
    return render_template('public/notices.html', notices=all_notices)

@app.route('/contact')
def contact():
    return render_template('public/contact.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Provides a route to serve the uploaded PDF files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/robots.txt')
def robots_txt():
    """Serves robots.txt file to prevent search engine indexing."""
    return send_from_directory('static', 'robots.txt')

# --- Admin Routes ---

@app.route('/admin')
def admin_redirect():
    """Redirects to the login page if not logged in, otherwise to the dashboard."""
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        
        if user:
            session['logged_in'] = True
            session['username'] = user['username']
            flash('You were successfully logged in!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    db = get_db()
    all_notices = db.execute('SELECT id, title, filename, timestamp FROM notices ORDER BY timestamp DESC').fetchall()
    gallery_images = db.execute('SELECT id, title, filename, is_active, sort_order, timestamp FROM gallery ORDER BY sort_order ASC, timestamp DESC').fetchall()
    return render_template('admin/dashboard.html', notices=all_notices, gallery_images=gallery_images)

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/add', methods=['POST'])
def add_notice():
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))

    title = request.form['title']
    notice_date = request.form['notice_date']
    
    if 'pdf_file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('admin_dashboard'))

    file = request.files['pdf_file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('admin_dashboard'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # To avoid overwriting files with the same name, you could append a timestamp
        # from datetime import datetime
        # filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{secure_filename(file.filename)}"
        
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        db = get_db()
        db.execute('INSERT INTO notices (title, filename, timestamp) VALUES (?, ?, ?)', (title, filename, notice_date))
        db.commit()

        flash('New notice has been successfully added!', 'success')
    else:
        flash('Invalid file type. Only PDFs are allowed.', 'danger')
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/<int:notice_id>', methods=['POST'])
def delete_notice(notice_id):
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))

    db = get_db()
    notice = db.execute('SELECT * FROM notices WHERE id = ?', (notice_id,)).fetchone()

    if notice:
        # Delete the file from the filesystem
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], notice['filename']))
        except FileNotFoundError:
            flash('File not found on server, but deleting from database.', 'warning')

        # Delete the record from the database
        db.execute('DELETE FROM notices WHERE id = ?', (notice_id,))
        db.commit()
        flash('Notice has been successfully deleted.', 'success')
    else:
        flash('Notice not found.', 'danger')
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_gallery_image', methods=['POST'])
def add_gallery_image():
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))

    title = request.form['image_title']
    sort_order = request.form.get('sort_order', 0)
    
    if 'image_file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('admin_dashboard'))

    file = request.files['image_file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('admin_dashboard'))

    if file and allowed_image_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid filename conflicts
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        name, ext = os.path.splitext(filename)
        filename = f"{timestamp}_{name}{ext}"
        
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        db = get_db()
        db.execute('INSERT INTO gallery (title, filename, sort_order) VALUES (?, ?, ?)',
                   (title, filename, sort_order))
        db.commit()

        flash('Gallery image uploaded successfully!', 'success')
    else:
        flash('Invalid file type. Please upload a valid image file.', 'danger')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/toggle_gallery_image/<int:image_id>', methods=['POST'])
def toggle_gallery_image(image_id):
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))

    db = get_db()
    image = db.execute('SELECT * FROM gallery WHERE id = ?', (image_id,)).fetchone()
    
    if image:
        new_status = 0 if image['is_active'] else 1
        db.execute('UPDATE gallery SET is_active = ? WHERE id = ?', (new_status, image_id))
        db.commit()
        flash(f'Gallery image {"activated" if new_status else "deactivated"} successfully!', 'success')
    else:
        flash('Gallery image not found.', 'danger')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_gallery_image/<int:image_id>', methods=['POST'])
def delete_gallery_image(image_id):
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))

    db = get_db()
    image = db.execute('SELECT * FROM gallery WHERE id = ?', (image_id,)).fetchone()
    
    if image:
        # Delete the file from filesystem
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], image['filename'])
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete from database
        db.execute('DELETE FROM gallery WHERE id = ?', (image_id,))
        db.commit()
        flash('Gallery image deleted successfully!', 'success')
    else:
        flash('Gallery image not found.', 'danger')

    return redirect(url_for('admin_dashboard'))


# --- Run the App ---
if __name__ == '__main__':
    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)