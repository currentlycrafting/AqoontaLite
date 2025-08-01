# 📚 Flask Learning App

A lightweight Flask web application for browsing educational lessons and taking quizzes. Each lesson is loaded dynamically from JSON files, and quizzes are interactive with automatic scoring.

---

## 🚀 Features

- 📂 Load lessons from structured JSON files  
- 📝 Interactive quizzes for each topic  
- 🔍 Simple HTML interface without templates (HTML is generated directly)  
- 📊 Immediate feedback and scoring after quiz submission  
- 📁 Clean separation of content (`data/lessons/` and `data/quizzes/`)  

---

## 🛠️ Project Structure
├── app.py # Main Flask app with routing and logic
├── data/
│ ├── lessons/ # Folder for lesson JSON files
│ └── quizzes/ # Folder for quiz JSON files


---

## 📄 Example Lesson JSON (`data/lessons/business.json`)

{
  "title": "Business Basics",
  "sections": [
    {
      "heading": "Introduction to Business",
      "content": "Business involves the activity of making one's living by producing or buying and selling products..."
    },
    {
      "heading": "Types of Businesses",
      "content": "There are several types of businesses, including sole proprietorships, partnerships, corporations..."
    }
  ]
}


## 💻 Running the App

### 1. Clone the repository

```bash
git clone https://github.com/your-username/flask-learning-app.git
cd flask-learning-app

python3 -m venv venv
source venv/bin/activate
pip3 install requirements.txt
python3 app.py




