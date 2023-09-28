# Wildlife App Server

## Introduction

The Wildlife App Server is a Flask application that serves as the core backend for handling image classification, user and image management, and communication with wildlife cameras. It stores and retrieves wildlife images, providing data to the frontend application for display and interaction.

## Technologies Used

- **Python**: The programming language used.
- **Flask**: Main framework used to build the server.
- **Flask-SQAlchemy**: Framework used to interact with the SQLite database in Python code.
- **Flask-JWT-Extended**: For JWT-based authentication.
- **SQLite**: Database used for storing user, camera, and image information.
- **PIL (Pillow)**: For image manipulation.
- **bcrypt**: For password hashing and verification.

## Features

### Image Management

- **Upload Image**: Receives JPEG images from authenticated cameras, captures the current timestamp, and stores both full-size and thumbnail versions of the image. Additionally, it establishes the necessary database relationships to link the image with the corresponding camera.
- **Serve Images**: Serves image meta data that can be used by the frontend to request either the thumbnail sized version or the full-sized.
- **Delete Image**: Allows for deletion of images by ID.

### Camera Integration

- **Camera Model**: Manages the relationship between cameras and users, storing camera details and linking to captured images.
- **Camera Pairing**: Allows users to pair cameras using a unique token.

### User Management

- **User Model**: Manages user information, including authentication and personal details.
- **JWT Authentication**: Securely manages user sessions.
- **User Registration**: Allows new users to register.
- **User Login**: Allows existing users to login using email and password.
- **Password Hashing**: Stores hashed passwords for security.

![Class Diagram](https://i.imgur.com/Nbk4NMg.png)
## Endpoints

### User Management
- `POST /register`: User registration.
- `POST /login`: User login.
- `POST /validate_token`: Validates JWT tokens.

### Image Management
- `POST /images`: Handles image upload from cameras.
- `GET /images/data`: Provides a list of image metadata.
- `GET /images/<int:image_id>/full`: Serves a full-size image.
- `GET /images/<int:image_id>/thumbnail`: Serves a thumbnail image.
- `GET /cameras/<int:camera_id>/images/data`: Retrieves image data for a specific camera.
- `GET /class/<string:class_name>/images/data`: Retrieves images based on their classification.
  
### Camera Management
- `POST /cameras`: Pairs a camera with a user.
- `GET /cameras/<string:token>/check_pair`: Checks if a camera is paired.

## Future Features

- **Image Classification**: Integrate a machine learning model for categorizing wildlife images with appropriate tags.
- **Notifications**: Implement a notification system for specific animal sightings.
- **User Image Classification**: Allow users to relabel images in the case of a classification error for further training.

## Code Structure

- `app/`: Core application folder
  - `__init__.py`: Initializes Flask app and database.
  - `models/`: Contains database models.
    - `user.py`: User model.
    - `camera.py`: Camera model.
    - `image.py`: Image model.
  - `routes/`: Contains route definitions.
    - `user_routes.py`: User-related routes.
    - `camera_routes.py`: Camera-related routes.
    - `image_routes.py`: Image-related routes.
  - `utils.py`: Utility functions like password hashing.
- `run.py`: Entry point for running the Flask app.

## Challenges and Solutions

### Challenge: Image Storage and Retrieval

- **Problem**: Implementing a scalable database system.
- **Solution**: Created three models. The User model has a one-to-many relationship with Camera, and Camera has a one-to-many with Image. This allows the server to retrieve camera specific images as the user requests.

### Challenge: User Authentication and Security

- **Problem**: Securely managing user sessions and passwords.
- **Solution**: Implemented JWT-based authentication and used bcrypt for password hashing and verification.

## Contact

Name - Heston Vaughan  
Email - [heston.cv@gmail.com](mailto:heston.cv@gmail.com)  
Project Link: [https://github.com/HestonCV/wildlife-app-server](https://github.com/HestonCV/wildlife-app-server)
