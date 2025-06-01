RUN THIS BOY
NOW WITH PERSISTENCE BOO <3 Hopefully nothing crashes lol

the sudo only if u get permission problems
```
sudo docker build -t backend .
sudo docker  run -it -p 8080:8080 -v ./app:/app/app -v  ./data:/app/data -v ./images:/etc/images backend

```
