# Universal Workflow Language Interface
![Logo](/Logo/Logo_readme_v1.png?raw=true)

UWLi (Universal Workflow Language interface) is a user interface for building and modifying UWL files. UWL is a data format used to represent high fidelity scientific procedures in a generalized, field agnostic workflow format.

To get involved in development or implementation or to learn more contact Robert Epps at repps@nrel.gov.

![Logo](/Logo/Summary_readme_v1.png?raw=true)

# Installation
## Windows
Clone this repository to your local machine. Navigate to "UWL.exe" and double click the file. A second window should appear followed by the interface.

## Python (Required for Mac)
### Conda Installation (optional)
If you do not have acess to pip or python, then a good way to install both is through Anaconda.
1. Go to the website https://anaconda.org/ and follow the instructions to download and install Anaconda.
2. Once installed, navigate to the Environments tab on the left side of the interface.
3. Click "Create" and pick an environment name like "uwl_env", and make sure Python version 3.11.9 is selected. Click create and wait for Anaconda to finish creating your environment.
4. Next navigate to your terminal or to Anaconda's CMD.exe Prompt, depending on your operating system, and activate your conda environment:
```shell
conda activate uwl_env
```
The command line should look roughly like this:
```shell
(uwl_env) C:\Users\bhill>
```

### Software Installation
The following instructions will allow you to run UWLi using python.
1. Clone this repository to your local machine, then navigate to the directory location using the command prompt or terminal. Replace "< file path >" with the directory file path location of your clone of this repository. Note the command prompt can be accessed through the Windows start menu or through Anaconda if available.
```shell
cd < file path >
```

2. Then install the required packages using the command prompt. This step only needs to be done once. After the packages have been installed, then simply follow steps 1 and 3 to launch the software.
```shell
pip install -r requirements.txt
```

3. Finally, run the python command to launch the software.
```shell
python main.py
```

### Common Problems
1. If the terminal displays an error related to PyQt5, then try uninstalling then reinstalling PyQt5 with pip.
```shell
pip uninstall pyqt5
pip install pyqt5
```

2. If you get a dependency error, check if you are running Python version 3.11.9.

UWLi should launch as a separate window and be available to use.
