{ pkgs }: {
  deps = [
    pkgs.python314
    pkgs.python314Packages.pip
    # System deps for Pygame
    pkgs.libGL
    pkgs.xorg.libX11
    pkgs.xorg.libXext
    pkgs.xorg.libXrender
    pkgs.SDL2
    pkgs.SDL2_image
    pkgs.SDL2_mixer
    pkgs.SDL2_ttf
    # Virtual display for headless Pygame
    pkgs.xvfb-run
    pkgs.xorg.xorgserver
  ];
}
