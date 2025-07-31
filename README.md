# Central-News-Fetcher
this is a news fetcher for telegram working as a bot for channels.

How to Build and Run with Docker
Build the Docker image:
    From your project's root directory, run:

     docker build -t telegram-news-bot .

Run the Docker container:
You need to pass your .env file to the container so it can access your configuration. 

   ````docker run --env-file .env --name my-news-bot -d telegram-news-bot````

`--env-file .env`: Securely passes your environment variables.

`--name my-news-bot`: Gives your container a memorable name.

`-d`: Runs the container in detached mode (in the background).

To view logs:
`docker logs -f my-news-bot`


To stop the container:
`docker stop my-news-bot`
