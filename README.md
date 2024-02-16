# Fourier-Transform-Image-Processing-Mixer
Fourier Transform Mixer is a desktop application designed to illustrate the importance of magnitude and phase components in signal processing, particularly focusing on images through Fourier Transform (FT). It emphasizes the contribution of different frequencies to the signal.

## Features

### Image Viewers
- **Open and View Images:** Load and view up to four grayscale images simultaneously in separate viewports.
- **Color Conversion:** Automatically convert colored images to grayscale upon opening.
- **Unified Size:** Ensure that all opened images are resized to match the dimensions of the smallest image.
- **FT Components Display:** Each image viewport includes fixed displays for the image and an adjustable display showing different FT components (Magnitude, Phase, Real, Imaginary).
- **Easy Browse:** Switch between images by double-clicking on the respective viewer.

### Output Ports
- **Two Output Viewports:** The mixer result can be displayed in one of two output viewports, mirroring the input image viewports.

### Brightness/Contrast Adjustment
- **Image Enhancement:** Adjust brightness and contrast of any image viewport and its components using mouse dragging.

### Components Mixer
- **Weighted Average:** Compute the inverse Fourier Transform (ifft) of a weighted average of the FT of the four input images.
- **Customizable Weights:** Customize the weights of each image's FT via sliders for intuitive control.

### Regions Mixer
- **Frequency Regions Selection:** Choose regions for each FT component (inner/low frequencies or outer/high frequencies) using a selectable rectangle.
- **Customizable Region Size:** Adjust the size/percentage of the selected region via sliders or resize handles.

### Real-time Mixing
- **Progress Bar:** Display a progress bar during lengthy ifft operations to indicate the mixing process.
- **Interrupt Handling:** Cancel previous mixing operations upon user request for updates, ensuring seamless operation.

## Usage

1. **Open Images:** Double-click on the viewport to browse and open images. Colored images are automatically converted to grayscale.
2. **Adjust Brightness/Contrast:** Enhance image visibility by adjusting brightness and contrast using mouse dragging.
3. **Select FT Components:** Choose different FT components (Magnitude, Phase, Real, Imaginary) for visualization in the adjustable display.
4. **Customize Weights:** Adjust weights of each image's FT components using sliders to control mixing.
5. **Select Frequency Regions:** Define frequency regions (inner/low or outer/high frequencies) for each FT component using selectable rectangles.
6. **Monitor Mixing:** Track the progress of mixing operations with the progress bar. Interrupt ongoing operations for updates as needed.

## Code Practice

- Follow proper variable naming conventions and avoid code repetition.
- Implement OOP concepts for encapsulation and organization, with the majority of code residing within relevant classes.
- Utilize Python's logging library for effective debugging and problem resolution, documenting main user interactions and steps.

