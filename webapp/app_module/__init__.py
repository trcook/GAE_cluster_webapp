from flask import Flask
app = Flask(__name__)




# from app_module.valid import validator
import app_module.main_views
import app_module.compute_views
