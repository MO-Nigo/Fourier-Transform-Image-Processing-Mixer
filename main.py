from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from cv2 import dft
import pyqtgraph as pg
import numpy as np
from image_loader import Loader
# from image_processing import handle_combobox_change
from image_processing import plot_component
from mixing import Mixer
import os
from os import path 
import sys
import logging
import cv2
from sklearn.preprocessing import MinMaxScaler

# Set up the logging configuration
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

FORM_CLASS,_ = loadUiType(path.join(path.dirname(__file__),"main.ui"))

class MainApp(QMainWindow , FORM_CLASS):
    def __init__(self , parent=None):
        super(MainApp,self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)

        # Add logging statements
        logging.info("Application initialized")
        self.setup_ui_elements()
        self.setup_style_sheet()
        self.setup_image_views()
        self.setup_double_click_events()

        
        # App UI Customization
        self.setWindowTitle("Signal Equalizer")
        self.setWindowIcon(QIcon("download.png"))
        self.showMaximized()
        self.setup_combobox_handlers()
        self.common_shape = (255, 255)
        self.brightness_step = 10
        self.contrast_step = 50         
        self.brightness = 10
        self.contrast = 1.0
        self.image_dict = {'imgview11': None, 'imgview12': None, 'imgview13': None, 'imgview14': None}
        self.ft_components = {
            'imgview21': None,
            'imgview22': None,
            'imgview23': None,
            'imgview24': None,
        }
        # Variables to track mouse movement
        self.is_mouse_pressed = False
        self.mouse_last_pos = None

        # Add a variable to store the mixed array
        self.mixed_array = None

        # # Connect the btnMix button to the mix_arrays method
        # self.btnMix.clicked.connect(self.mix_arrays)
        
        # Create a QTimer for delaying the mixed image display
        self.delay_timer = QTimer(self)
        self.delay_timer.timeout.connect(self.display_mixed_array)

        
        
    def style_graph_widget(self):
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setBackground('w')
           
    def setup_style_sheet(self):
        
        self.setStyleSheet('''
            QLabel {
                font-size: 14px;
                color: black;
            }
            QPushButton {
                background-color: white;
                color: black;
                border: 1px solid #CCCCFF;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #CCCCFF;
                color: black;
            }
            QSlider::handle:horizontal {
                background: #CCCCFF;
                border: 1px solid #CCCCFF;
                width: 20px;
            }
            QSlider::handle:vertical {
                background: #CCCCFF;
                border: 1px solid #CCCCFF;
                width: 20px;
            }
            QComboBox {
                background-color: white;
                border: 1px solid #CCCCFF;
                padding: 1px 18px 1px 3px;
            }
            QComboBox:hover {
                background-color: #CCCCFF;
                border: 1px solid #CCCCFF;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #CCCCFF;
            }
            QComboBox QAbstractItemView {
                background: #CCCCFF;
                border: 1px solid #CCCCFF;
            }
        ''')

 
        # Customize the style sheet for the mixoutBox combobox
        self.mixoutBox.setStyleSheet(
            '''
            QComboBox {
                background-color: #CCCCFF;
                color: black;
                border: 1px solid #CCCCFF;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QComboBox:hover {
                background-color: white;
                color: black;
            }
            '''
        )
        self.modeBox.setStyleSheet(
            '''
            QComboBox {
                background-color: #CCCCFF;
                color: black;
                border: 1px solid #CCCCFF;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QComboBox:hover {
                background-color: white;
                color: black;
            }
            '''
        )
        self.roiBox.setStyleSheet(
            '''
            QComboBox {
                background-color: #CCCCFF;
                color: black;
                border: 1px solid #CCCCFF;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QComboBox:hover {
                background-color: white;
                color: black;
            }
            QProgressBar {
                border: 2px solid #CCCCFF;
                border-radius: 5px;
                background: white;
                padding: 1px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #CCCCFF;
                width: 5px;
                margin: 0.5px;
            }
        ''')
        
    # triggers
        # Assuming self.sliders is a list containing all your sliders
        sliders = [self.slider1, self.slider2, self.slider3, self.slider4]
        for index, slider in enumerate(sliders):
            slider.valueChanged.connect(lambda value, i=index, s=slider: self.update_label(value, s, i))
            slider.valueChanged.connect(self.mix_arrays)

        self.roiBox.currentIndexChanged.connect(self.mix_arrays)


    def update_label(self, value, slider, index):
        label_name = f"labelSlider{index + 1}"
        getattr(self, label_name).setText(f"{value}%")
        
    def setup_double_click_events(self):
         # Connect double-click events to the load_image_dialog method
        self.frame11.mouseDoubleClickEvent = lambda event: self.load_image_dialog('imgview11')
        self.frame12.mouseDoubleClickEvent = lambda event: self.load_image_dialog('imgview12')
        self.frame13.mouseDoubleClickEvent = lambda event: self.load_image_dialog('imgview13')
        self.frame14.mouseDoubleClickEvent = lambda event: self.load_image_dialog('imgview14')

        # Connect mouse events to adjust_brightness_contrast methods
        self.frame11.mousePressEvent = lambda event: self.mouse_press_event(event, 'imgview11')
        self.frame11.mouseMoveEvent = lambda event: self.mouse_move_event(event, 'imgview11')
        self.frame11.mouseReleaseEvent = lambda event: self.mouse_release_event(event, 'imgview11')
        
        self.frame12.mousePressEvent = lambda event: self.mouse_press_event(event, 'imgview12')
        self.frame12.mouseMoveEvent = lambda event: self.mouse_move_event(event, 'imgview12')
        self.frame12.mouseReleaseEvent = lambda event: self.mouse_release_event(event, 'imgview12')
        
        self.frame13.mousePressEvent = lambda event: self.mouse_press_event(event, 'imgview13')
        self.frame13.mouseMoveEvent = lambda event: self.mouse_move_event(event, 'imgview13')
        self.frame13.mouseReleaseEvent = lambda event: self.mouse_release_event(event, 'imgview13')
        
        self.frame14.mousePressEvent = lambda event: self.mouse_press_event(event, 'imgview14')
        self.frame14.mouseMoveEvent = lambda event: self.mouse_move_event(event, 'imgview14')
        self.frame14.mouseReleaseEvent = lambda event: self.mouse_release_event(event, 'imgview14')

    def setup_combobox_handlers(self):
        # connect the combobox with the events 
        self.box1.currentIndexChanged.connect(lambda: self.handle_combobox_change(self.box1, 'imgview21'))
        self.box2.currentIndexChanged.connect(lambda: self.handle_combobox_change(self.box2, 'imgview22'))
        self.box3.currentIndexChanged.connect(lambda: self.handle_combobox_change(self.box3, 'imgview23'))
        self.box4.currentIndexChanged.connect(lambda: self.handle_combobox_change(self.box4, 'imgview24'))


        
    
    def setup_ui_elements(self):
    
        ## Values el comboboxes, 34an mt7tago4 tft7o qt
        self.box1.setObjectName("box1")
        self.box1.addItems(["Choose component","FT Magnitude", "FT Phase", "FT Real","FT Imaginary"])
        self.box1.setCurrentIndex(0)

        self.box2.setObjectName("box2")
        self.box2.addItems(["Choose component","FT Magnitude", "FT Phase", "FT Real","FT Imaginary"])
        self.box2.setCurrentIndex(0)

        self.box3.setObjectName("box3")
        self.box3.addItems(["Choose component","FT Magnitude", "FT Phase", "FT Real","FT Imaginary"])
        self.box3.setCurrentIndex(0)

        self.box4.setObjectName("box4")
        self.box4.addItems(["Choose component","FT Magnitude", "FT Phase", "FT Real","FT Imaginary"])
        self.box4.setCurrentIndex(0)


        self.mixoutBox.setObjectName("mixoutBox")
        self.mixoutBox.addItem("Mixer Output")
        self.mixoutBox.addItem("1")
        self.mixoutBox.addItem("2")

        self.modeBox.setObjectName("modeBox")
        self.modeBox.addItem("Mode")
        self.modeBox.addItem("Mag/Phase")
        self.modeBox.addItem("Real/Imag")

        self.roiBox.setObjectName("roiBox")
        self.roiBox.addItem("ROI")
        self.roiBox.addItem("Inner")
        self.roiBox.addItem("Outter")

       

        # Add QGraphicsView widgets to each frame

    def setup_image_views(self):
        
        self.addImageView(self.frame11, 'imgview11')
        self.addImageView(self.frame12, 'imgview12')
        self.addImageView(self.frame13, 'imgview13')
        self.addImageView(self.frame14, 'imgview14')
        self.addImageView(self.frame21, 'imgview21')
        self.addImageView(self.frame22, 'imgview22')
        self.addImageView(self.frame23, 'imgview23')
        self.addImageView(self.frame24, 'imgview24')
        self.addImageView(self.frame31, 'imgview31')
        self.addImageView(self.frame32, 'imgview32')

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Image Views in Frames')
        self.show()
        # Add a dictionary to store rubber bands for each image view
        self.rubber_bands = {
            'imgview21': QRubberBand(QRubberBand.Rectangle, self.frame21),
            'imgview22': QRubberBand(QRubberBand.Rectangle, self.frame22),
            'imgview23': QRubberBand(QRubberBand.Rectangle, self.frame23),
            'imgview24': QRubberBand(QRubberBand.Rectangle, self.frame24),
        }
    
    def mouse_press_event(self, event, imgview_name):
        # Handle mouse press event
        self.is_mouse_pressed = True
        self.mouse_last_pos = event.pos()
        event.accept()

    def mouse_move_event(self, event, imgview_name):
        # Handle mouse move event
        if self.is_mouse_pressed and self.mouse_last_pos:
            dx = event.pos().x() - self.mouse_last_pos.x()
            dy = event.pos().y() - self.mouse_last_pos.y()
            self.adjust_brightness_contrast(dx, dy, imgview_name)
            self.mouse_last_pos = event.pos()
        event.accept()
    
    def mouse_release_event(self, event, imgview_name):
        # Handle mouse release event
        self.is_mouse_pressed = False
        self.mouse_last_pos = None
        event.accept()

    def adjust_brightness_contrast(self, dx, dy, imgview_name):
        # Adjust brightness and contrast based on mouse movement
        if imgview_name in ['imgview11', 'imgview12', 'imgview13', 'imgview14']:
            # Modify the calculation to consider the direction of the mouse movement
            brightness_change = dx / self.brightness_step
            contrast_change = dy/ self.contrast_step

            # Update the brightness value, subtracting the change for left movement
            self.brightness += brightness_change
            self.contrast += contrast_change

            # Update the image after adjusting brightness
            self.update_image(imgview_name)
 
    def update_image(self, imgview_name):
        img_view = self.findChild(QGraphicsView, imgview_name)
        if img_view:
            scene = img_view.scene()
            if scene:
                items = scene.items()
                if items:
                    pixmap_item = items[0]  # Assuming there is only one item in the scene

                    # Load the original image
                    original_image, loaded_pixmap = self.image_dict[imgview_name], self.grayscale_pix_map

                    # Adjust brightness and contrast
                    adjusted_image = self.adjust_brightness_contrast_internal(original_image, self.brightness, self.contrast)

                    # Convert NumPy array to QImage
                    height, width = adjusted_image.shape
                    bytes_per_line = width
                    q_image = QImage(adjusted_image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)

                    # Update the existing QPixmap in the QGraphicsPixmapItem
                    pixmap_item.setPixmap(QPixmap.fromImage(q_image))


    def adjust_brightness_contrast_internal(self, image, brightness, contrast):
        # Convert the image to a NumPy array
        img_array = np.array(image)

        # Adjust brightness and contrast
        img_array = np.clip((img_array + brightness) * contrast, 0, 255).astype(np.uint8)

        return img_array
    
    def load_image_dialog(self, imgview_name):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.xpm *.jpg *.bmp *.gif)", options=options)
        load= Loader
        if file_name:
            try:

                # Utilize the load_image function from imageloader module
                image_data,loaded_pixmap =load.load_image(self, file_name, imgview_name)      
                
                self.image_dict[imgview_name]=image_data 
                # Store grayscale_pix_map as an attribute
                self.grayscale_pix_map = loaded_pixmap
                logging.info(f"Loaded image: {file_name}")
            except Exception as e:
                logging.error(f"Error loading image: {e}")      
     
    def handle_combobox_change(self, combobox, imgview_name):
        current_index = combobox.currentIndex()
        imgview_mapping = {
        'imgview21': 'imgview11',
        'imgview22': 'imgview12',
        'imgview23': 'imgview13',
        'imgview24': 'imgview14',
        }
        try:
            # Retrieve the source imgview based on the target imgview using the dictionary
            source_imgview_name = imgview_mapping.get(imgview_name)
            # Retrieve the image from the source imgview
            source_img = self.image_dict.get(source_imgview_name)
            ft_component = plot_component(self, imgview_name, source_img, current_index)
            self.ft_components[imgview_name] = ft_component
            logging.info(f"Changed combobox {combobox.objectName()} to index {current_index}")
        except Exception as e:
            logging.error(f"Error handling combobox change: {e}")

         
    def addImageView(self, parent_frame, imgview_name):
        # Create a QGraphicsView for image display

        img_view = QGraphicsView(parent_frame)
        img_view.setObjectName(imgview_name)

        # Set up a QGraphicsScene and QGraphicsPixmapItem
        scene = QGraphicsScene()
        pixmap_item = QGraphicsPixmapItem()
        scene.addItem(pixmap_item)
        img_view.setScene(scene)

        # Load an example image 
        pixmap = QPixmap('C:/Users/Struggler/Desktop/Task 4/task4/icon.png')
        pixmap_item.setPixmap(pixmap)

        # Fit the view to the pixmap item
        img_view.fitInView(pixmap_item, Qt.AspectRatioMode.IgnoreAspectRatio)

        # Add the QGraphicsView to the frame's layout
        frame_layout = QVBoxLayout(parent_frame)
        frame_layout.addWidget(img_view)

        # Enable rubber band selection on the QGraphicsView
        img_view.setRubberBandSelectionMode(Qt.IntersectsItemBoundingRect)

        # Create a rubber band selection rectangle
        rubber_band = QRubberBand(QRubberBand.Rectangle, img_view)
        rubber_band.setGeometry(QRect())

        def start_selection(event):
            # Start the rubber band selection
            rubber_band.setGeometry(QRect(event.pos(), QSize()))
            rubber_band.show()

        def update_selection(event):
            # Update the rubber band selection rectangle
            rubber_band.setGeometry(QRect(rubber_band.pos(), event.pos()).normalized())
            rectangle_geometry = rubber_band.geometry()
            self.x1 = rectangle_geometry.x()
            self.y1 = rectangle_geometry.y()

            self.x2 = self.x1 + rectangle_geometry.width()
            self.y2 = self.y1 + rectangle_geometry.height()
            # Propagate the rubber band selection to other image views
            self.handle_rubber_band_selection()

        if imgview_name in ['imgview21', 'imgview22', 'imgview23', 'imgview24']:    
            # Connect the mouse events to the corresponding functions
            img_view.mousePressEvent = start_selection
            img_view.mouseMoveEvent = update_selection
    
    def handle_rubber_band_selection(self):
        # Handle rubber band selection, e.g., propagate the selection to other image views
        for imgview_name, rubber_band in self.rubber_bands.items():
            if imgview_name != 'imgview21' and any(self.ft_components[imgview_name].flatten()):  # Skip the source image
                rubber_band.setGeometry(QRect(self.x1, self.y1, self.x2 - self.x1, self.y2 - self.y1))
                rubber_band.show()
            
    def mix_arrays(self):
        try:
            # Retrieve weights from sliders
            weight1 = self.slider1.value() / 100
            weight2 = self.slider2.value() / 100
            weight3 = self.slider3.value() / 100
            weight4 = self.slider4.value() / 100
            weights = [ weight1 , weight2, weight3 ,weight4]
            dims = [self.x1,self.y1,self.x2,self.y2]

            # Retrieve FT component arrays
            array21 = self.ft_components['imgview21']
            array22 = self.ft_components['imgview22']
            array23 = self.ft_components['imgview23']
            array24 = self.ft_components['imgview24']
            arrays = [array21, array22, array23, array24]

            # Mix arrays based on selected combination
            self.mixed_array = None
            index_1 = self.box1.currentIndex()
            index_2 = self.box2.currentIndex()
            index_3 = self.box3.currentIndex()
            index_4 = self.box4.currentIndex()
            indicies = [index_1, index_2, index_3, index_4]
            roi = self.roiBox.currentText()
            mode = self.modeBox.currentText()
            mixer=Mixer
            if mode == "Mag/Phase":  # Magnitude-Phase
                self.mixed_array = mixer.mix_magnitude_phase(arrays, indicies,weights,dims,roi)
            elif mode == "Real/Imag":  # Real-Imaginary
                self.mixed_array = mixer.mix_real_imaginary(arrays, indicies,weights,dims,roi)
                

            self.display_mixed_array(self.mixed_array)

        except Exception as e:
            logging.error(f"Error mixing arrays: {e}")

        
    def display_mixed_array(self, mixed_array):
        try:
            # self.progressBar.setValue(0)  # Each step is 5% of the progress bar

            # Apply inverse Fourier transform to get the mixed image
            mixed_image = np.clip(np.abs(np.fft.ifft2(mixed_array)),0,255)

            # Convert the mixed image to uint8 for display
            mixed_image_uint8 = mixed_image.astype(np.uint8)

            # Check the current text of the mixoutBox combobox
            mixout_box_text = self.mixoutBox.currentText()

            # Display the mixed image in the appropriate QGraphicsView
            if mixout_box_text == "1":
                img_view = self.findChild(QGraphicsView, 'imgview31')
            elif mixout_box_text == "2":
                img_view = self.findChild(QGraphicsView, 'imgview32')
            else:
                logging.warning("Invalid mixoutBox selection. Unable to determine QGraphicsView.")
                return

            if img_view:                
                # Retrieve the existing scene
                scene = img_view.scene()
                # Clear the existing items in the scene
                scene.clear()
                pixmap_item = QGraphicsPixmapItem()

                # Convert the mixed image to a QImage
                height, width = mixed_image_uint8.shape
                bytes_per_line = width
                mixed_qimage = QImage(
                    mixed_image_uint8.tobytes(), width, height, bytes_per_line, QImage.Format_Grayscale8
                )
                pixmap_item.setPixmap(QPixmap.fromImage(mixed_qimage))
                scene.addItem(pixmap_item)

                # Fit the view to the new pixmap item
                img_view.setScene(scene)
                img_view.fitInView(pixmap_item, Qt.AspectRatioMode.IgnoreAspectRatio)
                logging.info("Mixed array displayed successfully.")
            else:
                logging.warning("Unable to find QGraphicsView for display.")

        except Exception as e:
            logging.error(f"Error displaying mixed array: {e}")
    


def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()


