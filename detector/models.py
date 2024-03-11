from flask_sqlalchemy import SQLAlchemy
from flask import url_for
db = SQLAlchemy()


from datetime import datetime


class UniqueImage(db.Model):
    """ Base model for images. """
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    img_type = db.Column(db.String(50), nullable=False)

    capture_date = db.Column(db.DateTime, nullable=True)
    camera = db.Column(db.String(100), nullable=True)
    shutter_speed = db.Column(db.String(50), nullable=True)
    aperture = db.Column(db.String(50), nullable=True)
    focal_length = db.Column(db.String(50), nullable=True)
    iso = db.Column(db.Integer, nullable=True)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)

    keywords = db.relationship('Keyword', backref='image')


class ImageVariant(db.Model):
    """ Model for for real images, unedited and edited. """
    id = db.Column(db.Integer, primary_key=True)
    unique_img_id = db.Column(db.Integer, db.ForeignKey('unique_image.id'))
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)

    brightness = db.Column(db.Float)
    red_avg = db.Column(db.Float)
    green_avg = db.Column(db.Float)
    blue_avg = db.Column(db.Float)

    edited = db.Column(db.Boolean)

    unique_img = db.relationship('UniqueImage', backref='img_variant', uselist=False)
    detection_results = db.relationship('DetectionResult', backref='img_variant')


    def getInfo(self, i: int):
        
        infoDict = {}
        infoDict['IMG_ID'] = int(i)
        infoDict['ISO'] = float(self.unique_img.iso)
        infoDict['SHUTTER'] = float(self.unique_img.shutter_speed)
        infoDict['FOCAL'] = float(self.unique_img.focal_length)
        infoDict['BRIGHTNESS'] = float(self.brightness)
        infoDict['RED'] = float(self.red_avg)
        infoDict['GREEN'] = float(self.green_avg)
        infoDict['BLUE'] = float(self.blue_avg)

        for result in self.detection_results:
            infoDict[result.detector.name] = result.ai_result_float

        return infoDict
    
    def getInfoWithHTML(self, i: int):
        
        infoDict = {}
        infoDict['IMG_ID'] = int(i)
        infoDict['ISO'] = float(self.unique_img.iso)
        infoDict['SHUTTER'] = float(self.unique_img.shutter_speed)
        infoDict['FOCAL'] = float(self.unique_img.focal_length)
        infoDict['BRIGHTNESS'] = float(self.brightness)
        infoDict['RED'] = float(self.red_avg)
        infoDict['GREEN'] = float(self.green_avg)
        infoDict['BLUE'] = float(self.blue_avg)
        infoDict['URL'] = url_for('static', filename=f'/Bildebank/archive/unedited/{self.file_name}')

        for result in self.detection_results:
            infoDict[result.detector.name] = result.ai_result_float

        return infoDict
    


class ImageAi(db.Model):
    """ Model for AI-generated images. """
    id = db.Column(db.Integer, primary_key=True)
    unique_img_id = db.Column(db.Integer, db.ForeignKey('unique_image.id'))
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)

    unique_img = db.relationship('UniqueImage', backref='img_ai', uselist=False)
    detection_results = db.relationship('DetectionResult', backref='img_ai')

    def getInfo(self, i: int):
        
        infoDict = {}
        infoDict['IMG_ID'] = int(i)

        for result in self.detection_results:
            infoDict[result.detector.name] = result.ai_result_float

        return infoDict
    
    def getInfoWithHTML(self, i: int):
        
        infoDict = {}
        infoDict['IMG_ID'] = int(i)
        infoDict['URL'] = url_for('static', filename=f'/Bildebank/archive/AI/{self.file_name}')

        for result in self.detection_results:
            infoDict[result.detector.name] = result.ai_result_float

        return infoDict


class ImageRealestate(db.Model):
    """ Model for real estate images. """
    id = db.Column(db.Integer, primary_key=True)
    unique_img_id = db.Column(db.Integer, db.ForeignKey('unique_image.id'))
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)

    exposure_sequence = db.Column(db.Integer, nullable=False)
    shutter_speed = db.Column(db.String(50), nullable=True)
    brightness = db.Column(db.Float, nullable=False)

    unique_img = db.relationship('UniqueImage', backref='img_realestate', uselist=False)
    detection_results = db.relationship('DetectionResult', backref='img_realestate')

    def getInfo(self, i: int):
        
        infoDict = {}
        infoDict['IMG_ID'] = int(i)
        infoDict['ISO'] = float(self.unique_img.iso)
        infoDict['SHUTTER'] = float(self.shutter_speed)
        infoDict['FOCAL'] = float(self.unique_img.focal_length)
        infoDict['BRIGHTNESS'] = float(self.brightness)
        infoDict['EXPOSURE'] = int(self.exposure_sequence)

        for result in self.detection_results:
            infoDict[result.detector.name] = result.ai_result_float

        return infoDict
    
    def getInfoWithHTML(self, i: int):
        
        infoDict = {}
        infoDict['IMG_ID'] = int(i)
        infoDict['ISO'] = float(self.unique_img.iso)
        infoDict['SHUTTER'] = float(self.shutter_speed)
        infoDict['FOCAL'] = float(self.unique_img.focal_length)
        infoDict['BRIGHTNESS'] = float(self.brightness)
        infoDict['EXPOSURE'] = int(self.exposure_sequence)
        infoDict['URL'] = url_for('static', filename=f'/Bildebank/archive/realestate/{self.file_name}')

        for result in self.detection_results:
            infoDict[result.detector.name] = result.ai_result_float

        return infoDict 


class Keyword(db.Model):
    """ Model for image keywords """
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('unique_image.id'), nullable=False)
    name = db.Column(db.String(100), nullable=True)

class AIDetector(db.Model):
    """ Model for AI detectors. """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    detection_results = db.relationship('DetectionResult', backref='detector')

    def __repr__(self):
        return self.name

class DetectionResult(db.Model):
    """ Model for AI detector results. """
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image_variant.id'), nullable=True, default=None)
    ai_image_id = db.Column(db.Integer, db.ForeignKey('image_ai.id'), nullable=True, default=None)
    realestate_img_id = db.Column(db.Integer, db.ForeignKey('image_realestate.id'), nullable=True, default=None)

    detector_id = db.Column(db.Integer, db.ForeignKey('ai_detector.id'), nullable=False)
    
    detection_date = db.Column(db.DateTime, nullable=False, default=datetime.now())
    ai_result_string = db.Column(db.String(50), nullable=False)
    ai_result_float = db.Column(db.Float, nullable=True)


    def __rep__(self):
        return f'{self.ai_result_float}, {self.detector_id}'