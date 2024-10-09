serve:
   npm start

build:
   npm run build

update-all:
	npm update
	nix flake update

# format all Nix and Lua files
format:
  prettier -w .
