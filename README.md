# Web Shop API - Python3 + Docker #

3 Types of users: 
  - Admin: deleting users, checking statistics
  - Storekepeer: adding products to DB via file 
  - Buyer: searching and buying products, checking his own orders
 
### REQUESTS ###

 - #### port 5001 - ADMIN - Admin Authorization token needed ###
    - [GET] /productStatistics
    - [GET] /categoryStatistics

- #### port 5002 - AUTHENTICATION ####
  - [POST] /register - 
        example:
        ```json
        {
            "forename": "...",
            "surname": "...",
            "email": "...",
            "password": "...",
            "isCustomer": True
        }
        ```
    - [POST] /login -  returns Authorization Tokens
        example:
        ```json
        {
        "email": "...",
        "password": "..."
        }
        ```
    - [POST] /refresh -  Any Authorization token needed
        example:
        ```json
        {
        "Authorization": "Bearer <REFRESH_TOKEN>"
        }
        ```
    - [POST] delete - Admin Authorization token needed
        example:
        ```json
        {
            "email": "..."
        }
        ```  
 
- #### port 5003 - STOREKEPEER - Storekepeer Authorization token needed ####
    - [POST[ /update [POST] - Request contains CSV file  Categories,Product,Quantity,Price. Multiple categories are delimited by '|' "pipe", if product exists categories must all have same name as product already in DB
    - Deamon thread is tasked with input handling, working together with Storekepeer although inaccessible to user  ./shop/deamon.py
    
 - #### port 5004 - BUYER - Buyer Authorization token needed ####
    - [GET] /search?name=<PRODUCT_NAME>&category=<CATEGORY_NAME> 
    - [POST] /order - Orders can be PENDING or DELIVERED
        example:
        ```json
        {
            "requests": [
                {
                    "id": 1,
                    "quantity":2
                },
                {
                    "id": 3,
                    "quantity":4
                }
            ]
        }
        ```
    - [GET] /status - returns status of all of buyer's orders
    
    
    
# Runing the server

In order to run this web server, you will need docker. Create images from dockerfiles and run the following command
```bash
docker swarm init --advertise-addr 127.0.0.1
docker stack deploy --compose-file <path_to_stack.yaml> <name_of_server>
```
In order to close the swarm
```bash
docker swarm leave --force
```

Database can be checked using adminer on ``localhost:8080`` adress.
Tests can be run with the following commands - names for roles should match those already in DB, at start only "admin"
```bash
python tests/main.py --type all --with-authentication --authentication-address http://127.0.0.1:5002 --jwt-secret "JWT_SECRET_KEY" --roles-field roles --administrator-role "admin" --customer-role "kupac" --warehouse-role "magacioner" --customer-address http://127.0.0.1:5004 --warehouse-address http://127.0.0.1:5003 --administrator-address http://127.0.0.1:5001
```
For the specific test, you can run following commands
- Authentication test
```bash
python tests/main.py --type authentication --authentication-address http://127.0.0.1:5002 --jwt-secret "JWT_SECRET_KEY" --roles-field roles --administrator-role "admin" --customer-role "kupac" --warehouse-role "magacioner"
```
- Level 0 test
```bash
python tests/main.py --type level0 --with-authentication --authentication-address http://127.0.0.1:5002 --customer-address http://127.0.0.1:5004 --warehouse-address http://127.0.0.1:5003
```
- Level 1 test
```bash
python tests/main.py --type level1 --with-authentication --authentication-address http://127.0.0.1:5002 --customer-address http://127.0.0.1:5004 --warehouse-address http://127.0.0.1:5003
```
- Level 2 test
```bash
python tests/main.py --type level2 --with-authentication --authentication-address http://127.0.0.1:5002 --customer-address http://127.0.0.1:5004 --warehouse-address http://127.0.0.1:5003
```
- Level 3 test
```bash
python tests/main.py --type level3 --with-authentication --authentication-address http://127.0.0.1:5002 --customer-address http://127.0.0.1:5004 --warehouse-address http://127.0.0.1:5003 --administrator-address http://127.0.0.1:5001
```
Tests do not delete contents of DB nor do they reset AI, you must do it for correct results in repeated test.
Changes in code are updated in docker only after deploying that image and running cluster again - tips are to reset docker after leaving swarm and giving diferent name to your new server, docker has trouble with reconecting to adminer again and this hepled me avoiding the issue.
