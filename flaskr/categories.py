from flask import Blueprint, render_template

bp = Blueprint('categories', __name__, url_prefix='/categories')

# Agriculture
@bp.route('/agriculture')
def agriculture():
    return render_template('categories/agriculture.html')

# Education
@bp.route('/education')
def education():
    return render_template('categories/education.html')

# Women and Child
@bp.route('/women_child')
def women_child():
    return render_template('categories/women_child.html')

# Transport & Infrastructure
@bp.route('/transport')
def transport():
    return render_template('categories/transport.html')

# Sports & Culture
@bp.route('/sports_culture')
def sports_culture():
    return render_template('categories/sports_culture.html')

# Housing
@bp.route('/housing')
def housing():
    return render_template('categories/housing.html')

# Health
@bp.route('/health')
def health():
    return render_template('categories/health.html')

# Skills & Employment
@bp.route('/skills')
def skills():
    return render_template('categories/skills.html')
