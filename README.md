Please export your OPENAI_API_TOKEN before running!!!


# Linux/MacOs
Only use sudo if nothing else works!!
```
sudo docker build -t backend .
export OPENAI_API_TOKEN="my_token"
sudo docker  run -it -p 8080:8080 -e OPENAI_API_TOKEN=$OPENAI_API_TOKEN -v ./app:/app/app -v  ./data:/app/data -v ./images:/etc/images -v ./logs:/etc/logs  backend
```

# Windows
```
docker build -t backend .
set OPENAI_API_TOKEN="my_token"
docker  run -it -p 8080:8080 -e OPENAI_API_TOKEN=%OPENAI_API_TOKEN% -v ./app:/app/app -v  ./data:/app/data -v ./images:/etc/images -v ./logs:/etc/logs backend
```