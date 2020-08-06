Module Implemented: Segmenting and Recognizing models and LaTeX transformation of encoding

Description:
It is an implementation of modules 3 and 4, viz, 
Module 3 -- Segmenting and Recognising models, implemented using a multi-scale architecture based on DenseNet121.
Module 4 -- Latex Transformation of the encoding, which takes in the encoding from module 3 and converts it into a LateX string. The model used is a GRU based decoder.

Both the modules have been combined to form an end-to-end model.
The LaTeX string obtained is parsed using a python module pylatexenc. The solution to the parsed string is obtained by making an API call to https://www.symbolab.com/solver/algebra-calculator.

For now, we have made a Django app to show the working; backend will later be connected with the mobile app.


Setting Up:
1. If desired, create a virtual environment of your choice.
2. Run "pip install -r requirements.txt" to install the python modules required to run the code.
3. Navigate to the location of the file manage.py and run the command "python manage.py runserver" in the terminal.
4. Open your browser and go to the URL http://localhost:8000 or http://127.0.0.1:8000.
5. Upload an image of a handwritten mathematical expression and submit.
6. The solution will show up in text areas under it.