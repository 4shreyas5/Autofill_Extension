from flask import Flask,jsonify,request
import pickle
from pyppeteer import launch
import nest_asyncio
import asyncio
import nltk
import string
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import easyocr

app = Flask(__name__)

model = pickle.load(open('model.pkl','rb'))
tfid = pickle.load(open('vectoriser.pkl','rb'))
categ_model = pickle.load(open('category_model.pkl','rb'))
categ_tfid = pickle.load(open('category_vectoriser.pkl','rb'))


def transform_text(text):
    # Convert the text to lowercase
    text = text.lower()

    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))

    # Tokenize the text
    tokens = nltk.word_tokenize(text)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]

    # Stemming using Porter Stemmer
    porter = PorterStemmer()
    tokens = [porter.stem(word) for word in tokens]

    # Join the tokens back into a string
    processed_text = ' '.join(tokens)

    return processed_text



# Download NLTK resources (run only once)
nltk.download('stopwords')
nltk.download('punkt')


nest_asyncio.apply()

async def take_screenshot(url):
    try:
        # Increase the timeout for browser launch (in milliseconds)
        browser = await launch(args=['--no-sandbox', '--disable-dev-shm-usage'], timeout=30000)
        page = await browser.newPage()

        # Navigate to the website
        await page.goto(url, {'waitUntil': 'networkidle0'})

        # Wait for 2 seconds using asyncio.sleep
        await asyncio.sleep(2)

        # Take a full-page screenshot with higher quality (adjust the quality value as needed)
        screenshot_path = 'screenshot.png'  # Replace with your desired file path
        await page.screenshot({'path': screenshot_path, 'fullPage': True, 'quality': 100})

        # Close the browser
        await browser.close()

    except Exception as e:
        print(f"Error during browser launch: {e}")
    reader = easyocr.Reader(['en'])
    results = reader.readtext('screenshot.png')
    # Concatenate all OCR results into a single string
    original_text = []
    for (_,text,_) in results:
        original_text.append(text)
    return original_text




def predict(url):
    result = {}
    textList = asyncio.get_event_loop().run_until_complete(take_screenshot(url))
    trans_text=[]
    for i in textList:
        trans_text.append(transform_text(i))
    for i in range(len(textList)):
        vec = tfid.transform([trans_text[i]]).toarray()
        predict = model.predict(vec)
        if predict == 1:
            vec = categ_tfid.transform([trans_text[i]]).toarray()
            categ_predict = categ_model.predict(vec)
            category = ""
            if categ_predict==0:
                category += "forced action"
            elif categ_predict==1:
                category += "misdirection"
            elif categ_predict==2:
                category += "obstruction"
            elif categ_predict == 3:
                category += "scarcity"
            elif categ_predict == 4:
                category += "sneaking"
            elif categ_predict==5:
                category += "social proof"
            elif categ_predict ==6:
                category += "urgency"
            result[textList[i]] = category
        else:
            continue
    return result

@app.route('/',methods = ["POST"])
def home():
    data = request.json
    currentUrl = data.get("url",'')
    result = predict(currentUrl)
    return jsonify(result)

app.run()
