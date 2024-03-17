from flask import render_template
from website import db  # Import db from the current package
from website.errors import bp  # Import bp from the errors module within the current package
from flask_login import current_user


@bp.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html', user=current_user), 404


@bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html', user=current_user), 500
