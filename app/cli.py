import click
from flask.cli import with_appcontext
from . import db
from .models import User
import os
from datetime import datetime
import shutil

def init_app(app):
    @app.cli.command('make-admin')
    @click.argument('username')
    def make_admin(username):
        """Make a user an admin."""
        user = User.query.filter_by(username=username).first()
        if user:
            user.is_admin = True
            db.session.commit()
            print(f'Made {username} an admin')
        else:
            print(f'User {username} not found')

    @app.cli.command('backup-db')
    def backup_db():
        """Backup the database."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        src = 'instance/recipes.db'
        dst = f'{backup_dir}/recipes_{timestamp}.db'
        
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f'Database backed up to {dst}')
        else:
            print('Database file not found')

    @app.cli.command('restore-db')
    @click.argument('backup_file')
    def restore_db(backup_file):
        """Restore the database from a backup."""
        if not os.path.exists(backup_file):
            print(f'Backup file {backup_file} not found')
            return
        
        # Stop Flask app if running
        dst = 'instance/recipes.db'
        if os.path.exists(dst):
            os.rename(dst, f'{dst}.old')
        
        try:
            shutil.copy2(backup_file, dst)
            print(f'Database restored from {backup_file}')
        except Exception as e:
            print(f'Error restoring database: {e}')
            if os.path.exists(f'{dst}.old'):
                os.rename(f'{dst}.old', dst)
                print('Reverted to old database') 