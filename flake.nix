{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { systems
    , nixpkgs
    , ...
    } @ inputs:
    let
      eachSystem = f:
        nixpkgs.lib.genAttrs (import systems) (
          system:
          f nixpkgs.legacyPackages.${system}
        );
    in
    {
      devShells = eachSystem (pkgs: {
        default = pkgs.mkShell {
          buildInputs = [
            pkgs.nodejs
            pkgs.nodePackages.pnpm
            pkgs.yarn
            pkgs.nodePackages.prettier
          ];
        };
      });
    };
}
