https://github.com/mba7/SerialPort-RealTime-Data-Plotter/blob/master/com_monitor.py

```
(venv_w) D:\IdeaProjects\firmware>python --version
Python 3.8.2
(venv_w) D:\IdeaProjects\firmware>pip --version
pip 23.2.1 from d:\ideaprojects\firmware\venv_w\lib\site-packages\pip (python 3.8)
```

PythonQwt-0.10.3
https://github.com/PlotPyStack/PythonQwt

plotpy-1.99.0
https://plotpy.readthedocs.io/en/latest/
 using  PythonQwt==0.9.0
 
Installation PlotPy
```
git clone https://github.com/PlotPyStack/plotpy.git
cd plotpy
pip install build
python -m build
```
in folder plotpy/dist are 2 files:  
D:\IdeaProjects\firmware\plotpy\dist\PlotPy-1.99.0.tar.gz
D:\IdeaProjects\firmware\plotpy\dist\PlotPy-1.99.0-cp38-cp38-win_amd64.whl
```
pip install quidata PythonQwt SciPy Pillow tiffile pyserial PySide6
pip install plotpy --no-index --find-links D:\IdeaProjects\firmware\plotpy\dist\PlotPy-1.99.0-cp38-cp38-win_amd64.whl
```
Log
```
(venv_w) D:\IdeaProjects\firmware>pip install plotpy --no-index --find-links D:\IdeaProjects\firmware\plotpy\dist\PlotPy-1.99.0-cp38-cp38-win_amd64.whl
Looking in links: d:\IdeaProjects\firmware\plotpy\dist\PlotPy-1.99.0-cp38-cp38-win_amd64.whl
Processing d:\ideaprojects\firmware\plotpy\dist\plotpy-1.99.0-cp38-cp38-win_amd64.whl
Requirement already satisfied: guidata>=3.0.1 in d:\ideaprojects\firmware\venv_w\lib\site-packages (from plotpy) (3.0.5)
Requirement already satisfied: PythonQwt>=0.10 in d:\ideaprojects\firmware\venv_w\lib\site-packages (from plotpy) (0.10.3)
Requirement already satisfied: NumPy>=1.3 in d:\ideaprojects\firmware\venv_w\lib\site-packages (from plotpy) (1.24.4)
Requirement already satisfied: SciPy>=0.7 in d:\ideaprojects\firmware\venv_w\lib\site-packages (from plotpy) (1.10.1)
Requirement already satisfied: Pillow in d:\ideaprojects\firmware\venv_w\lib\site-packages (from plotpy) (10.0.1)
Requirement already satisfied: tifffile in d:\ideaprojects\firmware\venv_w\lib\site-packages (from plotpy) (2023.7.10)
Requirement already satisfied: h5py>=3.0 in d:\ideaprojects\firmware\venv_w\lib\site-packages (from guidata>=3.0.1->plotpy) (3.9.0)
Requirement already satisfied: QtPy>=1.9 in d:\ideaprojects\firmware\venv_w\lib\site-packages (from guidata>=3.0.1->plotpy) (2.4.0)
Requirement already satisfied: requests in d:\ideaprojects\firmware\venv_w\lib\site-packages (from guidata>=3.0.1->plotpy) (2.31.0)
Requirement already satisfied: tomli in d:\ideaprojects\firmware\venv_w\lib\site-packages (from guidata>=3.0.1->plotpy) (2.0.1)
Requirement already satisfied: packaging in d:\ideaprojects\firmware\venv_w\lib\site-packages (from QtPy>=1.9->guidata>=3.0.1->plotpy) (23.2)
Requirement already satisfied: charset-normalizer<4,>=2 in d:\ideaprojects\firmware\venv_w\lib\site-packages (from requests->guidata>=3.0.1->plotpy) (3.3.0)
Requirement already satisfied: idna<4,>=2.5 in d:\ideaprojects\firmware\venv_w\lib\site-packages (from requests->guidata>=3.0.1->plotpy) (3.4)
Requirement already satisfied: urllib3<3,>=1.21.1 in d:\ideaprojects\firmware\venv_w\lib\site-packages (from requests->guidata>=3.0.1->plotpy) (2.0.6)
Requirement already satisfied: certifi>=2017.4.17 in d:\ideaprojects\firmware\venv_w\lib\site-packages (from requests->guidata>=3.0.1->plotpy) (2023.7.22)
Installing collected packages: plotpy
Successfully installed plotpy-1.99.0
```