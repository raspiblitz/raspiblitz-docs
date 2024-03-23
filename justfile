serve:
   npm start

build:
   npm run build

deploy:
   GIT_USER=fusion44 USE_SSH=true yarn deploy

# format all Nix and Lua files
format:
  prettier -w .
