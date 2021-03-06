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
    stdenv.cc.cc.lib
    pam
    python38Packages.tox
  ];
  shellHook = ''
    export PYTHONPATH=`pwd`/$VENV/${python.sitePackages}:$PYTHONPATH;
    export LD_LIBRARY_PATH="${stdenv.cc.cc.lib}/lib64:$LD_LIBRARY_PATH";
  '';
}
