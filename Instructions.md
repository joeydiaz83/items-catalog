`OBJECTIVE:`</br>
-  Develop an application that provides:
 - a list of items within a variety of categories
 - user registration
 - authentication


 **Note:** Registered users will have the ability to post, edit and delete their own items.

 ** Project Display Example **</br>
 You are encouraged to redesign and strive for even better solutions on the frontend.

 `http://localhost:8000/`
 ![image1](images/image1.png)
 In this sample project, the homepage displays all current categories along with the latest added items.

 `http://localhost:8000/catalog/Snowboarding/items`
![image2](images/image2.png)
Selecting a specific category shows you all the items available for that category.

`http://localhost:8000/catalog/Snowboarding/Snowboard`
![image3](images/image3.png)
Selecting a specific item shows you specific information of that item.

`http://localhost:8000/ (logged in)`
![image4](images/image4.png)
After logging in, a user has the ability to add, update, or delete item info.

`http://localhost:8000/catalog/Snowboarding/Snowboard (logged in)`
![image5](images/image5.png)

`http://localhost:8000/catalog/Snowboard/edit (logged in)`
![image6](/Users/joeydiaz/Desktop/Udacity-Full_Stack_nano_degree/FSND-Virtual-Machine/vagrant/Project2_item_catalog/image6.png)

`http://localhost:8000/catalog/Snowboard/delete (logged in)`
![image7](images/image6.png)

`http://localhost:8000/catalog.json`
![image7](images/image7.png)
The application provides a JSON endpoint, at the very least


`ITERATIVE DEVELOPMENT CHECKLIST`
- [ ] **Mock-ups** </br>
Creation of mock-ups for every page and design URLs for each page

- [ ] **Routing** </br>
Setup all the routing for the application in Flask, ensuring I can navigate to all pages (even though not created yet)

- [ ] **Templates & Forms** </br>
Create all templates and forms ensuring they all render properly

- [ ] **C.R.U.D. Functionality** </br>
Ensure all the actions are retrieving data from the database

- [ ] **API Endpoints** </br>
Allow data to be sent if the client request a specific item in JSON form</br>
Test this API calls in your browser to ensure to finish this step

- [ ] **Styling & Message Flashing** </br>
Add styling with javascript, css and a few static images.

Left it on Lesson 4: Iterative Development, video 4
