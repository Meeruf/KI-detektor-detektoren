from flask import Blueprint
from flask import render_template, redirect, flash, url_for, send_from_directory
from flask import request, session
from .magic import RunTheDetectorDetector
from .models import ImageVariant, ImageRealestate, ImageAi, UniqueImage, DetectionResult, AIDetector
import matplotlib
matplotlib.use('Agg')  # Use the non-interactive backend suitable for scripts
import matplotlib.pylab as plt
from matplotlib.ticker import FuncFormatter
from sqlalchemy import or_, and_
from io import BytesIO
from flask import send_file
import seaborn as sns
import pandas as pd
import os
import re
import base64
from .seleniumScripts import ChatGPT

from .models import db

from PIL import Image, ImageStat

run_detector = RunTheDetectorDetector()


views = Blueprint('views', __name__)


""" Home Page """
@views.route('/')
def home():
    context = {}
    return render_template('index.html', context=context)



@views.route('/spesifikk')
def getspesificimage():
    imgs = ImageVariant.query.filter(ImageVariant.file_name == '20210913-_DSC3251.jpg', ImageVariant.edited == True).first()
    
    for result in imgs.detection_results:
        print(result.ai_result_float)
        print(result.detector.name)

    return "Ok"



@views.route('/matrix')
def matrix():
    imgs_unedited = ImageVariant.query.filter(ImageVariant.edited == False).all()
    imgs_ki = ImageAi.query.all()


    imgs = []
    i = 1
    for img in imgs_ki:
        imgs.append(img.getInfo(i))
        i += 1

    SORT_FOR = 'contentatscale.ai'

    df = pd.DataFrame(imgs)
    df_total_below_10 = df[(df[SORT_FOR] > 95)]
    df_total_above_50 = df_total_below_10[(df['isitAI.com'] < 50) | (df['illuminarty.ai'] < 50)]


    #melted_df = pd.melt(high_score_df, value_vars=['illuminarty.ai', 'contentatscale.ai'], var_name='Detector', value_name='Score')
    total_img = len(imgs_ki)
    print('Totalt:',  len(imgs_ki))
    print(len(df_total_below_10))
    print(len(df_total_above_50))

    labels = [f'Totalt antall bilder', 'ContentAtScale > 95%', 'Illuminarty eller IsItAI \n < 50%']
    counts = [len(imgs_ki), len(df_total_below_10), len(df_total_above_50)]


    # Creating a count plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(labels, counts, color=['lightgray', 'lightgreen', 'lightblue', 'green'])
    ax.set_title(f'({SORT_FOR}) - Detektor variasjon for KI-bilder')
    ax.set_ylabel('Number of Images')

    # Adding text inside each bar
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() / 2),
                    xytext=(0, 0),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='center', 
                    fontsize=16)

     # Save the plot to a BytesIO object instead of showing it
    img = BytesIO()
    plt.savefig(img, format='png')  # Correctly specify the format here
    img.seek(0)  # Go to the beginning of the BytesIO object"""

    # Return the plot as a response
    return send_file(img, mimetype='image/png')






@views.route('/movefiles')
def movefiles():
    def atoi(text):
        return int(text) if text.isdigit() else text
    # Function to split the filename into parts that are either digits or non-digits
    def natural_keys(text):
        return [atoi(c) for c in re.split(r'(\d+)', text)]


    LOAD_FROM = f'/Users/fure/03Prosjekter/VSProjects/AIDetectors/detector/static//Bildebank/temporary'
    LOAD_TO = f'/Users/fure/03Prosjekter/VSProjects/AIDetectors/detector/static//Bildebank/analyze'
    images = [os.path.join(LOAD_FROM, f) for f in sorted(os.listdir(LOAD_FROM), key=natural_keys) if f.endswith(('.jpg', '.jpeg', 'webp', 'png'))] 

    name = 442
    for img in images:
        file_type = img.split('.')[1]
        print(file_type)
        os.replace(img, f'{LOAD_TO}/{name}.{file_type}')
        name += 1


    return 'OK'


@views.route('/sammendrag')
def sammendrag():
    unedited_imgs = ImageVariant.query.filter(ImageVariant.edited == False).all()
    edited_imgs = ImageVariant.query.filter(ImageVariant.edited == True).all()
    re_imgs = ImageRealestate.query.filter_by().all()
    ki_imgs = ImageAi.query.all()

    mainUneditedList = []
    i = 1
    for img in unedited_imgs:
        mainUneditedList.append(img.getInfo(i))
        i += 1

    mainEditedList = []
    i = 1
    for img in edited_imgs:
        mainEditedList.append(img.getInfo(i))
        i += 1

    mainKIList = []
    i = 1
    for img in ki_imgs:
        mainKIList.append(img.getInfo(i))
        i += 1

    mainREList = []
    i = 1
    for img in re_imgs:
        mainREList.append(img.getInfo(i))
        i += 1
    
    unedited_data = pd.DataFrame(mainUneditedList)
    edited_data = pd.DataFrame(mainEditedList)
    ki_data = pd.DataFrame(mainKIList)
    re_data = pd.DataFrame(mainREList)

    # ALL COLUMS UNEDITED
    corr_data_unedtied = unedited_data.corr()
    corr_html_unedtied = corr_data_unedtied.to_html(classes='table table-striped')

    # DETECTORS ONLY UNEDITED
    detectors_only_unedited = unedited_data[['isitAI.com', 'illuminarty.ai', 'contentatscale.ai', 'hivemoderation.com']]
    detector_only_corr_unedited = detectors_only_unedited.corr()
    detector_only_corr_unedited_html = detector_only_corr_unedited.to_html(classes='table table-striped')

    # DETECTORS ONLY EDITED
    detectors_only_edited = edited_data[['isitAI.com', 'illuminarty.ai', 'contentatscale.ai', 'hivemoderation.com']]
    corr_data_edited = detectors_only_edited.corr()
    corr_html_edited = corr_data_edited.to_html(classes='table table-striped')

    # DETECTORS ONLY AI
    detectors_only_ai = ki_data[['isitAI.com', 'illuminarty.ai', 'contentatscale.ai', 'hivemoderation.com']]
    corr_data_ai = detectors_only_ai.corr()
    corr_html_ai = corr_data_ai.to_html(classes='table table-striped')

    # DETECTORS ONLY RE
    detectors_only_re = re_data[['isitAI.com', 'illuminarty.ai', 'contentatscale.ai', 'hivemoderation.com']]
    corr_data_re = detectors_only_re.corr()
    corr_html_re = corr_data_re.to_html(classes='table table-striped')

    

    def create_plot(data):
        plt.subplots(figsize=(7, 3))
        plt.xlabel('AI DETEKTOR')
        plt.ylabel('Sannsynlighet for KI (%)')
        plt.ylim(0, 100)

        print(len(data['isitAI.com']))

        sns.barplot(x=1, y=data['isitAI.com'], color='purple', label='1: isitAI.com',)
        sns.barplot(x=2, y=data['illuminarty.ai'], color='green', label='2: illuminarty.ai')
        sns.barplot(x=3, y=data['contentatscale.ai'], color='red', label='3: contentatscale.ai')
        sns.barplot(x=4, y=data['hivemoderation.com'], color='darkgray', label='4: hivemoderation.com')
        plt.legend()

        formatter = FuncFormatter(lambda x, _: f'{int(x)}%')
        plt.gca().yaxis.set_major_formatter(formatter)

        img = BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        return img



    unedited_plot = create_plot(unedited_data)
    edited_plot = create_plot(edited_data)
    KI_plot = create_plot(ki_data)

    RE_plot = create_plot(re_data)

    context = {
        'isitAI.com': round(unedited_data['isitAI.com'].describe()[1], 2),
        'contentatscale.ai': round(unedited_data['contentatscale.ai'].describe()[1], 2),
        'illuminarty.ai': round(unedited_data['illuminarty.ai'].describe()[1], 2),
        'hivemoderation.com': round(unedited_data['hivemoderation.com'].describe()[1], 2),
        'KI_isitAI.com': round(ki_data['isitAI.com'].describe()[1], 2),
        'KI_contentatscale.ai': round(ki_data['contentatscale.ai'].describe()[1], 2),
        'KI_illuminarty.ai': round(ki_data['illuminarty.ai'].describe()[1], 2),
        'KI_hivemoderation.com': round(ki_data['hivemoderation.com'].describe()[1], 2),
        'RE_isitAI.com': round(re_data['isitAI.com'].describe()[1], 2),
        'RE_contentatscale.ai': round(re_data['contentatscale.ai'].describe()[1], 2),
        'RE_illuminarty.ai': round(re_data['illuminarty.ai'].describe()[1], 2),
        'RE_hivemoderation.com': round(re_data['hivemoderation.com'].describe()[1], 2),
        'edited_isitAI.com': round(edited_data['isitAI.com'].describe()[1], 2),
        'edited_contentatscale.ai': round(edited_data['contentatscale.ai'].describe()[1], 2),
        'edited_illuminarty.ai': round(edited_data['illuminarty.ai'].describe()[1], 2),
        'edited_hivemoderation.com': round(edited_data['hivemoderation.com'].describe()[1], 2),
        'unedited_plot': base64.b64encode(unedited_plot.getvalue()).decode('utf-8'),
        'edited_plot': base64.b64encode(edited_plot.getvalue()).decode('utf-8'),
        'KI_plot': base64.b64encode(KI_plot.getvalue()).decode('utf-8'),
        'RE_plot': base64.b64encode(RE_plot.getvalue()).decode('utf-8'),
        'total_real_imgs': len(unedited_data),
        'total_edited_imgs': len(edited_data),
        'total_KI_imgs': len(ki_data),
        'total_RE_imgs': len(re_data),
        'corr_html_unedited': corr_html_unedtied,
        'detectors_only_ai_corr': corr_html_ai,
        'detectors_only_unedited_corr': detector_only_corr_unedited_html,
        'detectors_only_edited_corr': corr_html_edited,
        'detectors_only_re_corr': corr_html_re,
        
    }

    return render_template('sammendrag.html', context=context)






""" RealEstate"""
@views.route('/realestate', methods=['GET', 'POST'])
def realestate():
    plt.subplots(figsize=(13, 7))
    imgs = ImageRealestate.query.filter(or_(ImageRealestate.exposure_sequence == 4, ImageRealestate.exposure_sequence == 5)).all()
    imgs = ImageRealestate.query.all()

    
    mainList = []
    i = 1
    for img in imgs:
        mainList.append(img.getInfo(i))
        i += 1

    pd_data = pd.DataFrame(mainList)

    SORT_BY = ['EXPOSURE']
    pd_data = pd_data.sort_values(by=SORT_BY)

    print(' ')
    print('BOLIGFOTO')
    print(pd_data.describe())
    print(pd_data[['isitAI.com', 'illuminarty.ai', 'contentatscale.ai', 'hivemoderation.com', 'BRIGHTNESS']].corr())

    sns.scatterplot(x=range(0, len(pd_data['IMG_ID'])), y=pd_data['isitAI.com'], s=10, color='purple', label='1: isitAI.com')
    #sns.scatterplot(x=range(0, len(pd_data['IMG_ID'])), y=pd_data['illuminarty.ai'], s=10, color='green', label='2: illuminarty.ai')
    sns.scatterplot(x=range(0, len(pd_data['IMG_ID'])), y=pd_data['contentatscale.ai'], s=10, color='red', label='3: contentatscale.ai')
    sns.scatterplot(x=range(0, len(pd_data['IMG_ID'])), y=pd_data['hivemoderation.com'], s=10, color='darkgray', label='4: hivemoderation.com')



     # Save the plot to a BytesIO object instead of showing it
    img = BytesIO()
    plt.savefig(img, format='png')  # Correctly specify the format here
    img.seek(0)  # Go to the beginning of the BytesIO object

    # Return the plot as a response
    return send_file(img, mimetype='image/png')



""" AI """
@views.route('/ai', methods=['GET'])
def ai():
    plt.subplots(figsize=(13, 7))
    plt.title('KI Bilder')
    imgs = ImageAi.query.all()

    tempImgList = []
    i = 1
    for img in imgs:
        tempImgList.append(img.getInfo(i))
        i += 1
    
    pd_ai_img = pd.DataFrame(tempImgList)

    SORT_BY = ['IMG_ID']
    pd_ai_img = pd_ai_img.sort_values(by=SORT_BY)
    
    print(' ')
    print('AI BILDER')
    print(pd_ai_img.describe())
    print(' ')
    print(pd_ai_img[['isitAI.com', 'illuminarty.ai', 'contentatscale.ai', 'hivemoderation.com']].corr())

    sns.scatterplot(x=range(0, len(pd_ai_img['IMG_ID'])), y=pd_ai_img['isitAI.com'], s=10, color='purple', label='1: isitAI.com')
    sns.scatterplot(x=range(0, len(pd_ai_img['IMG_ID'])), y=pd_ai_img['illuminarty.ai'], s=10, color='green', label='2: illuminarty.ai')
    sns.scatterplot(x=range(0, len(pd_ai_img['IMG_ID'])), y=pd_ai_img['contentatscale.ai'], s=10, color='red', label='3: contentatscale.ai')
    sns.scatterplot(x=range(0, len(pd_ai_img['IMG_ID'])), y=pd_ai_img['hivemoderation.com'], s=10, color='darkgray', label='4: hivemoderation.com', )
    sns.scatterplot(x=range(0, len(pd_ai_img['IMG_ID'])), y=pd_ai_img['OpenAI'], s=10, color='blue', label='5: OpenAI',)

    #sns.scatterplot(x=range(0, len(unedited_data['IMG_ID'])), y=unedited_data[sofie123].corr(), label='contentatscale.ai', s=10)

    plt.legend()

    # Save the plot to a BytesIO object instead of showing it
    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')  # Correctly specify the format here
    img.seek(0)  # Go to the beginning of the BytesIO object

    # Return the plot as a response
    return send_file(img, mimetype='image/png')




""" RUN DETECTORS """
@views.route('/run', methods=['GET', 'POST'])
def run():
    if request.method == 'POST':
        if 'WORKING' in run_detector.status.values():
            run_detector.stop()
        else:
            run_detector.run()

    return render_template('run.html')




""" LEGGE INN MANUELT """
@views.route('/aiai', methods=['GET', 'POST'])
def aiai():
    import re

    ai_imgs = ImageAi.query.all()

    ai_start = 1
    real_start = 0
    for index in range(ai_start, len(ai_imgs)):
        img = ai_imgs[index]
        print(img.file_name)
        result = DetectionResult()
        
        
        string_answer = input('Enter Answer: ')
        if string_answer == 'EXIT':
            break
        
        float_answer = re.sub("[^0-9]", "", string_answer)
        result.ai_result_string = string_answer
        result.ai_result_float = float_answer
        result.detector_id = 5
        result.ai_image_id = img.id

        db.session.add(result)
        db.session.commit()

        print(string_answer)
        print(float_answer)

    return 'OK'



""" AI """
@views.route('/html_graf', methods=['GET'])
def html_graph():



    queried_data = ImageVariant.query.filter(ImageVariant.edited == True).all()
    queried_data_KI = ImageAi.query.all()
    queried_data_RE = ImageRealestate.query.filter_by(exposure_sequence=5)

    imgs = []
    for data in queried_data:
        all_above = True
        for result in data.detection_results:   
            if result.ai_result_float > 10 and result.detector_id == 2:
                all_above = False
            
        if all_above:
            imgs.append(data)



    imgsAI = ImageAi.query.filter().all()

    mergeList = []
    mainList = []
    i = 1
    for img in imgs:
        data = img.getInfoWithHTML(i)
        mainList.append(data)
        mergeList.append(data)
        i += 1

    mainListAi = []
    for img in imgsAI:
        data = img.getInfo(i)
        mainListAi.append(data)
        mergeList.append(data)
        i += 1


    width = 100 / len(mainList)
    totalwidth = width * len(mainList)

    context = {
        'images': mainList,
        'width': width,
        'totalwidth': totalwidth,
    }

    return render_template('visu.html', context=context)



""" RUN DETECTORS """
@views.route('/documentation', methods=['GET'])
def documentation():

    return render_template('documentation.html')