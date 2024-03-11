import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from PIL import Image, ImageStat
from .models import UniqueImage, ImageVariant, AIDetector, DetectionResult, Keyword, ImageRealestate, ImageAi
from .models import db
from detector import app
import threading
from . import functions
import time


class RunTheDetectorDetector():
    def __init__(self):
        """ 
        Creates an instance object that will connect the the listed detectors, 
        upload the images then collect the results to be saved in the database.

        1: BEFORE USE:
        Set the correct settings for the type of image you are analyzing, and set the destination folder for completed images depending on images types.

        2: HOW TO USE:
        Use the 'run' method to start collecting results. The instance will collect images from the 'analyze' folder, then upload them to the detectors. 
        Results will be added to the pending_data dictionary consecutively, and as soon as an image have results from all listed detectors, 
        the result will be saved in the database. When saved successfully, the image file will be moved to the 'analyzed' folder. """
        
        """ SETTINGS """
        EDITED = False                                #
        REALESTATE = False                            #
        AI = True                                     #
        DESTIANTION_FOLDER = 'realestate'             # OPTIONS: 'AI', 'edited', 'realestate', 'unedited'

        """VARIABLES"""
        # Images in the analyze folder will append to self.images when the run method is called.
        self.images = None
        self.LOAD_FROM = f'{app.static_folder}/Bildebank/analyze'

        # Selenium driver variables
        self.driver_objects = []
        self.options = Options()
        self.options.add_experimental_option("detach", True)

        # Image looping and collection of data
        self.currently_working = False
        self.pending_data = {}
        self.composition_name_for_loop = ''
        self.exposure_sequence = 1
        self.lock = threading.Lock()
        self.status = {}

        # Terminal updates while scanning
        self.progress = {'count': 0, 'total:': 0, 'message': ''}
        
        # SETTINGS
        self.SETTINGS = {
            'FOLDER_PATH':      f'/Bildebank/archive/{DESTIANTION_FOLDER}',
            'edited':           EDITED,
            'multiple_compositions': REALESTATE,
            'ai_image': AI
        }

        # Hivemoderation flow variables
        self.firstClick = True
        self.terms_of_agreement_clicked = False

    
    def run(self):
        """ 
        ..:: REMEMBER TO SET THE CORRECT IMAGE TYPE SETTINGS ::..
        - Collects images from the 'analyze' folder, connects to the listed detectors, then save the data to the database.
        - Images are sent to each detector in separate threads. 
        Some detectors use more time to analyze than other, meaning some threads may finish sooner than others. """
        
        self.images = [os.path.join(self.LOAD_FROM, f) for f in sorted(os.listdir(self.LOAD_FROM), key=functions.natural_keys) if f.endswith(('.jpg', '.jpeg', 'webp', 'png'))]     
        self.currently_working = True
        self.progress['total'] = len(self.images) * 4
        
        # Currently listed detectors. Each detectors have separate methods and selenium scripts to run successfully.
        ADRESSES = {
            'isitAI.com': 'https://isitai.com/ai-image-detector/',
            'illuminarty.ai': 'https://app.illuminarty.ai/#/image',
            'hivemoderation.com': 'https://chromewebstore.google.com/detail/hive-ai-detector/cmeikcgfecnhojcbfapbmpbjgllklcbi?utm_source=ext_app_menu',
            'contentatscale.ai': 'https://contentatscale.ai/ai-image-detector/?fpr=ddiy&fp_sid=aiiamgedetect',
        }
        
        # Is it AI
        worker1 = threading.Thread(target=self.loopImages, args=(ADRESSES, 'isitAI.com'))
        # Illuminarty´
        worker2 = threading.Thread(target=self.loopImages, args=(ADRESSES, 'illuminarty.ai'))
        # Hive AI detector
        worker3 = threading.Thread(target=self.loopImages, args=(ADRESSES, 'hivemoderation.com'))
        # Contentatscale.com
        worker4 = threading.Thread(target=self.loopImages, args=(ADRESSES, 'contentatscale.ai'))
        
        def startWorkers():
            worker1.start()
            time.sleep(1)
            worker2.start()
            time.sleep(1)
            worker4.start()
            time.sleep(1)
            worker3.start()
        startWorkers()

        # Save results thread.
        worker6 = threading.Thread(target=self.process_pending_data)
        worker6.start()

    def loopImages(self, webpage_adress, detector_name):
        """ Loops through all the images in self.images. 
        1: Each image will be sent throught a custom function that manage each unique detector website with Selenium.
        2: These funtions will return either the result or a "TIMEOUT". If timout, if will wait 10 seconds then try the same image again.
        3: The metadata from the image will be collected.
        4: The result and metadata from each image will be temporary saved in self.pending_data until results from all listed detectors exists.
        5: The process of saving complete images to the database happens in self.process_pending_data.
        
        Parameters
        ----------
        webpage_adress: str
            The webpage URL from where the Selenium will start working from.
        webpage_name:
            The name of the detector. This parameter is also the identifyer for the detector while in temporary storage, 
            and the identifyer the AIDetector database model. Changing this name after collection of results have started, 
            will result in creating a new detector in the database like it would be a complete different detector. 
            Therefore, dont change this name after collection have started.     """

        with app.app_context():
            # app.app_context is neccery as this method is running in separate threads.
            
            # Create driver instances for each detector.
            driver = webdriver.Chrome(options=self.options)
            driver.get(webpage_adress[detector_name])
            self.status[detector_name] = 'WORKING'

            # Import selenium scripts
            from detector import seleniumScripts

            # .:: Step 1 ::.
            # Main loop for self.images, created from the files in the 'analyze' folder. Each file is sent to separate functions 
            # that is created for each AI-detector website.  
            for i in range(0, len(self.images)):

                # This while loop will break if the results is returned successfully.
                while True:
                    
                    # .:: Step 2 ::.
                    # Get result for the current image from the listed detectors.
                    if detector_name == 'isitAI.com':
                        ai_result = seleniumScripts.isitAI(self, self.images[i], driver)
                    if detector_name == 'illuminarty.ai':
                        ai_result = seleniumScripts.illuminarty(self, self.images[i], driver)
                    if detector_name == 'hivemoderation.com':
                        ai_result = seleniumScripts.hivemoderation(self, self.images[i], driver)
                    if detector_name == 'contentatscale.ai':
                        ai_result = seleniumScripts.contentatscale(self, self.images[i], driver)

                    # Checks if the result is a 'TIMEOUT', then retry after 10 seconds.
                    if ai_result == 'TIMEOUT':
                        time.sleep(10)
                    else:
                        break
                
                # .:: Step 3 ::.
                # Get the metadata from the current image.
                meta = self.get_metadata(self.images[i], ai_result, detector_name)
                
                # If current image does not exist in the dicionary as a key, create a key with the unique image file name before saving the result.
                if self.images[i] not in self.pending_data:
                    self.pending_data[self.images[i]] = {}

                # .:: Step 4 ::.
                # Temporary save the result and metadata for the current image until a result from all listed detectors exists.
                self.pending_data[self.images[i]][detector_name] = meta
                self.progress['count'] += 1

            # When all images is analysed, quit the driver.
            driver.quit()
            self.status[detector_name] = 'COMPLETE'

    def process_pending_data(self):
        """ Will scan the variable self.pending_data every 4 seconds for images containing results from all listed detectors.

        When found, the data is saved to the database, and removed from the temporary storage variable.
        This is to avoid data being saved permanently if a detector thread should timeout permanently or fail in other ways.  
        """
        
        
        time.sleep(4)
        with app.app_context():
            while self.currently_working:
                time.sleep(4)
                with self.lock:

                    # Loops through all images in temporary storage.
                    for image in list(self.pending_data.keys()):

                        # When a image have 4 results, it has a result from all listed detectors.
                        if len(self.pending_data[image]) == 4:
                            print(f'.::Saving data::.')
                            img_saved = ''

                            # Loops throught the results from each AI-detector.
                            for webpage in self.pending_data[image]:
                                time.sleep(0.1)

                                data = self.pending_data[image][webpage]
                                # Send the image data to appropiate function depending
                                # on the image type that is set in the settings before scanning.
                                
                                if self.SETTINGS['multiple_compositions']:
                                    self.save_to_DB_multiple_comp(data)
                                
                                elif self.SETTINGS['ai_image']:
                                    self.save_to_DB_AI(data)

                                else:
                                    self.save_to_DB(data)
                                

                                # Update terminal
                                img_saved = data['IMG_NAME']
                                print(f'Saved result from: {webpage}')
                            print(f'-- Save Complete: {img_saved} \n\n')

                            # Move the image file to the archive folder set in the settings, 
                            # and delete the temporary data in self.pending_data.
                            os.replace(image, f"{app.static_folder}{self.SETTINGS['FOLDER_PATH']}/{img_saved}")
                            del self.pending_data[image]



                # Determines when scanning from all detectors is complete.
                if 'WORKING' not in self.status.values():
                    self.currently_working = False
                    break
        
                    
            # Checks if everything got saved correctly.
            self.status_report()
                
    def status_report(self):
        """ Loops throught all images in self.images when all images have been scanned to look for missing data. 
        Report is printed in terminal.   """
        MISSING_DATA = False
        MISSING_DATA_LIST = []
        for IMG_PATH in self.images:
            if self.SETTINGS['ai_image']:
                img = ImageAi.query.filter_by(file_name=os.path.basename(IMG_PATH)).first()
            else:
                if self.SETTINGS['multiple_compositions']:
                    img = ImageRealestate.query.filter_by(file_name=os.path.basename(IMG_PATH)).first()
                else:
                    img = ImageVariant.query.filter_by(file_name=os.path.basename(IMG_PATH), edited=self.SETTINGS['edited']).first()  

            if len(img.detection_results) != 4:
                MISSING_DATA = True
                MISSING_DATA_LIST.append(img.file_name)
            

        # Terminal report
        print('.::DATA REPORT::. ')
        print('Is data missing: ', MISSING_DATA, '\n')
        if MISSING_DATA:
            print(MISSING_DATA_LIST)
        else:
            print('ALL GOOD :)\n')

    def get_metadata(self, IMG_PATH, ai_result, detector_name):
        """ Collects the metadata, the result and the name of the AI-detector used, process all the data, and returns the data in a dictionary with appropiate key values.
        
        Parameters
        ----------
        IMG_PATH : str
            The image file path. Used to open the file with PILLOW to collect the metadata.
        ai_result : str
            The result in the format of percentage in how likely the image is AI-generated.
        detector_name : str
            The name of the AI-detector used to get the result.

        Returns
        -------
        A dictionary with metadata from the image, the result and the detector used.
        
        """
        image = Image.open(IMG_PATH)

        meta_keywords_list  = []
        try:
            meta_keywords = meta_keywords.decode('ASCII').replace('ASCII', '').replace('\x00', '')
            meta_keywords_list = [word.strip() for word in meta_keywords.split(',')]

        except (AttributeError, UnboundLocalError):
            meta_keywords = []

        ai_result_float = float(ai_result)
    
        # If the image is a AI-generated image, ignore exif data as it doesnt exist.
        if self.SETTINGS['ai_image'] == True:
            return {
                'IMG_NAME':     os.path.basename(IMG_PATH),
                'IMG_PATH':     IMG_PATH,
                'ai_result':    round(ai_result_float, 2),
                'keywords':     meta_keywords_list,
                'width':        int(image.width),
                'height':       int(image.height),
                'webpage_name': detector_name,
            }

        else:
            exif_data = image._getexif()

            # Get focal lenght
            focal = exif_data.get(41989)
            if focal == None:
                focal =  str(exif_data.get(37386))

            # Get ISO value
            iso = exif_data.get(34866)
            if iso == None:
                iso = exif_data.get(34867)


            # Calculate average brightness
            stat = ImageStat.Stat(image.convert('L'))
            average_brightness = sum(stat.mean) / len(stat.mean)

            # Get the pixel values
            pixels = list(image.getdata())

            sum_red, sum_green, sum_blue = 0, 0, 0
            for red, green, blue in pixels:
                sum_red += red
                sum_green += green
                sum_blue += blue


            return {
                'IMG_NAME':     os.path.basename(IMG_PATH),
                'IMG_PATH':     IMG_PATH,
                'ai_result':    round(ai_result_float, 2),
                'camera':       f'{exif_data.get(271)} {exif_data.get(272)}',
                'capture_date': datetime.strptime(str(exif_data.get(306)), "%Y:%m:%d %H:%M:%S"),
                'lens':         str(exif_data.get(42036)),
                'focal':        str(focal),
                'aperture':     str(round(2 ** (exif_data.get(37378) / 2), 1)),
                'ISO':          str(exif_data.get(34866)),
                'shutter':      str(round(2 ** (-float(exif_data.get(37377))), 2)),
                'brightness':   float(average_brightness),
                'red':          round(sum_red / len(pixels), 1),
                'blue':         round(sum_blue / len(pixels), 1),
                'green':        round(sum_green / len(pixels), 1),
                'minmax_lens':  str(exif_data.get(42034)),
                'keywords':     meta_keywords_list,
                'width':        int(image.width),
                'height':       int(image.height),
                'webpage_name': detector_name,
            }

    def save_to_DB(self, data):
        """ Method used to save the image metadata and AI-detector result to the database. Used for real images, unedited and edited.
        
        Parameters
        ----------
        data : dictionary
            A dictionary containing metadata, result and name of the detector. 
        """
        detector_name = data['webpage_name']

        main_img = UniqueImage.query.filter_by(file_name=data['IMG_NAME']).first()
        if main_img == None:
            main_img = UniqueImage()
            main_img.file_name = data['IMG_NAME']
            main_img.img_type = ''
            main_img.capture_date = data['capture_date']
            main_img.camera = data['camera']
            main_img.shutter_speed = data['shutter']
            main_img.iso = data['ISO']
            main_img.aperture = data['aperture']
            main_img.focal_length = data['focal']
            main_img.height = data['height']
            main_img.width = data['width']
            db.session.add(main_img)
            db.session.commit()


        img = ImageVariant.query.filter_by(file_name=data['IMG_NAME'], edited=self.SETTINGS['edited']).first()
        if img == None:
            img = ImageVariant()
            img.file_path = f"{self.SETTINGS['FOLDER_PATH']}/{data['IMG_NAME']}"
            img.file_name = data['IMG_NAME']
            img.unique_img_id = main_img.id
            img.edited = self.SETTINGS['edited']
            img.brightness = data['brightness']
            img.red_avg = data['red']
            img.blue_avg = data['blue']
            img.green_avg = data['green']

            db.session.add(img)
            db.session.commit()

        for keyword in data['keywords']:
            keyword = Keyword()
            keyword.name = keyword
            keyword.image_id = main_img.id
            db.session.add(keyword)
            db.session.commit()

        detector = AIDetector.query.filter_by(name=detector_name).first()
        if detector == None:
            detector = AIDetector()
            detector.name = detector_name
            db.session.add(detector)
            db.session.commit()

        result = DetectionResult()
        result.image_id = img.id
        result.detector_id = detector.id
        result.ai_result_string = data['ai_result']
        result.ai_result_float = float(data['ai_result'])

        db.session.add(result)
        db.session.commit()

    def save_to_DB_AI(self, data):
        """ Method used to save the image metadata and AI-detector results to the database. Used for AI-generated images.
        
        Parameters
        ----------
        data : dictionary
            A dictionary containing metadata, result and name of the detector. 
        """
        detector_name = data['webpage_name']

        main_img = UniqueImage.query.filter_by(file_name=data['IMG_NAME']).first()
        if main_img == None:
            main_img = UniqueImage()
            main_img.file_name = data['IMG_NAME']
            main_img.img_type = 'AI'
            main_img.height = data['height']
            main_img.width = data['width']
            db.session.add(main_img)
            db.session.commit()


        img = ImageAi.query.filter_by(file_name=data['IMG_NAME']).first()
        if img == None:
            img = ImageAi()
            img.file_path = f"{self.SETTINGS['FOLDER_PATH']}/{data['IMG_NAME']}"
            img.file_name = data['IMG_NAME']

            db.session.add(img)
            db.session.commit()

        for keyword in data['keywords']:
            keyword = Keyword()
            keyword.name = keyword
            keyword.image_id = main_img.id
            db.session.add(keyword)
            db.session.commit()

        detector = AIDetector.query.filter_by(name=detector_name).first()
        if detector == None:
            detector = AIDetector()
            detector.name = detector_name
            db.session.add(detector)
            db.session.commit()

        result = DetectionResult()
        result.ai_image_id = img.id
        result.detector_id = detector.id
        result.ai_result_string = data['ai_result']
        result.ai_result_float = float(data['ai_result'])

        db.session.add(result)
        db.session.commit()

    def save_to_DB_multiple_comp(self, data):
        """ Method used to save the image metadata and AI-detector results to the database. Used for real estate images.
        
        Parameters
        ----------
        data : dictionary
            A dictionary containing metadata, result and name of the detector. 
        """
        detector_name = data['webpage_name']
        if self.exposure_sequence == 1:
            self.composition_name_for_loop = data['IMG_NAME']

        new_img = UniqueImage.query.filter_by(file_name=self.composition_name_for_loop).first()
        if not new_img:
            new_img = UniqueImage()
            new_img.file_name = self.composition_name_for_loop
            new_img.img_type = ''
            new_img.capture_date = data['capture_date']
            new_img.camera = data['camera']
            new_img.iso = data['ISO']
            new_img.aperture = data['aperture']
            new_img.focal_length = data['focal']
            db.session.add(new_img)
            db.session.commit()

        img = ImageRealestate.query.filter_by(file_name=data['IMG_NAME']).first()
        if not img:
            img = ImageRealestate()
            img.file_name = data['IMG_NAME']
            img.file_path = f"{self.SETTINGS['FOLDER_PATH']}/{data['IMG_NAME']}"
            img.unique_img_id = new_img.id
            img.shutter_speed = data['shutter']
            img.exposure_sequence = self.exposure_sequence
            img.brightness = data['brightness']

            db.session.add(img)
            db.session.commit()

        for keyword in data['keywords']:
            keyword = Keyword()
            keyword.name = keyword
            keyword.image_id = img.id
            db.session.add(keyword)
            db.session.commit()

        detector = AIDetector.query.filter_by(name=detector_name).first()
        if not detector:
            detector = AIDetector()
            detector.name = detector_name
            db.session.add(detector)
            db.session.commit()

        result = DetectionResult()
        result.realestate_img_id = img.id
        result.detector_id = detector.id
        result.ai_result_string = str(data['ai_result'])
        result.ai_result_float = float(data['ai_result'])

        db.session.add(result)
        db.session.commit()

        self.exposure_sequence += 1
        if self.exposure_sequence == 5:
            self.exposure_sequence = 1

         
    def stop(self):
        for driver in self.driver_objects:
            driver.quit()

    