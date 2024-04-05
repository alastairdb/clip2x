{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    devenv = {
      url = "github:cachix/devenv";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    nixpkgs-python = {
      url = "github:cachix/nixpkgs-python";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, devenv, poetry2nix, ... }@inputs:
    let
      system = "x86_64-linux";
      pkgs = import inputs.nixpkgs {
        inherit system;
        overlays = [ self.overlays.${system}.default ];
      };
      binputs = [ pkgs.pandoc pkgs.xclip ];
      inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; })
        mkPoetryApplication;

    in {
      packages.${system} = { default = pkgs.clip2x; };

      overlays.${system}.default = (f: p: {
        clip2x = mkPoetryApplication {
          projectDir = self;
          propagatedBuildInputs = [ f.pandoc f.xclip ];
        };
      });

      devShell.${system} = devenv.lib.mkShell {
        inherit inputs pkgs;
        modules = [
          ({ pkgs, config, ... }: {
            # This is your devenv configuration
            packages = binputs;

            languages.python.enable = true;
            languages.python.version = "3.11";

            languages.python.poetry.enable = true;
            languages.python.poetry.activate.enable = true;

          })
        ];
      };
    };
}
