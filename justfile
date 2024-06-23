serve:
   npm start

build:
   npm run build

deploy:
   GIT_USER=fusion44 USE_SSH=true yarn deploy

update-all:
	npm update
	yarn upgrade
	nix flake update

# format all Nix and Lua files
format:
  prettier -w .
