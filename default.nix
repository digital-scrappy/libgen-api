{ pkgs ? import <nixpkgs> {} }:

(pkgs.buildFHSUserEnv {
  name = "pipzone";
  targetPkgs = pkgs: (with pkgs; [
    python39
    python39Packages.pip
    python39Packages.poetry
    python39Packages.virtualenv
    python39Packages.urllib3
  ]);
  runScript = "bash";
}).env
