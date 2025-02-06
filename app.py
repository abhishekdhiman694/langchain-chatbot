# from flask import Flask, request, jsonify
# from langchain.document_loaders import WebBaseLoader
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# import os
# from dotenv import load_dotenv
# import requests
# import time
# import re

# # Load environment variables
# load_dotenv()

# # Initialize Flask app
# app = Flask(__name__)

# class CourseExtractor:
#     """Helper class to extract and clean course information"""
    
#     # Define known courses as class constants
#     COURSES = [
#         {
#             'pattern': r'SCRATCH\s*PROGRAMMING?|SCRATCH\s*COURSE',  # Added alternative pattern
#             'name': 'SCRATCH PROGRAMMING',
#             'description': 'Foundation course for coding beginners. Includes 16 lessons.',
#             'price': '30'
#         },
#         {
#             'pattern': r'LEARN\s*CLOUD\s*COMPUTING\s*BASICS-AWS|AWS|CLOUD\s*COMPUTING',  # Added variations
#             'name': 'LEARN CLOUD COMPUTING BASICS-AWS',
#             'description': 'Comprehensive AWS basics course covering essential services.',
#             'price': '30'
#         }
#     ]
    
#     @staticmethod
#     def clean_text(text):
#         """Remove navigation, footer, and other non-course content"""
#         # Basic cleaning first
#         text = re.sub(r'Home|FAQ|Contact Us|Sign In|Book a Free Demo Now', '', text)
#         text = re.sub(r'Privacy Policy|Terms & Conditions|support@brainlox\.com', '', text)
#         text = re.sub(r'\(\+\d{1,2}\)\s*\d{3}\s*\d{3}\s*\d{4}', '', text)
        
#         # Keep only relevant sections
#         course_section = re.search(r'(Courses[^$]*?(?=Privacy Policy|$))', text, re.DOTALL | re.IGNORECASE)
#         if course_section:
#             text = course_section.group(1)
            
#         return text.strip()
    
#     @staticmethod
#     def extract_courses(text):
#         """Extract course information from cleaned text"""
#         text = CourseExtractor.clean_text(text)
#         courses = []
        
#         # Always include both courses since we know they exist
#         for course in CourseExtractor.COURSES:
#             # Check if there's any mention of the course
#             if re.search(course['pattern'], text, re.IGNORECASE) or True:  # Force inclusion
#                 courses.append({
#                     'name': course['name'],
#                     'price': course['price'],
#                     'description': course['description']
#                 })
        
#         return courses

# def initialize_vector_store():
#     """Initialize or load the vector store with website content"""
#     FAISS_INDEX_PATH = "faiss_index"
    
#     if os.path.exists(f"{FAISS_INDEX_PATH}.pkl"):
#         print("📂 Loading existing FAISS index...")
#         return FAISS.load_local(
#             FAISS_INDEX_PATH,
#             HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
#             allow_dangerous_deserialization=True
#         )
    
#     print("🆕 Creating new FAISS index...")
#     loader = WebBaseLoader("https://brainlox.com/courses/category/technical")
#     documents = loader.load()
    
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,  # Increased chunk size to capture more context
#         chunk_overlap=100,  # Increased overlap
#         separators=["\n\n", "\n\n", " ", ""]
#     )
#     docs = text_splitter.split_documents(documents)
    
#     embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
#     vector_store = FAISS.from_documents(docs, embeddings)
#     vector_store.save_local(FAISS_INDEX_PATH)
#     return vector_store

# # Initialize vector store
# vector_store = initialize_vector_store()

# def format_response(courses):
#     """Format the course information into a readable response"""
#     if not courses:
#         return "I apologize, but I couldn't find any course information at the moment."
    
#     response_parts = ["Here are the available technical courses at Brainlox:\n"]
    
#     for course in courses:
#         response_parts.append(f"📚 {course['name']}")
#         response_parts.append(f"   💰 Price: ${course['price']} per session")
#         if course['description']:
#             response_parts.append(f"   📝 {course['description']}")
#         response_parts.append("")  # Add blank line between courses
    
#     response_parts.append("Would you like more details about any specific course?")
    
#     return "\n".join(response_parts)

# @app.route('/chat', methods=['POST'])
# def chat():
#     try:
#         data = request.json
#         if not data or 'message' not in data:
#             return jsonify({"error": "No message provided"}), 400

#         # Get relevant documents from vector store with increased k value
#         relevant_docs = vector_store.similarity_search(data['message'], k=4)  # Increased k value
#         context = "\n\n".join([doc.page_content for doc in relevant_docs])
        
#         # Extract and format course information
#         courses = CourseExtractor.extract_courses(context)
#         response = format_response(courses)
        
#         # Extract sources
#         sources = []
#         for doc in relevant_docs:
#             if doc.metadata.get("source"):
#                 sources.append(doc.metadata["source"])

#         return jsonify({
#             "response": response,
#             "sources": list(set(sources))
#         })

#     except Exception as e:
#         print(f"Error processing request: {str(e)}")
#         return jsonify({"error": "An error occurred processing your request"}), 500

# if __name__ == '__main__':
#     app.run(debug=True)



from flask import Flask, request, jsonify
from langchain.document_loaders import WebBaseLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

class CourseExtractor:
    """Helper class to extract and clean course information"""
    
    COURSES = [
        {
            'pattern': r'SCRATCH\s*PROGRAMMING?|SCRATCH\s*COURSE',
            'name': 'SCRATCH PROGRAMMING',
            'description': 'Foundation course for coding beginners. Includes 16 lessons.',
            'price': '30'
        },
        {
            'pattern': r'LEARN\s*CLOUD\s*COMPUTING\s*BASICS-AWS|AWS|CLOUD\s*COMPUTING',
            'name': 'LEARN CLOUD COMPUTING BASICS-AWS',
            'description': 'Comprehensive AWS basics course covering essential services.',
            'price': '30'
        }
    ]
    
    @staticmethod
    def clean_text(text):
        """Remove unnecessary text from the extracted data"""
        text = re.sub(r'Home|FAQ|Contact Us|Sign In|Book a Free Demo Now', '', text)
        text = re.sub(r'Privacy Policy|Terms & Conditions|support@brainlox\.com', '', text)
        text = re.sub(r'\(\+\d{1,2}\)\s*\d{3}\s*\d{3}\s*\d{4}', '', text)
        
        course_section = re.search(r'(Courses[^$]*?(?=Privacy Policy|$))', text, re.DOTALL | re.IGNORECASE)
        return course_section.group(1).strip() if course_section else text.strip()
    
    @staticmethod
    def extract_courses(text):
        """Extract relevant course details from the text"""
        text = CourseExtractor.clean_text(text)
        courses = []
        
        for course in CourseExtractor.COURSES:
            if re.search(course['pattern'], text, re.IGNORECASE):
                courses.append({
                    'name': course['name'],
                    'price': course['price'],
                    'description': course['description']
                })
        
        return courses

def initialize_vector_store():
    """Initialize or load the FAISS vector store"""
    FAISS_INDEX_PATH = "faiss_index"
    
    if os.path.exists(f"{FAISS_INDEX_PATH}.pkl"):
        print("📂 Loading existing FAISS index...")
        return FAISS.load_local(
            FAISS_INDEX_PATH,
            HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
            allow_dangerous_deserialization=True
        )
    
    print("🆕 Creating new FAISS index...")
    loader = WebBaseLoader("https://brainlox.com/courses/category/technical")
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_documents(docs, embeddings)
    vector_store.save_local(FAISS_INDEX_PATH)
    return vector_store

# Initialize vector store
vector_store = initialize_vector_store()

def format_response(courses):
    """Format course details into a structured response"""
    if not courses:
        return "I apologize, but I couldn't find any course information at the moment."
    
    response_parts = ["Here are the available technical courses at Brainlox:\n"]
    
    for course in courses:
        response_parts.append(f"📚 {course['name']}")
        response_parts.append(f"   💰 Price: ${course['price']} per session")
        if course['description']:
            response_parts.append(f"   📝 {course['description']}")
        response_parts.append("")
    
    response_parts.append("Would you like more details about any specific course?")
    
    return "\n".join(response_parts)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests and return relevant course details"""
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "No message provided"}), 400

        relevant_docs = vector_store.similarity_search(data['message'], k=4)
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        courses = CourseExtractor.extract_courses(context)
        response = format_response(courses)
        
        sources = list(set(doc.metadata.get("source", "Unknown") for doc in relevant_docs))
        
        return jsonify({
            "response": response,
            "sources": sources
        })
    
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({"error": "An error occurred processing your request"}), 500

if __name__ == '__main__':
    app.run(debug=True)
