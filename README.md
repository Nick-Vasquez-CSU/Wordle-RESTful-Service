### Backend Project 2

| Group 5         |
| --------------- |
| Himani Tawade   |
| Satish Bisa     |
| Nick Vasquez    |
| Akhil  |

##### HOW TO RUN THE PROJECT

1. Copy the contents of our [nginx config file](https://github.com/himanitawade/Web-Back-End-Project2/blob/master/nginxconfig.txt) into a new file within `/etc/nginx/sites-enabled` called `nginxconfig`. Assuming the nginx service is already running, restart the service using `sudo service nginx restart`.

Nginx Config:

```
server {
    listen 80;
    listen [::]:80;

    server_name tuffix-vm;

    location /registration {
        proxy_pass http://127.0.0.1:5000/registration;
    }

    location /newgame {
        auth_request /auth;
        proxy_pass http://gameservice;
    }

    location /addguess {
            auth_request /auth;
            proxy_pass http://gameservice;
    }

    location /allgames {
            auth_request /auth;
            proxy_pass http://gameservice;
    }

    location /onegame {
        auth_request /auth;
        proxy_pass http://gameservice;
    }


    location = /auth {
           internal;
           proxy_pass http://127.0.0.1:5000/login;
    }

}

upstream gameservice {
    server 127.0.0.1:5100;
    server 127.0.0.1:5200;
    server 127.0.0.1:5300;
}
```

1. Initialize primary, secondary1, and secondary2 directories properly.

 ```c
      In the var folder...
       
        - add a folder "primary", with folders "data" and "mount" inside of it.
        - add a folder "mount" inside of secondary1 folder.
        - add a folder "mount" inside of secondary2 folder.
   ```



2. Start the API (from project folder)

   ```c
      foreman start
      // NOTE: if there's an error upon running this where it doesn't recognize hypercorn, log out of Ubuntu and log back in. If        there is an error regarding ./bin/litefs specifically run "chmod +x ./bin/litefs" first, then retry "foreman start". 
   ```

3. Initialize the databases/database replicas within the var folder (from project folder)

   ```c
      // step 1. give the script permissions to execute
      chmod +x ./bin/init.sh

      // step 2. run the script
      ./bin/init.sh
   ```

4. Populate the word databases

   ```c
      python3 dbpop.py
   ```

5. Test all the endpoints using httpie
   - user
      - register account: `http POST http://tuffix-vm/registration username="yourusername" password="yourpassword"`
    
       Sample Output:
       ```
      {
         "id": 3,
         "password": "tawade",
         "username": "himani"
      }
      ```
     - login {Not accesible}: 'http --auth himani:tawade GET http://tuffix-vm/login'
     Sample Output:
     ```
      HTTP/1.1 404 Not Found
      Connection: keep-alive
      Content-Encoding: gzip
      Content-Type: text/html
      Date: Fri, 18 Nov 2022 21:04:31 GMT
      Server: nginx/1.18.0 (Ubuntu)
      Transfer-Encoding: chunked

      <html>
      <head><title>404 Not Found</title></head>
      <body>
      <center><h1>404 Not Found</h1></center>
      <hr><center>nginx/1.18.0 (Ubuntu)</center>
      </body>
      </html>
      ```
   - game

      NOTE:
        - all functions which WRITE to db are written specifically to the PRIMARY database connection.
        - all functions which READ to db are read specifically from either one of the 3 database connections:
            - PRIMARY
            - SECONDARY1
            - SECONDARY2
          this is handled by randomly (using random.choice()) selecting a DB connection from a list of them whenever a GET                 method is called. When executing a GET method, you can see in the terminal the addresses of all the DB connections,             and the address of the specific DB that ends up being used for the actual read. This is how we handled the Read                 Distribution Functionality. 

      - create a new game: `http --auth yourusername:yourpassword POST http://tuffix-vm/newgame`
      
      Sample Output:
      ```
      'http --auth himani:tawade POST http://tuffix-vm/newgame'
      {
         "answerid": 3912,
         "gameid": "b0039f36-6784-11ed-ba4a-615e339a8400",
         "username": "himani"
      }
      ```
      Note - this will return a `gameid`
    - add a guess: `http --auth yourusername:yourpassword PUT http://tuffix-vm/addguess gameid="gameid" word="yourguess"`

    Sample Output:
    ```
      http --auth himani:tawade PUT http://tuffix-vm/addguess gameid="b0039f36-6784-11ed-ba4a-615e339a8400" word="amigo"
     {
        "Accuracy": "XXOOO",
        "guessedWord": "amigo"
     }
     ```
    - display your active games: `http --auth yourusername:yourpassword GET http://tuffix-vm/allgames`

    Sample Output:
    ```
      http --auth himani:tawade GET http://tuffix-vm/allgames
      [
         {
            "gameid": "b0039f36-6784-11ed-ba4a-615e339a8400",
            "gstate": "In-progress",
            "guesses": 1
         }
      ]
      ```
    - display the game status and stats for one game: `http --auth yourusername:yourpassword GET http://tuffix-vm/onegame?id=gameid`
       - example: `.../onegame?id=b97fcbb0-6717-11ed-8689-e9ba279d21b6`
    Sample Output:
    ```
      http --auth himani:tawade GET http://tuffix-vm/onegame?id="b0039f36-6784-11ed-ba4a-615e339a8400"
      [
         {
             "gameid": "b0039f36-6784-11ed-ba4a-615e339a8400",
            "gstate": "In-progress",
            "guesses": 1
          },
          {
             "accuracy": "XXOOO",
             "guessedword": "amigo"
          }
      ]
      ```
