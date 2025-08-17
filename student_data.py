# STUDENT DATA CONFIGURATION
# Add your student details here for each roll number (2473A31XXX pattern)
# Format: "roll_number": {"name": "Student Name", "semester": "X", "section": "Y"}

STUDENT_DATA = {
    # Example entries - Replace with your actual student data
    "2473A31139": {
        "name": "Sample Student",
        "semester": "3", 
        "section": "A"
    },
    
    # Add your students here:
    # "2473A31001": {
    #     "name": "John Doe",
    #     "semester": "3",
    #     "section": "A"
    # },
    # "2473A31002": {
    #     "name": "Jane Smith", 
    #     "semester": "3",
    #     "section": "A"
    # },
    # "2473A31003": {
    #     "name": "Mike Johnson",
    #     "semester": "3", 
    #     "section": "B"
    # },
    
    # Continue adding students following this pattern...
    # Maximum possible: 2473A31000 to 2473A31999 (1000 students)
}

# Admin user (keep this)
ADMIN_DATA = {
    "admin": {
        "name": "Department Admin",
        "semester": "",
        "section": "",
        "role": "admin"
    }
}