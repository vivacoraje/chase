from . import main
from flask import render_template
import json

@main.route('/')
def home():
    return render_template(
      'index.html', 
      style='/static/css/app.24128ce2a4fbf9cb77f6266cc1b6d90b.css',
      manifest='/static/js/manifest.2ae2e69a05c33dfc65f8.js',
      vendor='/static/js/vendor.9bad099314efa6aeac70.js',
      app='/static/js/app.9e33d0d691b041d16aae.js'
      )
