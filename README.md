## HCA Backend

### Prerequisites

To use the `gpt-image-1` model in this project, ensure you have:

1. **A valid OpenAI API key**  
    - Your OpenAI profile must be verified.  
    - Visit [OpenAI Organization Settings](https://platform.openai.com/settings/organization/general) and check the "Verifications" section for a "Verified" status.

2. **Sufficient account balance**  
    - Make sure your balance covers usage of the `gpt-image-1` model.

3. **Export your API token**  
    - Obtain your token from [OpenAI API Keys](https://platform.openai.com/settings/organization/api-keys).
    - Export the token as an environment variable before running the backend:

      ```bash
      export OPENAI_API_TOKEN="your_token_here"
      ```

**Note:** The backend will not work without a verified profile and a valid API token.

### Linux/MacOs
Only use sudo if nothing else works!!

```
sudo docker build -t backend .
export OPENAI_API_TOKEN="my_token"
sudo docker  run -it -p 8080:8080 -e OPENAI_API_TOKEN=$OPENAI_API_TOKEN -v ./app:/app/app -v  ./data:/app/data -v ./images:/etc/images -v ./logs:/etc/logs -v ./audio:/etc/audio backend
```

### Windows
```
docker build -t backend .
set OPENAI_API_TOKEN="my_token"
docker  run -it -p 8080:8080 -e OPENAI_API_TOKEN=%OPENAI_API_TOKEN% -v ./app:/app/app -v  ./data:/app/data -v ./images:/etc/images -v ./logs:/etc/logs -v ./audio:/etc/audio backend
```
