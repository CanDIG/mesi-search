{ pkgs ? import <nixpkgs> {} }:
with pkgs;
mkShell {
  VENV = "env";
  buildInputs = [
    git
    python38Full
    stdenv
    libpqxx
    zlib
    zlib.dev
    libffi
    libffi.dev
    travis
  ];
  shellHook = ''
    export PYTHONPATH=`pwd`/$VENV/${python.sitePackages}:$PYTHONPATH

  '';
}
