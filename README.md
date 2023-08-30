# Wildlife App Server

## Introduction

The Wildlife App Server is a Flask application that serves as the core backend for handling image classification, user and image management, and communication with wildlife cameras. It stores and retrieves wildlife images, providing data to the frontend application for display and interaction.

## Technologies Used

- **Python**: The programming language used.
- **Flask**: Main framework used to build the server.
- **SQAlchemy**: Framework used to interact with the SQLite database in Python code.
- **SQLite**: Database used for storing user, camera, and image information.

## Features

### Image Management

- **Upload Image**: Accepts images from cameras, along with classification and date information, and stores them for retrieval.
- **Serve Images**: Retrieves images sorted by date and sends them to the frontend for display.
- **Delete Image**: Allows for deletion of images by ID.

### Camera Integration

- **Camera Model**: Manages the relationship between cameras and users, storing camera details and linking to captured images.

### User Management (Future Implementation)

- **User Model**: Designed to manage user information, including authentication and personal details (not implemented yet).

## Endpoints

- `POST /upload`: Handles image upload from cameras.
- `GET /images`: Provides a list of images sorted by date.
- `GET /image/<filename>`: Serves a specific image by filename.
- `DELETE /image/<image_id>`: Deletes an image by ID.

### Future Features

- **User Specific Interactions**: Although, user login has not been implemented, the infrastructure is there to allow users to securely access only images from their own cameras.
- **Notifications**: Implement a notification system for specific animal sightings.
- **User Classification**: Allow users to relabel images in the case of a classification error.

## Code Structure

The code is divided into two main parts:

- **server.py**: Handles the core functionality, including routes and interactions with the database.
- **models.py**: Defines the database models for users, cameras, and images.

## Challenges and Solutions

### Challenge: Image Storage and Retrieval

- **Problem**: Implementing a scalable database system.
- **Solution**: Created three models. The User model has a one-to-many relationship with Camera, and Camera has a one-to-many with Image. This allows the server to retrieve camera specific images as the user requests.

## Contact

Name - Heston Vaughan  
Email - [heston.cv@gmail.com](mailto:heston.cv@gmail.com)  
Project Link: [https://github.com/username/wildlife-app-server](https://github.com/username/wildlife-app-server)
